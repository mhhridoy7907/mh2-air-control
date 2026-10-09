
import ctypes
import json
import math
import threading
import time
from ctypes import wintypes

import requests

FIREBASE_URL = (
    "http**************************b."
    "asi************irebasedatabase.app"
)
CONTROL_URL = FIREBASE_URL + "/control.json"

RECONNECT_DELAY = 2.0
STREAM_READ_TIMEOUT = 40
STALE_TIMEOUT = 0.8
TICK_INTERVAL = 0.004

STEERING_DEADZONE = 0.06
STEERING_FULL = 0.90
STEERING_PWM_PERIOD = 0.12
STEERING_MIN_DUTY = 0.20

USE_SCANCODE = True

VK_UP = 0x26
VK_DOWN = 0x28
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_SPACE = 0x20

ALL_KEYS = (VK_UP, VK_DOWN, VK_LEFT, VK_RIGHT, VK_SPACE)

KEY_NAMES = {
    VK_UP: "UP",
    VK_DOWN: "DOWN",
    VK_LEFT: "LEFT",
    VK_RIGHT: "RIGHT",
    VK_SPACE: "SPACE",
}

EXTENDED_KEYS = {VK_UP, VK_DOWN, VK_LEFT, VK_RIGHT}

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MAPVK_VK_TO_VSC = 0

VALID_COMMANDS = ("UP", "DOWN", "LEFT", "RIGHT", "NONE")

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
winmm = ctypes.WinDLL("winmm")


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

user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)
user32.MapVirtualKeyW.restype = wintypes.UINT

lock = threading.RLock()
stop_event = threading.Event()

state = {"key": "NONE", "steering": 0.0, "space": False}
last_packet_at = 0.0
held = set()
scan_cache = {}
last_log = None

HANDLER_TYPE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)
console_handler_ref = None


def scan_code(vk):
    if vk not in scan_cache:
        scan_cache[vk] = user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    return scan_cache[vk]


def send_key(vk, release=False):
    flags = 0

    if USE_SCANCODE:
        flags |= KEYEVENTF_SCANCODE

    if vk in EXTENDED_KEYS:
        flags |= KEYEVENTF_EXTENDEDKEY

    if release:
        flags |= KEYEVENTF_KEYUP

    event = INPUT()
    event.type = INPUT_KEYBOARD
    event.union.ki = KEYBDINPUT(
        wVk=vk,
        wScan=scan_code(vk),
        dwFlags=flags,
        time=0,
        dwExtraInfo=0,
    )

    result = user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))

    if result != 1:
        print(
            f"[INPUT ERROR] {KEY_NAMES[vk]} "
            f"Windows error={ctypes.get_last_error()}"
        )
        return False

    return True


def sync_keys(desired):
    with lock:
        for vk in list(held - desired):
            if send_key(vk, release=True):
                held.discard(vk)

        for vk in desired - held:
            if send_key(vk):
                held.add(vk)


def release_all(force=False):
    with lock:
        targets = set(ALL_KEYS) if force else set(held)

        for vk in targets:
            if send_key(vk, release=True):
                held.discard(vk)

        if force:
            held.clear()


def neutral_state():
    global last_packet_at

    with lock:
        state["key"] = "NONE"
        state["steering"] = 0.0
        state["space"] = False
        last_packet_at = 0.0


def parse_key(value):
    key = str(value or "NONE").upper().strip()
    return key if key in VALID_COMMANDS else "NONE"


def parse_steering(value):
    try:
        number = float(value or 0)
    except (ValueError, TypeError, OverflowError):
        return 0.0

    if not math.isfinite(number):
        return 0.0

    return max(-1.0, min(1.0, number))


def parse_space(value):
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")

    return bool(value)


def merge_state(data):
    global last_packet_at

    with lock:
        if "key" in data:
            state["key"] = parse_key(data["key"])

        if "steering" in data:
            state["steering"] = parse_steering(data["steering"])

        if "space" in data:
            state["space"] = parse_space(data["space"])

        last_packet_at = time.monotonic()


def replace_state(data):
    with lock:
        state["key"] = "NONE"
        state["steering"] = 0.0
        state["space"] = False

    merge_state(data)


def handle_payload(event_type, payload):
    path = payload.get("path", "/")
    data = payload.get("data")

    if path == "/":
        if isinstance(data, dict):
            if event_type == "put":
                replace_state(data)
            else:
                merge_state(data)
        elif event_type == "put":
            neutral_state()
    elif path in ("/key", "/steering", "/space"):
        merge_state({path[1:]: data})


def stream_once():
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }

    with requests.get(
        CONTROL_URL,
        headers=headers,
        stream=True,
        timeout=(10, STREAM_READ_TIMEOUT),
    ) as response:
        response.raise_for_status()
        print("[Firebase] Connected")

        event_type = None
        snapshot_pending = True

        for raw_line in response.iter_lines(chunk_size=1):
            if stop_event.is_set():
                return

            if not raw_line:
                continue

            line = raw_line.decode("utf-8", "replace").strip()

            if line.startswith("event:"):
                event_type = line[6:].strip()
                continue

            if not line.startswith("data:"):
                continue

            current_event = event_type
            event_type = None

            if current_event in ("cancel", "auth_revoked"):
                raise RuntimeError(f"Stream closed by server: {current_event}")

            if current_event not in ("put", "patch"):
                continue

            try:
                payload = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue

            if not isinstance(payload, dict):
                continue

            if snapshot_pending and current_event == "put":
                snapshot_pending = False
                neutral_state()
                continue

            handle_payload(current_event, payload)


def stream_worker():
    while not stop_event.is_set():
        try:
            neutral_state()
            release_all()
            stream_once()

            if not stop_event.is_set():
                print("[Firebase] Stream ended")
        except requests.exceptions.RequestException as error:
            print(f"[Firebase ERROR] {error}")
        except Exception as error:
            print(f"[ERROR] {error}")

        neutral_state()
        release_all()
        stop_event.wait(RECONNECT_DELAY)


def steering_pressed(magnitude, now):
    if magnitude < STEERING_DEADZONE:
        return False

    if magnitude >= STEERING_FULL:
        return True

    duty = (magnitude - STEERING_DEADZONE) / (
        STEERING_FULL - STEERING_DEADZONE
    )
    duty = max(STEERING_MIN_DUTY, min(1.0, duty))

    return (now % STEERING_PWM_PERIOD) < duty * STEERING_PWM_PERIOD


def compute_desired(now):
    with lock:
        command = state["key"]
        steering = state["steering"]
        space = state["space"]
        age = now - last_packet_at

    desired = set()

    if last_packet_at == 0.0 or age > STALE_TIMEOUT:
        return desired, "NONE", 0.0, False

    if command == "UP":
        desired.add(VK_UP)
    elif command == "DOWN":
        desired.add(VK_DOWN)

    if command == "LEFT":
        steering = 1.0
    elif command == "RIGHT":
        steering = -1.0

    if steering_pressed(abs(steering), now):
        desired.add(VK_LEFT if steering > 0 else VK_RIGHT)

    if space:
        desired.add(VK_SPACE)

    return desired, command, steering, space


def log_change(command, steering, space):
    global last_log

    with lock:
        names = tuple(
            KEY_NAMES[vk] for vk in ALL_KEYS if vk in held
        )

    summary = (command, round(steering, 2), space)

    if summary != last_log:
        last_log = summary
        print(
            f"[CONTROL] {command} | STEER={steering:+.2f} | "
            f"SPACE={space} | HOLD={list(names)}"
        )


def controller_loop():
    while not stop_event.is_set():
        now = time.monotonic()
        desired, command, steering, space = compute_desired(now)

        sync_keys(desired)
        log_change(command, steering, space)

        stop_event.wait(TICK_INTERVAL)


def console_handler(event):
    stop_event.set()
    release_all(force=True)
    return False


def install_console_handler():
    global console_handler_ref

    console_handler_ref = HANDLER_TYPE(console_handler)
    kernel32.SetConsoleCtrlHandler(console_handler_ref, True)


def main():
    print("=" * 48)
    print("          MH2 AIR CONTROL")
    print("=" * 48)
    print("Both fists      = UP (accelerate)")
    print("Both open hands = DOWN (brake)")
    print("Tilt hands      = LEFT / RIGHT")
    print("Mixed hands     = SPACE")
    print("Ctrl+C          = Stop")
    print()

    install_console_handler()
    winmm.timeBeginPeriod(1)

    worker = threading.Thread(target=stream_worker, daemon=True)
    worker.start()

    try:
        controller_loop()
    except KeyboardInterrupt:
        print("\n[STOP] Keyboard interrupt")
    finally:
        stop_event.set()
        release_all(force=True)
        winmm.timeEndPeriod(1)
        print("[EXIT] All keys released.")


if __name__ == "__main__":
    main()