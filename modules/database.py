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
        status TEXT DEFAULT 'Available',
        added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rental_type TEXT DEFAULT 'Per Day',
        rental_rate REAL DEFAULT 0,
        last_action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def add_product(name, tag_id, category, status, rental_type, rental_rate):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    try:
        # Check if tag_id already exists
        cursor.execute("SELECT id FROM products WHERE tag_id = ?", (tag_id,))
        if cursor.fetchone():
            return "Error: A product with this RFID tag already exists."

        # Insert the new product
        cursor.execute("""
            INSERT INTO products (name, tag_id, category, status, rental_type, rental_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, tag_id, category, status, rental_type, rental_rate))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return f"Error: {e}"
    finally:
        conn.close()


def update_product(product_id, name, tag_id, category, status, rental_type, rental_rate):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, tag_id = ?, category = ?, status = ?, rental_type = ?, rental_rate = ?
        WHERE id = ?
    """, (name, tag_id, category, status, rental_type, rental_rate, product_id))
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
    cursor.execute("""
        SELECT id, name, tag_id, category, status, added_time, rental_type, rental_rate
        FROM products
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize the database when the module is imported
initialize_db()
