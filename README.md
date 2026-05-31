# 🎮 Etch A Sketch - Pygame Drawing System

A fast and interactive **Etch A Sketch-style drawing application** built with Python and Pygame.  
It supports both **manual joystick control** and an **automatic image-to-drawing mode** that converts images into drawing paths and renders them in real time.

---

## 🚀 Features

- 🎮 Manual drawing with dual joystick control (X / Y axis)
- 🤖 Automatic drawing mode from image (`resim.png`)
- 🧠 Pixel-based path generation algorithm
- ⚡ Smooth rendering at 60 FPS
- 🖼️ Image-to-sketch conversion system
- 🧹 Clear canvas and restart option

---

## 🧩 Controls

- **C** → Clear canvas  
- **Q** → Quit application  
- **A** → Start auto-draw from `resim.png`  
- **Mouse** → Joystick control  

---

## 🖼️ Auto Mode System

The auto mode works in the following steps:

1. Loads the image (`monalisa.png`)
2. Extracts dark pixels
3. Generates an optimized drawing path
4. Draws step-by-step like an Etch A Sketch machine

---

## 📦 Requirements

- Python 3.x  
- Pygame

Install dependencies:

```bash
pip install pygame
