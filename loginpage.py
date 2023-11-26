import tkinter as tk
from tkinter import Label, Entry, Button
import subprocess

class LoginPage(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)

        # Create a header frame with a blue background
        self.header_frame = tk.Frame(self, bg="blue")
        self.header_frame.pack(fill="x")

        # Create a title label within the header frame
        self.title_label = Label(self.header_frame, text="ML Integrated Smart Camera", font=("Helvetica", 36), fg="white", bg="blue")
        self.title_label.pack(pady=20)

        # Create a frame for the labels and fields on the login page
        self.label_frame = tk.Frame(self)
        self.label_frame.pack(pady=20, padx=20, anchor="w")

        # Create username label and entry
        self.username_label = Label(self.label_frame, text="Username:", font=("Helvetica", 24))
        self.username_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.username_entry = Entry(self.label_frame, font=("Helvetica", 24), width=20)
        self.username_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        # Create password label and entry with a toggle button
        self.password_label = Label(self.label_frame, text="Password:", font=("Helvetica", 24))
        self.password_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.password_entry = Entry(self.label_frame, show="*", font=("Helvetica", 24), width=20)
        self.password_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.toggle_button = Button(self.label_frame, text="Show Password", command=self.toggle_password, font=("Helvetica", 15))
        self.toggle_button.grid(row=1, column=3, padx=2, pady=10, sticky="w")

        self.login_button = Button(self.label_frame, text="Login", command=self.switch_to_home_page, font=("Helvetica", 24))
        self.login_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.close_button = Button(self.label_frame, text="Close", command=self.close, font=("Helvetica", 24))
        self.close_button.grid(row=2, column=1, padx=150, pady=10, sticky="w")

        # Create a label for status messages
        self.status_label = Label(self, text="", font=("Helvetica", 24))
        self.status_label.pack(pady=20)
    
    

    def toggle_password(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.config(show="*")
        else:
            self.password_entry.config(show="")

    def close(self):
        self.master.destroy()

    def switch_to_home_page(self):
        if self.validate_credentials():
            self.master.destroy()

            subprocess.Popen(['python', 'home_page.py']),
            subprocess.Popen(['python', 'face_detection.py']),
            subprocess.Popen(['python', 'face_recog.py'])
            

    # Add your credential validation logic here
    def validate_credentials(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password are correct
        if username == "admin" and password == "admin":
            # log.log_event("  login successfull")
            return True
        else:
            # If the credentials are incorrect, display a message in the status_label
            self.status_label.config(text="Invalid credentials. Please try again.", fg="red")
            # log.log_event("   Failed login")
            return False

# Run the login page as a standalone application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ML Integrated Smart Camera - Login")

    # Set the window size to be full-sized
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    login_page = LoginPage(root)
    login_page.pack(fill="both", expand=True)

    root.mainloop()
