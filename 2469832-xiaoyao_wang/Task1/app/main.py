from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import base64
import hashlib
import hmac
import secrets
import time
from functools import wraps

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
CORS(app)

order_db = []

# ----------------------------
# Auth + users (added)
# ----------------------------

# In-memory user DB:
# users[user_id] = { id, email, password_hash, role }
users = {}

# Simple session store:
# sessions[token] = { user_id, created_at, revoked }
sessions = {}

ALLOWED_ROLES = {"merchant", "user", "customer", "admin"}


def _json_error(message, status=400, code=None):
    payload = {"error": message}
    if code:
        payload["code"] = code
    return jsonify(payload), status


def _hash_password(password: str) -> str:
    # Simple SHA256 hashing. (In production, use bcrypt/argon2 + salt.)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(_hash_password(password), password_hash)


def _make_token(user_id: int) -> str:
    # "JWT-like" token without JWT lib: base64(payload).base64(signature)
    # payload = "uid:<id>|ts:<epoch>|nonce:<random>"
    payload = f"uid:{user_id}|ts:{int(time.time())}|nonce:{secrets.token_urlsafe(16)}"
    payload_b64 = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8").rstrip("=")

    # signature is just random secret per session to allow invalidation; stored server-side
    sig = secrets.token_urlsafe(24).encode("utf-8")
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")

    return f"{payload_b64}.{sig_b64}"


def _get_bearer_token():
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None
    parts = auth.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0].strip(), parts[1].strip()
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def _get_current_user():
    token = _get_bearer_token()
    if not token:
        return None, None

    session = sessions.get(token)
    if not session or session.get("revoked"):
        return None, token

    user = users.get(session["user_id"])
    if not user:
        return None, token

    return user, token


def require_auth(roles=None):
    """
    Role-based access control decorator.
    - roles=None: any authenticated user
    - roles=set/list/tuple of roles: must match user's role
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, _token = _get_current_user()
            if not user:
                return _json_error("Unauthorized", status=401, code="unauthorized")

            if roles is not None:
                allowed = set(roles)
                if user.get("role") not in allowed:
                    return _json_error("Forbidden", status=403, code="forbidden")

            # attach to request context (simple)
            request.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ----------------------------
# Existing endpoints (kept working)
# ----------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/cart/checkout", methods=["POST"])
@require_auth(roles={"customer", "user", "admin"})
def cart_checkout():
    """
    Basic checkout stub. Creates an order in order_db.
    Accepts any JSON; expects optionally: items, total, merchant_id.
    """
    data = request.get_json(silent=True) or {}
    user = request.current_user

    order = {
        "id": len(order_db) + 1,
        "user_id": user["id"],
        "role": user["role"],
        "items": data.get("items", []),
        "total": data.get("total", 0),
        "merchant_id": data.get("merchant_id"),
        "status": "created",
        "created_at": int(time.time()),
    }
    order_db.append(order)
    return jsonify({"order": order}), 201


@app.route("/orders", methods=["GET"])
@require_auth(roles={"customer", "user", "admin"})
def orders():
    """
    Returns:
    - admin: all orders
    - others: only own orders
    """
    user = request.current_user
    if user["role"] == "admin":
        return jsonify({"orders": order_db}), 200

    mine = [o for o in order_db if o.get("user_id") == user["id"]]
    return jsonify({"orders": mine}), 200


@app.route("/merchant/suborders", methods=["GET"])
@require_auth(roles={"merchant", "admin"})
def merchant_suborders():
    """
    Merchant view:
    - admin: all orders
    - merchant: orders matching merchant_id == user.id
    """
    user = request.current_user
    if user["role"] == "admin":
        return jsonify({"suborders": order_db}), 200

    mine = [o for o in order_db if o.get("merchant_id") == user["id"]]
    return jsonify({"suborders": mine}), 200


# ----------------------------
# Auth endpoints
# ----------------------------

def _find_user_by_email(email: str):
    for _uid, u in users.items():
        if u.get("email", "").lower() == (email or "").lower():
            return u
    return None


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "").strip().lower()

    if not email or not password or not role:
        return _json_error("email, password, and role are required", 400, "bad_request")

    if role not in ALLOWED_ROLES:
        return _json_error(f"Invalid role. Allowed: {sorted(ALLOWED_ROLES)}", 400, "invalid_role")

    if _find_user_by_email(email):
        return _json_error("Email already registered", 409, "email_exists")

    user_id = len(users) + 1
    user = {"id": user_id, "email": email, "password_hash": _hash_password(password), "role": role}
    users[user_id] = user

    # Return safe user object (no password_hash)
    safe = {"id": user["id"], "email": user["email"], "role": user["role"]}
    return jsonify({"user": safe}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return _json_error("email and password are required", 400, "bad_request")

    user = _find_user_by_email(email)
    if not user or not _verify_password(password, user["password_hash"]):
        return _json_error("Invalid credentials", 401, "invalid_credentials")

    token = _make_token(user["id"])
    sessions[token] = {"user_id": user["id"], "created_at": int(time.time()), "revoked": False}

    safe = {"id": user["id"], "email": user["email"], "role": user["role"]}
    return jsonify({"token": token, "user": safe}), 200


@app.route("/api/logout", methods=["POST"])
@require_auth()
def api_logout():
    _user, token = _get_current_user()
    if not token:
        return _json_error("Unauthorized", 401, "unauthorized")

    if token in sessions:
        sessions[token]["revoked"] = True

    return jsonify({"ok": True}), 200


@app.route("/api/me", methods=["GET"])
@require_auth()
def api_me():
    user = request.current_user
    safe = {"id": user["id"], "email": user["email"], "role": user["role"]}
    return jsonify({"user": safe}), 200


# ----------------------------
# Role dashboards (added)
# ----------------------------

@app.route("/api/dashboard/customer", methods=["GET"])
@require_auth(roles={"customer"})
def dashboard_customer():
    user = request.current_user
    my_orders = [o for o in order_db if o.get("user_id") == user["id"]]
    return jsonify(
        {
            "role": "customer",
            "summary": {"my_orders": len(my_orders)},
            "recent_orders": sorted(my_orders, key=lambda x: x.get("created_at", 0), reverse=True)[:10],
        }
    ), 200


@app.route("/api/dashboard/user", methods=["GET"])
@require_auth(roles={"user"})
def dashboard_user():
    user = request.current_user
    my_orders = [o for o in order_db if o.get("user_id") == user["id"]]
    total_spent = sum(float(o.get("total") or 0) for o in my_orders)
    return jsonify(
        {
            "role": "user",
            "summary": {"my_orders": len(my_orders), "total_spent": total_spent},
        }
    ), 200


@app.route("/api/dashboard/merchant", methods=["GET"])
@require_auth(roles={"merchant"})
def dashboard_merchant():
    user = request.current_user
    my_suborders = [o for o in order_db if o.get("merchant_id") == user["id"]]
    revenue = sum(float(o.get("total") or 0) for o in my_suborders)
    return jsonify(
        {
            "role": "merchant",
            "summary": {"suborders": len(my_suborders), "revenue": revenue},
            "recent_suborders": sorted(my_suborders, key=lambda x: x.get("created_at", 0), reverse=True)[:10],
        }
    ), 200


@app.route("/api/dashboard/admin", methods=["GET"])
@require_auth(roles={"admin"})
def dashboard_admin():
    by_role = {}
    for u in users.values():
        by_role[u["role"]] = by_role.get(u["role"], 0) + 1

    return jsonify(
        {
            "role": "admin",
            "summary": {
                "users_total": len(users),
                "users_by_role": by_role,
                "orders_total": len(order_db),
                "active_sessions": sum(1 for s in sessions.values() if not s.get("revoked")),
            },
        }
    ), 200


# Admin management helpers (optional but useful for dashboard needs)
@app.route("/api/admin/users", methods=["GET"])
@require_auth(roles={"admin"})
def admin_list_users():
    safe_users = [{"id": u["id"], "email": u["email"], "role": u["role"]} for u in users.values()]
    return jsonify({"users": safe_users}), 200


@app.route("/api/admin/orders", methods=["GET"])
@require_auth(roles={"admin"})
def admin_list_orders():
    return jsonify({"orders": order_db}), 200


# ----------------------------
# (Optional) Static/template routes remain compatible if used elsewhere
# ----------------------------

@app.route("/", methods=["GET"])
def index():
    # If you had a template, keep behavior; otherwise return a simple JSON.
    template_path = os.path.join(app.template_folder or "", "index.html")
    if os.path.exists(template_path):
        return render_template("index.html")
    return jsonify({"message": "Flask API"}), 200


@app.route("/static/<path:path>", methods=["GET"])
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    # Seed an admin user for convenience (only if none exist)
    if not any(u.get("role") == "admin" for u in users.values()):
        admin_id = len(users) + 1
        users[admin_id] = {
            "id": admin_id,
            "email": "admin@example.com",
            "password_hash": _hash_password("admin123"),
            "role": "admin",
        }

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)