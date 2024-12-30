import threading
import serial
from tkinter import messagebox


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

    def run(self):
        try:
            self.ser = serial.Serial(
                '/dev/tty.usbserial-AR0JT4RL', 115200, timeout=1)
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
        hex_data = raw_data.hex()
        if hex_data.startswith("a55a"):
            return hex_data[:40]  # Extract the first 40 characters
        print("None")
        return None


# Singleton pattern for managing the RFID thread
rfid_thread = None


def start_rfid_thread(callback=None):
    print("Starting RFID thread")
    """Start the RFID thread."""
    global rfid_thread
    if not rfid_thread or not rfid_thread.is_alive():
        rfid_thread = RFIDReaderThread()
        if callback:
            rfid_thread.set_on_tag_detected_callback(callback)
        rfid_thread.start()
    return rfid_thread


def stop_rfid_thread():
    print("Stop RFID thread")
    """Stop the RFID thread."""
    global rfid_thread
    if rfid_thread:
        rfid_thread.stop()
        rfid_thread.join()
        rfid_thread = None
