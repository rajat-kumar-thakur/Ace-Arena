from game_window import main
import os
from tkinter import *


root = Tk()
root.title("Ace-Arena")
root.iconbitmap(os.path.dirname(os.path.abspath(__file__)) + "/resources/icon.ico")

root.geometry("1000x563")
root.configure(bg="#FFFFFF")


canvas = Canvas(
    root,
    bg = "#FFFFFF",
    height = 563,
    width = 1000,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

def button_click():
    root.destroy()
    main()

def rules():
    new = Toplevel()
    new.title("Ace-Arena")
    new.iconbitmap(os.path.dirname(os.path.abspath(__file__)) + "/resources/icon.ico")

    new.geometry("1500x844")
    new.configure(bg="#FFFFFF")
    canvas = Canvas(
        new,
        bg="#FFFFFF",
        height=844,
        width=1500,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    image_image = PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/assets/frame0/image_2.png")
    image = canvas.create_image(
        750.0,
        422.0,
        image=image_image
    )

    new.resizable(False, False)
    new.mainloop()

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/assets/frame0/image_1.png")
image_1 = canvas.create_image(
    500.0,
    281.0,
    image=image_image_1
)

button_image_1 = PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/assets/frame0/button_1.png")
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=rules,
    relief="flat"
)
button_1.place(
    x=176.0,
    y=308.0,
    width=199.0,
    height=56.0
)

button_image_2 = PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/assets/frame0/button_2.png")
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=root.destroy,
    relief="flat"
)
button_2.place(
    x=183.0,
    y=415.0,
    width=184.0,
    height=56.0
)

button_image_3 = PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/assets/frame0/button_3.png")
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=button_click,
    relief="flat"
)
button_3.place(
    x=152.0,
    y=201.0,
    width=247.0,
    height=56.0
)
root.resizable(False, False)
root.mainloop()

