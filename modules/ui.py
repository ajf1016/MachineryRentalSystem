from tkinter import ttk, messagebox
import tkinter as tk
from modules.database import (add_product, fetch_all_products, delete_product, update_product,
                              fetch_product_by_tag, add_rental, update_product_status, fetch_active_rental, end_rental)
from .rfid_handler import start_rfid_thread, stop_rfid_thread
from .utils import format_time_to_ist
import time


# Global Variables
active_tab = None
last_detected_tag = None
last_detected_time = 0


def create_ui(root):
    global active_tab

    # Create Notebook (Tabs)
    notebook = ttk.Notebook(root)

    # Create frames for each tab
    register_frame = ttk.Frame(notebook)
    rental_frame = ttk.Frame(notebook)
    product_management_frame = ttk.Frame(notebook)

    # Add tabs
    notebook.add(register_frame, text="Register Products")
    notebook.add(rental_frame, text="Rental Flow")
    notebook.add(product_management_frame, text="Products Management")
    notebook.pack(fill="both", expand=True)

    # Initialize UI for each tab
    create_register_products_ui(register_frame)
    create_rental_flow_ui(rental_frame)
    create_products_table_ui(product_management_frame)

    # Tab change event
    def on_tab_changed(event):
        global active_tab
        selected_tab = event.widget.tab(event.widget.index("current"))["text"]
        active_tab = selected_tab

        # Debugging log for tab change
        print(f"Active tab changed to: {active_tab}")

    # Bind the event and initialize the active tab
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
    active_tab = notebook.tab(notebook.index("current"))["text"]

    # Handle application close
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))


def on_close(root):
    stop_rfid_thread()  # Stop RFID thread
    root.destroy()  # Destroy application


def create_register_products_ui(frame):
    global last_detected_tag, last_detected_time

    # Styling
    style = ttk.Style()
    style.configure("TFrame", background="#f9f9f9")
    style.configure("TLabel", background="#f9f9f9", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12, "bold"))

    # Frames for layout
    form_frame = ttk.Frame(frame)
    form_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    rental_form_frame = ttk.Frame(frame)
    rental_form_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Product Registration UI
    ttk.Label(form_frame, text="Product Registration", font=("Arial", 14, "bold")).pack(pady=10)
    product_entries = create_product_form(form_frame)

    ttk.Button(form_frame, text="Add Product", command=lambda: handle_add(product_entries)).pack(pady=10)

    # Rental Information UI
    ttk.Label(rental_form_frame, text="Rental Information", font=("Arial", 14, "bold")).pack(pady=10)
    product_info_label = ttk.Label(rental_form_frame, text="", font=("Arial", 12), anchor="w", relief="sunken")
    product_info_label.pack(fill="x", padx=10, pady=10)

    rental_entries = create_rental_form(rental_form_frame)

    ttk.Button(rental_form_frame, text="Submit Rental",
               command=lambda: submit_rental(rental_entries, product_info_label)).pack(pady=10)

    # RFID Detection
    def on_tag_detected(tag_id):
        global last_detected_tag, last_detected_time

        current_time = time.time()
        debounce_interval = 5  # Prevent rapid detections

        if tag_id == last_detected_tag and (current_time - last_detected_time) < debounce_interval:
            return

        last_detected_tag = tag_id
        last_detected_time = current_time

        product = fetch_product_by_tag(tag_id)
        if product:
            handle_product_detection(product, product_entries, product_info_label)
        else:
            product_info_label.config(text="No product found. Please register.")

    # Start RFID reader thread
    start_rfid_thread(on_tag_detected)


def create_product_form(frame):
    fields = [
        ("Product Name", "name"),
        ("RFID Tag", "tag"),
        ("Category", "category"),
        ("Rental Type", "type"),
        ("Rental Rate", "rate"),
        ("Status", "status"),
    ]
    entries = {}
    for label, key in fields:
        ttk.Label(frame, text=label).pack(anchor="w", padx=10, pady=5)
        if key in ["type", "status"]:
            values = ["Per Day", "Per Hour"] if key == "type" else ["Available", "Not Available"]
            combobox = ttk.Combobox(frame, values=values, state="readonly")
            combobox.set(values[0])
            combobox.pack(fill="x", padx=10, pady=5)
            entries[key] = combobox
        else:
            entry = ttk.Entry(frame)
            entry.pack(fill="x", padx=10, pady=5)
            entries[key] = entry
    return entries


def create_rental_form(frame):
    fields = [
        ("Customer Name", "name"),
        ("Phone Number", "phone"),
        ("Email (Optional)", "email"),
        ("Vehicle Number Plate (Optional)", "vehicle"),
        ("Place", "place"),
        ("Rental Duration (Days/Hours)", "duration"),
    ]
    entries = {}
    for label, key in fields:
        ttk.Label(frame, text=label).pack(anchor="w", padx=10, pady=5)
        entry = ttk.Entry(frame)
        entry.pack(fill="x", padx=10, pady=5)
        entries[key] = entry
    return entries


def handle_add(product_entries):
    name = product_entries["name"].get()
    tag_id = product_entries["tag"].get()
    category = product_entries["category"].get()
    rental_type = product_entries["type"].get()
    rental_rate = product_entries["rate"].get()
    status = product_entries["status"].get()

    if not name or not tag_id:
        messagebox.showerror("Error", "Product Name and RFID Tag are required.")
        return

    try:
        rental_rate = float(rental_rate)
    except ValueError:
        messagebox.showerror("Error", "Rental Rate must be a number.")
        return

    result = add_product(name, tag_id, category, status, rental_type, rental_rate)
    if result:
        messagebox.showerror("Error", result)
    else:
        messagebox.showinfo("Success", "Product added successfully!")


def submit_rental(rental_entries, product_info_label):
    customer_name = rental_entries["name"].get()
    phone = rental_entries["phone"].get()
    place = rental_entries["place"].get()
    duration = rental_entries["duration"].get()

    if not customer_name or not phone or not place or not duration:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Further logic for rentals can be added here
    messagebox.showinfo("Success", "Rental submitted successfully!")


def handle_product_detection(product, product_entries, product_info_label):
    product_id, name, status, rental_type, rental_rate = product
    product_entries["name"].delete(0, "end")
    product_entries["name"].insert(0, name)
    product_info_label.config(text=f"Product Name: {name}\nStatus: {status}")


def create_rental_flow_ui(frame):
    # Table for Rental History
    ttk.Label(frame, text="Rental History", font=("Arial", 15, "bold")).pack(pady=10)

    rental_table = ttk.Treeview(frame, columns=("ID", "Customer", "Phone", "Product", "Type", "Place", "Duration",
                                                "Start Time", "End Time", "Cost"), show="headings")
    for col in rental_table["columns"]:
        rental_table.heading(col, text=col)
    rental_table.pack(fill="both", expand=True, padx=10, pady=10)
    ttk.Button(frame, text="Refresh", command=lambda: refresh_table(rental_table)).pack(pady=10)


def refresh_table(table):
    table.delete(*table.get_children())
    rentals = fetch_all_products()  # Replace with actual rental data
    for rental in rentals:
        table.insert("", "end", values=rental)


def create_products_table_ui(frame):
    ttk.Label(frame, text="Products Management", font=("Arial", 20, "bold")).pack(pady=10)

    product_table = ttk.Treeview(frame, columns=("ID", "Name", "Tag", "Category", "Status", "Type", "Rate"),
                                  show="headings")
    for col in product_table["columns"]:
        product_table.heading(col, text=col)
    product_table.pack(fill="both", expand=True, padx=10, pady=10)
    ttk.Button(frame, text="Refresh", command=lambda: refresh_table(product_table)).pack(pady=10)
