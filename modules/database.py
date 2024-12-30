import sqlite3


def initialize_db():
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()

    # Create the products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tag_id TEXT UNIQUE NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'Available'
    )
    """)
    conn.commit()
    conn.close()


def add_product(name, tag_id, category, status):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, tag_id, category, status) VALUES (?, ?, ?, ?)",
                       (name, tag_id, category, status))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return f"Error: {e}"
    finally:
        conn.close()


def update_product(product_id, name, tag_id, category, status):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, tag_id = ?, category = ?, status = ?
        WHERE id = ?
    """, (name, tag_id, category, status, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def fetch_all_products():
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize the database when the module is imported
initialize_db()
