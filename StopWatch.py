import tkinter as tk


class Stopwatch(tk.Label):
    def __init__(self, parent, **kwargs):
        tk.Label.__init__(self, parent, text="Time: 00:00", **kwargs)
        self.value = 0
        self.job_id = None
        self.freeze_label = True

    def tick(self):
        self.value += 1
        if self.freeze_label:
            text = "Time: {:02d}:{:02d}".format(*divmod(self.value, 60))
            self.configure(text=text)
        if self.value > 0:
            self.job_id = self.after(1000, self.tick)

    def start(self, starting_value=0):
        if self.job_id is not None:
            return

        self.value = starting_value
        self.stop_requested = False
        self.after(1000, self.tick)

    def stop(self):
        self.after_cancel(self.job_id)
        self.value = 0
        self.job_id = None

    def freeze(self, value):
        self.freeze_label = value
        if self.freeze_label:
            text = "Time: {:02d}:{:02d}".format(*divmod(self.value, 60))
            self.configure(text=text)

