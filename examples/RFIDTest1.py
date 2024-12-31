import serial

ser = serial.Serial('/dev/tty.usbserial-AR0JT4RL', 115200, timeout=1)


def parse_tag_data(raw_data):
    """
    Parse the raw RFID data to extract the stable tag ID.
    """
    hex_data = raw_data.hex()
    if hex_data.startswith("a55a"):
        # Extract the stable part of the tag ID (first 24 bytes or 48 hex characters)
        return hex_data[:48]
    return None


try:
    print("Listening for tag data...")
    while True:
        raw_data = ser.readline()
        if raw_data:
            hex_data = raw_data.hex()
            if hex_data.startswith("a55a"):
                # Extract the stable part of the tag ID (first 24 bytes or 48 hex characters)
                tag_id = hex_data[:40]
                print(f"Tag ID: {tag_id}")
            # print(f"Raw Hex Data: {hex_data}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()
