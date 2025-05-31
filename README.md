# Hand Controlled Virtual Mouse

A Python-based hand-controlled virtual mouse using MediaPipe for hand tracking and PyAutoGUI for controlling system mouse actions. This project allows you to move the cursor and perform clicks, double-clicks, click-and-drag (for text selection), right-click, middle-click, and scroll by using simple hand gestures in front of a webcam.

## Features

* **Cursor Movement**: Move the OS cursor by tracking the index finger tip.
* **Left-Click / Double-Click / Drag**: Pinch thumb + index finger to click, double-click, or click-and-drag (for text selection).
* **Right-Click**: Pinch thumb + middle finger.
* **Middle-Click**: Pinch thumb + ring finger.
* **Scroll**: Pinch index + middle finger and move hand up/down to scroll vertically.

## Requirements

* Python 3.8 or higher
* Webcam (built-in or external)
* Windows, macOS, or Linux with a supported display and webcam drivers

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/skgtheking/hand_mouse.git
   cd hand_mouse
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the main script**:

   ```bash
   python main.py
   ```

2. A window named **"Hand Mouse Complete"** will open showing the webcam feed with hand landmarks.

3. Use the following gestures to control your mouse:

   * **Cursor Movement**: Move your index finger (landmark 8) in front of the camera.
   * **Left-Click**: Pinch thumb (landmark 4) and index finger (landmark 8) briefly. Holding the pinch longer than a short interval triggers drag (mouseDown) for text selection; releasing ends the drag (mouseUp).
   * **Double-Click**: Quickly perform two thumb+index pinches within 0.3 seconds.
   * **Drag (Text Selection)**: Pinch thumb + index and hold. Once held longer than 0.1 seconds (configurable), the script calls `mouseDown()`. Move your hand while holding the pinch to select text. Release to `mouseUp()`.
   * **Right-Click**: Pinch thumb (landmark 4) and middle finger (landmark 12).
   * **Middle-Click**: Pinch thumb (landmark 4) and ring finger (landmark 16).
   * **Scroll**: Pinch index (landmark 8) and middle (landmark 12) and move your hand up or down. The midpoint of those two landmarks determines scroll amount.

4. **Exit**: Press **ESC** to close the window and terminate the program.

## Configuration

* Inside `main.py`, you can customize gesture thresholds and timing in the state dictionaries:

  ```python
  left_state = {
      'left_thresh': 40,               # Pixel distance for thumb-index pinch
      'double_click_interval': 0.3,     # Seconds for double-click window
      'drag_interval': 0.1,             # Seconds to hold pinch before dragging
      ...
  }
  right_state = {
      'right_thresh': 40,              # Pixel distance for thumb-middle pinch
      ...
  }
  middle_state = {
      'middle_thresh': 40,             # Pixel distance for thumb-ring pinch
      ...
  }
  scroll_state = {
      'scroll_thresh': 40,             # Pixel distance for index-middle pinch
      'scroll_divisor': 10,            # Divisor to scale vertical movement into scroll units
      ...
  }
  ```
* Adjust these values to suit your lighting conditions, camera resolution, and personal comfort.

## Project Structure

```
hand_mouse/
├── main.py             # Core script implementing hand tracking and mouse control
├── requirements.txt    # Python dependencies (opencv-python, mediapipe, pyautogui)
├── .gitignore          # Ignored files (venv/, __pycache__/, etc.)
└── README.md           # This README file
```

## Contributing

Feel free to submit issues or pull requests to improve gesture recognition, add new gestures (e.g., horizontal scroll, custom modifier clicks), or enhance stability. Please follow standard GitHub flow:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes and commit (`git commit -m "feat: describe your feature"`)
4. Push to your branch (`git push origin feature-name`)
5. Open a Pull Request

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
