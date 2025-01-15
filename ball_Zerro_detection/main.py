import cv2
import cvzone
import tempfile
import os
import customtkinter as ctk
from datetime import datetime
from ultralytics import YOLO

model = YOLO("YoloV8_model_1.pt")

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    while True:
        success, img = cap.read()
        if not success:
            break

        results = model(img, stream=True)
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) in [0, 1]:  # Assuming class indices for ball and zero
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1

                    cvzone.cornerRect(img, (x1, y1, w, h))

        # Set window size based on frame dimensions
        cv2.namedWindow('Objects Detected by YOLO', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Objects Detected by YOLO', img.shape[1], img.shape[0])

        cv2.imshow('Objects Detected by YOLO', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def upload_video():
    video_path = ctk.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if video_path:
        process_video(video_path)

def connect_to_camera(rtsp_entry):
    rtsp_url = rtsp_entry.get()
    if rtsp_url:
        process_video(rtsp_url)

def main():
    root = ctk.CTk()
    root.title("Object Detection App")
    root.geometry("600x450")  # Increased height to accommodate the entry widget

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    heading_label = ctk.CTkLabel(root, text="Object Detection App", font=("Arial", 23))
    heading_label.pack(pady=12)

    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=5)  # Reduced vertical padding for button frame

    upload_button = ctk.CTkButton(button_frame, text="Upload Video", command=upload_video)
    upload_button.pack(pady=12, padx=10)

    entry_frame = ctk.CTkFrame(root)  # New frame for the entry widget
    entry_frame.pack(pady=5)  # Reduced vertical padding for entry frame

    rtsp_label = ctk.CTkLabel(entry_frame, text="Enter RTSP Stream URL:", font=("Arial", 17))
    rtsp_label.pack(side="top")

    rtsp_entry = ctk.CTkEntry(entry_frame, font=("Arial", 15), width=523)
    rtsp_entry.insert(0, "rtsp://<IP address of device>:<RTSP port>/Streaming/channels/<channel number><stream number>")
    rtsp_entry.pack(side="bottom")

    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=5)

    camera_button = ctk.CTkButton(button_frame, text="Connect to Camera", command=lambda: connect_to_camera(rtsp_entry))
    camera_button.pack(pady=12, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()