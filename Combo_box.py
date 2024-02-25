import os

import tkinter as tk


class Combobox(tk.Frame):
    def __init__(self, parent, values=[], frame_args={}, entry_args={}, label_args={}, listbox_args={},
                 replace_entry_with_label=True):
        tk.Frame.__init__(self, parent, **frame_args)

        self.parent = parent
        self.values = values
        self.listbox_args = listbox_args
        self.box_opened_count = False
        self.mouse_on_self = False
        self.box_opened = 0
        self.pack_propagate(0)
        self.label_image = tk.PhotoImage(
            file=(os.path.dirname(os.path.abspath(__file__)) + "/resources/arrow.png"))
        self.other_label_image = tk.PhotoImage(
            file=(os.path.dirname(os.path.abspath(__file__)) + "/resources/arrow_up.png"))
        try:
            self.textvariable = entry_args["textvariable"]
        except:
            self.textvariable = tk.StringVar()
            entry_args["textvariable"] = self.textvariable
        try:
            self.highlightthickness = entry_args["highlightthickness"]
        except:
            self.highlightthickness = 0
        if "image" in label_args:
            label_args.pop("image")
        if replace_entry_with_label:
            self.entry = entry = tk.Label(self, **entry_args)
        else:
            self.entry = entry = tk.Entry(self, **entry_args)
        entry.pack(side="left", expand=True, fill="both")

        self.entry.config(highlightthickness=self.highlightthickness)

        self.label = label = tk.Label(
            self, image=self.label_image, cursor="hand2", **label_args)
        label.pack(side="right", fill="both")

        try:
            activecolor = label_args.pop("activebackground")
            try:
                color = label_args["background"]
            except:
                try:
                    color = label_args["bg"]
                except:
                    color = "white"
            label.bind("<Enter>", lambda event,
                                         color=activecolor: self.label_hover(event, color))
            label.bind("<Leave>", lambda event,
                                         color=color: self.label_hover(event, color))
        except:
            pass

        divider = tk.Frame(self, width=1, bg="black")
        divider.pack(side="right", pady=4, fill="both")
        self.bind("<Button-1>", self.focusin, "+")
        self.label.bind("<Button-1>", self.focusin, "+")
        self.entry.bind("<Button-1>", self.focusin, "+")
        divider.bind("<Button-1>", self.focusin, "+")

        self.bind("<Enter>", self.on_self, "+")
        self.label.bind("<Enter>", self.on_self, "+")
        self.entry.bind("<Enter>", self.on_self, "+")
        divider.bind("<Enter>", self.on_self, "+")
        self.bind("<Leave>", self.off_self, "+")
        self.label.bind("<Leave>", self.off_self, "+")
        self.entry.bind("<Leave>", self.off_self, "+")
        divider.bind("<Leave>", self.off_self, "+")

        if os.name != "nt":
            self.parent.bind("<Button-1>", self.focusout, "+")

    def on_self(self, event):
        self.mouse_on_self = True

    def off_self(self, event):
        self.mouse_on_self = False

    def open_listbox(self, event):
        self.entry.config(highlightthickness=self.highlightthickness)

        if self.box_opened_count:
            if self.box_opened == 1:
                self.box_opened = 0
            else:
                self.delete_box()
                self.box_opened += 1
                return

        self.entry.update()
        self.label.update()
        loc_x = self.winfo_rootx()
        loc_y = self.entry.winfo_rooty() + self.winfo_height() - 2
        width = self.entry.winfo_width() + self.label.winfo_width() + 3
        self.box = box = tk.Toplevel(self.parent)
        box.wm_overrideredirect(1)
        self.listbox = listbox = tk.Listbox(box, **self.listbox_args)
        if os.name == "nt":
            height_increment = 17
        else:
            height_increment = 19
        height = 0
        for item in self.values:
            listbox.insert("end", item)
            height += height_increment
        listbox.pack(fill="both")
        listbox.config(width=0, height=0)
        box.wm_geometry("%dx%d+%d+%d" % (width, height, loc_x, loc_y))
        listbox.update()
        box.wm_geometry("%dx%d" % (width, listbox.winfo_height()))
        listbox.bind("<<ListboxSelect>>", self.listbox_select)
        listbox.bind("<Motion>", self.on_listbox_enter)
        self.label.config(image=self.other_label_image)
        self.box.focus_set()
        self.box.bind("<FocusOut>", self.window_move, "+")

    def focusin(self, event):
        self.open_listbox(event=event)
        self.box_opened_count = True

    def focusout(self, event):
        for item in self.winfo_children():
            if str(item) in str(event.widget):
                return
        try:
            self.delete_box()
        except:
            pass

    def window_move(self, event):
        if self.mouse_on_self:
            return
        try:
            self.delete_box()
        except:
            pass

    def label_hover(self, event, color):
        event.widget.config(background=color)

    def delete_box(self, event=None):
        self.box.unbind("<FocusOut>")
        self.label.config(image=self.label_image)
        self.box.destroy()
        self.box_opened_count = False

    def listbox_select(self, event):
        widget = event.widget
        try:
            index = widget.curselection()[0]
        except:
            return
        selected = widget.get(index)
        self.delete_box()
        self.textvariable.set(selected)
        self.event_generate("<<ComboboxSelect>>")

    def on_listbox_enter(self, event):
        index = event.widget.index("@%s,%s" % (event.x, event.y))
        event.widget.selection_clear(0, "end")
        event.widget.select_set(index)
