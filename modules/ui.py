from tkinter import ttk
from tkinter import messagebox
from modules.database import add_product, update_product, delete_product, fetch_all_products


def create_ui(root):
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

    # Placeholder content for Rental Flow
    ttk.Label(rental_frame, text="Track Rentals Here").pack(pady=20)


def create_register_products_ui(frame):
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

    ttk.Label(form_frame, text="Status").grid(row=3, column=0, padx=5, pady=5)
    status_combobox = ttk.Combobox(
        form_frame, values=["Available", "Not Available"], state="readonly")
    status_combobox.set("Available")
    status_combobox.grid(row=3, column=1, padx=5, pady=5)

    # Buttons
    def handle_add():
        name = product_name_entry.get()
        tag_id = tag_entry.get()
        category = category_entry.get()
        status = status_combobox.get()

        if not name or not tag_id:
            messagebox.showerror(
                "Error", "Product Name and RFID Tag are required.")
            return

        result = add_product(name, tag_id, category, status)
        if result:
            messagebox.showerror("Error", result)
        else:
            messagebox.showinfo("Success", "Product added successfully!")
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
        row=4, column=0, padx=5, pady=10)
    ttk.Button(form_frame, text="Delete Product", command=handle_delete).grid(
        row=4, column=1, padx=5, pady=10)

    # Treeview for Displaying Products
    tree = ttk.Treeview(frame, columns=("ID", "Name", "Tag",
                        "Category", "Status"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Tag", text="RFID Tag")
    tree.heading("Category", text="Category")
    tree.heading("Status", text="Status")
    tree.column("ID", width=50)
    tree.column("Name", width=150)
    tree.column("Tag", width=150)
    tree.column("Category", width=100)
    tree.column("Status", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_treeview():
        for item in tree.get_children():
            tree.delete(item)
        for product in fetch_all_products():
            tree.insert("", "end", values=product)

    refresh_treeview()
