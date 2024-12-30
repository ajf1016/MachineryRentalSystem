import tkinter as tk
from ttkbootstrap import Style

# Import modules
from modules.ui import create_ui

# Initialize the application


def main():
    style = Style(theme="solar")
    root = style.master
    root.title("Machinery Rental Management System")
    root.geometry("800x600")

    # Call the UI creation function
    create_ui(root)

    root.mainloop()


if __name__ == "__main__":
    main()
