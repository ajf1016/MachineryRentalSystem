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


# Cutter 11 : a55a0019833000e200001b260c02562050e0f800c001840d0a
# Cutter 02 : a55a0019833000e200001b66040172172092e200cf01cb0d0a
# Cutter 03 : a55a0019833000e200001b660401601720816400ca01490d0a
# Cutter 13 : a55a0019833000e200001b6604016317208f1100d901220d0a
# grinder 05 : a55a0019833000e200001b6604009417203cbf00c001d00d0a
