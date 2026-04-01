import cv2
import numpy as np
import face_recognition
import os
import mediapipe as mp
import serial
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
from datetime import datetime

# -------------------------------
# 1️⃣ Load known faces
# -------------------------------
path = 'known_faces'
known_encodings = []
known_names = []

for file_name in os.listdir(path):
    if file_name.endswith(('.jpg', '.png')):
        img_path = os.path.join(path, file_name)
        image = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            name = os.path.splitext(file_name)[0]
            known_names.append(name)

# -------------------------------
# 2️⃣ Serial port setup (once)
# -------------------------------
serial_port_found = False
try:
    ser = serial.Serial('COM3', 9600, timeout=1)  # Update COM port accordingly
    serial_port_found = True
except:
    print("⚠ Serial port not found. Spoof detection will only mark once.")

spoof_attempt_marked = False

# -------------------------------
# 3️⃣ MediaPipe FaceMesh setup
# -------------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# -------------------------------
# 4️⃣ Attendance control
# -------------------------------
attendance_running = False
recognized_names = set()  # use set to avoid duplicates

# -------------------------------
# Generate timestamped CSV file
# -------------------------------
now = datetime.now()
date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
csv_file = f"attendance_{date_str}.csv"

# Create CSV file with headers
with open(csv_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Date", "Time"])

# -------------------------------
# 5️⃣ Attendance loop (camera processing)
# -------------------------------
def attendance_loop(video_label):
    global attendance_running, spoof_attempt_marked
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Camera not opened")
        return

    while attendance_running:
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Face detection (HOG for speed)
        face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Adjust coordinates to original frame size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            # Compare with known faces
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.45:
                    name = known_names[best_match_index]
                else:
                    name = "Unknown"
            else:
                name = "Unknown"

            # Draw rectangle + label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Spoof detection (once)
            if name == "Unknown" and serial_port_found and not spoof_attempt_marked:
                print("❌ Spoof attempt detected!")
                spoof_attempt_marked = True

            # Log recognized names in CSV
            if name != "Unknown" and name not in recognized_names:
                recognized_names.add(name)
                now_inner = datetime.now()
                with open(csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, now_inner.strftime("%Y-%m-%d"), now_inner.strftime("%H:%M:%S")])
                print(f"✅ Recognized and logged: {name}")

        # MediaPipe FaceMesh overlay
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_draw.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                )

        # Convert OpenCV frame to Tkinter image
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_attendance()

    cap.release()
    cv2.destroyAllWindows()

# -------------------------------
# 6️⃣ GUI setup
# -------------------------------
root = tk.Tk()
root.title("Face Recognition Attendance")
root.geometry("900x700")

# Video frame
video_label = tk.Label(root)
video_label.pack()

# Start / Stop buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

def start_attendance_gui():
    global attendance_running
    if not attendance_running:
        attendance_running = True
        threading.Thread(target=attendance_loop, args=(video_label,)).start()
        print("✅ Attendance started")

def stop_attendance():
    global attendance_running
    attendance_running = False
    print("🛑 Attendance stopped")

start_btn = tk.Button(button_frame, text="Start Attendance", command=start_attendance_gui, bg="green", fg="white", width=20)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(button_frame, text="Stop Attendance", command=stop_attendance, bg="red", fg="white", width=20)
stop_btn.grid(row=0, column=1, padx=10)

exit_btn = tk.Button(button_frame, text="Exit", command=root.destroy, bg="gray", fg="white", width=20)
exit_btn.grid(row=0, column=2, padx=10)

root.mainloop()
