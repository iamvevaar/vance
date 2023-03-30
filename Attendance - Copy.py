import numpy
import cv2
import face_recognition
import csv
from datetime import datetime
import numpy as np
import pyttsx3
import sqlite3

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


conn = sqlite3.connect('attendance.db')
c = conn.cursor()

try:
    # attempt to create the attendance_records table
    c.execute('''CREATE TABLE attendance_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  time DATETIME)''')
    # commit the changes to the database
    conn.commit()
    print("Table created successfully.")
except sqlite3.OperationalError as e:
    # if the table already exists, catch the error and print a message
    print("Table already exists. Skipping table creation.")

# close the connection to the database
conn.close()

video_capture = cv2.VideoCapture(0)

# load known faces
vevaar_image = face_recognition.load_image_file("faces/vevaar.jpg")
vevaar_encoding = face_recognition.face_encodings(vevaar_image)[0]

pooja_image = face_recognition.load_image_file("faces/pooja.png")
pooja_encoding = face_recognition.face_encodings(pooja_image)[0]

mummy_image = face_recognition.load_image_file("faces/mummy.jpg")
mummy_encoding = face_recognition.face_encodings(mummy_image)[0]

raju_image = face_recognition.load_image_file("faces/raju.png")
raju_encoding = face_recognition.face_encodings(raju_image)[0]

known_face_encodings = [vevaar_encoding, pooja_encoding, mummy_encoding, raju_encoding]
known_face_names = ["Vevaar", "Pooja", "Mummy", "Raju"]

# list of expected students
students = known_face_names.copy()

face_locations = []
face_encodings = []

# get the current date and time

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")

f = open(f"{current_date}.csv", "w+", newline="")
lnwriter = csv.writer(f)

while True:
    _, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Recognized Face
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distance)

        if (matches[best_match_index]):
            name = known_face_names[best_match_index]

        # Add the text if a person is presenst
        if name in known_face_names:
            font = cv2.FONT_HERSHEY_PLAIN
            bottomLeftCornerOfText = (10, 100)
            fontScale = 1.5
            fontColor = (255, 0, 0)
            thickness = 3
            lineType = 2
            cv2.putText(frame, name + " IS Present", bottomLeftCornerOfText, font, fontScale, fontColor, thickness,
                        lineType)

            if name in students:
                students.remove(name)
                current_time = now.strftime("%H:%M:%S")
                lnwriter.writerow([name, current_time])

                now = datetime.now()
                time_string = now.strftime("%Y-%m-%d %H:%M:%S")
                data = (name, time_string,)

                conn = sqlite3.connect('attendance.db')
                c = conn.cursor()
                c.execute("INSERT INTO attendance_records (name, time) VALUES (?, ?)", data)
                conn.commit()
                conn.close()

    cv2.imshow("Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        label = name + str(" is Present")
        print(label)
        speak(label)
        break

video_capture.release()
cv2.destroyAllWindows()
f.close()
