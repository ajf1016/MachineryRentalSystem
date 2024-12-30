from tkinter import ttk, messagebox
from modules.database import (add_product, fetch_all_products, delete_product, update_product,
                              fetch_product_by_tag, add_rental, update_product_status, fetch_active_rental, end_rental)
from .rfid_handler import start_rfid_thread, stop_rfid_thread
import time
import sqlite3

active_tab = None
last_detected_tag = None
last_detected_time = 0


def create_ui(root):
    global active_tab
    # Add tabs for Register Products and Rental Flow
    notebook = ttk.Notebook(root)

    # Create frames for tabs
    register_frame = ttk.Frame(notebook)
    rental_frame = ttk.Frame(notebook)

    notebook.add(register_frame, text="Register Products")
    notebook.add(rental_frame, text="Rental Flow")
    notebook.pack(fill="both", expand=True)

    # Create Register Products UI
    create_register_products_ui(register_frame)
    create_rental_flow_ui(rental_frame)

    # Handle tab change
    def on_tab_changed(event):
        global active_tab

        # Get the active tab
        selected_tab = event.widget.tab(event.widget.index("current"))["text"]
        active_tab = selected_tab

        # Start or stop RFID thread based on the tab
        if selected_tab == "Rental Flow":
            print("selected_tab : ", selected_tab)
        elif selected_tab == "Register Products":
            print("selected_tab : ", selected_tab)

    # Bind tab change event
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # Initialize active tab
    active_tab = notebook.tab(notebook.index("current"))["text"]

    # Handle application close
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))


def on_close(root):
    stop_rfid_thread()  # Stop the RFID reader thread
    root.destroy()  # Destroy the application


def create_register_products_ui(frame):
    global last_detected_tag, last_detected_time

    # Frames
    form_frame = ttk.Frame(frame, relief="solid", borderwidth=1)
    form_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    rental_form_frame = ttk.Frame(frame, relief="solid", borderwidth=1)
    rental_form_frame.pack(side="right", fill="both",
                           expand=True, padx=10, pady=10)

    # Product Registration Form
    ttk.Label(form_frame, text="Product Registration",
              font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(form_frame, text="Product Name").pack(
        anchor="w", padx=10, pady=5)
    product_name_entry = ttk.Entry(form_frame)
    product_name_entry.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="RFID Tag").pack(anchor="w", padx=10, pady=5)
    tag_entry = ttk.Entry(form_frame)
    tag_entry.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Category").pack(anchor="w", padx=10, pady=5)
    category_entry = ttk.Entry(form_frame)
    category_entry.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Rental Type").pack(anchor="w", padx=10, pady=5)
    rental_type_combobox = ttk.Combobox(
        form_frame, values=["Per Day", "Per Hour"], state="readonly"
    )
    rental_type_combobox.set("Per Day")
    rental_type_combobox.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Rental Rate").pack(anchor="w", padx=10, pady=5)
    rental_rate_entry = ttk.Entry(form_frame)
    rental_rate_entry.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Status").pack(anchor="w", padx=10, pady=5)
    status_combobox = ttk.Combobox(
        form_frame, values=["Available", "Not Available"], state="readonly"
    )
    status_combobox.set("Available")
    status_combobox.pack(fill="x", padx=10, pady=5)

    ttk.Button(form_frame, text="Add Product",
               command=lambda: handle_add()).pack(pady=10)

    # Rental Information Form
    ttk.Label(rental_form_frame, text="Rental Information",
              font=("Arial", 14, "bold")).pack(pady=10)
    product_info_label = ttk.Label(
        rental_form_frame, text="", font=("Arial", 12), justify="left")
    product_info_label.pack(fill="x", padx=10, pady=10)

    rental_fields = {}
    fields = [
        ("Customer Name", "name"),
        ("Phone Number", "phone"),
        ("Email (Optional)", "email"),
        ("Vehicle Number Plate (Optional)", "vehicle"),
        ("Place", "place"),
        ("Rental Duration (Days/Hours)", "duration"),
    ]
    for label, key in fields:
        ttk.Label(rental_form_frame, text=label).pack(
            anchor="w", padx=10, pady=5)
        entry = ttk.Entry(rental_form_frame)
        entry.pack(fill="x", padx=10, pady=5)
        rental_fields[key] = entry

    ttk.Label(rental_form_frame, text="Entry Time").pack(
        anchor="w", padx=10, pady=5)
    entry_time_label = ttk.Label(
        rental_form_frame, text="", relief="sunken", anchor="w")
    entry_time_label.pack(fill="x", padx=10, pady=5)

    ttk.Label(rental_form_frame, text="Exit Time").pack(
        anchor="w", padx=10, pady=5)
    exit_time_label = ttk.Label(
        rental_form_frame, text="", relief="sunken", anchor="w")
    exit_time_label.pack(fill="x", padx=10, pady=5)

    ttk.Button(rental_form_frame, text="Submit Rental",
               command=lambda: submit_rental()).pack(pady=10)

    # Functions for Product Form
    def handle_add():
        name = product_name_entry.get()
        tag_id = tag_entry.get()
        category = category_entry.get()
        rental_type = rental_type_combobox.get()
        rental_rate = rental_rate_entry.get()
        status = status_combobox.get()

        if not name or not tag_id:
            messagebox.showerror(
                "Error", "Product Name and RFID Tag are required.")
            return

        try:
            rental_rate = float(rental_rate)
        except ValueError:
            messagebox.showerror("Error", "Rental Rate must be a number.")
            return

        result = add_product(name, tag_id, category,
                             status, rental_type, rental_rate)
        if result:
            messagebox.showerror("Error", result)
        else:
            messagebox.showinfo("Success", "Product added successfully!")

    def submit_rental():
        customer_name = rental_fields["name"].get()
        phone = rental_fields["phone"].get()
        email = rental_fields["email"].get()
        vehicle = rental_fields["vehicle"].get()
        place = rental_fields["place"].get()
        duration = rental_fields["duration"].get()
        entry_time = entry_time_label.cget("text")

        if not customer_name or not phone or not place or not duration:
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        try:
            product = fetch_product_by_tag(tag_entry.get())
            if product:
                product_id = product[0]
                rental_id = add_rental(
                    product_id, customer_name, phone, email, vehicle, place, int(
                        duration)
                )
                update_product_status(product_id, "Rented")
                messagebox.showinfo(
                    "Success", f"Rental created successfully for {customer_name}!"
                )
            else:
                messagebox.showerror(
                    "Error", "No product associated with this tag!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # RFID Detection
    def on_tag_detected(tag_id):
        global last_detected_tag, last_detected_time

        current_time = time.time()
        debounce_interval = 5

        if tag_id == last_detected_tag and (current_time - last_detected_time) < debounce_interval:
            print(f"Ignoring repeated detection for tag {tag_id}")
            return

        last_detected_tag = tag_id
        last_detected_time = current_time

        product = fetch_product_by_tag(tag_id)
        if product:
            product_id, name, status, rental_type, rental_rate = product
            product_name_entry.delete(0, "end")
            product_name_entry.insert(0, name)
            tag_entry.delete(0, "end")
            tag_entry.insert(0, tag_id)
            rental_type_combobox.set(rental_type)
            rental_rate_entry.delete(0, "end")
            rental_rate_entry.insert(0, rental_rate)
            status_combobox.set(status)
            product_info_label.config(
                text=f"Product Name: {name}\nRental Type: {rental_type}\nRental Rate: {rental_rate}"
            )

            # Update Entry Time
            entry_time_label.config(text=time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            messagebox.showinfo(
                "Info", "No product found. You can register it now.")
            tag_entry.delete(0, "end")
            tag_entry.insert(0, tag_id)
            product_info_label.config(text="")

    # Start RFID Reader
    start_rfid_thread(on_tag_detected)


def calculate_rental_cost(start_time, rental_type, rental_rate):
    from datetime import datetime

    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = datetime.now()
    duration = (end - start).total_seconds()

    if rental_type == "Per Hour":
        hours = duration / 3600
        return round(hours * rental_rate, 2)
    elif rental_type == "Per Day":
        days = duration / (24 * 3600)
        return round(days * rental_rate, 2)
    return 0


last_detected_tag = None
last_detected_time = 0


def create_rental_flow_ui(frame):
    import sqlite3
    # Title
    ttk.Label(frame, text="Rental History", font=(
        "Arial", 18, "bold")).pack(pady=10)

    # Table for Rental History
    rental_table = ttk.Treeview(frame, columns=(
        "ID", "Customer", "Phone", "Product Name", "Rental Type", "Place", "Duration", "Entry Time", "Exit Time", "Total Cost"), show="headings")

    # Define headings
    rental_table.heading("ID", text="ID")
    rental_table.heading("Customer", text="Customer")
    rental_table.heading("Phone", text="Phone")
    rental_table.heading("Product Name", text="Product Name")
    rental_table.heading("Rental Type", text="Rental Type")
    rental_table.heading("Place", text="Place")
    rental_table.heading("Duration", text="Duration")
    rental_table.heading("Entry Time", text="Entry Time")
    rental_table.heading("Exit Time", text="Exit Time")
    rental_table.heading("Total Cost", text="Total Cost")

    # Define column widths
    rental_table.column("ID", width=50)
    rental_table.column("Customer", width=150)
    rental_table.column("Phone", width=150)
    rental_table.column("Product Name", width=150)
    rental_table.column("Rental Type", width=100)
    rental_table.column("Place", width=150)
    rental_table.column("Duration", width=100)
    rental_table.column("Entry Time", width=150)
    rental_table.column("Exit Time", width=150)
    rental_table.column("Total Cost", width=100)

    rental_table.pack(fill="both", expand=True, padx=10, pady=10)

    # Load Rental History
    def load_rental_history():
        for item in rental_table.get_children():
            rental_table.delete(item)
        conn = sqlite3.connect("db/rental.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                rentals.id, 
                rentals.customer_name, 
                rentals.phone, 
                products.name AS product_name, 
                rentals.rental_type, 
                rentals.place, 
                rentals.rental_duration, 
                rentals.start_time, 
                rentals.end_time, 
                rentals.total_cost
            FROM rentals
            INNER JOIN products ON rentals.product_id = products.id
        """)
        rows = cursor.fetchall()
        for row in rows:
            rental_table.insert("", "end", values=row)
        conn.close()

    # Refresh Table Button
    refresh_button = ttk.Button(
        frame, text="Refresh Table", command=load_rental_history)
    refresh_button.pack(pady=10)

    # Initial load of rental history
    load_rental_history()
