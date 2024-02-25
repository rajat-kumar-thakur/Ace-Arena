from ToolTip import ToolTip
import tkinter as tk

class HoverButton(tk.Button):
    def __init__(self, parent, movetype="Click", alt=None, ttjustify="left", ttbackground="#ffffe0", ttforeground="black", ttrelief="solid", ttborderwidth=0, ttfont=("tahoma", "8", "normal"), ttlocationinvert=False, ttheightinvert=False, **kwargs):
        self.command = kwargs.pop("command")
        self.clickedbackground = kwargs.pop("clickedbackground")
        tk.Label.__init__(self, parent, **kwargs)
        self.default_highlight = self["highlightbackground"]
        self.default_background = self["background"]
        self.text = alt
        self.parent = parent
        self.movetype = movetype
        self.job = None
        self.job2 = None
        self.on_button = False

        self.hover_time = 600
        self.auto_click_time = 1000

        if alt:
            self.tool_tip = ToolTip(self, ttjustify, ttbackground, ttforeground,
                                    ttrelief, ttborderwidth, ttfont, ttlocationinvert, ttheightinvert)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def cancel_jobs(self):
        if self.text:
            if self.job is not None:
                self.parent.after_cancel(self.job)
                self.job = None
            self.tool_tip.hidetip()
        if self.job2 is not None:
            self.parent.after_cancel(self.job2)
            self.job2 = None

    def on_click(self, event):
        if self["state"] == "normal":
            self.config(bg=self.clickedbackground)
            self.cancel_jobs()

    def on_release(self, event):
        if self["state"] == "normal":
            if self.on_button:
                self.parent.after(0, self.command)
                self.config(bg=self["activebackground"])
            else:
                self.config(bg=self.default_background)
            self.cancel_jobs()
            self.hover_time = 2600
            if self.text:
                self.job = self.parent.after(
                    self.hover_time, self.complete_enter)
            if (self.movetype == "Accessability Mode") and (self["state"] == "normal"):
                self.job2 = self.parent.after(
                    self.auto_click_time, self.run_command)
            self.hover_time = 600

    def on_enter(self, event):
        self.on_button = True
        self.cancel_jobs()
        if self["state"] == "normal":
            self.config(
                background=self["activebackground"], highlightbackground="black")
        if self.text:
            self.job = self.parent.after(self.hover_time, self.complete_enter)
        if (self.movetype == "Accessability Mode") and (self["state"] == "normal"):
            self.job2 = self.parent.after(
                self.auto_click_time, self.run_command)

    def run_command(self):
        self.parent.after(0, self.command)
        self.job2 = self.parent.after(self.auto_click_time, self.run_command)

    def complete_enter(self):
        self.after(600, self.begin_motion_binding)
        self.tool_tip.showtip(self.text)

    def begin_motion_binding(self):
        if self.on_button:
            self.bind("<Motion>", self.b1motion)

    def b1motion(self, event):
        self.unbind("<Motion>")
        if self.text:
            if self.job is not None:
                self.parent.after_cancel(self.job)
                self.job = None
            if self.job2 is not None:
                self.parent.after_cancel(self.job2)
                self.job2 = None
            self.tool_tip.hidetip()
            self.hover_time = 2600
            self.job = self.parent.after(self.hover_time, self.complete_enter)
            if (self.movetype == "Accessability Mode") and (self["state"] == "normal"):
                self.job2 = self.parent.after(
                    self.auto_click_time, self.run_command)
            self.hover_time = 600

    def on_leave(self, event):
        self.on_button = False
        self.reset()
        self.cancel_jobs()
        self.tool_tip.hidetip()

    def disable(self):
        self.reset()
        self.config(state="disabled")

    def reset(self):
        self.config(background=self.default_background,
                    highlightbackground=self.default_highlight)

    def change_command(self, command):
        self.command = command
