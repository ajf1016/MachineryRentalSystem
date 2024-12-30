from tkinter import ttk, messagebox
from modules.database import add_product, fetch_all_products, delete_product, update_product
import threading
import serial
from modules.rental_flow import detect_rfid

rfid_thread = None  # Global RFID thread reference
active_tab = None


def start_rfid_reader(on_tag_detected):
    global rfid_thread
    if rfid_thread and rfid_thread.is_alive():
        rfid_thread.stop()
    rfid_thread = RFIDReaderThread(on_tag_detected)
    rfid_thread.start()


def stop_rfid_reader():
    global rfid_thread
    if rfid_thread:
        rfid_thread.stop()
        rfid_thread.join()


def on_close(root):
    stop_rfid_reader()
    root.destroy()


def on_tag_detected(tag_id):
    """
    Dispatch the detected tag to the correct tab handler.
    """
    if active_tab == "Register Products":
        if register_on_tag_detected:
            register_on_tag_detected(tag_id)
    elif active_tab == "Rental Flow":
        if rental_on_tag_detected:
            rental_on_tag_detected(tag_id)


register_on_tag_detected = None
rental_on_tag_detected = None


def create_ui(root):
    global active_tab

    notebook = ttk.Notebook(root)
    register_frame = ttk.Frame(notebook)
    rental_frame = ttk.Frame(notebook)

    notebook.add(register_frame, text="Register Products")
    notebook.add(rental_frame, text="Rental Flow")
    notebook.pack(fill="both", expand=True)

    # Create tabs
    create_register_products_ui(register_frame)
    create_rental_flow_ui(rental_frame)

    def on_tab_changed(event):
        global active_tab
        selected_tab = event.widget.tab(event.widget.index("current"))["text"]
        active_tab = selected_tab

        if selected_tab == "Rental Flow":
            # Start RFID reader for rental flow
            start_rfid_reader(on_tag_detected)
        else:
            stop_rfid_reader()  # Stop RFID reader when switching tabs

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # Initialize active tab
    active_tab = notebook.tab(notebook.index("current"))["text"]
    if active_tab == "Rental Flow":
        start_rfid_reader(on_tag_detected)

    # Handle application close
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))


def parse_tag_data(raw_data):
    """
    Parse the raw RFID data to extract the stable tag ID.
    """
    hex_data = raw_data.hex()
    if hex_data.startswith("a55a"):
        # Extract the stable part of the tag ID (first 24 bytes or 48 hex characters)
        return hex_data[:40]
    return None


class RFIDReaderThread(threading.Thread):
    def __init__(self, on_tag_detected):
        super().__init__()
        self.on_tag_detected = on_tag_detected
        self.running = True
        self.ser = None  # Initialize serial port variable here

    def run(self):
        try:
            self.ser = serial.Serial(
                '/dev/tty.usbserial-AR0JT4RL', 115200, timeout=1)
            while self.running:
                raw_data = self.ser.readline()
                if raw_data:
                    tag_id = parse_tag_data(raw_data)
                    if tag_id:
                        self.on_tag_detected(tag_id)
        except serial.SerialException as e:
            print(f"Error: {e}")
            messagebox.showerror("RFID Reader Error", f"Device error: {
                                 e}. Ensure the RFID reader is connected and no other process is using the port.")
        except FileNotFoundError:
            print("Error: Serial port not found.")
            messagebox.showerror(
                "RFID Reader Error", "Serial port not found. Please check the connection.")

        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.running = False


def create_register_products_ui(frame):
    global register_on_tag_detected
    # Frame for Form
    form_frame = ttk.Frame(frame)
    form_frame.pack(side="top", fill="x", padx=10, pady=10)

    # Product Form
    ttk.Label(form_frame, text="Product Name").grid(
        row=0, column=0, padx=5, pady=5)
    product_name_entry = ttk.Entry(form_frame)
    product_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="RFID Tag").grid(
        row=1, column=0, padx=5, pady=5)
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Category").grid(
        row=2, column=0, padx=5, pady=5)
    category_entry = ttk.Entry(form_frame)
    category_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Rental Type").grid(
        row=3, column=0, padx=5, pady=5)
    rental_type_combobox = ttk.Combobox(
        form_frame, values=["Per Day", "Per Hour"], state="readonly")
    rental_type_combobox.set("Per Day")
    rental_type_combobox.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Rental Rate").grid(
        row=4, column=0, padx=5, pady=5)
    rental_rate_entry = ttk.Entry(form_frame)
    rental_rate_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Status").grid(row=5, column=0, padx=5, pady=5)
    status_combobox = ttk.Combobox(
        form_frame, values=["Available", "Not Available"], state="readonly")
    status_combobox.set("Available")
    status_combobox.grid(row=5, column=1, padx=5, pady=5)

    # Buttons
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
            refresh_treeview()

    def handle_edit():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to edit.")
            return

        product = tree.item(selected_item)["values"]
        product_id = product[0]

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

        update_product(product_id, name, tag_id, category,
                       status, rental_type, rental_rate)
        messagebox.showinfo("Success", "Product updated successfully!")
        refresh_treeview()

    def handle_delete():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product_id = tree.item(selected_item)["values"][0]
        delete_product(product_id)
        messagebox.showinfo("Success", "Product deleted successfully!")
        refresh_treeview()

    ttk.Button(form_frame, text="Add Product", command=handle_add).grid(
        row=6, column=0, padx=5, pady=10)
    ttk.Button(form_frame, text="Edit Product", command=handle_edit).grid(
        row=6, column=1, padx=5, pady=10)
    ttk.Button(form_frame, text="Delete Product", command=handle_delete).grid(
        row=6, column=2, padx=5, pady=10)

    # Treeview for Displaying Products
    tree = ttk.Treeview(frame, columns=("ID", "Name", "Tag", "Category",
                        "Status", "Added Time", "Rental Type", "Rental Rate"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Tag", text="RFID Tag")
    tree.heading("Category", text="Category")
    tree.heading("Status", text="Status")
    tree.heading("Added Time", text="Added Time")
    tree.heading("Rental Type", text="Rental Type")
    tree.heading("Rental Rate", text="Rental Rate")
    tree.column("ID", width=50)
    tree.column("Name", width=150)
    tree.column("Tag", width=150)
    tree.column("Category", width=100)
    tree.column("Status", width=100)
    tree.column("Added Time", width=150)
    tree.column("Rental Type", width=100)
    tree.column("Rental Rate", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_treeview():
        for item in tree.get_children():
            tree.delete(item)
        for product in fetch_all_products():
            tree.insert("", "end", values=product)

    def on_tag_detected(tag_id):
        tag_entry.delete(0, "end")
        tag_entry.insert(0, tag_id)

    refresh_treeview()

    # Auto-fill RFID Tag when a tag is detected

    def on_detected(tag_id):
        """
        Auto-fill RFID Tag in the registration form when detected.
        """
        tag_entry.delete(0, "end")
        tag_entry.insert(0, tag_id)

    register_on_tag_detected = on_detected

    # Start RFID Reader in a separate thread
    rfid_reader = RFIDReaderThread(on_tag_detected)
    rfid_reader.start()

    # Stop the reader when the app closes
    frame.winfo_toplevel().protocol("WM_DELETE_WINDOW", rfid_reader.stop)


def create_rental_flow_ui(frame):
    global rental_on_tag_detected

    rental_frame = ttk.Frame(frame)
    rental_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    product_details = ttk.Label(rental_frame, text="", font=("Arial", 12))
    product_details.pack(pady=10)

    def on_detected(tag_id):
        """
        Handle detected tag in rental flow and update the UI.
        """
        result = detect_rfid(tag_id)
        if "error" in result:
            product_details.config(text=f"Error: {result['error']}")
        else:
            details = (
                f"Product Name: {result['name']}\n"
                f"Category: {result['category']}\n"
                f"Old Status: {result['old_status']}\n"
                f"New Status: {result['new_status']}\n"
                f"Timestamp: {result['time']}"
            )
            product_details.config(text=details)

    rental_on_tag_detected = on_detected
