import cv2
import os
import face_recognition
import log
import numpy as np
import shutil
import threading
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import time

time.sleep(2)


def mail_sent(toaddr, filename, path, body):
        fromaddr = "testingautomation243@gmail.com"
        toaddr = toaddr
        msg = MIMEMultipart() 
        msg['From'] = fromaddr 
        msg['To'] = toaddr 
        msg['Subject'] = "Face Recorded detection"
        body = body
        msg.attach(MIMEText(body, 'plain')) 
        filename = filename
        attachment = open(path, "rb") 
        p = MIMEBase('application', 'octet-stream') 
        p.set_payload((attachment).read()) 
        encoders.encode_base64(p) 
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        msg.attach(p) 
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.starttls() 
        s.login(fromaddr, "qfbhurcoigibaezh") 
        text = msg.as_string() 
        s.sendmail(fromaddr, toaddr, text)
        log.log_event("sent mail")
        s.quit()
 
path = 'registered'
images = [f for f in os.listdir(path) if f.endswith('.jpg')]

# Load the known face encodings and corresponding names
known_face_encodings = []
known_face_names = []

for img_path in images:
    try:
        img = face_recognition.load_image_file(os.path.join(path, img_path))
        encode = face_recognition.face_encodings(img)[0]
        known_face_encodings.append(encode)
        known_face_names.append(img_path[:-4])  # Remove the file extension
    except Exception as e:
        print(f"Error processing image: {img_path}, {e}")
log.log_event("Encoding complete")
    
video_folder = 'face_detected_videos'
known_persons_folder = 'known_persons'  # Create this folder if it doesn't exist
unknown_persons_folder = 'unknown_persons'  # Create this folder if it doesn't exist

while True:
    # List video files in the folder
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

    for video_file in video_files:
            
        video_path = os.path.join(video_folder, video_file)
        cap = cv2.VideoCapture(video_path)
        name1 = ""    
        if not os.path.exists(video_path):
            print("Video file does not exist:", video_file)

        if not cap.isOpened():
            print("Error opening video capture")

        while True:
            success, img = cap.read()
            if not success:
                break

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            face_detected = False

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(known_face_encodings, encodeFace)
                faceDis = face_recognition.face_distance(known_face_encodings, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = known_face_names[matchIndex].upper()
                    if name != name1:
                        name1 = name
                        # Release the video capture object before moving the file
                        cap.release()
                        # Move the video to the "known_persons" folder
                        output_path = os.path.join(known_persons_folder, video_file)
                        shutil.move(video_path, output_path)
                        log.log_event(f"Detected: {name}")
                        face_detected = True
                        break

                    # If no face was detected, move the video to "unknown_persons" folder
                else:
                    cap.release()
                    output_path = os.path.join(unknown_persons_folder, video_file)
                    shutil.move(video_path, output_path)
                    log.log_event("unknown person")
                        
                    email_thread = threading.Thread(target=mail_sent,args=("sandeepgoudkmp@gmail.com", "unknown.mp4",  output_path, "unknown person detected attached recording above"))
                    email_thread.start()
                    break

                time.sleep(0.1)

            cv2.destroyAllWindows()
