import serial

ser = serial.Serial('/dev/tty.usbserial-AR0JT4RL', 115200, timeout=1)

try:
    print("Listening for tag data...")
    while True:
        raw_data = ser.readline()  # Read raw binary data
        if raw_data:
            hex_data = raw_data.hex()  # Convert to hexadecimal
            print(f"Raw Hex Data: {hex_data}")

            # Check if the frame starts with 'a55a' (start bytes)
            if hex_data.startswith('a55a'):
                # Extract the payload (example: tag data starts at byte 6 and ends before checksum)
                tag_data = hex_data[8:-8]  # Adjust based on actual protocol
                print(f"Extracted Tag Data: {tag_data}")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()
