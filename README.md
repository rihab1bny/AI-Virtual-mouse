# 🖱️ AI Virtual Mouse using Hand Tracking

Control your mouse using just your hand gestures with the power of computer vision!

This project uses **MediaPipe** and **OpenCV** to track hand landmarks in real-time, allowing you to perform common mouse actions like clicking, scrolling, zooming, and taking screenshots — all with gestures.

---

## 📁 Files

- **`HandTrackingModule.py`** → Main file to run the hand-tracking virtual mouse.
- **`motions.txt`** → Contains all the supported gestures and their corresponding actions.

---

## ✋ Supported Gestures

| Gesture                        | Action         |
|-------------------------------|----------------|
| Index + Middle Up             | Left Click     |
| Index + Middle + Ring Up      | Right Click    |
| Close & Open Thumb + Index    | Volume Control |
| Thumb + Pinky Up              | Zoom In        |
| Thumb Up                      | Zoom Out       |
| All Fingers Up                | Scroll Up      |
| Fist                          | Scroll Down    |
| Fist (All fingers curled)     | Screenshot     |

*See `motions.txt` for more details.*

---

## 🛠️ Requirements

- Python 3.x
- [MediaPipe](https://google.github.io/mediapipe/)
- OpenCV
- NumPy
- PyAutoGUI

▶️ How to Run :
python HandTrackingModule.py
