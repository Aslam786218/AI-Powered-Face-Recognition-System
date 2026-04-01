import cv2
import numpy as np
import face_recognition
import os
import sqlite3
from datetime import datetime

# Path to known face images
path = 'known_faces'
images = []
classNames = []
myList = os.listdir(path)

# Load known images
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Encode known faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("[INFO] Encoding known faces...")
encodeListKnown = findEncodings(images)
print("[INFO] Encoding complete. Starting webcam...")

# Initialize database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        name TEXT,
        time TEXT
    )
''')
conn.commit()

# To avoid duplicate entries in one run
marked_names = set()

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()

            if name not in marked_names:
                marked_names.add(name)
                now = datetime.now()
                dtString = now.strftime('%Y-%m-%d %H:%M:%S')

                # Insert into DB
                cursor.execute("INSERT INTO attendance (name, time) VALUES (?, ?)", (name, dtString))
                conn.commit()
                print(f"[✓] Attendance marked for {name} at {dtString}")

            # Draw rectangle and name on webcam
            y1, x2, y2, x1 = [v * 4 for v in faceLoc]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Webcam - Press q to Exit', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
