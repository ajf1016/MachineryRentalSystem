import threading
import serial
import serial.tools.list_ports
from tkinter import messagebox
import platform


class RFIDReaderThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.ser = None
        self.on_tag_detected_callback = None  # Callback for tag detection
        print("Class called")

    def set_on_tag_detected_callback(self, callback):
        """Set the callback function for detected tags."""
        self.on_tag_detected_callback = callback

    def find_serial_port(self):
        """Find the appropriate serial port dynamically based on the OS."""
        try:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if platform.system() == "Windows":
                    # Windows ports usually have "COM" in their names
                    if "COM" in port.device.upper():
                        return port.device
                elif platform.system() == "Darwin":  # macOS
                    # macOS ports usually contain "usbserial" or "tty"
                    if "usbserial" in port.device.lower() or "tty" in port.device.lower():
                        return port.device
            return None
        except Exception as e:
            messagebox.showerror(
                "RFID Reader Error",
                f"Error detecting serial port: {e}. Ensure the device is connected.",
            )
            return None

    def run(self):
        try:
            serial_port = self.find_serial_port()
            if not serial_port:
                raise FileNotFoundError("No compatible serial port found.")

            self.ser = serial.Serial(serial_port, 115200, timeout=1)
            print(f"Connected to RFID reader on port {serial_port}")

            while self.running:
                raw_data = self.ser.readline()
                if raw_data:
                    tag_id = self.parse_tag_data(raw_data)
                    if tag_id and self.on_tag_detected_callback:
                        self.on_tag_detected_callback(tag_id)
        except serial.SerialException as e:
            messagebox.showerror(
                "RFID Reader Error", f"SerialException: {e}. Ensure the device is connected."
            )
        except FileNotFoundError:
            messagebox.showerror(
                "RFID Reader Error", "Serial port not found. Ensure the device is connected."
            )
        except Exception as e:
            # Error: list indices must be integers or slices, not tuple
            print(f"Errorzzz: {e}")
            messagebox.showerror(
                "RFID Reader Error", f"Unexpected error occurred: {e}"
            )
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        """Stop the RFID reader thread."""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

    @staticmethod
    def parse_tag_data(raw_data):
        """Parse the raw RFID data to extract the stable tag ID."""
        try:
            hex_data = raw_data.hex()
            if hex_data.startswith("a55a"):  # Example header check
                return hex_data[:40]  # Extract the first 40 characters
        except Exception as e:
            print(f"Error parsing tag data: {e}")
        return None


# Singleton pattern for managing the RFID thread
rfid_thread = None


def start_rfid_thread(callback=None):
    """Start the RFID thread."""
    print("Starting RFID thread")
    global rfid_thread
    if not rfid_thread or not rfid_thread.is_alive():
        rfid_thread = RFIDReaderThread()
        if callback:
            rfid_thread.set_on_tag_detected_callback(callback)
        rfid_thread.start()
    return rfid_thread


def stop_rfid_thread():
    """Stop the RFID thread."""
    print("Stopping RFID thread")
    global rfid_thread
    if rfid_thread:
        rfid_thread.stop()
        rfid_thread.join()
        rfid_thread = None
