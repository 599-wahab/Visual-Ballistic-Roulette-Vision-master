import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import cvzone
import datetime
from ultralytics import YOLO
import customtkinter as ctk

DISTANCE_THRESHOLD = 10  # Distance threshold for calculating speed (in pixels)
FPS = 23  # Frames per second of the video

class WebcamWidget:
    def __init__(self, master=None, *args, **kwargs):
        self.video_source = "bandicam_2024-03-20_04-36-59-211.mp4"  # Set the video source to the default webcam
        self.vid = cv2.VideoCapture(self.video_source)
        self.detected_objects_list = []  # List to store detected objects
        self.yolo_model = YOLO("YoloV8_model_5.pt")  # Initialize YOLO model

        # Initialize previous center and passed_12_oclock
        self.prev_center = None
        self.passed_12_oclock = False
        self.last_pass_time = datetime.datetime.now()  # Initialize last_pass_time
        self.lap_count = 0  # Initialize lap count
        self.lap_times = []  # List to store lap times
        self.max_laps = 10  # Maximum number of laps

        # Create a frame to hold the camera widget and buttons
        self.frame = ctk.CTkFrame(master)
        self.frame.pack()

        # Create a label to display the webcam feed
        self.label = ctk.CTkLabel(self.frame)
        self.label.pack()

        # Create a button to connect to the camera
        self.connect_button = ctk.CTkButton(self.frame, text="Connect to Camera", command=self.connect_camera)
        self.connect_button.pack(side="left", padx=5, pady=5)

        # Create a button to start detection
        self.start_button = ctk.CTkButton(self.frame, text="Start", command=self.start_detection)
        self.start_button.pack(side="left", padx=5, pady=5)

        # Create a button to reset
        self.reset_button = ctk.CTkButton(self.frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5, pady=5)

        self.speed_label = ctk.CTkLabel(self.frame, text="Speed: N/A")
        self.speed_label.pack(side="left", padx=5, pady=5)

        self.update()

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            # Resize the frame to 800x600
            frame = cv2.resize(frame, (800, 600))

            results = self.yolo_model(frame)

            # Process YOLO results and draw bounding boxes
            for r in results:
                for box in r.boxes:
                    if int(box.cls[0]) in [0, 1]:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        w, h = x2 - x1, y2 - y1
                        cvzone.cornerRect(frame, (x1, y1, w, h))

                        # Check if the y-coordinate of the box is below the threshold
                        if y1 < 120:  # Assuming the 12 o'clock position is at y-coordinate 120
                            if not self.passed_12_oclock:
                                self.passed_12_oclock = True
                                if len(self.lap_times) < self.max_laps:
                                    self.lap_times.append(datetime.datetime.now())
                                else:
                                    self.lap_times.pop(0)
                                    self.lap_times.append(datetime.datetime.now())
                                self.lap_count += 1

                        # Calculate the distance moved by the ball
                        if self.prev_center is not None:
                            center = ((x1 + x2) // 2, (y1 + y2) // 2)
                            distance = ((center[0] - self.prev_center[0])**2 + (center[1] - self.prev_center[1])**2)**0.5
                            if distance > DISTANCE_THRESHOLD and self.passed_12_oclock:
                                time_taken = (datetime.datetime.now() - self.last_pass_time).total_seconds()
                                speed_mps = DISTANCE_THRESHOLD / time_taken
                                # Assuming self.speed_label is initialized elsewhere
                                self.speed_label.config(text=f"Speed: {speed_mps:.2f} m/s")

                        self.prev_center = ((x1 + x2) // 2, (y1 + y2) // 2)

            # Convert the frame to an image and display it in the label
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(frame)
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        # Call the update function after a delay
        self.label.after(int(1000 / FPS), self.update)

    def connect_camera(self):
        # Function to connect to the camera (you can modify this as needed)
        print("Connected to camera.")

    def start_detection(self):
        # Function to start detection (you can modify this as needed)
        print("Detection started.")

    def reset(self):
        # Function to reset (you can modify this as needed)
        self.passed_12_oclock = False
        self.prev_center = None
        self.lap_count = 0
        self.lap_times.clear()
        print("Reset.")

    def get_detected_objects(self):
        return self.detected_objects_list

# Example usage:
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Webcam Object Detection")
    webcam_widget = WebcamWidget(root)
    root.mainloop()
