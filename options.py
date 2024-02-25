import tkinter as tk


class OptionBar(tk.Frame):
    def __init__(self, parent, invert=False, manager="pack", height=30, bg="#1c1a1a", fade_colors=None, **kwargs):
        tk.Frame.__init__(self, parent, height=height, bg=bg, **kwargs)
        try:
            self.colors = list(fade_colors)
        except:
            self.colors = ["#4f4f4f", "#484849", "#424142", "#3c3b3c", "#363435",
                           "#1f4f1d", "#1f561d", "#1f2c1d", "#1f3e1d", "#222020", "#1f1d1d", "#1c1a1a"]
        self.bg = bg
        self.fade(invert=invert, manager=manager)
        self.buffers = []

    def fade(self, invert, manager):
        if invert:
            if manager == "grid":
                tk.Frame(self, bg=self["bg"], height=3).grid(
                    row=0, column=0, columnspan=100, sticky="new")
                row = 1
                for color in reversed(self.colors):
                    tk.Frame(self, height=1, bg=color).grid(
                        row=row, column=0, columnspan=100, sticky="ew")
                    row += 1
            elif manager == "pack":
                for color in self.colors:
                    tk.Frame(self, height=1, bg=color).pack(
                        side="bottom", fill="both")
            else:
                raise Exception(
                    "OptionBar(invert=True) does not support manager '%s'. Try using grid or pack instead." % manager)
        else:
            if manager == "pack":
                for color in self.colors:
                    tk.Frame(self, height=1, bg=color).pack(
                        side="top", fill="both")
            else:
                raise Exception(
                    "OptionBar(invert=False) does not support manager '%s'. Try using pack instead." % manager)

    def add_buffer(self, width, **kwargs):
        new_label = tk.Label(self, bg=self.bg, width=width)
        new_label.grid(**kwargs)
        self.buffers.append(new_label)

    def clear_buffers(self):
        for i in self.buffers:
            i.grid_forget()
        self.buffers = []

