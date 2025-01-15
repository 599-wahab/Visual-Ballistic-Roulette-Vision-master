import cv2
import cvzone
import tkinter as tk
from datetime import datetime
from ultralytics import YOLO

# Define the speed calculation constants
DISTANCE_THRESHOLD = 10  # Distance threshold for calculating speed (in pixels)
FPS = 23  # Frames per second of the video
model = YOLO("YoloV8_model_5.pt")

class RouletteTracker:
    def __init__(self, speed_label, laps_label):
        self.lap_count = 0
        self.start_time = None
        self.last_pass_time = None
        self.passed_12_oclock = False
        self.prev_center = None
        self.speed_label = speed_label
        self.laps_label = laps_label

    def reset(self):
        self.lap_count = 0
        self.start_time = None
        self.last_pass_time = None
        self.passed_12_oclock = False
        self.prev_center = None
        self.speed_label.config(text="Speed: 0 m/s")
        self.laps_label.config(text="Laps: 0")

    def process_frame(self, frame):
        results = model(frame, stream=True)
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) in [0, 1]:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    cvzone.cornerRect(frame, (x1, y1, w, h))

                    # Check if the y-coordinate of the box is below the threshold
                    if y1 < 120:  # Assuming the 12 o'clock position is at y-coordinate 120
                        self.passed_12_oclock = True

                    # Calculate the distance moved by the ball
                    if self.prev_center is not None:
                        center = ((x1 + x2) // 2, (y1 + y2) // 2)
                        distance = ((center[0] - self.prev_center[0])**2 + (center[1] - self.prev_center[1])**2)**0.5
                        if distance > DISTANCE_THRESHOLD and self.passed_12_oclock:
                            time_taken = (datetime.now() - self.last_pass_time).total_seconds()
                            speed_mps = DISTANCE_THRESHOLD / time_taken
                            self.speed_label.config(text=f"Speed: {speed_mps:.2f} m/s")
                            cv2.putText(frame, f"Speed: {speed_mps:.2f} m/s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                    self.prev_center = ((x1 + x2) // 2, (y1 + y2) // 2)

        if self.passed_12_oclock and not self.last_pass_time:
            self.last_pass_time = datetime.now()

        if self.passed_12_oclock and not self.start_time:
            self.start_time = datetime.now()

        if self.passed_12_oclock and self.last_pass_time:
            lap_time = (datetime.now() - self.last_pass_time).total_seconds()
            print(f"Lap {self.lap_count + 1}: {lap_time:.2f} seconds")
            self.last_pass_time = datetime.now()
            self.lap_count += 1
            self.laps_label.config(text=f"Laps: {self.lap_count}")
            cv2.putText(frame, f"Laps: {self.lap_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if self.lap_count >= 10:
            self.reset()


def process_video(video_path, speed_label, laps_label):
    cap = cv2.VideoCapture(video_path)
    tracker = RouletteTracker(speed_label, laps_label)

    while True:
        success, frame = cap.read()
        if not success:
            break

        tracker.process_frame(frame)

        cv2.imshow('Video Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def upload_video(speed_label, laps_label):
    video_path = tk.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if video_path:
        process_video(video_path, speed_label, laps_label)


def connect_to_camera(rtsp_entry, speed_label, laps_label):
    rtsp_url = rtsp_entry.get()
    if rtsp_url:
        process_video(rtsp_url, speed_label, laps_label)

def main():
    root = tk.Tk()
    root.title("Ball and zero Detected App")
    root.geometry("800x600")  # Increased window size

    heading_label = tk.Label(root, text="Ball and zero Detected App", font=("Arial", 23))
    heading_label.pack(pady=12)

    speed_label = tk.Label(root, text="Speed: 0 m/s", font=("Arial", 17))
    speed_label.pack(pady=12)

    laps_label = tk.Label(root, text="Laps: 0", font=("Arial", 17))
    laps_label.pack(pady=12)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    upload_button = tk.Button(button_frame, text="Upload Video", command=lambda: upload_video(speed_label, laps_label))
    upload_button.pack(pady=12, padx=10)

    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=5)

    rtsp_label = tk.Label(entry_frame, text="Enter RTSP Stream URL:", font=("Arial", 17))
    rtsp_label.pack(side="top")

    rtsp_entry = tk.Entry(entry_frame, font=("Arial", 15), width=60)
    rtsp_entry.insert(0, "rtsp://")
    rtsp_entry.pack(side="bottom")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    camera_button = tk.Button(button_frame, text="Connect to Camera", command=lambda: connect_to_camera(rtsp_entry, speed_label, laps_label))
    camera_button.pack(pady=12, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
