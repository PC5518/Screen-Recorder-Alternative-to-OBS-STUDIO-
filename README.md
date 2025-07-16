# ⚡ SimpleScreenCapture - Minimal Screen Recorder with Area Selection

Lightweight. Clean. No bloat.  
A fully Python-based screen recording tool with area selection — built from scratch as an ultra-light alternative to OBS Studio.  
No GPU overload. No overheating. Just what you need: pick an area and start recording.
DEMO VIDEO THAT HOW IT WORKS : "https://youtu.be/uU-oeBjNfHg"
---

## 💡 Why I Built This

I was frustrated with the complexity and performance issues of heavy tools like OBS Studio.  
Even for simple recordings, OBS would **eat RAM**, **stress my CPU**, and **heat up the laptop** like a furnace.  
So I asked myself:

> “Can I build a minimal recorder with just Python — fast, simple, and focused?”

This tool was born from that curiosity. I wanted to understand **how recording actually works**,  
**how area selection can be done visually**, and **how to build a full GUI using Tkinter** — and most importantly,  
do it all in a way that's **resource-friendly and intuitive** for users.

---

## 🚀 Features

- 🎯 **Drag-and-Select Screen Area**  
  Beautiful on-screen interface to select any part of the screen before recording.

- 🖥️ **Real-Time Recording**  
  Capture your screen directly with smooth FPS settings (default 60 FPS).

- 💾 **Save as MP4**  
  Automatically encodes and saves your video using `cv2.VideoWriter` with `.mp4` output.

- 🔧 **Simple GUI**  
  Built with `Tkinter`, the GUI allows you to select FPS, filename, and monitor the recording status.

- 🧠 **Multithreading**  
  Recording happens on a separate thread to keep the GUI responsive and clean.

- 🛑 **Start / Stop Anytime**  
  Instantly begin or end recordings. No long setups.

- 📦 **No External Recorder Dependency**  
  No OBS. No FFMPEG install required. Just Python, OpenCV, NumPy, and MSS.

---

## 🔍 Tech Stack

| Tool      | Role                                  |
|-----------|----------------------------------------|
| `Tkinter` | GUI for user input and controls        |
| `OpenCV`  | Handles area selection + video writing |
| `MSS`     | Grabs screen frames efficiently        |
| `NumPy`   | Frame processing                       |
| `Threading` | Keeps GUI responsive during recording |

---

## 🎬 How It Works

1. Launch the GUI
2. Click **"Select Area"** → Drag and select any region of your screen.
3. Set your **FPS** and **Filename**
4. Click **"Start Recording"** and your screen is being recorded!
5. Click **"Stop Recording"** anytime to save the video.

---

## 🧠 Who Should Use This?

- Students who want to quickly record a demo or project screen
- Developers tired of heavy recorders like OBS
- Anyone who just needs **simple screen recording** without GPU/RAM pressure

---

## 🧪 My Curiosity

Honestly, this was less about recording and more about learning:
- How does `cv2.VideoWriter` really work?
- How can you grab live screen frames?
- How to manage threads in GUI apps?
- How to make the user feel like it's *really interactive*?

This project helped me explore all of that.

---

## 🖼️ Preview (Optional)

> You can upload a screenshot or screen-recording gif like this:


---

## ⚙️ Requirements

- Python 3.7+
- `opencv-python`
- `numpy`
- `mss`

Install with:

```bash
pip install opencv-python numpy mss

