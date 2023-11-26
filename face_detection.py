import cv2
import os
import shutil
import log

video_folder = 'motion_detected_videos/'
output_folder = 'face_detected_videos/'  # Create this folder if it doesn't exist


# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
while True:
        # List video files in the folder
        video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

        for video_file in video_files:
            video_path = os.path.join(video_folder, video_file)
            video_capture = cv2.VideoCapture(video_path)
            face_detected = False  # Flag to track if a face is detected in the video

            while video_capture.isOpened():
                ret, frame = video_capture.read()

                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the frame
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) > 0:
                    # Face detected in this frame, perform face recognition and email sending if needed
                    face_detected = True
                    #print("Face detected in", video_file)
                    # You would need a face recognition library here for matching.

            # Release the video capture object
            video_capture.release()

            # If a face was detected, move the video to the "face_detected_videos" folder
            if face_detected:
                output_path = os.path.join(output_folder, video_file)
                shutil.move(video_path, output_path)
                

            cv2.destroyAllWindows()