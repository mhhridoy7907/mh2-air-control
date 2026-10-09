# MH2 Air Control 🎮

**Gesture-Based PC Game Control Using Python, MediaPipe & Firebase**

MH2 Air Control is a real-time, camera-based gesture control system that lets users control PC games using hand movements. It combines a browser-based webcam interface, MediaPipe hand tracking, Firebase Realtime Database, and Python-based Windows keyboard simulation.

## ✨ Features

- 🖐️ Real-time hand tracking using MediaPipe
- 📷 Browser webcam integration
- 🎮 Gesture-based keyboard control
- 🔥 Firebase Realtime Database communication
- 🐍 Python-powered Windows keyboard simulation
- ↔️ Forward, backward, left, and right commands
- 🌐 Browser-based control interface
- 🔄 Automatic Firebase reconnection
- 🛑 Automatic key release when the Python controller exits

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML5 & CSS3 | Responsive control interface |
| JavaScript | Gesture detection and command handling |
| MediaPipe Hands | Hand landmark tracking |
| Firebase Realtime Database | Real-time command transmission |
| Python | Keyboard input automation |
| Windows API (`ctypes`) | Simulated keyboard events |

## 🖐️ Gesture Controls

| Hand Gesture | Command | Action |
|---|---|---|
| Both hands in fists | `UP` | Move forward |
| Both hands open | `DOWN` | Brake or move backward, depending on the game |
| Left hand lower than right | `LEFT` | Steer left |
| Right hand lower than left | `RIGHT` | Steer right |
| Neutral gesture | `NONE` | Release all keys |
| Hands not detected | `NONE` | Release all keys |

*Gesture recognition depends on camera positioning, lighting, and hand-tracking accuracy.*

## 📁 Project Structure

```text
mh2-air-control/
├── index.html       # Webcam interface and gesture detection
├── control.py      # Python keyboard controller
└── README.md       # Project documentation
```

## 🚀 Getting Started

### 1. Requirements

- Windows PC
- Python 3
- Modern web browser
- Webcam
- Internet connection
- Firebase Realtime Database

### 2. Install Python Dependency

```bash
pip install requests
```

### 3. Configure Firebase

Set the Firebase Realtime Database URL in both `index.html` and `control.py`.

The current implementation sends commands to:

```text
/control
```

Example Firebase data:

```json
{
  "key": "UP",
  "gesture": "both_fist",
  "timestamp": 1791560000000
}
```

Configure appropriate Firebase security rules. Do not leave the database publicly writable in a deployed application.

### 4. Run the Web Interface

Serve `index.html` using a local web server or deploy it to a trusted HTTPS hosting service. Allow webcam access when prompted.

Camera access generally requires HTTPS or localhost.

### 5. Start the Python Controller

Open a terminal on Windows and run:

```bash
python control.py
```

Keep the Python controller running while using the gesture interface.

### 6. Test the Controls

1. Open the web interface.
2. Click **START CAMERA**.
3. Position both hands within the camera view.
4. Perform a supported gesture.
5. Keep the game window focused so it can receive keyboard input.

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
Python Firebase Listener
   ↓
Windows SendInput API
   ↓
PC Game
```

The browser detects hand gestures and writes commands to Firebase. Python listens for database changes and translates recognized commands into keyboard events.

## ⚠️ Limitations

- Game controls must match the configured keyboard mappings.
- Some games may ignore simulated keyboard input.
- Network latency can affect responsiveness.
- The browser needs webcam permission.
- The current implementation requires internet access and a reachable Firebase database.
- Firebase security rules and authentication should be configured before public deployment.

## 🔒 Security

- Restrict Firebase read and write access.
- Avoid exposing an unrestricted database URL endpoint.
- Use authentication and suitable database rules for production.
- Only grant camera permission to trusted pages.

## 👨‍💻 Author

**MH2 HRIDOY**

- GitHub: [@mhhridoy7907](https://github.com/mhhridoy7907)
- Portfolio: [mh2-hridoy.web.app](https://mh2-hridoy.web.app)

## 📄 License

Choose a license before publishing this project for reuse. The MIT License is a common option for open-source projects.

---

**MH2 Air Control** — Turning hand gestures into real-time PC game controls. 🚀
