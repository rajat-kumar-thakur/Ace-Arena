import json
import os
from Combo_box import Combobox
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.colorchooser import askcolor


DEFAULT_SETTINGS = {"movetype": "Drag",
                    "gamemode": "Practice Mode",
                    "canvas_default_item_hover_time": "300",
                    "default_cardsender_freeze_time": "600",
                    "show_footer": "True",
                    "show_header": "True",
                    "continuous_points": "True",
                    "card_back": "python_card_back",
                    "canvas_color": "#103b0a",
                    "larger_cards": "False"
                    }


class Settings(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)
        self.title("TkSolitaire Settings")
        self.resizable(False, False)
        self.config(background="#b0acac")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.custom_game_settings = None
        self.updated_settings = False

        self.wm_protocol("WM_DELETE_WINDOW", self.delete_window)

        try:
            self.settings = settings = json.load(open(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/settings.json"))
            movetype = settings["movetype"]
            gamemode = settings["gamemode"]
            if gamemode[0] == "Custom":
                self.custom_game_settings = gamemode
                gamemode = gamemode[0]
            canvas_default_item_hover_time = int(
                settings["canvas_default_item_hover_time"])
            default_cardsender_freeze_time = int(
                settings["default_cardsender_freeze_time"])
            show_footer = settings["show_footer"] == "True"
            show_header = settings["show_header"] == "True"
            continuous_points = settings["continuous_points"] == "True"
            card_back = settings["card_back"]
            canvas_color = settings["canvas_color"]
            larger_cards = settings["larger_cards"]
        except:
            with open((os.path.dirname(os.path.abspath(__file__)) + "/resources/settings.json"), "w") as handle:
                handle.write(str(DEFAULT_SETTINGS).replace("'", '"'))
            self.settings = settings = json.load(open(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/settings.json"))
            settings = json.load(open(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/settings.json"))
            movetype = settings["movetype"]
            gamemode = settings["gamemode"]
            canvas_default_item_hover_time = int(
                settings["canvas_default_item_hover_time"])
            default_cardsender_freeze_time = int(
                settings["default_cardsender_freeze_time"])
            show_footer = settings["show_footer"] == "True"
            show_header = settings["show_header"] == "True"
            continuous_points = settings["continuous_points"] == "True"
            card_back = settings["card_back"]
            canvas_color = settings["canvas_color"]
            larger_cards = settings["larger_cards"]

        self.movetype_chooser_var = tk.StringVar(value=movetype)
        self.gametype_chooser_var = tk.StringVar(value=gamemode)
        self.hovertime_scale_var = tk.IntVar(
            value=canvas_default_item_hover_time)
        self.cardsender_scale_var = tk.IntVar(
            value=default_cardsender_freeze_time)
        self.card_back_var = tk.StringVar(value=card_back)
        self.canvas_color_var = tk.StringVar(value=canvas_color)
        self.header_button_var = tk.BooleanVar(value=show_header)
        self.footer_button_var = tk.BooleanVar(value=show_footer)
        self.larger_cards_button_var = tk.BooleanVar(
            value=larger_cards)
        self.continuous_points_button_var = tk.BooleanVar(
            value=continuous_points)
        self.movetype_chooser_options = ["Drag", "Click", "Accessability Mode"]
        self.gametype_chooser_options = [
            "TkSolitaire Classic", "Vegas", "Practice Mode", "Custom"]

        self.create_widgets()
        self.config_widgets()
        self.grid_all()

        try:
            self.iconbitmap(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/icon.ico")
        except:
            icon = tk.PhotoImage(file=(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/icon.png"))
            self.tk.call('wm', 'iconphoto', self._w, icon)

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TScale", background="#b0acac")
        self.intro_label = tk.Label(self, text="TkSolitaire Settings", font=(
            "Calibri", 10, "normal"), bg="#b0acac", fg="grey")
        self.movetype_chooser = Combobox(self, self.movetype_chooser_options,
                                         {"height": 21, "width": 200, "bg": "#cccaca", "highlightbackground": "black",
                                          "highlightthickness": 1},
                                         {"textvariable": self.movetype_chooser_var, "anchor": "w",
                                          "padx": 2, "background": "#cccaca", "cursor": "arrow"},
                                         {"width": 10, "relief": "flat",
                                          "activebackground": "#b0b2bf", "bg": "#cccaca"},
                                         {"relief": "flat", "highlightbackground": "black", "highlightthickness": 1,
                                          "bg": "#d4d2d2"})
        self.gametype_chooser = Combobox(self, self.gametype_chooser_options,
                                         {"height": 21, "width": 200, "bg": "#cccaca", "highlightbackground": "black",
                                          "highlightthickness": 1},
                                         {"textvariable": self.gametype_chooser_var, "anchor": "w",
                                          "padx": 2, "background": "#cccaca", "cursor": "arrow"},
                                         {"width": 10, "relief": "flat",
                                          "activebackground": "#b0b2bf", "bg": "#cccaca"},
                                         {"relief": "flat", "highlightbackground": "black", "highlightthickness": 1,
                                          "bg": "#d4d2d2"})
        self.movetype_label = tk.Label(self,
                                       text="Move Type:", bg="#b0acac", fg="black")
        self.gametype_label = tk.Label(self,
                                       text="Game Type:", bg="#b0acac", fg="black")

        self.hovertime_scale = ttk.Scale(self, from_=0, to=2000, variable=self.hovertime_scale_var,
                                         value=self.hovertime_scale_var.get(), command=self.hovertime_scale_change)
        self.cardsender_scale = ttk.Scale(self, from_=0, to=2000, variable=self.cardsender_scale_var,
                                          value=self.cardsender_scale_var.get(), command=self.cardsender_scale_change)
        self.hovertime_entry = tk.Spinbox(self, from_=0, to=2000, increment=100, textvariable=self.hovertime_scale_var,
                                          relief="flat", highlightbackground="black",
                                          highlightthickness=1, bg="#cccaca", buttonbackground="#cccacc",
                                          disabledbackground="#cccaca", disabledforeground="grey")
        self.cardsender_entry = tk.Spinbox(self, from_=0, to=2000, increment=100,
                                           textvariable=self.cardsender_scale_var,
                                           relief="flat", highlightbackground="black", highlightthickness=1,
                                           bg="#cccaca", buttonbackground="#cccacc")
        self.hover_after_label = tk.Label(self,
                                          text="Auto click after:                 \n(Accessibility Mode only)",
                                          anchor="w", bg="#b0acac")
        self.card_stack_hover_after_label = tk.Label(self,
                                                     text="Game solver wait time:", bg="#b0acac")

        self.python_card_button = tk.Radiobutton(self, text="Python card", variable=self.card_back_var,
                                                 highlightthickness=0,
                                                 value="python_card_back", anchor="w", bg="#b0acac",
                                                 activebackground="#706c6c")
        self.traditional_card_button = tk.Radiobutton(self, text="Classic card", variable=self.card_back_var,
                                                      highlightthickness=0,
                                                      value="card_back", anchor="w", bg="#b0acac",
                                                      activebackground="#706c6c")
        self.larger_cards_button = tk.Checkbutton(self, highlightthickness=0,
                                                  text="Use larger cards   (will require game restart)",
                                                  variable=self.larger_cards_button_var, anchor="w", bg="#b0acac",
                                                  activebackground="#706c6c")

        self.color_entry_label = tk.Label(self,
                                          text="Canvas Background Color:", bg="#b0acac")
        self.color_entry = tk.Entry(self, textvariable=self.canvas_color_var, state='disabled', relief="flat",
                                    highlightbackground="black", highlightthickness=1,
                                    bg=self.canvas_color_var.get(), disabledbackground=self.canvas_color_var.get(),
                                    disabledforeground=self.generate_altered_colour(self.canvas_color_var.get()),
                                    cursor="arrow")

        self.continuous_points_button = tk.Checkbutton(self, highlightthickness=0,
                                                       text="Continuous Points (Vegas mode only)",
                                                       variable=self.continuous_points_button_var, anchor="w",
                                                       bg="#b0acac", activebackground="#706c6c")

        self.header_button = tk.Checkbutton(self,
                                            text="Show Header", variable=self.header_button_var, highlightthickness=0,
                                            anchor="w", bg="#b0acac", activebackground="#8ccc8d")
        self.footer_button = tk.Checkbutton(self,
                                            text="Show Footer", variable=self.footer_button_var, highlightthickness=0,
                                            anchor="w", bg="#b0acac", activebackground="#706c6c")
        self.save_button = tk.Button(self, text="Save", relief="solid", borderwidth=1,
                                     command=self.save, bg="#b0acac", activebackground="#706c6c")
        self.reset_button = tk.Button(self, text="Reset", relief="solid", borderwidth=1,
                                      command=self.reset_all, bg="#b0acac", activebackground="#706c6c")

    def config_widgets(self):
        self.movetype_chooser.bind(
            "<<ComboboxSelect>>", self.movetype_chooser_select)
        self.gametype_chooser.bind(
            "<<ComboboxSelect>>", self.gametype_chooser_select)

        self.hovertime_entry.config(validate="all", validatecommand=((self.register(
            lambda var, scale=self.hovertime_scale: self.validate_entry(var, scale))), "%P"))
        self.cardsender_entry.config(validate="all", validatecommand=((self.register(
            lambda var, scale=self.cardsender_scale: self.validate_entry(var, scale))), "%P"))

        if self.gametype_chooser_var.get() != "Vegas":
            self.continuous_points_button.config(state="disabled")
        else:
            self.continuous_points_button.bind("<Enter>", self.enter_button)
            self.continuous_points_button.bind("<Leave>", self.leave_button)
        if self.movetype_chooser_var.get() != "Accessability Mode":
            self.hovertime_scale.state(["disabled"])
            self.hovertime_entry.config(
                state="disabled", highlightbackground="grey")
            self.hover_after_label.config(state="disabled")

        self.python_card_button.bind("<Enter>", self.enter_button)
        self.traditional_card_button.bind("<Enter>", self.enter_button)
        self.larger_cards_button.bind("<Enter>", self.enter_button)
        self.header_button.bind("<Enter>", self.enter_button)
        self.footer_button.bind("<Enter>", self.enter_button)
        self.python_card_button.bind("<Leave>", self.leave_button)
        self.traditional_card_button.bind("<Leave>", self.leave_button)
        self.larger_cards_button.bind("<Leave>", self.leave_button)
        self.header_button.bind("<Leave>", self.leave_button)
        self.footer_button.bind("<Leave>", self.leave_button)
        self.save_button.bind("<Enter>", self.enter_button)
        self.reset_button.bind("<Enter>", self.enter_button)
        self.save_button.bind("<Leave>", self.leave_button)
        self.reset_button.bind("<Leave>", self.leave_button)

        self.color_entry.bind("<Button-1>", self.open_colorpicker)
        self.color_entry.bind("<Enter>", lambda event: self.color_entry.config(
            highlightbackground=self.color_entry["bg"]))
        self.color_entry.bind("<Leave>", self.leave_combo)

        self.hovertime_entry.bind("<Enter>", self.enter_entry)
        self.hovertime_entry.bind("<Leave>", self.leave_entry)
        self.cardsender_entry.bind("<Enter>", self.enter_entry)
        self.cardsender_entry.bind("<Leave>", self.leave_entry)

        self.movetype_chooser.bind("<Enter>", self.enter_combo)
        self.movetype_chooser.bind("<Leave>", self.leave_combo)
        self.gametype_chooser.bind("<Enter>", self.enter_combo)
        self.gametype_chooser.bind("<Leave>", self.leave_combo)

        self.last_gamemode = self.gametype_chooser_var.get()

    def enter_entry(self, event):
        if event.widget["state"] == "normal":
            event.widget.config(highlightbackground="grey")

    def leave_entry(self, event):
        if event.widget["state"] == "normal":
            event.widget.config(highlightbackground="black")

    def enter_combo(self, event):
        event.widget.config(highlightbackground="grey")

    def leave_combo(self, event):
        event.widget.config(highlightbackground="black")

    def grid_all(self):
        self.intro_label.grid(row=0, column=0, columnspan=4,
                              padx=8, pady=2, sticky="ew")
        tk.Label(self, text="Game:", font=("Calibri", 11, "bold"), bg="#b0acac", fg="blue").grid(
            row=1, column=0, columnspan=2, padx=8, pady=2, sticky="w")
        self.movetype_label.grid(
            row=2, column=0, columnspan=2, padx=8, pady=7, sticky="w")
        self.movetype_chooser.grid(
            row=2, column=1, columnspan=3, padx=8, pady=7, sticky="ew")
        self.gametype_label.grid(
            row=3, column=0, columnspan=2, padx=8, pady=7, sticky="w")
        self.gametype_chooser.grid(
            row=3, column=1, columnspan=3, padx=8, pady=7, sticky="ew")
        ttk.Separator(self).grid(row=4, column=0, columnspan=4,
                                 padx=6, pady=5, sticky="ew")
        tk.Label(self, text="Timing:", font=("Calibri", 11, "bold"), bg="#b0acac", fg="blue").grid(
            row=5, column=0, columnspan=2, padx=8, pady=2, sticky="w")
        self.hover_after_label.grid(
            row=6, column=0, padx=8, pady=7, sticky="w")
        self.hovertime_scale.grid(
            row=6, column=1, columnspan=2, padx=8, pady=7, sticky="ew")
        self.hovertime_entry.grid(row=6, column=3, padx=8, pady=7, sticky="ew")
        self.card_stack_hover_after_label.grid(
            row=7, column=0, columnspan=2, padx=8, pady=7, sticky="w")
        self.cardsender_scale.grid(
            row=7, column=1, columnspan=2, padx=8, pady=7, sticky="ew")
        self.cardsender_entry.grid(
            row=7, column=3, padx=8, pady=7, sticky="ew")
        ttk.Separator(self).grid(row=8, column=0, columnspan=4,
                                 padx=6, pady=5, sticky="ew")
        tk.Label(self, text="Cards:", font=("Calibri", 11, "bold"), bg="#b0acac", fg="blue").grid(
            row=9, column=0, columnspan=2, padx=8, pady=2, sticky="w")
        self.python_card_button.grid(
            row=10, column=0, columnspan=2, padx=8, pady=7, sticky="ew")
        self.traditional_card_button.grid(
            row=10, column=2, columnspan=2, padx=8, pady=7, sticky="ew")
        self.larger_cards_button.grid(
            row=11, column=0, columnspan=4, padx=8, pady=7, sticky="ew")
        ttk.Separator(self).grid(row=12, column=0,
                                 columnspan=4, padx=8, pady=5, sticky="ew")
        self.color_entry_label.grid(row=13, column=0,
                                    columnspan=2, padx=8, pady=5, sticky="w")
        self.color_entry.grid(row=13, column=2,
                              columnspan=2, padx=8, pady=5, sticky="ew")
        ttk.Separator(self).grid(row=14, column=0,
                                 columnspan=4, padx=8, pady=5, sticky="ew")
        self.continuous_points_button.grid(
            row=15, column=0, columnspan=4, padx=8, pady=7, sticky="ew")
        self.header_button.grid(
            row=16, column=0, columnspan=2, padx=8, pady=7, sticky="ew")
        self.footer_button.grid(
            row=16, column=2, columnspan=2, padx=8, pady=7, sticky="ew")
        ttk.Separator(self).grid(row=17, column=0,
                                 columnspan=4, padx=8, pady=5, sticky="ew")
        self.save_button.grid(row=18, column=3, padx=8, pady=7, sticky="ew")
        self.reset_button.grid(row=18, column=2, padx=8, pady=7, sticky="ew")

    def open_colorpicker(self, event):
        color = askcolor(parent=self, color=self.canvas_color_var.get(
        ), title="Choose canvas background color")[1]
        if color:
            self.canvas_color_var.set(color)
            self.color_entry.config(bg=color, disabledbackground=color,
                                    disabledforeground=self.generate_altered_colour(color))

    def generate_altered_colour(self, color):
        rgb = list(self.hex_to_rgb(color))
        rgb[0] = max(1, min(255, 240 - rgb[0]))
        rgb[1] = max(1, min(255, 240 - rgb[1]))
        rgb[2] = max(1, min(255, 240 - rgb[2]))
        return self.rgb_to_hex(*rgb)

    def hex_to_rgb(self, color):
        value = color.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def rgb_to_hex(self, red, green, blue):
        return '#%02x%02x%02x' % (red, green, blue)

    def reset_all(self):
        self.focus()
        self.movetype_chooser_var.set("Drag")
        self.gametype_chooser_var.set("TkSolitaire Classic")
        self.continuous_points_button.unbind("<Enter>")
        self.continuous_points_button.unbind("<Leave>")
        self.hovertime_scale.config(value=300)
        self.hovertime_scale.state(["disabled"])
        self.cardsender_scale.config(value=600)
        self.hovertime_scale_var.set(300)
        self.cardsender_scale_var.set(600)
        self.hovertime_entry.config(
            state="disabled", highlightbackground="grey")
        self.hover_after_label.config(state="disabled")
        self.continuous_points_button.config(state="disabled")
        self.continuous_points_button_var.set(True)
        self.canvas_color_var.set("#103b0a")
        self.color_entry.config(bg="#103b0a", disabledbackground="#103b0a")
        self.header_button_var.set(True)
        self.footer_button_var.set(True)
        self.larger_cards_button_var.set(False)
        self.card_back_var.set("python_card_back")
        self.last_gamemode = self.gametype_chooser_var.get()

    def red_bg(self, widget):
        widget.config(bg="red")
        widget.bind("<Key>", lambda event,
                                    widget=widget: self.normal_bg(event, widget))
        widget.bind("<Button-1>", lambda event,
                                         widget=widget: self.normal_bg(event, widget))

    def normal_bg(self, event, widget):
        widget.config(bg="#cccaca")
        widget.unbind("<Key>")
        widget.unbind("<Button-1>")

    def save(self):
        settings = {}
        settings["movetype"] = self.movetype_chooser_var.get()
        if self.gametype_chooser_var.get() == "Custom":
            settings["gamemode"] = self.custom_game_settings
        else:
            settings["gamemode"] = self.gametype_chooser_var.get()
        empty_entries = 0
        try:
            settings["canvas_default_item_hover_time"] = str(
                self.hovertime_scale_var.get())
        except:
            if self.hovertime_entry["state"] == 'normal':
                self.red_bg(self.hovertime_entry)
                empty_entries += 1
            else:
                self.hovertime_scale_var.set(0)
                settings["canvas_default_item_hover_time"] = str(
                    self.hovertime_scale_var.get())
        try:
            settings["default_cardsender_freeze_time"] = str(
                self.cardsender_scale_var.get())
        except:
            self.red_bg(self.cardsender_entry)
            empty_entries += 1
        if empty_entries > 0:
            return
        settings["show_footer"] = str(self.footer_button_var.get())
        settings["show_header"] = str(self.header_button_var.get())
        settings["continuous_points"] = str(
            self.continuous_points_button_var.get())
        settings["card_back"] = str(self.card_back_var.get())
        settings["canvas_color"] = str(self.canvas_color_var.get())
        settings["larger_cards"] = str(
            self.larger_cards_button_var.get())
        self.updated_settings = True
        with open((os.path.dirname(os.path.abspath(__file__)) + "/resources/settings.json"), "w") as handle:
            handle.write(str(settings).replace("'", '"'))
        self.event_generate("<<SettingsClose>>")
        self.destroy()

    def enter_button(self, event):
        event.widget.config(bg="#706c6c")

    def leave_button(self, event):
        event.widget.config(bg="#b0acac")

    def validate_entry(self, var, scale):
        if var == "":
            return True
        elif " " in var:
            return False
        else:
            try:
                int(var)
                return True
            except:
                return False

    def hovertime_scale_change(self, val):
        self.focus()
        self.hovertime_scale_var.set(round(self.hovertime_scale_var.get()))

    def cardsender_scale_change(self, val):
        self.focus()
        self.cardsender_scale_var.set(round(self.cardsender_scale_var.get()))

    def gametype_chooser_select(self, event):
        self.focus()
        if self.gametype_chooser_var.get() != "Vegas":
            self.continuous_points_button.config(state="disabled")
            self.continuous_points_button.unbind("<Enter>")
            self.continuous_points_button.unbind("<Leave>")
        else:
            self.continuous_points_button.config(state="normal")
            self.continuous_points_button.bind("<Enter>", self.enter_button)
            self.continuous_points_button.bind("<Leave>", self.leave_button)

    def update_custom(self, event, item):
        if item:
            self.custom_game_settings = item
            self.last_gamemode = self.gametype_chooser_var.get()
        else:
            self.gametype_chooser_var.set(self.last_gamemode)

    def movetype_chooser_select(self, event):
        self.focus()
        if self.movetype_chooser_var.get() == "Accessability Mode":
            self.hovertime_scale.state(["!disabled"])
            self.hovertime_entry.config(
                state="normal", highlightbackground="black")
            self.hover_after_label.config(state="normal")
        else:
            self.hovertime_scale.state(["disabled"])
            self.hovertime_entry.config(
                state="disabled", highlightbackground="grey")
            self.hover_after_label.config(state="disabled")

    def delete_window(self, *args):
        if not self.updated_settings:
            settings = {}
            settings["movetype"] = self.movetype_chooser_var.get()
            if self.gametype_chooser_var.get() == "Custom":
                settings["gamemode"] = self.custom_game_settings
            else:
                settings["gamemode"] = self.gametype_chooser_var.get()
            empty_entries = 0
            try:
                settings["canvas_default_item_hover_time"] = str(
                    self.hovertime_scale_var.get())
            except:
                if self.hovertime_entry["state"] == "normal":
                    self.red_bg(self.hovertime_entry)
                    empty_entries += 1
                else:
                    self.hovertime_scale_var.set(0)
                    settings["canvas_default_item_hover_time"] = str(
                        self.hovertime_scale_var.get())
            try:
                settings["default_cardsender_freeze_time"] = str(
                    self.cardsender_scale_var.get())
            except:
                self.red_bg(self.cardsender_entry)
                empty_entries += 1
            if empty_entries > 0:
                return

            settings["show_footer"] = str(self.footer_button_var.get())
            settings["show_header"] = str(self.header_button_var.get())
            settings["continuous_points"] = str(
                self.continuous_points_button_var.get())
            settings["canvas_color"] = str(self.canvas_color_var.get())
            settings["card_back"] = str(self.card_back_var.get())
            settings["larger_cards"] = str(
                self.larger_cards_button_var.get())
            if self.settings != settings:
                save = messagebox.askyesnocancel(
                    "Save Settings.", "You haven't saved your settings. Do you want to save them?", parent=self,
                    default="yes", icon="warning")
                if save:
                    with open((os.path.dirname(os.path.abspath(__file__)) + "/resources/settings.json"), "w") as handle:
                        handle.write(str(settings).replace("'", '"'))
                elif save is None:
                    return
        self.event_generate("<<SettingsClose>>")
        self.destroy()

