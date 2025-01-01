# Machinery Rental Management System

## Project Description
Machinery Rental Management System is a Python-based application designed to manage and track the rental of machinery. Utilizing RFID technology, the system automates the registration, rental, and return processes, ensuring a seamless experience for both operators and customers.

## Features
- **Product Registration**: Easily register machinery with relevant details and an RFID tag.
- **Rental Management**: Handle the entire rental process, from checking out machinery to returning it.
- **Inventory Tracking**: Keep track of all machinery statuses in real-time.
- **RFID Integration**: Automate machinery identification and management through RFID technology.
- **Reporting**: Generate reports on rentals, returns, and usage patterns.

## Installation

### Prerequisites
- Python 3.7 or above
- PyInstaller (for bundling the application)
- All dependencies listed in `requirements.txt`

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/shitcodebykaushik/MachineryRentalSystem.git
   cd MachineryRentalSystem

2. **Install packages and run**
   ```bash
   python3 -m venv venv
   pip install -r requirements.txt
   python main.py
3.**Building the Application with PyInstaller**
   ```bash
   pyinstaller --onefile --add-data "db/rental.db:db" main.py
```
3. ##Usage
4.  -Connect the RFID Reader into your PC through USB Port
    -Register new machinery using the "Register Products" tab.
    -Manage rentals in the "Rental Flow" tab.
    -View and manage current inventory in the "Products Management" tab.
