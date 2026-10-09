
import requests
import json
import time
import ctypes
from ctypes import wintypes


FIREBASE_URL = (
    "https://test-input-cd686-default-rtdb."
    "asia-southeast1.firebasedatabase.app"
)

CONTROL_URL = FIREBASE_URL + "/control.json"

user32 = ctypes.WinDLL("user32", use_last_error=True)

VK_UP = 0x26
VK_DOWN = 0x28
VK_LEFT = 0x25
VK_RIGHT = 0x27

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

RECONNECT_DELAY = 2
REQUEST_TIMEOUT = 30

KEY_MAP = {
    "UP": VK_UP,
    "DOWN": VK_DOWN,
    "LEFT": VK_LEFT,
    "RIGHT": VK_RIGHT,
}

held_keys = set()
current_command = "NONE"



class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


user32.SendInput.argtypes = (
    wintypes.UINT,
    ctypes.POINTER(INPUT),
    ctypes.c_int,
)
user32.SendInput.restype = wintypes.UINT


def send_key_event(vk, key_up=False):
    flags = KEYEVENTF_EXTENDEDKEY

    if key_up:
        flags |= KEYEVENTF_KEYUP

    event = INPUT()
    event.type = INPUT_KEYBOARD
    event.union.ki = KEYBDINPUT(
        wVk=vk,
        wScan=0,
        dwFlags=flags,
        time=0,
        dwExtraInfo=0,
    )

    ctypes.set_last_error(0)

    sent = user32.SendInput(
        1,
        ctypes.byref(event),
        ctypes.sizeof(INPUT),
    )

    if sent != 1:
        print(
            f"[INPUT ERROR] Windows error: "
            f"{ctypes.get_last_error()}"
        )
        return False

    return True


def key_down(vk):
    return send_key_event(vk, False)


def key_up(vk):
    return send_key_event(vk, True)



def release_all_keys():
    global held_keys, current_command

    for vk in list(held_keys):
        key_up(vk)

    held_keys.clear()
    current_command = "NONE"
    print("[RELEASE] All keys")



def set_key(command):
    global held_keys, current_command

    command = str(command).strip().upper()

    desired_commands = {
        "UP": {"UP"},
        "DOWN": {"DOWN"},
        "LEFT": {"UP", "LEFT"},
        "RIGHT": {"UP", "RIGHT"},
        "NONE": set(),
    }

    if command not in desired_commands:
        print(f"[INVALID COMMAND] {command}")
        return

    wanted = {
        KEY_MAP[name]
        for name in desired_commands[command]
    }

    for vk in held_keys - wanted:
        if key_up(vk):
            print(f"[KEY UP] {vk}")

    for vk in wanted - held_keys:
        if key_down(vk):
            print(f"[KEY DOWN] {vk}")

    held_keys = wanted
    current_command = command

    names = [
        name for name, vk in KEY_MAP.items()
        if vk in held_keys
    ]

    print(f"[COMMAND] {command} | HOLD: {names}")



def handle_firebase_event(event_type, payload):
    if event_type not in ("put", "patch"):
        return

    if not isinstance(payload, dict):
        return

    path = payload.get("path", "/")
    value = payload.get("data")

    if path == "/":
        if isinstance(value, dict):
            set_key(value.get("key", "NONE"))

    elif path == "/key":
        set_key(value)

    elif isinstance(value, dict) and "key" in value:
        set_key(value["key"])


def firebase_stream():
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }

    print("=" * 50)
    print("          MH2 AIR CONTROL")
    print("=" * 50)
    print("UP    = Forward")
    print("DOWN  = Backward")
    print("LEFT  = Forward + Left")
    print("RIGHT = Forward + Right")
    print("NONE  = Release all keys")
    print(f"INPUT size: {ctypes.sizeof(INPUT)}")
    print("Press Ctrl+C to stop.")
    print()

    while True:
        try:
            with requests.get(
                CONTROL_URL,
                headers=headers,
                stream=True,
                timeout=(10, REQUEST_TIMEOUT),
            ) as response:

                response.raise_for_status()
                print("[Firebase] Connected")

                event_type = None

                for raw_line in response.iter_lines(
                    decode_unicode=True
                ):
                    if raw_line is None:
                        continue

                    line = raw_line.strip()

                    if not line:
                        continue

                    if line.startswith("event:"):
                        event_type = line[6:].strip()

                    elif line.startswith("data:"):
                        try:
                            payload = json.loads(
                                line[5:].strip()
                            )
                        except json.JSONDecodeError:
                            continue

                        handle_firebase_event(
                            event_type,
                            payload,
                        )

        except KeyboardInterrupt:
            print("\n[STOP] Keyboard interrupt")
            break

        except requests.exceptions.RequestException as error:
            print(f"[Firebase ERROR] {error}")
            release_all_keys()
            time.sleep(RECONNECT_DELAY)

        except Exception as error:
            print(f"[ERROR] {error}")
            release_all_keys()
            time.sleep(RECONNECT_DELAY)



if __name__ == "__main__":
    try:
        firebase_stream()

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        release_all_keys()
        print("[EXIT] All keys released.")
