import tkinter as tk

class ToolTip:
    def __init__(self, widget, justify, background, foreground, relief, borderwidth, font, locationinvert, heightinvert):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        self.transition = 10

        self.justify = justify
        self.background = background
        self.foreground = foreground
        self.relief = relief
        self.borderwidth = borderwidth
        self.font = font
        self.locationinvert = locationinvert
        self.heightinvert = heightinvert

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text:
            return
        pos_x, pos_y, cx, cy = self.widget.bbox("insert")
        xoffset = 21
        if not self.locationinvert:
            pos_x = pos_x + self.widget.winfo_rootx() + xoffset
        else:
            pos_x = pos_x + self.widget.winfo_rootx() - xoffset*3
        if not self.heightinvert:
            pos_y = pos_y + cy + self.widget.winfo_rooty() + 40
        else:
            pos_y = pos_y + cy + self.widget.winfo_rooty() - 20
        self.tipwindow = tw = tk.Toplevel(self.widget, bg="#2e2b2b")
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (pos_x, pos_y))
        label = tk.Label(tw, text="  "+self.text+"  ", justify=self.justify, background=self.background,
                         foreground=self.foreground, relief=self.relief, borderwidth=self.borderwidth, font=self.font)
        label.pack(ipadx=1)
        tw.attributes("-alpha", 0)
        def fade_in():
            alpha = tw.attributes("-alpha")
            if alpha != 1:
                alpha += .1
                tw.attributes("-alpha", alpha)
                tw.after(self.transition, fade_in)
            else:
                tw.attributes("-alpha", 1)
        fade_in()

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        try:
            def fade_away():
                alpha = tw.attributes("-alpha")
                if alpha > 0:
                    alpha -= .1
                    tw.attributes("-alpha", alpha)
                    task = tw.after(self.transition, fade_away)
                else:
                    tw.destroy()
            if not tw.attributes("-alpha") in [0, 1]:
                tw.destroy()
            else:
                fade_away()
        except Exception as e:
            if tw:
                tw.destoy()
