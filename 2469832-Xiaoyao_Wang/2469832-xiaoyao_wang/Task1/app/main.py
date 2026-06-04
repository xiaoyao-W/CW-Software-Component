from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import base64
import hashlib
import hmac
import secrets
import time
from functools import wraps

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'), 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
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
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def _current_user():
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


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user, _token = _current_user()
        if not user:
            return _json_error("unauthorized", 401)
        # attach to request context (simple)
        request.user = user
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    roles_set = set(roles)

    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user:
                return _json_error("unauthorized", 401)
            if user.get("role") not in roles_set:
                return _json_error("forbidden", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _safe_user(u):
    if not u:
        return None
    return {"id": u["id"], "email": u["email"], "role": u["role"]}


# ----------------------------
# Frontend routes
# ----------------------------

@app.route('/')
def index():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/login')
def login_page():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/user_dashboard')
def user_dashboard_page():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'user_dashboard.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/merchant_dashboard')
def merchant_dashboard_page():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'merchant_dashboard.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/admin_dashboard')
def admin_dashboard_page():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'admin_dashboard.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/register')
def register_page():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)

# ----------------------------
# Existing endpoints (kept)
# ----------------------------

@app.get("/health")
def health():
    return jsonify(status="ok")


# ----------------------------
# Auth endpoints (added)
# ----------------------------

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "").strip().lower()

    if not email:
        return _json_error("missing email", 400)
    if not password:
        return _json_error("missing password", 400)
    if role not in ALLOWED_ROLES:
        return _json_error(f"invalid role (allowed: {sorted(ALLOWED_ROLES)})", 400)

    if any(u["email"] == email for u in users.values()):
        return _json_error("email already registered", 409)

    user_id = len(users) + 1
    user = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "role": role,
    }
    users[user_id] = user

    return jsonify(user=_safe_user(user)), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email:
        return _json_error("missing email", 400)
    if not password:
        return _json_error("missing password", 400)

    user = next((u for u in users.values() if u["email"] == email), None)
    if not user or not _verify_password(password, user["password_hash"]):
        return _json_error("invalid credentials", 401)

    token = _make_token(user["id"])
    sessions[token] = {"user_id": user["id"], "created_at": int(time.time()), "revoked": False}

    return jsonify(token=token, user=_safe_user(user)), 200


@app.post("/api/logout")
@login_required
def logout():
    _user, token = _current_user()
    if token and token in sessions:
        sessions[token]["revoked"] = True
    return jsonify(status="logged_out"), 200


@app.get("/api/me")
@login_required
def me():
    user = getattr(request, "user", None)
    return jsonify(user=_safe_user(user)), 200


# ----------------------------
# Role dashboards (added)
# ----------------------------

@app.get("/api/dashboard/customer")
@roles_required("customer")
def customer_dashboard():
    user = request.user
    # show customer's cart + orders
    carts = [o for o in order_db if o.get("type") == "cart" and str(o.get("customer_id")) == str(user["id"])]
    orders = [o for o in order_db if o.get("type") == "order" and str(o.get("customer_id")) == str(user["id"])]
    return jsonify(user=_safe_user(user), carts=carts, orders=orders), 200


@app.get("/api/dashboard/merchant")
@roles_required("merchant")
def merchant_dashboard():
    user = request.user
    # show merchant suborders by merchant_id if present, else all (demo-friendly)
    suborders = [o for o in order_db if o.get("type") == "suborder" and str(o.get("merchant_id")) == str(user["id"])]
    return jsonify(user=_safe_user(user), suborders=suborders), 200


@app.get("/api/dashboard/user")
@roles_required("user")
def user_dashboard():
    user = request.user
    # "platform user" summary (demo)
    total_orders = len([o for o in order_db if o.get("type") == "order"])
    total_carts = len([o for o in order_db if o.get("type") == "cart"])
    return jsonify(user=_safe_user(user), metrics={"orders": total_orders, "carts": total_carts}), 200


@app.get("/api/dashboard/admin")
@roles_required("admin")
def admin_dashboard():
    user = request.user
    role_counts = {r: 0 for r in sorted(ALLOWED_ROLES)}
    for u in users.values():
        role_counts[u["role"]] = role_counts.get(u["role"], 0) + 1

    return jsonify(
        user=_safe_user(user),
        stats={
            "users": len(users),
            "sessions": len([s for s in sessions.values() if not s.get("revoked")]),
            "orders": len([o for o in order_db if o.get("type") == "order"]),
            "role_counts": role_counts,
        },
    ), 200


# ----------------------------
# Existing endpoints (protected + kept working)
# ----------------------------

# Endpoint for Story 1: Customer
@app.route("/cart/items", methods=["POST"])
@roles_required("customer")
def add_to_cart():
    data = request.get_json(silent=True) or {}

    # Keep existing behavior, but if customer_id missing, default to authenticated user id
    if "customer_id" not in data:
        data["customer_id"] = request.user["id"]

    for k in ("customer_id", "stall_id", "item_id", "qty"):
        if k not in data:
            return jsonify(error=f"missing {k}"), 400

    # Ensure customer can only operate on own cart
    if str(data["customer_id"]) != str(request.user["id"]):
        return _json_error("forbidden", 403)

    cart = next(
        (
            o
            for o in order_db
            if o.get("type") == "cart"
            and str(o.get("customer_id")) == str(data["customer_id"])
            and o.get("status") == "open"
        ),
        None,
    )
    if not cart:
        cart = {"type": "cart", "id": len(order_db) + 1, "customer_id": data["customer_id"], "status": "open", "items": []}
        order_db.append(cart)

    item = next(
        (i for i in cart["items"] if str(i["stall_id"]) == str(data["stall_id"]) and str(i["item_id"]) == str(data["item_id"])),
        None,
    )
    if item:
        item["qty"] += int(data["qty"])
    else:
        cart["items"].append({"stall_id": data["stall_id"], "item_id": data["item_id"], "qty": int(data["qty"])})

    return jsonify(cart=cart), 200


@app.route("/cart/checkout", methods=["POST"])
@roles_required("customer")
def checkout_cart():
    data = request.get_json(silent=True) or {}

    # Keep existing behavior, but if customer_id missing, default to authenticated user id
    if "customer_id" not in data:
        data["customer_id"] = request.user["id"]

    if "customer_id" not in data:
        return jsonify(error="missing customer_id"), 400

    # Ensure customer can only checkout own cart
    if str(data["customer_id"]) != str(request.user["id"]):
        return _json_error("forbidden", 403)

    cart = next(
        (
            o
            for o in order_db
            if o.get("type") == "cart"
            and str(o.get("customer_id")) == str(data["customer_id"])
            and o.get("status") == "open"
        ),
        None,
    )
    if not cart or not cart["items"]:
        return jsonify(error="cart empty"), 400

    cart["status"] = "checked_out"
    order = {
        "type": "order",
        "id": len(order_db) + 1,
        "customer_id": data["customer_id"],
        "items": cart["items"],
        "status": "placed",
    }
    order_db.append(order)
    return jsonify(order=order), 201


# Endpoint for Story 2: Platform
@app.post("/orders/<order_id>/split-sync")
@roles_required("admin", "user")
def split_sync(order_id):
    # Keep existing logic structure but fix ID comparisons (string/int)
    order = next((o for o in order_db if str(o.get("id")) == str(order_id) and o.get("type") == "order"), None)
    if not order:
        return jsonify(error="order_not_found"), 404

    # Simple split simulation: create one suborder per unique stall_id (merchant assignment omitted)
    items = order.get("items") or []
    if not items:
        return jsonify(error="order_has_no_items"), 400

    grouped = {}
    for it in items:
        stall_id = str(it.get("stall_id"))
        grouped.setdefault(stall_id, []).append(it)

    created = []
    for stall_id, stall_items in grouped.items():
        suborder = {
            "type": "suborder",
            "id": len(order_db) + 1,
            "order_id": order.get("id"),
            "stall_id": stall_id,
            # optional merchant_id could be added by platform logic; leave None for now
            "merchant_id": None,
            "items": stall_items,
            "status": "created",
        }
        order_db.append(suborder)
        created.append(suborder)

    return jsonify(order=order, suborders=created), 201


# Additional existing-like endpoints mentioned in prompt (added for completeness)
@app.get("/orders")
@roles_required("admin", "user")
def list_orders():
    orders = [o for o in order_db if o.get("type") == "order"]
    return jsonify(orders=orders), 200


@app.get("/merchant/suborders")
@roles_required("merchant", "admin")
def merchant_suborders():
    user = request.user
    suborders = [o for o in order_db if o.get("type") == "suborder"]
    # merchants see their own (if merchant_id is set); admins see all
    if user["role"] == "merchant":
        suborders = [s for s in suborders if str(s.get("merchant_id")) == str(user["id"])]
    return jsonify(suborders=suborders), 200


# ----------------------------
# App start (kept)
# ----------------------------

if __name__ == "__main__":
    app.run()