import sqlite3


# Modify the rentals table to include customer details
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

    # Create the rentals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        vehicle TEXT,
        place TEXT NOT NULL,
        rental_type TEXT DEFAULT 'Per Day',
        rental_duration INTEGER NOT NULL,
        total_cost REAL DEFAULT 0,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
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


def add_rental(product_id, customer_name, phone, email, vehicle, place, rental_duration):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    try:
        # Insert rental details into the table
        cursor.execute("""
            INSERT INTO rentals (
                product_id, customer_name, phone, email, vehicle, place, rental_duration
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, customer_name, phone, email, vehicle, place, rental_duration))
        conn.commit()
        rental_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    return rental_id


def end_rental(rental_id, total_cost):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE rentals
        SET end_time = CURRENT_TIMESTAMP, total_cost = ?
        WHERE id = ?
    """, (total_cost, rental_id))
    conn.commit()
    conn.close()


def fetch_product_by_tag(tag_id):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, status, rental_type, rental_rate
        FROM products
        WHERE tag_id = ?
    """, (tag_id,))
    product = cursor.fetchone()
    conn.close()
    return product


def update_product_status(product_id, status):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET status = ?, last_action_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, product_id))
    conn.commit()
    conn.close()


def fetch_active_rental(product_id):
    conn = sqlite3.connect("db/rental.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, start_time
        FROM rentals
        WHERE product_id = ? AND end_time IS NULL
    """, (product_id,))
    rental = cursor.fetchone()
    conn.close()
    return rental


# Initialize the database when the module is imported
initialize_db()
