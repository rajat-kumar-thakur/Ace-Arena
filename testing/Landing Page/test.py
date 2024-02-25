import json
import os
import random

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.colorchooser import askcolor

from PIL import Image, ImageTk
from game_window import main
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Main Window")
        self.geometry("300x200")

        self.button = tk.Button(self, text="Open Second Window", command=self.open_second_window)
        self.button.pack()

    def open_second_window(self):
        main()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()