import cv2
import face_recognition
import os
import numpy as np
import csv
import datetime
import tkinter as tk
from tkinter import messagebox
import platform

# ===============================
# Import liveness check
# ===============================
try:
    from liveness import check_liveness
except Exception as e:
    print("⚠️ liveness.py not found or failed to import. Running without liveness.")
    def check_liveness(*args, **kwargs):
        return True  # fallback if no sensor

# ===============================
# Load known faces
# ===============================
def load_known_faces(path='sample_images'):
    """
    Load all face images from the folder, encode them and return names and encodings.
    """
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(path):
        print(f"⚠️ Folder '{path}' not found. Please create it and add sample images.")
        return known_face_encodings, known_face_names

    for filename in os.listdir(path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(path, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0].capitalize())

    return known_face_encodings, known_face_names

# ===============================
# Write attendance to CSV
# ===============================
def mark_attendance(name):
    """
    Logs the name and time into today's CSV file (one entry per name).
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    filename = f"attendance_{date_str}.csv"

    already_logged = False
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == name:
                    already_logged = True
                    break

    if not already_logged:
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            if os.stat(filename).st_size == 0:
                writer.writerow(["Name", "Time"])
            writer.writerow([name, time_str])

# ===============================
# Get proper camera backend by OS
# ===============================
def get_camera_capture(index=0):
    os_name = platform.system()
    if os_name == "Windows":
        return cv2.VideoCapture(index, cv2.CAP_DSHOW)
    elif os_name == "Darwin":  # macOS
        return cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    else:  # Linux and others
        return cv2.VideoCapture(index, cv2.CAP_V4L2)

# ===============================
# Face recognition + liveness loop
# ===============================
def face_recognition_loop():
    """
    Captures frames from webcam, detects faces, runs recognition and liveness.
    """
    known_face_encodings, known_face_names = load_known_faces()
    attendance_set = set()

    video_capture = get_camera_capture()

    if not video_capture.isOpened():
        messagebox.showerror("Error", "❌ Failed to open webcam. Check camera permissions.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Failed to capture frame")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches and matches[best_match_index]:
                    name = known_face_names[best_match_index]

            # Scale back up face locations
            top, right, bottom, left = [v * 4 for v in face_location]

            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 200, 255), 2)

            if name != "Unknown" and name not in attendance_set:
                # ✅ Run liveness before marking attendance
                is_live = check_liveness()

                if is_live:
                    attendance_set.add(name)
                    mark_attendance(name)
                    cv2.putText(frame, name, (left + 6, bottom + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    print(f"✔️ Attendance marked for {name}")
                else:
                    cv2.putText(frame, f"{name} (Spoof!)", (left + 6, bottom + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                    print(f"❌ Spoof attempt detected for {name}")
                    messagebox.showwarning("Spoof", f"Liveness failed for {name}")

            else:
                # Draw Unknown label
                cv2.putText(frame, name, (left + 6, bottom + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        try:
            cv2.imshow('Smart Attendance System - Press Q to Quit', frame)
        except cv2.error as e:
            print("OpenCV display error:", e)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# ===============================
# GUI
# ===============================
class AttendanceApp:
    def __init__(self, master):
        self.master = master
        master.title("Smart Attendance System")
        master.geometry("400x250")
        master.configure(bg="#1e1e1e")

        self.label = tk.Label(master, text="Smart Attendance System",
                              font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#ffffff")
        self.label.pack(pady=20)

        self.start_button = tk.Button(master, text="Start Attendance", command=self.start_attendance,
                                      bg="#2ecc71", fg="white", font=("Arial", 12), padx=20, pady=10,
                                      activebackground="#27ae60", activeforeground="white")
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(master, text="Exit", command=master.quit,
                                     bg="#e74c3c", fg="white", font=("Arial", 12), padx=20, pady=10,
                                     activebackground="#c0392b", activeforeground="white")
        self.quit_button.pack(pady=10)

    def start_attendance(self):
        self.master.withdraw()
        face_recognition_loop()
        self.master.deiconify()

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
