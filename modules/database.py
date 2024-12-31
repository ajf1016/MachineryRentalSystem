import os
import shutil
from pathlib import Path
import sqlite3
import sys

# Get the bundled database location (PyInstaller runtime fix)
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundled_db_path = os.path.join(sys._MEIPASS, "db/rental.db")
else:
    # Running in development
    bundled_db_path = os.path.abspath("db/rental.db")

# Copy the database to a persistent location
user_home = Path.home()
db_dir = user_home / "HiDoAppData"
db_dir.mkdir(exist_ok=True)
db_path = db_dir / "rental.db"

try:
    if not db_path.exists():
        shutil.copy(bundled_db_path, db_path)
        print(f"Database copied to: {db_path}")  # Debugging log
except Exception as e:
    raise RuntimeError(f"Failed to set up database: {e}")


def get_db_connection():
    """Return a connection to the persistent database."""
    print(f"Connecting to database at: {db_path}")  # Debugging log
    return sqlite3.connect(db_path)


def initialize_db():
    """Initialize the database by creating necessary tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tag_id TEXT UNIQUE NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'Available',
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
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM products WHERE tag_id = ?", (tag_id,))
        if cursor.fetchone():
            raise ValueError("A product with this RFID tag already exists.")

        cursor.execute("""
            INSERT INTO products (name, tag_id, category, status, rental_type, rental_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, tag_id, category, status, rental_type, rental_rate))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        conn.close()


def update_product(product_id, name, tag_id, category, status, rental_type, rental_rate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, tag_id = ?, category = ?, status = ?, rental_type = ?, rental_rate = ?
        WHERE id = ?
    """, (name, tag_id, category, status, rental_type, rental_rate, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def fetch_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, tag_id, category, status, rental_type, rental_rate
        FROM products
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_rental(product_id, customer_name, phone, email, vehicle, place, rental_duration):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE rentals
        SET end_time = CURRENT_TIMESTAMP, total_cost = ?
        WHERE id = ?
    """, (total_cost, rental_id))
    conn.commit()
    conn.close()


def fetch_product_by_tag(tag_id):
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET status = ?, last_action_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, product_id))
    conn.commit()
    conn.close()


def fetch_active_rental(product_id):
    conn = get_db_connection()
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
