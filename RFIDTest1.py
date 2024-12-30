import serial

ser = serial.Serial('/dev/tty.usbserial-AR0JT4RL', 115200, timeout=1)

try:
    print("Listening for tag data...")
    while True:
        raw_data = ser.readline()
        if raw_data:
            hex_data = raw_data.hex()
            print(f"Raw Hex Data: {hex_data}")

            # Example parsing: Extract tag ID if data starts with '02' and ends with '03'
            if hex_data.startswith('02') and hex_data.endswith('03'):
                # Remove start ('02') and stop ('03') markers
                tag_id = hex_data[2:-2]
                print(f"Tag ID: {tag_id}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()


# Cutter 11 : a55a0019833000e200001b260c02562050e0f800c001840d0a
# Cutter 02 : a55a0019833000e200001b66040172172092e200cf01cb0d0a
# Cutter 03 : a55a0019833000e200001b660401601720816400ca01490d0a
# Cutter 13 : a55a0019833000e200001b6604016317208f1100d901220d0a
# grinder 05 : a55a0019833000e200001b6604009417203cbf00c001d00d0a
