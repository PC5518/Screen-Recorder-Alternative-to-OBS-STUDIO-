import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import mss
import time
import threading

# --- Global variables for state management ---
is_recording = False
recording_thread = None
bounding_box = {}

# --- Part 1: Area Selection (MODIFIED with on-screen instructions) ---

def select_screen_area():
    """
    Displays a screenshot with on-screen instructions and allows the user to select an area.
    Returns the bounding box dictionary for mss.
    """
    cropping = False
    selection_complete = False
    x_start, y_start, x_end, y_end = 0, 0, 0, 0

    def mouse_crop(event, x, y, flags, param):
        nonlocal x_start, y_start, x_end, y_end, cropping, selection_complete
        if event == cv2.EVENT_LBUTTONDOWN:
            x_start, y_start, x_end, y_end = x, y, x, y
            cropping = True
            selection_complete = False
        elif event == cv2.EVENT_MOUSEMOVE and cropping:
            x_end, y_end = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            x_end, y_end = x, y
            cropping = False
            selection_complete = True

    with mss.mss() as sct:
        sct.shot(output="fullscreen_selection.png")

    img = cv2.imread("fullscreen_selection.png")
    
    # Create a semi-transparent overlay
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (img.shape[1], img.shape[0]), (0, 0, 0), -1)
    img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0) # Add transparency

    window_name = "Screen Selection"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, mouse_crop)

    # Instructions text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255) # White
    line_type = 2
    text = "Drag to select area. Press 'c' to confirm or 'q' to cancel."
    text_size, _ = cv2.getTextSize(text, font, font_scale, line_type)
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = 50 # Position text near the top

    while True:
        display_img = img.copy()
        
        # Draw the instructional text on every frame
        cv2.putText(display_img, text, (text_x, text_y), font, font_scale, font_color, line_type)

        if cropping or selection_complete:
            # Draw the selection rectangle on top of the original (non-darkened) image
            # to make the selection area clear.
            temp_img = cv2.imread("fullscreen_selection.png")
            start_point = (min(x_start, x_end), min(y_start, y_end))
            end_point = (max(x_start, x_end), max(y_start, y_end))
            
            # Extract the selected region from the original bright image
            selected_region = temp_img[start_point[1]:end_point[1], start_point[0]:end_point[0]]
            
            # Place the bright selected region onto our darkened display image
            if selected_region.size > 0:
                display_img[start_point[1]:end_point[1], start_point[0]:end_point[0]] = selected_region
            
            # Draw the green rectangle
            cv2.rectangle(display_img, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)


        cv2.imshow(window_name, display_img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and selection_complete:
            break
        if key == ord('q'):
            cv2.destroyAllWindows()
            return None, "Selection cancelled."

    cv2.destroyAllWindows()
    
    left = min(x_start, x_end)
    top = min(y_start, y_end)
    right = max(x_start, x_end)
    bottom = max(y_start, y_end)

    bbox = {'top': top, 'left': left, 'width': right - left, 'height': bottom - top}
    if bbox['width'] == 0 or bbox['height'] == 0:
        return None, "Invalid area selected."
    
    return bbox, f"Area Selected: {bbox['width']}x{bbox['height']} at ({bbox['left']},{bbox['top']})"

# --- Part 2: Recording Logic (Unchanged) ---

def record_screen(fps, filename, bbox, stop_event, status_callback):
    """The core recording function that runs in a thread."""
    global is_recording
    
    screen_size = (bbox['width'], bbox['height'])
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(filename, fourcc, fps, screen_size)

    with mss.mss() as sct:
        last_time = time.time()
        while not stop_event.is_set():
            sct_img = sct.grab(bbox)
            frame = np.array(sct_img)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            video_writer.write(frame_bgr)

            # Frame rate control
            current_time = time.time()
            sleep_time = (1/fps) - (current_time - last_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_time = time.time()
    
    video_writer.release()
    is_recording = False
    print(f"Recording stopped. Video saved as '{filename}'")
    status_callback(f"Saved! Ready for next recording.")


# --- Part 3: The GUI Application (Slightly modified to handle thread callbacks) ---

class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("350x220")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10))
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5)

        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.frame, text="FPS:").grid(row=0, column=0, sticky=tk.W)
        self.fps_var = tk.StringVar(value="60")
        self.fps_entry = ttk.Entry(self.frame, textvariable=self.fps_var, width=10)
        self.fps_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(self.frame, text="Filename:").grid(row=1, column=0, sticky=tk.W)
        self.filename_var = tk.StringVar(value="recording.mp4")
        self.filename_entry = ttk.Entry(self.frame, textvariable=self.filename_var, width=25)
        self.filename_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        self.select_area_btn = ttk.Button(self.frame, text="Select Area", command=self.select_area)
        self.select_area_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        self.start_btn = ttk.Button(self.frame, text="Start Recording", command=self.start_recording, state=tk.DISABLED)
        self.start_btn.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.stop_btn = ttk.Button(self.frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.grid(row=3, column=2, sticky=tk.E)
        
        self.status_var = tk.StringVar(value="Ready. Please select an area.")
        self.status_bar = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=4, column=0, columnspan=3, pady=(15,0), sticky=(tk.W, tk.E))

    def select_area(self):
        global bounding_box
        self.update_status("Area selection active...")
        self.root.withdraw()
        time.sleep(0.5)
        
        bbox, message = select_screen_area()
        
        self.root.deiconify()
        self.update_status(message)
        
        if bbox:
            bounding_box = bbox
            self.start_btn.config(state=tk.NORMAL)
        else:
            bounding_box = {}
            self.start_btn.config(state=tk.DISABLED)

    def start_recording(self):
        global is_recording, recording_thread, bounding_box

        if is_recording:
            messagebox.showwarning("Warning", "Already recording.")
            return

        try:
            fps = int(self.fps_var.get())
            if fps <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "FPS must be a positive integer.")
            return

        filename = self.filename_var.get()
        if not filename:
            messagebox.showerror("Error", "Filename cannot be empty.")
            return
        if not filename.endswith('.mp4'):
            filename += '.mp4'

        is_recording = True
        self.stop_event = threading.Event()
        
        recording_thread = threading.Thread(
            target=record_screen, 
            args=(fps, filename, bounding_box, self.stop_event, self.update_status),
            daemon=True
        )
        recording_thread.start()
        
        self.update_ui_for_recording(True, filename)

    def stop_recording(self):
        global is_recording
        if not is_recording:
            return
            
        self.stop_event.set()
        is_recording = False
        self.update_ui_for_recording(False, self.filename_var.get())

    def update_ui_for_recording(self, recording_active, filename):
        if recording_active:
            self.start_btn.config(state=tk.DISABLED)
            self.select_area_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_status(f"Recording to {filename}...")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.select_area_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            # The status will be updated by the thread when it finishes.
            self.update_status("Stopping...")
    
    def update_status(self, message):
        """Thread-safe way to update the status bar."""
        self.status_var.set(message)


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.mainloop()