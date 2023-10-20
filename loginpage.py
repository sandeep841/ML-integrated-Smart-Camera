from tkinter import *
from functools import partial
import os


# Window
tkWindow = Tk()  
tkWindow.geometry('1204x740')  
tkWindow.title('ML Intergrated Smart Camera')

def validateLogin(username, password):
        print("username entered :", username.get())
        print("password entered :", password.get())
        uname = username.get()
        upass = password.get()
        if(uname  == "admin" and upass=="admin"):
                print("login Successful")
                txt = Label(tkWindow, text="login Successful").place(x=0, y=300)
                os.system('python face_detection.py')
                tkWindow.quit()
                tkWindow.destroy()
        else:
                print("login Failed")
                txt = Label(tkWindow, text="login Failed").place(x=0, y=300)
        return



font = ('times', 16, 'bold')
title = Label(tkWindow, text='ML Intergrated Smart Camera')
title.config(bg='darkviolet', fg='gold')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)
    
# Username label and text entry box
usernameLabel = Label(tkWindow, text="User Name").place(x=0, y=150)
username = StringVar()
usernameEntry = Entry(tkWindow, textvariable=username).place(x=100, y=150)  

# Password label and password entry box
passwordLabel = Label(tkWindow,text="Password").place(x=0, y=200)
password = StringVar()
passwordEntry = Entry(tkWindow, textvariable=password, show='*').place(x=100, y=200)    

validateLogin = partial(validateLogin, username, password)

# Login button
loginButton = Button(tkWindow, text="Login", command=validateLogin).place(x=50, y=250)  

CloseButton = Button(tkWindow, text="Close", command=tkWindow.destroy).place(x=100, y=250) 

tkWindow.mainloop()

