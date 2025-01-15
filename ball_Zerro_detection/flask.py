from flask import Flask, render_template, request
import cv2
import cvzone
from datetime import datetime
from ultralytics import YOLO

DISTANCE_THRESHOLD = 10  # Distance threshold for calculating speed (in pixels)
FPS = 23  # Frames per second of the video

app = Flask(__name__)

model = YOLO("YoloV8_model_5.pt")

class RouletteTracker:
    def __init__(self):
        self.lap_count = 0
        self.start_time = None
        self.last_pass_time = None
        self.passed_12_oclock = False
        self.prev_center = None
        self.speed = 0

    def reset(self):
        self.lap_count = 0
        self.start_time = None
        self.last_pass_time = None
        self.passed_12_oclock = False
        self.prev_center = None
        self.speed = 0

    def process_frame(self, frame):
        results = model(frame, stream=True)
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) in [0, 1]:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    cvzone.cornerRect(frame, (x1, y1, w, h))

                    if y1 < 120:
                        self.passed_12_oclock = True

                    if self.prev_center is not None:
                        center = ((x1 + x2) // 2, (y1 + y2) // 2)
                        distance = ((center[0] - self.prev_center[0])**2 + (center[1] - self.prev_center[1])**2)**0.5
                        if distance > DISTANCE_THRESHOLD and self.passed_12_oclock:
                            time_taken = (datetime.now() - self.last_pass_time).total_seconds()
                            self.speed = DISTANCE_THRESHOLD / time_taken

                    self.prev_center = ((x1 + x2) // 2, (y1 + y2) // 2)

        if self.passed_12_oclock and not self.last_pass_time:
            self.last_pass_time = datetime.now()

        if self.passed_12_oclock and not self.start_time:
            self.start_time = datetime.now()

        if self.passed_12_oclock and self.last_pass_time:
            self.lap_count += 1

        if self.lap_count >= 10:
            self.reset()

tracker = RouletteTracker()

@app.route('/')
def index():
    return render_template('index.html', speed=tracker.speed)

@app.route('/process_video', methods=['POST'])
def process_video():
    video_path = request.files['video']
    cap = cv2.VideoCapture(video_path)
    while True:
        success, frame = cap.read()
        if not success:
            break

        tracker.process_frame(frame)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_encoded = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')

    cap.release()

if __name__ == "__main__":
    app.run(debug=True)
