from tkinter import ttk, messagebox
import tkinter as tk
from modules.database import (add_product, fetch_all_products, delete_product, update_product,
                              fetch_product_by_tag, add_rental, update_product_status, fetch_active_rental, end_rental)
from .rfid_handler import start_rfid_thread, stop_rfid_thread
import time
import sqlite3
from .utils import format_time_to_ist

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
    product_management_frame = ttk.Frame(notebook)

    notebook.add(register_frame, text="Register Products")
    notebook.add(rental_frame, text="Rental Flow")
    notebook.add(product_management_frame, text="Products Management")

    notebook.pack(fill="both", expand=True)

    # Create Register Products UI
    create_register_products_ui(register_frame)
    create_rental_flow_ui(rental_frame)
    create_products_table_ui(product_management_frame)

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

 # Styles for consistent light theme
    style = ttk.Style()
    style.configure("TFrame", foreground="#000", background="#fff")
    style.configure("TLabel", foreground="#000",
                    background="#fff", font=("Arial", 12))
    style.configure("TEntry", foreground="#000",
                    background="#fff", font=("Arial", 12))
    style.configure("TCombobox", foreground="#000",
                    background="#fff", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12, "bold"),
                    background="#0078D7", foreground="#ffffff")

    # Frames
    form_frame = ttk.Frame(frame, relief="solid", borderwidth=1)
    form_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    rental_form_frame = ttk.Frame(frame, relief="solid", borderwidth=1)
    rental_form_frame.pack(side="right", fill="both",
                           expand=True, padx=10, pady=10)

    # Product Registration Form
    ttk.Label(form_frame, text="Product Registration",
              font=("Arial", 14, "bold"), foreground="#000", background="#fff").pack(pady=10)

    # Product Registration Fields
    product_fields = [
        ("Product Name", "name"),
        ("RFID Tag", "tag"),
        ("Category", "category"),
        ("Rental Type", "type"),
        ("Rental Rate", "rate"),
        ("Status", "status"),
    ]
    product_entries = {}
    for label, key in product_fields:
        ttk.Label(form_frame, text=label).pack(anchor="w", padx=10, pady=5)
        if key == "type":
            combobox = ttk.Combobox(
                form_frame, values=["Per Day", "Per Hour"], state="readonly")
            combobox.set("Per Day")
            combobox.pack(fill="x", padx=10, pady=5)
            product_entries[key] = combobox
        elif key == "status":
            combobox = ttk.Combobox(
                form_frame, values=["Available", "Not Available"], state="readonly")
            combobox.set("Available")
            combobox.pack(fill="x", padx=10, pady=5)
            product_entries[key] = combobox
        else:
            entry = ttk.Entry(form_frame)
            entry.pack(fill="x", padx=10, pady=5)
            product_entries[key] = entry

    ttk.Button(form_frame, text="Add Product",
               command=lambda: handle_add()).pack(pady=10)

    # Rental Information Form
    ttk.Label(rental_form_frame, text="Rental Information",
              font=("Arial", 14, "bold"), foreground="#000", background="#fff").pack(pady=10)
    product_info_label = ttk.Label(rental_form_frame, text="", font=(
        "Arial", 12), justify="left", foreground="#000", background="#fff", relief="sunken")
    product_info_label.pack(fill="x", padx=10, pady=10)

    # Rental Fields
    rental_fields = [
        ("Customer Name", "name"),
        ("Phone Number", "phone"),
        ("Email (Optional)", "email"),
        ("Vehicle Number Plate (Optional)", "vehicle"),
        ("Place", "place"),
        ("Rental Duration (Days/Hours)", "duration"),
    ]
    rental_entries = {}
    for label, key in rental_fields:
        ttk.Label(rental_form_frame, text=label).pack(
            anchor="w", padx=10, pady=5)
        entry = ttk.Entry(rental_form_frame)
        entry.pack(fill="x", padx=10, pady=5)
        rental_entries[key] = entry

    ttk.Label(rental_form_frame, text="Entry Time").pack(
        anchor="w", padx=10, pady=5)
    entry_time_label = ttk.Label(rental_form_frame, text="", relief="sunken", anchor="w", font=(
        "Arial", 12), background="#ffffff", foreground="#000000")
    entry_time_label.pack(fill="x", padx=10, pady=5)

    ttk.Label(rental_form_frame, text="Exit Time").pack(
        anchor="w", padx=10, pady=5)
    exit_time_label = ttk.Label(rental_form_frame, text="", relief="sunken", anchor="w", font=(
        "Arial", 12), background="#ffffff", foreground="#000000")
    exit_time_label.pack(fill="x", padx=10, pady=5)

    ttk.Button(rental_form_frame, text="Submit Rental",
               command=lambda: submit_rental()).pack(pady=10)

    # Functions for Product Form

    def handle_add():
        name = product_entries["name"].get()
        tag_id = product_entries["tag"].get()
        category = product_entries["category"].get()
        rental_type = product_entries["type"].get()
        rental_rate = product_entries["rate"].get()
        status = product_entries["status"].get()

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
        customer_name = rental_entries["name"].get()
        phone = rental_entries["phone"].get()
        email = rental_entries["email"].get()
        vehicle = rental_entries["vehicle"].get()
        place = rental_entries["place"].get()
        duration = rental_entries["duration"].get()
        entry_time = entry_time_label.cget("text")

        if not customer_name or not phone or not place or not duration:
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        if product_entries["status"].get() == "Rented":
            messagebox.showerror("Error", "Product is already rented!")
            return

        try:
            product = fetch_product_by_tag(product_entries["tag"].get())
            if product:
                product_id = product[0]
                add_rental(product_id, customer_name, phone,
                           email, vehicle, place, int(duration))
                update_product_status(product_id, "Rented")
                messagebox.showinfo(
                    "Success", f"Rental created successfully for {customer_name}!")
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
            product_id, name, status, rental_type, rental_rate = product
            product_entries["name"].delete(0, "end")
            product_entries["name"].insert(0, name)
            product_entries["tag"].delete(0, "end")
            product_entries["tag"].insert(0, tag_id)
            product_entries["type"].set(rental_type)
            product_entries["rate"].delete(0, "end")
            product_entries["rate"].insert(0, rental_rate)
            product_entries["status"].set(status)
            product_info_label.config(
                text=f"Product Name: {name}\nRental Type: {rental_type}\nRental Rate: {rental_rate}"
            )

            if status == "Rented":
                # Handle already rented product
                rental = fetch_active_rental(product_id)
                if rental:
                    rental_id, start_time = rental
                    confirm = messagebox.askyesno(
                        "End Rental",
                        f"The product '{name}' is currently rented. Do you want to mark it as received?",
                    )
                    if confirm:
                        # Calculate rental cost
                        total_cost = calculate_rental_cost(
                            start_time, rental_type, rental_rate
                        )
                        end_rental(rental_id, total_cost)
                        update_product_status(product_id, "Available")
                        exit_time_label.config(
                            text=time.strftime("%Y-%m-%d %H:%M:%S"))
                        messagebox.showinfo(
                            "Rental Ended",
                            f"Rental for '{name}' ended.\nTotal Cost: {total_cost:.2f}",
                        )
                        product_info_label.config(text="")
                        clear_rental_form()
            else:
                # Update Entry Time for new rental
                entry_time_label.config(
                    text=time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            messagebox.showinfo(
                "Info", "No product found. You can register it now."
            )
            product_entries["tag"].delete(0, "end")
            product_entries["tag"].insert(0, tag_id)
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

    def clear_rental_form():
        for key in rental_fields:
            rental_fields[key].delete(0, "end")
        entry_time_label.config(text="")
        exit_time_label.config(text="")


def create_rental_flow_ui(frame):
    import sqlite3
    # Set style for the background and table

    # Set style for the Treeview and headings
    style = ttk.Style()
    # style.theme_use("default")  # Ensure consistent styling
    style.configure(
        "Treeview",

        font=("Arial", 12),  # Slightly smaller font
        rowheight=25,  # Adjusted row height
        background="#ffffff",  # White background
        foreground="#000000",  # Black text
        fieldbackground="#ffffff",  # Background for rows
    )
    style.configure(
        "Treeview.Heading",
        font=("Arial", 15, "bold"),  # Slightly reduced heading font
        background="#fff",
        foreground="#000000",  # Black text for heading
    )
    style.map(
        "Treeview",
        background=[("selected", "#cdeafe")],  # Light blue when selected
        foreground=[("selected", "#000000")],  # Black text for selected
    )

    # Title
    title_label = ttk.Label(
        frame,
        text="Rental History",
        font=("Arial", 15, "bold"),  # Smaller title font for consistency
        background="#f9f9f9",
        foreground="#000000"
    )
    title_label.pack(pady=10)

    # Table for Rental History
    rental_table = ttk.Treeview(frame, columns=(
        "ID", "Customer", "Phone", "Product Name", "Rental Type", "Place", "Duration", "Entry Time", "Exit Time", "Total Cost"), show="headings")
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
    rental_table.column("ID", width=50, anchor="center")
    rental_table.column("Customer", width=150, anchor="center")
    rental_table.column("Phone", width=100, anchor="center")
    rental_table.column("Product Name", width=150, anchor="center")
    rental_table.column("Rental Type", width=100, anchor="center")
    rental_table.column("Place", width=150, anchor="center")
    rental_table.column("Duration", width=100, anchor="center")
    rental_table.column("Entry Time", width=150, anchor="center")
    rental_table.column("Exit Time", width=150, anchor="center")
    rental_table.column("Total Cost", width=100, anchor="center")
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
        print("ROWS : ", rows)
        for row in rows:
            formatted_start_time = format_time_to_ist(
                row[7]) if row[7] else "N/A"
            formatted_end_time = format_time_to_ist(
                row[8]) if row[8] else "N/A"
            rental_table.insert("", "end", values=(
                row[0],  # ID
                row[1],  # Customer Name
                row[2],  # Phone
                row[3],  # Place
                row[4],  # Duration
                row[5],  # Duration
                row[6],  # Duration
                formatted_start_time,  # Entry Time (formatted)
                formatted_end_time,  # Exit Time (formatted)
                row[9],  # Duration
            ))
        conn.close()

    # Refresh Table Button
    refresh_button = ttk.Button(
        frame, text="Refresh Table", command=load_rental_history)
    refresh_button.pack(pady=10)

    # Initial load of rental history
    load_rental_history()


def create_products_table_ui(frame):
    # Set style for the background and table
    style = ttk.Style()
    style.configure(
        "TFrame",
        background="#f9f9f9",  # Light background
    )
    style.configure(
        "Treeview",
        font=("Arial", 12),
        rowheight=30,
        background="#ffffff",
        foreground="#000000",
    )
    style.configure(
        "Treeview.Heading",
        font=("Arial", 15, "bold"),
        background="#f1f1f1",
        foreground="#000000",
    )
    style.map(
        "Treeview",
        background=[("selected", "#cdeafe")],
        foreground=[("selected", "#000000")],
    )

    # Title
    title_label = ttk.Label(
        frame,
        text="Products Management",
        font=("Arial", 20, "bold"),
        # color="black",
        background="#fff",
        foreground="#000000",
    )
    title_label.pack(pady=10)

    # Table for Products
    product_table = ttk.Treeview(
        frame,
        columns=(
            "ID",
            "Name",
            "RFID Tag",
            "Category",
            "Status",
            "Rental Type",
            "Rental Rate",
        ),
        show="headings",
    )
    product_table.heading("ID", text="ID")
    product_table.heading("Name", text="Name")
    product_table.heading("RFID Tag", text="RFID Tag")
    product_table.heading("Category", text="Category")
    product_table.heading("Status", text="Status")
    product_table.heading("Rental Type", text="Rental Type")
    product_table.heading("Rental Rate", text="Rental Rate")

    # Adjust column width
    product_table.column("ID", width=50, anchor="center")
    product_table.column("Name", width=200, anchor="center")
    product_table.column("RFID Tag", width=150, anchor="center")
    product_table.column("Category", width=150, anchor="center")
    product_table.column("Status", width=120, anchor="center")
    product_table.column("Rental Type", width=120, anchor="center")
    product_table.column("Rental Rate", width=120, anchor="center")

    product_table.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollbars
    scrollbar_x = ttk.Scrollbar(
        frame, orient="horizontal", command=product_table.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    scrollbar_y = ttk.Scrollbar(
        frame, orient="vertical", command=product_table.yview)
    scrollbar_y.pack(side="right", fill="y")

    product_table.configure(xscrollcommand=scrollbar_x.set,
                            yscrollcommand=scrollbar_y.set)

    # Load Products
    def load_products():
        for item in product_table.get_children():
            product_table.delete(item)
        products = fetch_all_products()
        for product in products:
            print("Product", product)
            product_table.insert("", "end", values=product)

    load_products()

    # Product Edit and Delete Buttons
    button_frame = ttk.Frame(frame)  # No `background` directly here
    button_frame.pack(fill="x", padx=10, pady=10)

    def handle_edit_product():
        selected_item = product_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to edit.")
            return

        product = product_table.item(selected_item)["values"]
        print("Selected Product:", product)
        if not product:
            messagebox.showerror("Error", "Failed to fetch product details.")
            return

        # Extract product details
        product_id, name, tag_id, category, status, rental_type,  rental_rate = product

        # Create edit window
        edit_window = tk.Toplevel()
        edit_window.title("Edit Product")
        edit_window.geometry("400x400")

        ttk.Label(edit_window, text="Product Name").pack(
            anchor="w", padx=10, pady=5)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, name)  # Auto-fill name
        name_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_window, text="RFID Tag").pack(
            anchor="w", padx=10, pady=5)
        tag_entry = ttk.Entry(edit_window)
        tag_entry.insert(0, tag_id)  # Auto-fill RFID tag
        tag_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_window, text="Category").pack(
            anchor="w", padx=10, pady=5)
        category_entry = ttk.Entry(edit_window)
        category_entry.insert(0, category)  # Auto-fill category
        category_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_window, text="Rental Type").pack(
            anchor="w", padx=10, pady=5)
        rental_type_combobox = ttk.Combobox(
            edit_window, values=["Per Day", "Per Hour"], state="readonly"
        )
        rental_type_combobox.set(rental_type)  # Auto-fill rental type
        rental_type_combobox.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_window, text="Rental Rate").pack(
            anchor="w", padx=10, pady=5)
        rental_rate_entry = ttk.Entry(edit_window)
        rental_rate_entry.insert(0, rental_rate)  # Auto-fill rental rate
        rental_rate_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(edit_window, text="Status").pack(anchor="w", padx=10, pady=5)
        status_combobox = ttk.Combobox(
            edit_window, values=["Available", "Not Available"], state="readonly"
        )
        status_combobox.set(status)  # Auto-fill status
        status_combobox.pack(fill="x", padx=10, pady=5)

        def save_changes():
            new_name = name_entry.get()
            new_tag_id = tag_entry.get()
            new_category = category_entry.get()
            new_rental_type = rental_type_combobox.get()
            new_rental_rate = rental_rate_entry.get()
            new_status = status_combobox.get()

            if not new_name or not new_tag_id:
                messagebox.showerror(
                    "Error", "Name and RFID Tag are required.")
                return

            try:
                new_rental_rate = float(new_rental_rate)
            except ValueError:
                messagebox.showerror("Error", "Rental Rate must be a number.")
                return

            update_product(product_id, new_name, new_tag_id, new_category,
                           new_status, new_rental_type, new_rental_rate)
            messagebox.showinfo("Success", "Product updated successfully!")
            edit_window.destroy()
            load_products()

        ttk.Button(edit_window, text="Save Changes", command=save_changes).pack(
            pady=10)
        ttk.Button(edit_window, text="Cancel",
                   command=edit_window.destroy).pack(pady=10)

    def handle_delete_product():
        selected_item = product_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product = product_table.item(selected_item)["values"]
        product_id = product[0]
        confirm = messagebox.askyesno(
            "Delete Product", f"Are you sure you want to delete the product '{product[1]}'?"
        )
        if confirm:
            delete_product(product_id)
            messagebox.showinfo("Success", "Product deleted successfully!")
            load_products()

    ttk.Button(button_frame, text="Edit Product",
               command=handle_edit_product).pack(side="left", padx=10, pady=10)
    ttk.Button(button_frame, text="Delete Product",
               command=handle_delete_product).pack(side="left", padx=10, pady=10)

    # Refresh Button
    ttk.Button(button_frame, text="Refresh Table", command=load_products).pack(
        side="right", padx=10, pady=10)
