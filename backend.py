from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, session

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kosher_phone.db"

app = Flask(__name__, static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-kosher-phone-secret")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")

SEED_PRODUCTS = [
    {"name": "Nokia 105 כשר", "price": 249, "old_price": 299, "level": "כשר בסיסי", "brand": "Nokia", "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80"},
    {"name": "Nokia 110 כשר", "price": 279, "old_price": 339, "level": "כשר בסיסי", "brand": "Nokia", "image": "https://images.unsplash.com/photo-1523206489230-c012c64b2b48?auto=format&fit=crop&w=900&q=80"},
    {"name": "Nokia 225 4G כשר", "price": 389, "old_price": 459, "level": "מהדרין", "brand": "Nokia", "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=900&q=80"},
    {"name": "Nokia 2720 כשר", "price": 579, "old_price": 649, "level": "מהדרין", "brand": "Nokia", "image": "https://images.unsplash.com/photo-1510557880182-3f8c2b41b014?auto=format&fit=crop&w=900&q=80"},
    {"name": "MobiTalk T8 מאושר", "price": 529, "old_price": 619, "level": "סים כשר", "brand": "MobiTalk", "image": "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=900&q=80"},
    {"name": "MobiTalk T9 Pro", "price": 689, "old_price": 799, "level": "מהדרין", "brand": "MobiTalk", "image": "https://images.unsplash.com/photo-1605236453806-6ff36851218e?auto=format&fit=crop&w=900&q=80"},
    {"name": "MobiTalk Business 4G", "price": 849, "old_price": 990, "level": "תומך וואטסאפ מסונן", "brand": "MobiTalk", "image": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?auto=format&fit=crop&w=900&q=80"},
    {"name": "Kosher Phone K20", "price": 699, "old_price": 790, "level": "מהדרין", "brand": "Kosher", "image": "https://images.unsplash.com/photo-1583573636246-18cb2246697f?auto=format&fit=crop&w=900&q=80"},
    {"name": "Kosher Phone K30", "price": 949, "old_price": 1090, "level": "תומך וואטסאפ מסונן", "brand": "Kosher", "image": "https://images.unsplash.com/photo-1573148195900-7845dcb9b127?auto=format&fit=crop&w=900&q=80"},
    {"name": "Kosher Phone Senior", "price": 459, "old_price": 549, "level": "כשר בסיסי", "brand": "Kosher", "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=900&q=80"},
    {"name": "Mircom C2 כשר", "price": 419, "old_price": 499, "level": "כשר בסיסי", "brand": "Mircom", "image": "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=900&q=80"},
    {"name": "Mircom C4 Plus", "price": 579, "old_price": 669, "level": "מהדרין", "brand": "Mircom", "image": "https://images.unsplash.com/photo-1522273400909-fd1a8f77637e?auto=format&fit=crop&w=900&q=80"},
    {"name": "Spark Kosher Mini", "price": 329, "old_price": 399, "level": "כשר בסיסי", "brand": "Spark", "image": "https://images.unsplash.com/photo-1567581935884-3349723552ca?auto=format&fit=crop&w=900&q=80"},
    {"name": "Spark Voice Max", "price": 619, "old_price": 739, "level": "סים כשר", "brand": "Spark", "image": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?auto=format&fit=crop&w=900&q=80"},
    {"name": "VoiceCom Basic", "price": 359, "old_price": 429, "level": "כשר בסיסי", "brand": "VoiceCom", "image": "https://images.unsplash.com/photo-1592813630410-7c5a42f93437?auto=format&fit=crop&w=900&q=80"},
    {"name": "VoiceCom Ultra", "price": 729, "old_price": 859, "level": "מהדרין", "brand": "VoiceCom", "image": "https://images.unsplash.com/photo-1556656793-08538906a9f8?auto=format&fit=crop&w=900&q=80"},
    {"name": "VoiceCom Office", "price": 899, "old_price": 1020, "level": "תומך וואטסאפ מסונן", "brand": "VoiceCom", "image": "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=900&q=80"},
    {"name": "Anker מטען מקורי 20W", "price": 89, "old_price": 119, "level": "אביזר", "brand": "Anker", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=900&q=80"},
    {"name": "Anker מטען רכב", "price": 79, "old_price": 99, "level": "אביזר", "brand": "Anker", "image": "https://images.unsplash.com/photo-1616788494672-ec7ca25fdda9?auto=format&fit=crop&w=900&q=80"},
    {"name": "Anker Power Bank 10000", "price": 149, "old_price": 189, "level": "אביזר", "brand": "Anker", "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=80"},
    {"name": "Jabra אוזניה חוטית", "price": 59, "old_price": 79, "level": "אביזר", "brand": "Jabra", "image": "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=80"},
    {"name": "Jabra אוזנית בלוטוס", "price": 179, "old_price": 229, "level": "אביזר", "brand": "Jabra", "image": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80"},
    {"name": "JBL אוזניות כפתור", "price": 129, "old_price": 169, "level": "אביזר", "brand": "JBL", "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80"},
    {"name": "JBL רמקול נייד", "price": 299, "old_price": 379, "level": "אביזר", "brand": "JBL", "image": "https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=900&q=80"},
    {"name": "Kosher סוללה מקורית K", "price": 119, "old_price": 149, "level": "אביזר", "brand": "Kosher", "image": "https://images.unsplash.com/photo-1609592806955-d58fcdd2c3e4?auto=format&fit=crop&w=900&q=80"},
    {"name": "Nokia סוללה BL-5C", "price": 69, "old_price": 89, "level": "אביזר", "brand": "Nokia", "image": "https://images.unsplash.com/photo-1587033411391-5d9e51cce126?auto=format&fit=crop&w=900&q=80"},
    {"name": "Mircom Dock טעינה", "price": 139, "old_price": 179, "level": "אביזר", "brand": "Mircom", "image": "https://images.unsplash.com/photo-1587033411391-5d9e51cce126?auto=format&fit=crop&w=900&q=80"},
    {"name": "Spark מטען מהיר", "price": 99, "old_price": 129, "level": "אביזר", "brand": "Spark", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=900&q=80"},
    {"name": "VoiceCom Pro Line", "price": 999, "old_price": 1190, "level": "תומך וואטסאפ מסונן", "brand": "VoiceCom", "image": "https://images.unsplash.com/photo-1616788494672-ec7ca25fdda9?auto=format&fit=crop&w=900&q=80"},
    {"name": "MobiTalk Family Safe", "price": 639, "old_price": 749, "level": "סים כשר", "brand": "MobiTalk", "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=900&q=80"},
]


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_status_column(conn: sqlite3.Connection) -> None:
    cols = [row["name"] for row in conn.execute("PRAGMA table_info(leads)").fetchall()]
    if "status" not in cols:
        conn.execute("ALTER TABLE leads ADD COLUMN status TEXT NOT NULL DEFAULT 'new'")


def seed_products(conn: sqlite3.Connection) -> None:
    existing_names = {r["name"] for r in conn.execute("SELECT name FROM products").fetchall()}
    missing = [p for p in SEED_PRODUCTS if p["name"] not in existing_names]
    if missing:
        conn.executemany(
            "INSERT INTO products (name, price, old_price, level, brand, image) VALUES (?, ?, ?, ?, ?, ?)",
            [(p["name"], p["price"], p["old_price"], p["level"], p["brand"], p["image"]) for p in missing],
        )


def init_db() -> None:
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            need TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new'
        )
        """
    )
    ensure_status_column(conn)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            old_price INTEGER NOT NULL,
            level TEXT NOT NULL,
            brand TEXT NOT NULL,
            image TEXT NOT NULL
        )
        """
    )

    seed_products(conn)
    conn.commit()
    conn.close()


def is_admin() -> bool:
    return bool(session.get("is_admin"))


def serialize_product(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "oldPrice": row["old_price"],
        "level": row["level"],
        "brand": row["brand"],
        "image": row["image"],
    }


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/admin")
def admin_page():
    if not is_admin():
        return redirect("/admin/login")
    return send_from_directory(BASE_DIR, "admin.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return send_from_directory(BASE_DIR, "admin-login.html")

    password = request.form.get("password", "")
    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect("/admin")
    return redirect("/admin/login?error=1")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect("/admin/login")


@app.route("/api/products")
def list_products():
    level = request.args.get("level", "").strip()
    brand = request.args.get("brand", "").strip()
    query = request.args.get("q", "").strip().lower()
    sort = request.args.get("sort", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()

    sql = "SELECT id, name, price, old_price, level, brand, image FROM products WHERE 1=1"
    params: list = []

    if level and level != "כל הדגמים":
        sql += " AND level = ?"
        params.append(level)
    if brand and brand != "כל המותגים":
        sql += " AND brand = ?"
        params.append(brand)
    if min_price.isdigit():
        sql += " AND price >= ?"
        params.append(int(min_price))
    if max_price.isdigit():
        sql += " AND price <= ?"
        params.append(int(max_price))
    if query:
        sql += " AND (LOWER(name) LIKE ? OR LOWER(level) LIKE ? OR LOWER(brand) LIKE ?)"
        q = f"%{query}%"
        params.extend([q, q, q])

    if sort == "price_asc":
        sql += " ORDER BY price ASC"
    elif sort == "price_desc":
        sql += " ORDER BY price DESC"
    elif sort == "name_asc":
        sql += " ORDER BY name ASC"
    else:
        sql += " ORDER BY id DESC"

    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    brands = [r["brand"] for r in conn.execute("SELECT DISTINCT brand FROM products ORDER BY brand ASC").fetchall()]
    conn.close()

    items = [serialize_product(r) for r in rows]
    return jsonify({"items": items, "count": len(items), "brands": brands})


@app.route("/api/leads", methods=["POST"])
def create_lead():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    need = str(payload.get("need", "")).strip()

    if not name or not phone or not need:
        return jsonify({"error": "missing_fields", "message": "name, phone, need are required"}), 400

    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    conn = get_db_connection()
    ensure_status_column(conn)
    cur = conn.execute(
        "INSERT INTO leads (name, phone, need, created_at, status) VALUES (?, ?, ?, ?, ?)",
        (name, phone, need, created_at, "new"),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cur.lastrowid, "message": "lead_saved"}), 201


@app.route("/api/admin/leads")
def list_leads_admin():
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401

    status = request.args.get("status", "all").strip()
    conn = get_db_connection()
    ensure_status_column(conn)

    sql = "SELECT id, name, phone, need, created_at, status FROM leads"
    params = []
    if status in {"new", "contacted"}:
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY id DESC"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify({"items": [dict(r) for r in rows], "count": len(rows)})


@app.route("/api/admin/leads/<int:lead_id>/status", methods=["POST"])
def update_lead_status(lead_id: int):
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip()
    if status not in {"new", "contacted"}:
        return jsonify({"error": "invalid_status"}), 400

    conn = get_db_connection()
    cur = conn.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "updated", "id": lead_id, "status": status})


@app.route("/api/admin/products")
def admin_list_products():
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401
    conn = get_db_connection()
    rows = conn.execute("SELECT id, name, price, old_price, level, brand, image FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({"items": [serialize_product(r) for r in rows], "count": len(rows)})


@app.route("/api/admin/products", methods=["POST"])
def admin_create_product():
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    level = str(payload.get("level", "")).strip()
    brand = str(payload.get("brand", "")).strip()
    image = str(payload.get("image", "")).strip()

    try:
        price = int(payload.get("price"))
        old_price = int(payload.get("oldPrice"))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_price"}), 400

    if not all([name, level, brand, image]):
        return jsonify({"error": "missing_fields"}), 400

    conn = get_db_connection()
    cur = conn.execute(
        "INSERT INTO products (name, price, old_price, level, brand, image) VALUES (?, ?, ?, ?, ?, ?)",
        (name, price, old_price, level, brand, image),
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return jsonify({"id": product_id, "message": "created"}), 201


@app.route("/api/admin/products/<int:product_id>", methods=["PUT"])
def admin_update_product(product_id: int):
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    level = str(payload.get("level", "")).strip()
    brand = str(payload.get("brand", "")).strip()
    image = str(payload.get("image", "")).strip()

    try:
        price = int(payload.get("price"))
        old_price = int(payload.get("oldPrice"))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_price"}), 400

    if not all([name, level, brand, image]):
        return jsonify({"error": "missing_fields"}), 400

    conn = get_db_connection()
    cur = conn.execute(
        "UPDATE products SET name = ?, price = ?, old_price = ?, level = ?, brand = ?, image = ? WHERE id = ?",
        (name, price, old_price, level, brand, image, product_id),
    )
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "updated", "id": product_id})


@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def admin_delete_product(product_id: int):
    if not is_admin():
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "deleted", "id": product_id})


@app.route("/<path:path>")
def static_files(path: str):
    if (BASE_DIR / path).exists():
        return send_from_directory(BASE_DIR, path)
    return jsonify({"error": "not_found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)

# Ensure DB/tables exist both for local run and Gunicorn (Render).
init_db()
