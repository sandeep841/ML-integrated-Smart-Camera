import log
import cv2
import os
import log
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import threading
from queue import Queue
import time

# Global variables for the camera capture object and myl label
cap = None
file_label = None
myl = None
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for mp4 format

def excel_event():
    # Function to process new rows
    def log_add(new_rows):
        status_queue.put(new_rows[["Timestamp", "Event"]].to_string(index=False, header=False))
    # Function to read Excel file and check for updates
    def check_updates():
        try:
            df = pd.read_excel("events_log.xlsx")
            return df
        except FileNotFoundError:
            print("File not found. Please make sure the file exists.")
            return pd.DataFrame()

    # Set up initial dataframe
    current_df = check_updates()
    log.log_event("Application Started")
    try:
        while True:
            time.sleep(1)  # Adjust the sleep interval as needed
            updated_df = check_updates()

            if not updated_df.empty:
                # Check for new rows based on Timestamp and Event columns
                new_rows = updated_df[
                    ~updated_df.set_index(["Timestamp", "Event"]).index.isin(
                        current_df.set_index(["Timestamp", "Event"]).index
                    )
                ]

                if not new_rows.empty:
                    log_add(new_rows)

                current_df = updated_df
    except KeyboardInterrupt:
        pass


# Queue for communication between threads
status_queue = Queue()
status_thread = threading.Thread(target=excel_event)
status_thread.start()

def add_event(event_text):
    global status_canvas_height
    event_frame = tk.Frame(status_canvas, bg='white', width=status_canvas.winfo_width(), height=40)
    event_label = tk.Label(event_frame, text=event_text, bg="white")
    event_label.pack(side="top")

    # Shift the existing events down
    for item in status_canvas.find_all():
        status_canvas.move(item, 0, 20)

    # Insert the new event at the top
    status_canvas.create_window((0, 0), window=event_frame, anchor='nw', width=status_canvas.winfo_width())

    status_canvas_height += 40

    status_canvas_frame.update_idletasks()
    status_canvas.config(scrollregion=status_canvas.bbox('all'))


last_processed_index = 0



def check_status_queue():
    global last_processed_index

    while not status_queue.empty():
        event_text = status_queue.get()
        add_event(event_text)

        # Update last_processed_index after processing an event
        last_processed_index += 1

    # Check for new events from Excel every 60 seconds (adjust as needed)
    root.after(1000, check_status_queue)

# Function to log an event and add it to the queue
def stop_camera_feed():
    global cap, myl
    if cap is not None:
        try:
            cap.release()
        except cv2.error as e:
            pass
        cap = None
    if myl is not None:
        myl.destroy()
        myl = None


def clear_dashboard_frame():
    for widget in dashboard.winfo_children():
        widget.destroy()


def clear_register_face_frame():
    for widget in register_face.winfo_children():
        widget.destroy()


def clear_files_frame():
    for widget in files.winfo_children():
        widget.destroy()


def show_register_face():
    stop_camera_feed()
    dashboard.pack_forget()
    files.pack_forget()
    clear_register_face_frame()  # Clear the previous "Register Face" frame

    register_face.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    global register_label
    register_label = tk.Label(register_face, bd=1, relief="solid")
    register_label.pack(padx=20, pady=5)

    form_frame = tk.Frame(register_face, bg="lightgray", bd=2, relief="sunken", padx=10, pady=15)
    form_frame.pack(padx=10, pady=10)

    name_label = tk.Label(form_frame, text="Person Name", font=("Helvetica", 16), bg="lightgrey")
    name_label.grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form_frame, font=("Helvetica", 16))
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    reg_status = tk.Label(register_face, text="", font=("Helvetica", 16), bg="white")
    reg_status.pack()

    reset_button = tk.Button(form_frame, text="Reset Camera", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                             command=reset_register_face)
    reset_button.grid(row=2, column=0, columnspan=2)

    def register_face_button():
        name = name_entry.get()

        if name:
            # Capture an image from the camera
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            ret, frame = cap.read()

            if ret:
                # Save the image to a file with the person's name
                image_folder = "registered"
                image_path = os.path.join(image_folder, f"{name}.jpg")
                cv2.imwrite(image_path, frame)
                log.log_event(f"{name} registered")
                reg_status.config(text="Person Registered Successfully", fg="green")
            else:
                reg_status.config(text="Failed to capture an image", fg="red")

            cap.release()
        else:
            reg_status.config(text="Please enter a valid person name", fg="red")

    register_button = tk.Button(form_frame, text="Register", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                                command=register_face_button)
    register_button.grid(row=1, column=0, columnspan=2)

    def update_camera_feed():
        ret, frame = cap.read()
        if ret:
            photo = convert_to_image(frame)
            register_label.configure(image=photo)
            register_label.image = photo
            register_label.after(10, update_camera_feed)  # Update every 10 milliseconds

    update_camera_feed()


def reset_register_face():
    stop_camera_feed()
    register_face.pack_forget()
    files.pack_forget()
    clear_register_face_frame()
    show_register_face()


def show_dashboard():
    stop_camera_feed()
    register_face.pack_forget()
    files.pack_forget()
    clear_dashboard_frame()  # Clear the previous "Register Face" frame

    dashboard.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    motion_view_active = False
    monitoring_mode = False
    start_frame = None  # Initialize start_frame

    def toggle_motion_view():
        nonlocal motion_view_active, start_frame
        motion_view_active = not motion_view_active
        start_frame = None if motion_view_active else None  # Reset start_frame

    def start_monitoring():
        nonlocal monitoring_mode, start_frame, out, alarm
        monitoring_mode = not monitoring_mode
        start_frame = None if monitoring_mode else None
        if monitoring_mode:
            monitoring.config(bg="lightgreen")
            log.log_event("Monitoring Mode ON")
        else:
            monitoring.config(bg="white")
            log.log_event("Monitoring Mode OFF")
            if out is not None:
                out.release()
                out = None
            alarm = False
    
    try:
        # Create a "Start Live Feed" button
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        out = None

        if cap.isOpened():
            # Create the feed_label label if it doesn't exist
            feed_label = tk.Label(dashboard, bd=1, relief="solid")
            feed_label.pack(side="left", anchor="nw", padx=20, pady=15)

            options = tk.Frame(dashboard, bg="blue")
            options.pack(side="right", anchor="ne", padx=70, pady=50)

            monitoring = tk.Button(options, text="Start monitoring", font=("Helvetica", 20), bd=2, relief="raised",
                                   command=start_monitoring)
            monitoring.pack(fill="x")

            motion_view_button = tk.Button(options, text="Motion View", font=("Helvetica", 20), bd=2, relief="raised",
                                           command=toggle_motion_view)
            motion_view_button.pack(fill="x", pady=40)

            alarm = False
            alarm_counter = 0

            while True:
                _, frame = cap.read()
                if _:

                    frame = frame1 = cv2.resize(frame, (640, 480))

                    if motion_view_active or monitoring_mode:

                        if start_frame is None:
                            start_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

                        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

                        difference = cv2.absdiff(frame_bw, start_frame)
                        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]

                        start_frame = frame_bw

                        if monitoring_mode:
                            if threshold.sum() > 10000:
                                alarm_counter += 1
                                if alarm_counter > 30:
                                    if not alarm:
                                        alarm = True
                                        # Start recording when the alarm is triggered
                                        video_filename = datetime.now().strftime(
                                            "motion_detected_videos/%Y_%m_%d_%H_%M_%S.mp4")
                                        log.log_event("Motion detected" + datetime.now().strftime(" %H_%M_%S"))
                                        # df = pd.DataFrame({"events": ["Monitoring Mode ON"]})
                                        # df.to_excel("logs.xlsx", index=False)
                                        out = cv2.VideoWriter(video_filename, fourcc, 20.0,
                                                              (frame.shape[1], frame.shape[0]), isColor=True)

                            else:
                                if alarm_counter > 0:
                                    alarm_counter -= 1
                                    if alarm_counter == 0 and out is not None:
                                        log.log_event("Recording stopped")
                                        out.release()
                                        out = None
                                        alarm = False

                        elif not monitoring_mode and alarm:
                            # Stop recording when the alarm is turned off
                            log.log_event("video recorded")
                            if out is not None:
                                out.release()
                                out = None

                        else:
                            None
                        # Write the frame to the video file if it's being recorded
                        if out is not None:
                            out.write(frame)

                        if motion_view_active:
                            motion_view_button.config(bg="lightgreen")

                            frame1 = cv2.merge((threshold, threshold, threshold))
                            photo = convert_to_image(frame1)

                    if not motion_view_active:

                        motion_view_button.config(bg="white")
                        # Detect faces in the frame and draw rectangles around them
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5,
                                                              minSize=(30, 30))
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        photo = convert_to_image(frame)

                    feed_label.configure(image=photo)
                    feed_label.image = photo
                    feed_label.update()
                else:
                    break

            cap.release()
    except Exception as e:
        print(f"An error occurred during show_dashboard: {str(e)}")

    try:

        if 'feed_label' not in globals():
            # Create a label with an error message
            feed_label = tk.Label(dashboard, text="Failed to start camera feed", bd=1, relief="solid")
            feed_label.pack(padx=20, pady=15)
    except Exception as e:
        print(f"An error occurred creating the dashboard widgets: {str(e)}")


def unknown_persons_show_files():
    stop_camera_feed()  # Stop the camera feed
    dashboard.pack_forget()
    register_face.pack_forget()
    clear_register_face_frame()
    clear_dashboard_frame()
    clear_files_frame()  # Clear the previous "Register Face" frame

    files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a Listbox to display the video files
    video_listbox = tk.Listbox(files, selectmode=tk.SINGLE)
    video_listbox.pack(fill=tk.BOTH, expand=True)

    # List video files in the "face_detected_videos" folder and add them to the Listbox
    video_folder = "unknown_persons"
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

    for video_file in video_files:
        video_listbox.insert(tk.END, video_file)

    # Create a "Play" button to play the selected video
    def play_video():
        global cap, file_label
        stop_video()  # Stop any currently playing video

        selected_video = video_listbox.get(video_listbox.curselection())
        if selected_video:
            video_path = os.path.join("unknown_persons", selected_video)
            cap = cv2.VideoCapture(video_path)

            # Create the file_label if it doesn't exist
            if file_label is None:
                file_label = tk.Label(files, bd=1, relief="solid")
                file_label.pack(padx=20, pady=15)

            def update_video_feed():
                _, frame = cap.read()
                if _:
                    frame = cv2.resize(frame, (640, 480))  # Resize frame if needed
                    photo = convert_to_image(frame)
                    file_label.configure(image=photo)
                    file_label.image = photo
                    file_label.update()
                    file_label.after(10, update_video_feed)  # Update every 10 milliseconds
                else:
                    stop_video()  # Stop video playback when it ends

            update_video_feed()

    def stop_video():
        global cap, file_label
        if cap is not None:
            cap.release()
            cap = None
        if file_label is not None:
            file_label.destroy()
            file_label = None

    media_menu = tk.Frame(files, bg="#7FFFD4")
    media_menu.pack(pady=(30, 0), padx=10)

    # Create a "Stop" button to stop the video
    stop_button = tk.Button(media_menu, text="Stop", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=stop_video)
    stop_button.grid(row=0, column=0, padx=10, pady=10)

    # Create a "Play" button to play the selected video
    play_button = tk.Button(media_menu, text="Play", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=play_video)
    play_button.grid(row=0, column=1, padx=5, pady=10)


def known_persons_show_files():
    stop_camera_feed()  # Stop the camera feed
    dashboard.pack_forget()
    register_face.pack_forget()
    clear_register_face_frame()
    clear_dashboard_frame()
    clear_files_frame()  # Clear the previous "Register Face" frame

    files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a Listbox to display the video files
    video_listbox = tk.Listbox(files, selectmode=tk.SINGLE)
    video_listbox.pack(fill=tk.BOTH, expand=True)

    # List video files in the "face_detected_videos" folder and add them to the Listbox
    video_folder = "known_persons"
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

    for video_file in video_files:
        video_listbox.insert(tk.END, video_file)

    # Create a "Play" button to play the selected video
    def play_video():
        global cap, file_label
        stop_video()  # Stop any currently playing video

        selected_video = video_listbox.get(video_listbox.curselection())
        if selected_video:
            video_path = os.path.join("known_persons", selected_video)
            cap = cv2.VideoCapture(video_path)

            # Create the file_label if it doesn't exist
            if file_label is None:
                file_label = tk.Label(files, bd=1, relief="solid")
                file_label.pack(padx=20, pady=15)

            def update_video_feed():
                _, frame = cap.read()
                if _:
                    frame = cv2.resize(frame, (640, 480))  # Resize frame if needed
                    photo = convert_to_image(frame)
                    file_label.configure(image=photo)
                    file_label.image = photo
                    file_label.update()
                    file_label.after(10, update_video_feed)  # Update every 10 milliseconds
                else:
                    stop_video()  # Stop video playback when it ends

            update_video_feed()

    def stop_video():
        global cap, file_label
        if cap is not None:
            cap.release()
            cap = None
        if file_label is not None:
            file_label.destroy()
            file_label = None

    media_menu = tk.Frame(files, bg="#7FFFD4")
    media_menu.pack(pady=(30, 0), padx=10)

    # Create a "Stop" button to stop the video
    stop_button = tk.Button(media_menu, text="Stop", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=stop_video)
    stop_button.grid(row=0, column=0, padx=10, pady=10)

    # Create a "Play" button to play the selected video
    play_button = tk.Button(media_menu, text="Play", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=play_video)
    play_button.grid(row=0, column=1, padx=5, pady=10)


def motion_show_files():
    stop_camera_feed()  # Stop the camera feed
    dashboard.pack_forget()
    register_face.pack_forget()
    clear_register_face_frame()
    clear_dashboard_frame()
    clear_files_frame()  # Clear the previous "Register Face" frame

    files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a Listbox to display the video files
    video_listbox = tk.Listbox(files, selectmode=tk.SINGLE)
    video_listbox.pack(fill=tk.BOTH, expand=True)

    # List video files in the "face_detected_videos" folder and add them to the Listbox
    video_folder = "motion_detected_videos"
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

    for video_file in video_files:
        video_listbox.insert(tk.END, video_file)

    # Create a "Play" button to play the selected video
    def play_video():
        global cap, file_label
        stop_video()  # Stop any currently playing video

        selected_video = video_listbox.get(video_listbox.curselection())
        if selected_video:
            video_path = os.path.join("motion_detected_videos", selected_video)
            cap = cv2.VideoCapture(video_path)

            # Create the file_label if it doesn't exist
            if file_label is None:
                file_label = tk.Label(files, bd=1, relief="solid")
                file_label.pack(padx=20, pady=15)

            def update_video_feed():
                _, frame = cap.read()
                if _:
                    frame = cv2.resize(frame, (640, 480))  # Resize frame if needed
                    photo = convert_to_image(frame)
                    file_label.configure(image=photo)
                    file_label.image = photo
                    file_label.update()
                    file_label.after(10, update_video_feed)  # Update every 10 milliseconds
                else:
                    stop_video()  # Stop video playback when it ends

            update_video_feed()

    def stop_video():
        global cap, file_label
        if cap is not None:
            cap.release()
            cap = None
        if file_label is not None:
            file_label.destroy()
            file_label = None

    media_menu = tk.Frame(files, bg="#7FFFD4")
    media_menu.pack(pady=(30, 0), padx=10)

    # Create a "Stop" button to stop the video
    stop_button = tk.Button(media_menu, text="Stop", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=stop_video)
    stop_button.grid(row=0, column=0, padx=10, pady=10)

    # Create a "Play" button to play the selected video
    play_button = tk.Button(media_menu, text="Play", padx=2, pady=2, font=("Helvetica", 16), bg="white",
                            command=play_video)
    play_button.grid(row=0, column=1, padx=5, pady=10)


def on_closing():
    stop_camera_feed()
    root.destroy()
    os._exit(0)

def convert_to_image(frame):
    try:
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        photo = ImageTk.PhotoImage(image=image)
        return photo
    except RuntimeError:
        return None


status_canvas_height = 0  # Initialize the status_canvas_height variable


def on_configure(event):
    status_canvas.configure(scrollregion=status_canvas.bbox('all'))


def start_status_thread():
    status_thread = threading.Thread(target=check_status_queue)
    status_thread.daemon = True
    status_thread.start()
    root.after(1000, check_status_queue)


root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.title("ML Integrated Smart Camera")



header = tk.Frame(root, bg="blue", height=40)
header.pack(side=tk.TOP, fill=tk.X)
title_label = tk.Label(header, text="ML Integrated Smart Camera", font=("Helvetica", 36), fg="white", bg="blue")
title_label.pack(pady=10)

menu = tk.Frame(root, bg="lightgrey", width=250, height=400, bd=1, relief="solid")
menu.pack(side=tk.LEFT, fill=tk.Y)

dashboard_button = tk.Button(menu, text="Dashboard", font=("Helvetica", 24), command=show_dashboard)
dashboard_button.pack(fill=tk.X)

register_face_button = tk.Button(menu, text="Register Face", font=("Helvetica", 24), command=show_register_face)
register_face_button.pack(fill=tk.X)

unknown_persons_files_button = tk.Button(menu, text="unknown persons", font=("Helvetica", 24),
                                         command=unknown_persons_show_files)
unknown_persons_files_button.pack(fill=tk.X)

known_persons_files_button = tk.Button(menu, text="known persons", font=("Helvetica", 24),
                                       command=known_persons_show_files)
known_persons_files_button.pack(fill=tk.X)

motion_files_button = tk.Button(menu, text="motion files", font=("Helvetica", 24), command=motion_show_files)
motion_files_button.pack(fill=tk.X)

close_button = tk.Button(menu, text="Close", font=("Helvetica", 24), command=on_closing)
close_button.pack(fill=tk.X, side=tk.BOTTOM)

dashboard = tk.Frame(root, width=400, height=400, bd=1, bg="blue", relief="solid")
files = tk.Frame(root, width=400, height=400, bd=1, bg="#7FFFD4", relief="solid")
register_face = tk.Frame(root, width=400, height=400, bd=1, bg="white", relief="solid")

# ====================status===================
status = tk.Frame(root, bg="lightgrey", width=250, height=400, bd=1, relief="solid")
status.pack(side=tk.RIGHT, fill=tk.Y)

status_label = tk.Label(status, text="Status", width=10, font=("Helvetica", 26))
status_label.pack(fill=tk.X)

status_canvas_frame = tk.Frame(status)
status_canvas_frame.place(relx=.5, rely=.5, anchor='center')

status_canvas_height = 0
status_canvas_width = 250

# Create the status canvas
status_canvas = tk.Canvas(status_canvas_frame, bg='white', width=status_canvas_width, height=status_canvas_height,
                          highlightthickness=0)
status_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a scrollbar for the canvas
scrollbar = tk.Scrollbar(status_canvas_frame, orient='vertical', command=status_canvas.yview)
scrollbar.pack(side='right', fill='y')

# Configure the canvas to use the scrollbar
status_canvas.configure(yscrollcommand=scrollbar.set)

# Add the canvas to the status frame
status_canvas_frame.pack(fill="both", expand=True)

# Bind the on_configure function to the canvas
status_canvas.bind('<Configure>', on_configure)

# Update the scroll region
status_canvas.config(scrollregion=status_canvas.bbox('all'))
unknown_persons_show_files()
start_status_thread()

try:
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.after(1000, check_status_queue)  # Schedule the function to run after 1000 milliseconds (1 second)
    root.mainloop()
except Exception as e:
    print(f"An error occurred during the main loop: {str(e)}")