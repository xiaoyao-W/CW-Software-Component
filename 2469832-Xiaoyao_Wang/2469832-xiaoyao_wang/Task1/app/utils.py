import os
import json
import sqlite3
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont


def load_environment():
    """Load environment variables from .env if available."""
    root = Path(__file__).parent.parent
    dotenv_path = root / '.env'
    try:
        from dotenv import load_dotenv
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path)
            print(f'Loaded environment from {dotenv_path}')
        else:
            print('No .env file found.')
    except ImportError:
        print('python-dotenv not installed, using os.environ directly.')


def get_llm_client():
    """Return a callable that sends prompts to an external LLM API.

    Expects FREEAPI_URL and FREEAPI_KEY in environment.
    """
    base_url = os.getenv('FREEAPI_URL')
    api_key = os.getenv('FREEAPI_KEY')
    if not base_url or not api_key:
        print('FREEAPI_URL or FREEAPI_KEY not set in environment.')
        return None

    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    def call_llm(prompt: str, model: str = 'openai/gpt-5.2', context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        if context:
            payload['context'] = context
        try:
            resp = requests.post(base_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {'error': str(e)}

    return call_llm


def ensure_data_dir() -> Path:
    """Ensure data directory exists and return its path."""
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def init_stall_db(stall_id: str) -> Path:
    """Create a stall-specific SQLite database with Orders and Order_Items tables."""
    data_dir = ensure_data_dir()
    db_path = data_dir / f'stall_{stall_id}.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            master_order_id TEXT,
            customer_name TEXT,
            items_json TEXT,
            subtotal REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id TEXT PRIMARY KEY,
            order_id TEXT,
            product_id TEXT,
            product_name TEXT,
            price REAL,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            stock INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    return db_path


def init_master_db() -> Path:
    """Create master database for managing stalls and master orders."""
    data_dir = ensure_data_dir()
    db_path = data_dir / 'master.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stalls (
            id TEXT PRIMARY KEY,
            name TEXT,
            owner_name TEXT,
            description TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS master_orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            items_json TEXT,
            total REAL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    return db_path


def get_master_db() -> Path:
    """Get master database path, initializing if needed."""
    return init_master_db()


def register_stall(stall_id: str, name: str, owner_name: str = '', description: str = '') -> None:
    """Register a new stall in the master database."""
    db_path = init_stall_db(stall_id)
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO stalls (id, name, owner_name, description) VALUES (?, ?, ?, ?)',
                (stall_id, name, owner_name, description))
    conn.commit()
    conn.close()


def list_stalls() -> List[Dict[str, Any]]:
    """List all registered stalls."""
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    cur.execute('SELECT id, name, owner_name, description FROM stalls')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'owner_name': r[2], 'description': r[3]} for r in rows]


def get_stall_products(stall_id: str) -> List[Dict[str, Any]]:
    """Get all products for a specific stall."""
    db_path = ensure_data_dir() / f'stall_{stall_id}.db'
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, price, stock FROM products')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'description': r[2], 'price': r[3], 'stock': r[4]} for r in rows]


def add_product_to_stall(stall_id: str, product: Dict[str, Any]) -> None:
    """Add a product to a stall."""
    db_path = init_stall_db(stall_id)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO products (id, name, description, price, stock) VALUES (?, ?, ?, ?, ?)',
        (product['id'], product['name'], product.get('description', ''),
         product.get('price', 0.0), product.get('stock', 100))
    )
    conn.commit()
    conn.close()


def user_login(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user and return user info if valid."""
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    cur.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?',
                (username, password))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'role': row[2]}
    return None


def register_user(username: str, password: str, role: str = 'user') -> bool:
    """Register a new user."""
    import uuid
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    user_id = str(uuid.uuid4())
    try:
        cur.execute('INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)',
                    (user_id, username, password, role))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result


def save_master_order(master_order_id: str, customer_name: str, items: List[Dict[str, Any]], total: float) -> None:
    """Save a master order to the master database."""
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO master_orders (id, customer_name, items_json, total, status) VALUES (?, ?, ?, ?, ?)',
        (master_order_id, customer_name, json.dumps(items), total, 'new')
    )
    conn.commit()
    conn.close()


def get_master_orders(customer_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get master orders, optionally filtered by customer."""
    master_db = get_master_db()
    conn = sqlite3.connect(master_db)
    cur = conn.cursor()
    if customer_name:
        cur.execute('SELECT id, customer_name, items_json, total, status, created_at FROM master_orders WHERE customer_name = ?',
                    (customer_name,))
    else:
        cur.execute('SELECT id, customer_name, items_json, total, status, created_at FROM master_orders')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'customer_name': r[1], 'items': json.loads(r[2]), 'total': r[3], 'status': r[4], 'created_at': r[5]} for r in rows]


def split_order_by_stall(cart_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Split cart items by stall_id for order processing.

    Args:
        cart_items: List of items with format {'stall_id', 'product_id', 'name', 'price', 'quantity'}

    Returns:
        Dict mapping stall_id to list of items for that stall
    """
    by_stall = {}
    for item in cart_items:
        stall_id = item.get('stall_id')
        if stall_id not in by_stall:
            by_stall[stall_id] = []
        by_stall[stall_id].append(item)
    return by_stall


def save_suborder(stall_id: str, suborder: Dict[str, Any]) -> None:
    """Save a sub-order to a stall's database.

    Args:
        stall_id: The stall identifier
        suborder: Dict with keys: id, master_order_id, customer_name, items (list), subtotal, status
    """
    db_path = init_stall_db(stall_id)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO orders (id, master_order_id, customer_name, items_json, subtotal, status) VALUES (?, ?, ?, ?, ?, ?)',
        (suborder['id'], suborder['master_order_id'], suborder['customer_name'],
         json.dumps(suborder['items']), suborder['subtotal'], suborder.get('status', 'pending'))
    )

    for item in suborder.get('items', []):
        item_id = item.get('id', str(uuid.uuid4()))
        cur.execute(
            'INSERT INTO order_items (id, order_id, product_id, product_name, price, quantity) VALUES (?, ?, ?, ?, ?, ?)',
            (item_id, suborder['id'], item.get('product_id'), item.get('name'),
             item.get('price'), item.get('quantity', 1))
        )

    conn.commit()
    conn.close()


def get_stall_orders(stall_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all orders for a specific stall."""
    db_path = ensure_data_dir() / f'stall_{stall_id}.db'
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if status:
        cur.execute('SELECT id, master_order_id, customer_name, items_json, subtotal, status, created_at FROM orders WHERE status = ?',
                    (status,))
    else:
        cur.execute('SELECT id, master_order_id, customer_name, items_json, subtotal, status, created_at FROM orders')
    rows = cur.fetchall()
    conn.close()
    orders = []
    for r in rows:
        order_items = get_order_items(r[0], db_path)
        orders.append({
            'id': r[0], 'master_order_id': r[1], 'customer_name': r[2],
            'items': json.loads(r[3]), 'subtotal': r[4], 'status': r[5], 'created_at': r[6],
            'order_items': order_items
        })
    return orders


def get_order_items(order_id: str, db_path: Path) -> List[Dict[str, Any]]:
    """Get all items for a specific order."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id, product_id, product_name, price, quantity FROM order_items WHERE order_id = ?', (order_id,))
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'product_id': r[1], 'name': r[2], 'price': r[3], 'quantity': r[4]} for r in rows]


def update_order_status(stall_id: str, order_id: str, new_status: str) -> bool:
    """Update the status of an order in a stall's database."""
    db_path = ensure_data_dir() / f'stall_{stall_id}.db'
    if not db_path.exists():
        return False
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    success = cur.rowcount > 0
    conn.close()
    return success


def generate_order_flow_image(output_path: str, order_data: Optional[Dict[str, Any]] = None) -> Path:
    """Generate an order flow diagram showing how a master order splits into sub-orders.

    Uses LLM to generate the diagram description, then creates a visual representation.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    llm_client = get_llm_client()
    order_desc = ""
    if order_data:
        order_desc = f"Master Order: {order_data.get('master_order_id', 'N/A')}\n"
        order_desc += f"Total Items: {len(order_data.get('items', []))}\n"
        order_desc += f"Stalls Involved: {len(order_data.get('suborders', []))}\n"

    if llm_client:
        prompt = f"""Generate a PlantUML sequence diagram showing the order splitting process for a marketplace:
        1. Customer submits cart with items from multiple stalls
        2. System creates master order
        3. System splits order by stall
        4. Each stall receives its sub-order
        5. Each stall processes and ships their portion

        Use standard PlantUML syntax with @startuml and @enduml.
        Return ONLY the PlantUML code, no explanations.
        {order_desc}"""
        try:
            response = llm_client(prompt)
            if 'error' not in response:
                text = response.get('text', '') or response.get('result', '')
                if '@startuml' in text:
                    return generate_flowchart_from_plantuml(text, output_path)
        except Exception as e:
            print(f'LLM call failed: {e}')

    return generate_fallback_order_flow(output_path)


def generate_flowchart_from_plantuml(plantuml_code: str, output_path: Path) -> Path:
    """Generate image from PlantUML code."""
    try:
        import subprocess
        plantuml_jar = os.getenv('PLANTUML_JAR')
        if plantuml_jar and Path(plantuml_jar).exists():
            puml_path = output_path.with_suffix('.puml')
            with open(puml_path, 'w') as f:
                f.write(plantuml_code)
            subprocess.run(['java', '-jar', plantuml_jar, '-tpng', str(puml_path), '-o', str(output_path.parent)],
                         capture_output=True, timeout=60)
            if output_path.with_suffix('.png').exists():
                return output_path.with_suffix('.png')
    except Exception as e:
        print(f'PlantUML generation failed: {e}')

    return generate_fallback_order_flow(output_path)


def generate_fallback_order_flow(output_path: Path) -> Path:
    """Generate a fallback order flow diagram using Pillow."""
    width, height = 900, 600
    img = Image.new('RGB', (width, height), color=(245, 245, 250))
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 16)
        font_normal = ImageFont.truetype("arial.ttf", 12)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((350, 20), "Marketplace Order Flow", fill=(30, 30, 80), font=font_large)

    boxes = [
        (50, 80, 200, 140, "Customer\nSubmit Cart", (100, 150, 255)),
        (350, 80, 500, 140, "Master Order\nCreated", (255, 180, 100)),
        (650, 80, 800, 140, "Order Split\nby Stall", (100, 200, 100)),
        (50, 220, 200, 280, "Stall A\nSub-order", (150, 100, 200)),
        (350, 220, 500, 280, "Stall B\nSub-order", (200, 100, 150)),
        (650, 220, 800, 280, "Stall C\nSub-order", (100, 180, 180)),
        (50, 350, 200, 410, "Stall A\nProcess", (100, 150, 255)),
        (350, 350, 500, 410, "Stall B\nProcess", (255, 180, 100)),
        (650, 350, 800, 410, "Stall C\nProcess", (100, 200, 100)),
        (200, 470, 700, 550, "Customer Receives\nAll Items", (80, 200, 80)),
    ]

    for box in boxes:
        x1, y1, x2, y2, text, color = box
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(50, 50, 50), width=2)
        lines = text.split('\n')
        y_offset = y1 + (y2 - y1 - len(lines) * 14) // 2
        for line in lines:
            x_offset = x1 + (x2 - x1 - len(line) * 6) // 2
            draw.text((x_offset, y_offset), line, fill=(255, 255, 255), font=font_normal)
            y_offset += 18

    arrows = [
        ((125, 140), (400, 80)),
        ((425, 140), (725, 80)),
        ((725, 140), (725, 220)),
        ((125, 220), (125, 280)),
        ((425, 220), (425, 280)),
        ((725, 280), (125, 350)),
        ((125, 350), (125, 410)),
        ((425, 350), (425, 410)),
        ((725, 410), (725, 470)),
        ((125, 410), (450, 470)),
        ((425, 410), (450, 470)),
        ((725, 470), (450, 550)),
    ]

    for start, end in arrows:
        draw.line([start, end], fill=(80, 80, 80), width=2)

    img.save(output_path)
    return output_path


def generate_order_flow_from_llm(order_info: Dict[str, Any]) -> Optional[str]:
    """Generate order flow description using LLM.

    Returns a text description of the order splitting process.
    """
    llm_client = get_llm_client()
    if not llm_client:
        return None

    items = order_info.get('items', [])
    stalls = set(item.get('stall_id') for item in items)

    prompt = f"""Describe the order splitting process for a marketplace order:
    - Master Order ID: {order_info.get('master_order_id', 'N/A')}
    - Customer: {order_info.get('customer_name', 'N/A')}
    - Items: {len(items)}
    - Stalls: {len(stalls)}

    Provide a brief description in Chinese explaining how the order flows from customer to stalls.
    Keep it under 100 words.
    """

    try:
        response = llm_client(prompt)
        if 'error' not in response:
            return response.get('text', '') or response.get('result', '')
    except Exception:
        pass
    return None


def process_checkout(cart_items: List[Dict[str, Any]], customer_name: str) -> Dict[str, Any]:
    """Process checkout: create master order and split into sub-orders.

    Args:
        cart_items: List of items with format {'stall_id', 'product_id', 'name', 'price', 'quantity'}
        customer_name: Name of the customer

    Returns:
        Dict with master_order_id and list of suborders
    """
    import uuid

    master_order_id = str(uuid.uuid4())
    by_stall = split_order_by_stall(cart_items)

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    save_master_order(master_order_id, customer_name, cart_items, total)

    suborders = []
    for stall_id, stall_items in by_stall.items():
        subtotal = sum(item['price'] * item['quantity'] for item in stall_items)
        suborder = {
            'id': str(uuid.uuid4()),
            'master_order_id': master_order_id,
            'customer_name': customer_name,
            'items': stall_items,
            'subtotal': subtotal,
            'status': 'pending'
        }
        save_suborder(stall_id, suborder)
        suborders.append({
            'stall_id': stall_id,
            'sub_order_id': suborder['id'],
            'items': stall_items,
            'subtotal': subtotal
        })

    flow_description = generate_order_flow_from_llm({
        'master_order_id': master_order_id,
        'customer_name': customer_name,
        'items': cart_items
    })

    return {
        'master_order_id': master_order_id,
        'total': total,
        'suborders': suborders,
        'flow_description': flow_description
    }


import uuid
