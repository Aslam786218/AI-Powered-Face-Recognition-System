import serial
import json
import time

# Update this to your ESP32 serial port
PORT = "/dev/cu.usbserial-0001"   # check with ls /dev/tty.* on Mac
BAUD = 115200

# Threshold for liveness (tweak after testing)
VARIATION_THRESHOLD = 100   # mm difference across depth map

def check_liveness(timeout=3):
    """
    Reads JSON packets from ESP32 VL53L5CX and checks if face is live.
    Returns True (live) or False (spoof).
    """
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        start_time = time.time()

        while time.time() - start_time < timeout:
            line = ser.readline().decode(errors="ignore").strip()
            if not line.startswith("{") or not line.endswith("}"):
                continue

            try:
                data = json.loads(line)
                variation = data.get("variation", 0)
                print(f"DEBUG: variation={variation} mm")

                if variation >= VARIATION_THRESHOLD:
                    ser.close()
                    return True   # real 3D object
                else:
                    ser.close()
                    return False  # flat spoof
            except json.JSONDecodeError:
                continue

        ser.close()
        return False  # timeout = treat as spoof
    except Exception as e:
        print("Serial error:", e)
        return False
