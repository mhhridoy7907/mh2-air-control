# MH2 Air Control 🎮

**Gesture-Based PC Game Control Using Python, MediaPipe & Firebase**

MH2 Air Control is a real-time, camera-based gesture control system that lets you control PC games using hand movements. It combines a browser-based webcam interface, MediaPipe hand tracking, Firebase Realtime Database, and a Python-powered Windows keyboard controller.

The system translates recognized hand gestures into keyboard inputs, enabling hands-free control of compatible PC and browser-based games.

## ✨ Features

- 🖐️ Real-time hand tracking using MediaPipe
- 📷 Browser-based webcam interface
- 🎮 Gesture-based keyboard control
- 🔥 Firebase Realtime Database integration
- 🐍 Python-powered Windows keyboard simulation
- ⌨️ Windows `SendInput` API integration
- ⚡ Scan-code keyboard input support
- ↔️ Forward, backward, left, and right controls
- 🎚️ Analog-style steering using configurable sensitivity
- 🛑 Automatic key release when control data becomes stale
- 🔄 Automatic Firebase reconnection
- 🧵 Separate Firebase streaming and controller loops
- 🔒 Thread-safe keyboard state management
- ␣ Optional SPACE key control
- 🧹 Keyboard cleanup on shutdown
- 🌐 Browser-based control interface

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML5 & CSS3 | Responsive control interface |
| JavaScript | Gesture recognition and command handling |
| MediaPipe Hands | Hand landmark tracking |
| Firebase Realtime Database | Real-time control data transmission |
| Python 3 | Control processing and keyboard automation |
| Requests | Firebase HTTP streaming |
| `ctypes` | Windows API integration |
| Windows `SendInput` | Simulated keyboard events |
| `threading` | Background Firebase listener and controller synchronization |

## 🖐️ Gesture Controls

| Hand Gesture | Command | Action |
|---|---|---|
| Both hands in fists | `UP` | Accelerate / move forward |
| Both hands open | `DOWN` | Brake or move backward, depending on the game |
| Left hand lower than right | `LEFT` | Steer left |
| Right hand lower than left | `RIGHT` | Steer right |
| Mixed hand gestures | `SPACE` | Activate the configured SPACE action |
| Neutral gesture | `NONE` | Release control keys |
| Hands not detected | `NONE` | Release control keys |

*Actual gesture mappings depend on the JavaScript implementation in `index.html`.*

## 🎚️ Steering System

MH2 Air Control supports analog-style steering through a normalized steering value.

| Parameter | Default | Purpose |
|---|---:|---|
| `STEERING_DEADZONE` | `0.06` | Ignores small steering movements |
| `STEERING_FULL` | `0.90` | Threshold for full steering |
| `STEERING_PWM_PERIOD` | `0.12` seconds | Steering pulse cycle |
| `STEERING_MIN_DUTY` | `0.20` | Minimum steering pulse duty |

Steering values range from `-1.0` to `+1.0`:

- `+1.0` — Full left steering
- `-1.0` — Full right steering
- `0.0` — No steering

Intermediate values control how frequently the corresponding directional key is pressed. This is keyboard-based steering simulation, not true analog gamepad input.

## 🛡️ Safety & Reliability

### Automatic key release

The controller monitors the age of the most recent control packet. If updates stop for longer than the configured stale timeout, the controller releases the active keys.

### Firebase reconnection

The Firebase listener runs in a background thread and attempts to reconnect after connection errors or stream termination.

### Thread-safe input handling

A shared lock protects keyboard state updates, while a separate controller loop synchronizes the desired keyboard state with the actual simulated key state.

### Shutdown cleanup

The controller attempts to release held keys when interrupted or stopped, helping prevent unwanted continuous keyboard input.

> **Important:** The browser should send regular control updates or heartbeats. With the default `STALE_TIMEOUT = 0.8`, a lack of new control packets can release keys even when the Firebase connection itself remains open.

## 📁 Project Structure

```text
mh2-air-control/
├── index.html       # Webcam interface and gesture recognition
├── control.py       # Python keyboard controller
└── README.md        # Project documentation
```

## 🚀 Getting Started

### 1. Requirements

- Windows PC
- Python 3.10 or compatible version
- Modern web browser
- Webcam
- Internet connection
- Firebase Realtime Database
- Compatible PC or browser-based game

### 2. Install Dependencies

Install the Python dependency:

```bash
python -m pip install requests
```

The Windows API modules used by the controller, including `ctypes` and `threading`, are included with Python.

### 3. Configure Firebase

Set your Firebase Realtime Database URL in `index.html` and `control.py`.

The Python controller listens to:

```text
/control
```

Example control data:

```json
{
  "key": "UP",
  "steering": 0.0,
  "space": false
}
```

Supported fields:

| Field | Type | Description |
|---|---|---|
| `key` | String | `UP`, `DOWN`, `LEFT`, `RIGHT`, or `NONE` |
| `steering` | Number | Steering intensity from `-1.0` to `+1.0` |
| `space` | Boolean | Whether SPACE should be held |

The controller supports Firebase root-level updates and individual updates to `key`, `steering`, and `space`.

**Security:** Configure Firebase Authentication and restrictive Realtime Database rules. Do not expose an unrestricted database endpoint to the public.

### 4. Run the Web Interface

Serve `index.html` through a local development server or deploy it to a trusted HTTPS hosting service.

1. Open the webpage in a supported browser.
2. Allow webcam access.
3. Click **START CAMERA**.
4. Position your hands within the camera view.

Camera access generally requires HTTPS or localhost.

### 5. Start the Python Controller

Open a Windows terminal in the project directory:

```bash
python control.py
```

Keep the terminal running while using the gesture interface.

The controller will connect to Firebase, process control updates, and simulate the configured keyboard inputs.

### 6. Test the Controls

1. Open a compatible game.
2. Keep the game window focused.
3. Start the webcam interface.
4. Perform each supported gesture.
5. Test acceleration, braking, steering, and SPACE independently.
6. Verify that keys are released when control updates stop.
7. Press `Ctrl+C` to stop the controller.

Start testing at low speed in a safe environment.

## ⚙️ How It Works

```text
Webcam
   ↓
MediaPipe Hand Tracking
   ↓
JavaScript Gesture Recognition
   ↓
Firebase Realtime Database
   ↓
Python Firebase Stream Worker
   ↓
Shared Control State
   ↓
Controller Loop
   ↓
Windows SendInput API
   ↓
PC Game
```

The browser detects hand landmarks and translates recognized gestures into control data. Firebase transmits that data to the Python application.

The Python stream worker processes incoming database events, while the controller loop periodically calculates the desired keyboard state. Windows keyboard events are then generated through the `SendInput` API.

The controller also monitors stale control data and attempts to release active keys when updates stop.

## ⚙️ Configuration

The main Python controller settings are defined near the beginning of `control.py`.

| Setting | Default | Description |
|---|---:|---|
| `RECONNECT_DELAY` | `2` seconds | Delay before reconnecting |
| `STREAM_READ_TIMEOUT` | `40` seconds | HTTP stream read timeout |
| `STALE_TIMEOUT` | `0.8` seconds | Maximum age of the last control packet |
| `TICK_INTERVAL` | `0.004` seconds | Controller loop wait interval |
| `USE_SCANCODE` | `True` | Enables scan-code keyboard input |

Adjust these values carefully and test their effects with your specific browser and game.

## ⚠️ Limitations

- The controller is designed for Windows.
- Games must support the configured keyboard controls.
- Some games may ignore simulated keyboard events.
- Scan-code support does not guarantee compatibility with every game.
- Network latency can affect responsiveness.
- Steering is simulated through keyboard presses rather than analog gamepad input.
- The browser requires webcam permission.
- Internet access and a reachable Firebase database are required.
- The browser's gesture mappings must match the Python controller's expected fields.
- Stale-data protection depends on correctly configured control updates and heartbeat behavior.
- Forced key release is best-effort and cannot guarantee recovery from every operating-system or application failure.

## 🔒 Security

- Use Firebase Authentication and restrictive database rules.
- Never publish Firebase administrative credentials or private keys.
- Avoid unrestricted public database read/write access.
- Serve the webcam interface through HTTPS or localhost.
- Grant camera access only to trusted pages.
- Review the permissions and security configuration before public deployment.

## 🧑‍💻 Author

**MH2 HRIDOY**
- WhatsApp: +880 1962-388570
- Portfolio: [mh2-hridoy.web.app](https://mh2-hridoy.web.app)
- Gmail: mhhridoy7907@gmail.com

## 📄 License

Choose and add a license file before publishing this project for reuse. The MIT License is a common choice for open-source software.

---

**MH2 Air Control** — Turning hand gestures into real-time PC game controls. 🚀
