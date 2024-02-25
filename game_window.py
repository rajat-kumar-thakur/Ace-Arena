from hover_button import HoverButton
from options import OptionBar
from Settings import Settings
from StopWatch import Stopwatch

import json
import os
import random

import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

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


class SolitareGameWindow(tk.Tk):
    def __init__(self, **kwargs):
        tk.Tk.__init__(self, **kwargs)

        try:
            self.attributes("-zoomed", True)
        except:
            self.state("zoomed")

        self.title("Ace-Arena")
        self.minsize(1370, 720)
        self.maxsize(1370, 720)
        self.resizable(False, False)

        solitaire_frame = SolitareGameFrame(self)
        solitaire_frame.pack(expand=True, fill="both")

        try:
            self.iconbitmap(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/icon.ico")
        except:
            icon = tk.PhotoImage(file=(os.path.dirname(
                os.path.abspath(__file__)) + "/resources/icon.png"))
            self.tk.call("wm", "iconphoto", self._w, icon)


class SolitareGameFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.bind_all("<Control-n>", self.new_game)
        # self.bind_all("<Control-r>", self.restart_game)
        self.bind_all("<Control-d>", lambda event: self.stack_onclick("deal_card_button"))
        self.bind_all("<Control-z>", self.undo_move)

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)

        self.card_drawing_count = 0
        self.cards_on_ace = 0
        self.parent = parent
        self.win_fullscreen = not parent.attributes("-fullscreen")
        self.card_moved_to_ace_by_sender = 0
        self.stock_left = 24
        self.redeals_left = 10
        self.larger_cards_pending = None
        self.last_active_card = ""
        self.card_stack_list = ""
        self.cards = []
        self.rect_images = []
        self.button_images = []
        self.dict_of_cards = {}
        self.card_back = None
        self.history = []
        self.redo = []
        self.game_started = False
        self.move_flag = False
        self.job = None
        self.win = None

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        try:
            self.load_settings()
        except:
            with open("resources/settings.json", "w") as handle:
                handle.write(str(DEFAULT_SETTINGS).replace("'", '"'))
            self.load_settings()

        self.load_images()
        self.shuffle_cards()
        self.draw_card_slots()
        self.generate_card_position()
        self.draw_remaining_cards()
        self.create_widgets()

    def load_settings(self, ignore_scaled_cards_prefix=False):
        settings = json.load(open("resources/settings.json"))
        self.movetype = settings["movetype"]
        self.gamemode = settings["gamemode"]

        self.canvas_default_item_hover_time = int(
            settings["canvas_default_item_hover_time"])
        self.default_cardsender_freeze_time = int(
            settings["default_cardsender_freeze_time"])
        self.show_footer = settings["show_footer"] == "True"
        self.show_header = settings["show_header"] == "True"
        self.continuous_points = settings["continuous_points"] == "True"
        self.larger_cards = settings["larger_cards"] == "True"

        self.canvas.config(bg=settings["canvas_color"])

        self.restart_game_button_enabled = True
        self.undo_last_move_button_enabled = True
        # self.redo_last_move_button_enabled = True
        self.show_stopwatch = True
        self.starting_points = 0
        self.point_increment = 10

        if not ignore_scaled_cards_prefix:
            if self.larger_cards:
                self.scaled_cards_prefix = "scaled_"
            else:
                self.scaled_cards_prefix = ""

        self.back_of_card_file = os.path.join("resources", self.scaled_cards_prefix + settings["card_back"] + ".png")
        self.card_back = settings["card_back"]

        if self.gamemode[0] == "Custom":
            self.restart_game_button_enabled = self.gamemode[1] == "True"
            self.undo_last_move_button_enabled = self.gamemode[2] == "True"
            self.redo_last_move_button_enabled = self.undo_last_move_button_enabled
            self.show_stopwatch = self.gamemode[4] == "True"
            self.starting_points = int(self.gamemode[5])
            self.point_increment = int(self.gamemode[6])
            self.total_redeals = self.gamemode[7]
            if self.total_redeals != "unlimited":
                self.total_redeals = int(self.total_redeals)
            self.gamemode = self.gamemode[0]
            self.continuous_points = False
        elif self.gamemode == "TkSolitaire Classic":
            self.total_redeals = 3
            self.continuous_points = False
        elif self.gamemode == "Vegas":
            self.total_redeals = 1
            self.restart_game_button_enabled = False
            self.undo_last_move_button_enabled = False
            self.redo_last_move_button_enabled = False
            self.starting_points = -52
        elif self.gamemode == "Practice Mode":
            self.total_redeals = "unlimited"
            self.show_stopwatch = False
            self.point_increment = 1
            self.refresh_points_after_game = True
            self.continuous_points = False

        self.canvas_item_hover_time = self.canvas_default_item_hover_time

    def create_widgets(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.header = header = OptionBar(self, invert=True, manager="grid")
        button_settings = {"movetype": self.movetype, "ttbackground": "#1c1c1b", "ttforeground": "white", "ttfont": (
            "Verdana", "10", "normal"), "relief": "flat", "bg": "#1c1a1a", "activebackground": "#4f4a4a",
                           "highlightbackground": "#1c1a1a", "clickedbackground": "#2e2b2b"}
        self.new_game_button = new_game_button = HoverButton(
            header, alt="Start a new game (Ctrl+N)", command=self.new_game,
            image=self.convert_pictures("new_game.png", main=False), **button_settings)
        self.restart_game_button = restart_game_button = HoverButton(
            header, alt="Restart game (Ctrl+R)", command=self.restart_game, state="disabled",
            image=self.convert_pictures("restart_game.png", main=False), **button_settings)
        self.deal_next_card_button = deal_next_card_button = HoverButton(header, alt="Deal next card (Ctrl+D)",
                                                                         command=lambda
                                                                             event="deal_card_button": self.stack_onclick(
                                                                             event),
                                                                         image=self.convert_pictures("deal.png",
                                                                                                     main=False),
                                                                         **button_settings)
        self.undo_last_move_button = undo_last_move_button = HoverButton(
            header, alt="Undo last Move (Ctrl+Z)", command=self.undo_move, state="disabled",
            image=self.convert_pictures("undo.png", main=False), **button_settings)
        self.redo_last_move_button = redo_last_move_button = HoverButton(
            header, alt="Redo last Move (Ctrl+Shift+Z)", command=self.redo_move, state="disabled",
            image=self.convert_pictures("redo.png", main=False), **button_settings)
        self.send_cards_up_button = send_cards_up_button = HoverButton(
            header, alt="Send Cards to Aces (F5)", command=self.send_cards_up,
            image=self.convert_pictures("ol.png", main=False), **button_settings)
        self.settings_button = settings_button = HoverButton(
            header, alt="Settings (F1)", command=self.open_settings,
            image=self.convert_pictures("settings.png", main=False), **button_settings)
        self.fullscreen_button = fullscreen_button = HoverButton(header, alt="Fullscreen (F11)",
                                                                 command=self.fullscreen, image=self.convert_pictures(
                "fullscreen.png", main=False), ttlocationinvert=True, **button_settings)

        header.columnconfigure(12, weight=1)

        new_game_button.grid(row=1, column=0, padx=6, pady=1)
        # if self.restart_game_button_enabled:
        #   restart_game_button.grid(row=1, column=1, padx=6, pady=1)
        header.add_buffer(width=4, row=1, column=2)
        deal_next_card_button.grid(row=1, column=3, padx=6, pady=1)

        header.add_buffer(width=3, row=1, column=4)

        if self.undo_last_move_button_enabled:
            undo_last_move_button.grid(row=1, column=5, padx=6, pady=1)
        # if self.redo_last_move_button_enabled:
        #   redo_last_move_button.grid(row=1, column=6, padx=6, pady=1)
        header.add_buffer(width=3, row=1, column=7)

        # send_cards_up_button.grid(row=1, column=9, padx=6, pady=1)
        header.add_buffer(width=4, row=1, column=10)
        # settings_button.grid(row=1, column=11, padx=6, pady=1)
        # fullscreen_button.grid(row=1, column=12, padx=16, pady=1, sticky="e")

        self.headerless_settings_button = headerless_settings_button = HoverButton(self.canvas, movetype=self.movetype,
                                                                                   alt="Settings", ttheightinvert=True,
                                                                                   ttbackground="#8ccc8d",
                                                                                   ttforeground="white",
                                                                                   ttfont=("Verdana", "10", "normal"),
                                                                                   bg=self.canvas["bg"],
                                                                                   activebackground=self.generate_altered_colour(
                                                                                       self.canvas["bg"]),
                                                                                   highlightbackground="#103b0a",
                                                                                   clickedbackground=self.generate_altered_colour(
                                                                                       self.canvas["bg"]),
                                                                                   command=self.open_settings,
                                                                                   relief="flat",
                                                                                   image=self.convert_pictures(
                                                                                       "settings.png", main=False))

        if self.show_header:
            header.grid(row=0, column=0, columnspan=100, sticky="ew")
        else:
            self.canvas.rowconfigure(1, weight=1)
            headerless_settings_button.grid(row=1, sticky="sw")
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.footer = footer = OptionBar(self)
        self.points_label = tk.Label(
            footer, text="Points: %s" % self.starting_points, fg="white", bg="#1c1a1a")
        self.stopwatch = stopwatch = Stopwatch(
            footer, fg="white", bg="#1c1a1a")
        if self.total_redeals != "unlimited":
            self.redeal_label = tk.Label(footer, text="Redeals left: " + str(
                max(0, self.total_redeals + self.redeals_left - 1)), fg="white", bg="#1c1a1a")
        else:
            self.redeal_label = tk.Label(
                footer, text="", fg="white", bg="#1c1a1a")
        self.stock_label = tk.Label(
            footer, text="Stock left: " + str(self.stock_left), fg="white", bg="#1c1a1a")
        self.tribute = tk.Label(
            footer, text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj", fg="white", bg="#1c1a1a")
        if self.show_footer:
            footer.grid(row=2, column=0, sticky="ew")

        self.points_label.pack(side="right", padx=6, pady=4)
        if self.show_stopwatch:
            stopwatch.pack(side="right", padx=6, pady=4)

    def open_settings(self, *args):
        if self.move_flag:
            return
        self.settings = settings = Settings(self)
        # settings.grab_set()
        settings.bind("<<SettingsClose>>", self.continue_settings)

    def fullscreen(self, event=None):
        self.parent.attributes(
            "-fullscreen", not self.parent.attributes("-fullscreen"))

        if self.win_fullscreen:
            self.fullscreen_button.config(
                image=self.convert_pictures("unfullscreen.png", main=False))
            self.win_fullscreen = False
        else:
            self.fullscreen_button.config(
                image=self.convert_pictures("fullscreen.png", main=False))
            self.win_fullscreen = True

    def continue_settings(self, *args):
        previous_movetype = self.movetype
        previous_larger_cards = self.larger_cards
        self.canvas.tag_unbind("card_below_rect", "<Enter>")
        self.canvas.tag_unbind("rect", "<Enter>")
        self.canvas.tag_unbind("rect", "<Leave>")
        self.canvas.tag_unbind("rect", "<Button-1>")
        self.canvas.delete("rect")
        self.last_active_card = ""
        self.card_stack_list = ""

        self.load_settings(ignore_scaled_cards_prefix=True)

        self.update_idletasks()

        back_of_card = Image.open(self.back_of_card_file)
        self.back_of_card = (ImageTk.PhotoImage(back_of_card))
        self.canvas.itemconfig("face_down", image=self.back_of_card)

        self.restart_game_button.movetype = self.movetype
        self.undo_last_move_button.movetype = self.movetype
        self.redo_last_move_button.movetype = self.movetype
        self.send_cards_up_button.movetype = self.movetype
        self.new_game_button.movetype = self.movetype
        self.deal_next_card_button.movetype = self.movetype
        self.settings_button.movetype = self.movetype
        self.fullscreen_button.movetype = self.movetype
        self.headerless_settings_button.movetype = self.movetype

        if self.restart_game_button_enabled:
            if not self.restart_game_button.winfo_ismapped():
                self.restart_game_button.grid(row=1, column=1, padx=6, pady=1)
        else:
            self.restart_game_button.grid_forget()

        if self.undo_last_move_button_enabled:
            if not self.undo_last_move_button.winfo_ismapped():
                self.undo_last_move_button.grid(
                    row=1, column=5, padx=6, pady=1)
        else:
            self.undo_last_move_button.grid_forget()

        if self.redo_last_move_button_enabled:
            if not self.redo_last_move_button.winfo_ismapped():
                self.redo_last_move_button.grid(
                    row=1, column=6, padx=6, pady=1)
        else:
            self.redo_last_move_button.grid_forget()

        self.points_label.pack_forget()
        self.stopwatch.pack_forget()
        self.redeal_label.pack_forget()
        self.stock_label.pack_forget()
        self.tribute.pack_forget()

        if self.show_footer:
            if not self.footer.winfo_ismapped():
                self.update_idletasks()
                self.footer.grid(row=2, column=0, sticky="ew")
        else:
            self.footer.grid_forget()
        self.points_label["text"] = (
                "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
        self.points_label.pack(side="right", padx=6, pady=4)
        if self.show_stopwatch:
            self.stopwatch.pack(side="right", padx=6, pady=4)
        if self.total_redeals != "unlimited":
            self.redeal_label.config(
                text="Redeals left: " + str(max(0, self.total_redeals + self.redeals_left - 1)))
            if self.game_started:
                self.redeal_label.pack(side="left", padx=6, pady=4)
        if self.game_started:
            self.stock_label.pack(side="left", padx=6, pady=4)
            self.tribute.pack(side="right", padx=6, pady=4)

        self.headerless_settings_button.grid_forget()
        if self.show_header:
            if not self.header.winfo_ismapped():
                self.update_idletasks()
                self.header.grid(row=0, column=0, columnspan=100, sticky="ew")
        else:
            self.header.grid_forget()
            self.canvas.rowconfigure(1, weight=1)
            self.headerless_settings_button.config(bg=self.canvas["bg"])
            self.headerless_settings_button.default_background = self.canvas["bg"]
            self.headerless_settings_button["activebackground"] = self.generate_altered_colour(
                self.canvas["bg"])
            self.canvas.update_idletasks()
            self.headerless_settings_button.grid(row=1, sticky="sw")

        if self.movetype != previous_movetype:
            for card in self.canvas.find_withtag("face_up"):
                card_tag = self.canvas.gettags(card)[0]
                self.canvas.tag_unbind(card_tag, "<Button-1>")
                self.canvas.tag_unbind(card_tag, "<Button1-Motion>")
                self.canvas.tag_unbind(card_tag, "<ButtonRelease-1>")
                self.canvas.tag_unbind(card_tag, "<Enter>")
                self.canvas.tag_unbind(card_tag, "<Leave>")
                if self.movetype == "Accessability Mode":
                    self.canvas.tag_bind(card_tag, "<Enter>", self.enter_card)
                    self.canvas.tag_bind(card_tag, "<Leave>", self.leave_hover)
                    self.canvas.tag_bind(
                        card_tag, "<Button-1>", self.card_onclick)
                elif self.movetype == "Click":
                    self.canvas.tag_bind(
                        card_tag, "<Button-1>", self.card_onclick)
                else:
                    self.canvas.tag_bind(
                        card_tag, "<Button-1>", self.end_onclick)
                    self.canvas.tag_bind(
                        card_tag, "<Button1-Motion>", self.move_card)
                    self.canvas.tag_bind(
                        card_tag, "<ButtonRelease-1>", self.drop_card)
                    self.canvas.tag_bind(
                        card_tag, "<Enter>", self.on_draggable_card)
                    self.canvas.tag_bind(
                        card_tag, "<Leave>", self.leave_draggable_card)

            for card in self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slot")):
                card_tag = self.canvas.gettags(card)[0]
                if card_tag == "empty_cardstack_slot":
                    continue
                else:
                    if self.movetype == "Accessability Mode":
                        self.canvas.tag_bind(
                            card_tag, "<Enter>", self.enter_stack)
                        self.canvas.tag_bind(
                            card_tag, "<Leave>", self.leave_hover)
                    else:
                        self.canvas.tag_unbind(card_tag, "<Enter>")
                        self.canvas.tag_unbind(card_tag, "<Leave>")

            self.canvas.tag_unbind("empty_slot", "<Enter>")
            self.canvas.tag_unbind("empty_ace_slot", "<Enter>")
            self.canvas.tag_unbind("empty_cardstack_slot", "<Enter>")
            self.canvas.tag_unbind("empty_slot", "<Leave>")
            self.canvas.tag_unbind("empty_ace_slot", "<Leave>")
            self.canvas.tag_unbind("empty_cardstack_slot", "<Leave>")
            self.canvas.tag_unbind("empty_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_ace_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_cardstack_slot", "<Button-1>")

            self.canvas.tag_unbind("empty_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_ace_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_cardstack_slot", "<Button-1>")

            self.canvas.tag_unbind("empty_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_ace_slot", "<Button-1>")
            self.canvas.tag_unbind("empty_slot", "<Button1-Motion>")
            self.canvas.tag_unbind("empty_slot", "<ButtonRelease-1>")
            self.canvas.tag_unbind("empty_ace_slot", "<Button1-Motion>")
            self.canvas.tag_unbind("empty_ace_slot", "<ButtonRelease-1>")
            self.canvas.tag_unbind("empty_cardstack_slot", "<Button-1>")

            if self.movetype == "Accessability Mode":
                self.canvas.tag_bind("empty_slot", "<Enter>", self.enter_card)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Enter>", self.enter_card)
                self.canvas.tag_bind("empty_cardstack_slot",
                                     "<Enter>", self.enter_refill)
                self.canvas.tag_bind("empty_slot", "<Leave>", self.leave_hover)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Leave>", self.leave_hover)
                self.canvas.tag_bind("empty_cardstack_slot",
                                     "<Leave>", self.leave_hover)
                self.canvas.tag_bind(
                    "empty_slot", "<Button-1>", self.card_onclick)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Button-1>", self.card_onclick)
                self.canvas.tag_bind("empty_cardstack_slot",
                                     "<Button-1>", self.refill_card_stack)
            elif self.movetype == "Click":
                self.canvas.tag_bind(
                    "empty_slot", "<Button-1>", self.card_onclick)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Button-1>", self.card_onclick)
                self.canvas.tag_bind("empty_cardstack_slot",
                                     "<Button-1>", self.refill_card_stack)
            else:
                self.canvas.tag_bind(
                    "empty_slot", "<Button-1>", self.end_onclick)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Button-1>", self.end_onclick)
                self.canvas.tag_bind(
                    "empty_slot", "<Button1-Motion>", self.move_card)
                self.canvas.tag_bind(
                    "empty_slot", "<ButtonRelease-1>", self.drop_card)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<Button1-Motion>", self.move_card)
                self.canvas.tag_bind(
                    "empty_ace_slot", "<ButtonRelease-1>", self.drop_card)
                self.canvas.tag_bind("empty_cardstack_slot",
                                     "<Button-1>", self.refill_card_stack)
        ret = False
        if self.total_redeals != "unlimited":
            if self.stock_left <= 1 and (self.total_redeals + self.redeals_left - 1) == 0:
                self.deal_next_card_button.disable()
                ret = True
            else:
                self.deal_next_card_button.config(state="normal")
        else:
            self.deal_next_card_button.config(state="normal")

        if not ret:
            if self.stock_left == 0:
                self.deal_next_card_button.change_command(
                    lambda event=None: self.refill_card_stack(event))
            else:
                self.deal_next_card_button.change_command(
                    lambda event="deal_card_button": self.stack_onclick(event))
        self.compare_cardset(previous_larger_cards)

    def compare_cardset(self, previous_larger_cards):
        if not os.path.isdir("resources/scaled_cards"):
            self.create_scaled_images()
        if not previous_larger_cards and self.larger_cards:
            self.larger_cards_pending = self.larger_cards
            self.larger_cards = previous_larger_cards
            restart_game = messagebox.askquestion(
                "Restart game",
                "In order to use the larger card set, you must restart your game. Do you want to restart now?",
                icon="warning")
            if restart_game == "yes":
                self.restart_game()
        elif previous_larger_cards and not self.larger_cards:
            self.larger_cards_pending = self.larger_cards
            self.larger_cards = previous_larger_cards
            restart_game = messagebox.askquestion(
                "Restart game",
                "In order to use the regular card set, you must restart your game. Do you want to restart now?",
                icon="warning")
            if restart_game == "yes":
                self.restart_game()

    def generate_altered_colour(self, color):
        rgb = list(self.hex_to_rgb(color))
        if rgb[0] > 200:
            rgb[0] = round(((rgb[0])) * 1 / 2)
        else:
            rgb[0] = round(min(255, 10 + rgb[0] * 2))
        if rgb[1] > 130:
            rgb[1] = round((rgb[1]) * 1 / 2)
        else:
            rgb[1] = round(min(255, 10 + rgb[1] * 2))
        if rgb[2] > 130:
            rgb[2] = round((rgb[2]) * 1 / 2)
        else:
            rgb[2] = round(min(255, 10 + rgb[2] * 2))
        return self.rgb_to_hex(*rgb)

    def hex_to_rgb(self, color):
        value = color.lstrip("#")
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def rgb_to_hex(self, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)

    def create_scaled_images(self):
        path = os.path.join("resources", "scaled_cards")
        try:
            os.mkdir(path)
        except:
            pass
        suits = ["clubs", "diamonds", "spades", "hearts"]
        ranks = ["ace", "2", "3", "4", "5", "6", "7",
                 "8", "9", "10", "jack", "queen", "king"]
        for suit in suits:
            for rank in ranks:
                name_of_old_image = os.path.join(
                    "resources", "cards", "{}_of_{}.png".format(rank, suit))
                name_of_image = os.path.join(
                    "resources", "scaled_cards", "{}_of_{}.png".format(rank, suit))
                im = Image.open(name_of_old_image)
                resized_img = im.resize((100, 130), Image.ANTIALIAS)
                resized_img.save(name_of_image, 'PNG', quality=90)

        im = Image.open("resources/card_back.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_card_back.png", 'PNG', quality=90)
        im = Image.open("resources/python_card_back.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_python_card_back.png", 'PNG', quality=90)
        im = Image.open("resources/ace_of_clubs_slot.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_ace_of_clubs_slot.png", 'PNG', quality=90)
        im = Image.open("resources/ace_of_spades_slot.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_ace_of_spades_slot.png", 'PNG', quality=90)
        im = Image.open("resources/ace_of_hearts_slot.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_ace_of_hearts_slot.png", 'PNG', quality=90)
        im = Image.open("resources/ace_of_diamonds_slot.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_ace_of_diamonds_slot.png", 'PNG', quality=90)
        im = Image.open("resources/empty_slot.png")
        resized_img = im.resize((100, 130), Image.ANTIALIAS)
        resized_img.save("resources/scaled_empty_slot.png", 'PNG', quality=90)

    def load_images(self):
        card_dir = "cards"
        if self.larger_cards:
            card_dir = "scaled_cards"
            if not os.path.isdir("resources/scaled_cards"):
                self.create_scaled_images()

        suits = ["clubs", "diamonds", "spades", "hearts"]
        ranks = ["ace", "2", "3", "4", "5", "6", "7",
                 "8", "9", "10", "jack", "queen", "king"]

        for suit in suits:
            for rank in ranks:
                name_of_image = os.path.join(
                    "resources", card_dir, "{}_of_{}.png".format(rank, suit))
                image = Image.open(name_of_image)
                self.cards.append("{}_of_{}".format(rank, suit))
                self.dict_of_cards[("{}_of_{}".format(rank, suit))] = (
                    ImageTk.PhotoImage(image))
        back_of_card = Image.open(self.back_of_card_file)
        self.back_of_card = (ImageTk.PhotoImage(back_of_card))

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def generate_card_position(self):
        rows = 7
        column = 0

        for i in range(rows):
            for e in range(column):
                self.draw_down_cards((i + 1), (e + 1))
            column += 1
            self.draw_up_cards((i + 1), (column))

    def draw_up_cards(self, row, col):
        card_tag = str(self.cards[self.card_drawing_count])
        card_image = self.dict_of_cards[self.cards[self.card_drawing_count]]
        if self.larger_cards:
            self.canvas.create_image(
                165 + row * 130, col * 20, image=card_image, tag=(card_tag, "face_up"), anchor=tk.NW)
        else:
            self.canvas.create_image(
                195 + row * 110, col * 20, image=card_image, tag=(card_tag, "face_up"), anchor=tk.NW)
        if self.movetype == "Accessability Mode":
            self.canvas.tag_bind(card_tag, "<Enter>", self.enter_card)
            self.canvas.tag_bind(card_tag, "<Leave>", self.leave_hover)
            self.canvas.tag_bind(card_tag, "<Button-1>", self.card_onclick)
        elif self.movetype == "Click":
            self.canvas.tag_bind(card_tag, "<Button-1>", self.card_onclick)
        else:
            self.canvas.tag_bind(card_tag, "<Button-1>", self.end_onclick)
            self.canvas.tag_bind(card_tag, "<Button1-Motion>", self.move_card)
            self.canvas.tag_bind(card_tag, "<ButtonRelease-1>", self.drop_card)
            self.canvas.tag_bind(card_tag, "<Enter>", self.on_draggable_card)
            self.canvas.tag_bind(card_tag, "<Leave>",
                                 self.leave_draggable_card)
        self.card_drawing_count += 1

    def draw_down_cards(self, row, col):
        card_tag = str(self.cards[self.card_drawing_count])
        self.canvas.tag_unbind(card_tag, "<Button-1>")
        self.canvas.tag_unbind(card_tag, "<Button1-Motion>")
        self.canvas.tag_unbind(card_tag, "<ButtonRelease-1>")
        self.canvas.tag_unbind(card_tag, "<Enter>")
        self.canvas.tag_unbind(card_tag, "<Leave>")
        if self.larger_cards:
            self.canvas.create_image(
                165 + row * 130, col * 20, image=self.back_of_card, tag=(card_tag, "face_down"), anchor=tk.NW)
        else:
            self.canvas.create_image(
                195 + row * 110, col * 20, image=self.back_of_card, tag=(card_tag, "face_down"), anchor=tk.NW)
        self.card_drawing_count += 1

    def draw_remaining_cards(self):
        remaining_cards = 52 - self.card_drawing_count
        for i in range(remaining_cards):
            card_tag = str(self.cards[self.card_drawing_count])
            self.canvas.tag_unbind(card_tag, "<Enter>")
            self.canvas.tag_unbind(card_tag, "<Leave>")
            self.canvas.create_image(20, 20, image=self.back_of_card, tag=(
                card_tag, "face_down"), anchor=tk.NW)
            if self.movetype == "Accessability Mode":
                self.canvas.tag_bind(card_tag, "<Enter>", self.enter_stack)
                self.canvas.tag_bind(card_tag, "<Leave>", self.leave_hover)
                self.canvas.tag_bind(
                    card_tag, "<Button-1>", self.stack_onclick)
            else:
                self.canvas.tag_bind(
                    card_tag, "<Button-1>", self.stack_onclick)
            self.card_drawing_count += 1

    def create_round_rectangle(self, x1, y1, x2, y2, r=17, **kwargs):
        points = (
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r, x2,
        y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1,
        y1)
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def convert_pictures(self, url, main=True):
        picture = Image.open(os.path.join("resources", url))
        picture = (ImageTk.PhotoImage(picture))
        if main:
            self.canvas.images.append(picture)
        else:
            self.button_images.append(picture)
        return picture

    def self_configure(self, event, width=None):
        # adjust locations of ace slots for desktops with taskbars on side of screen
        self.aces_adjusted = False
        if width:
            width_offset = width
        else:
            width_offset = event.width

        aces = list(self.canvas.find_withtag("empty_ace_slot"))
        aces.sort()
        if width_offset < 1350:
            if not self.aces_moved:
                self.aces_moved = True
                self.aces_adjusted = True
                for item in aces:
                    for card in self.canvas.find_overlapping(*self.canvas.bbox(item)):
                        self.canvas.move(card, -60, 0)
        if width_offset >= 1350:
            if self.aces_moved:
                self.aces_adjusted = False
                for item in reversed(aces):
                    for card in self.canvas.find_overlapping(*self.canvas.bbox(item)):
                        self.canvas.move(card, 60, 0)
                self.aces_moved = False

    def draw_card_slots(self):
        self.aces_moved = False
        self.canvas.images = list()
        if not self.larger_cards:
            positions_of_main_rects = [
                (305, 20), (415, 20), (525, 20), (635, 20), (745, 20), (855, 20), (965, 20)]
        else:
            positions_of_main_rects = [
                (295, 20), (425, 20), (555, 20), (685, 20), (815, 20), (945, 20), (1075, 20)]

        self.empty_slot = empty_slot = self.convert_pictures(self.scaled_cards_prefix + "empty_slot.png")
        for item in positions_of_main_rects:
            self.canvas.create_image(
                *item, image=empty_slot, tag=("empty_slot"), anchor=tk.NW)

        if not self.larger_cards:
            self.canvas.create_image(1170, 20, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                           "ace_of_spades_slot.png"),
                                     tag=("spades", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1270, 20, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                           "ace_of_hearts_slot.png"),
                                     tag=("hearts", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1170, 140, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                            "ace_of_clubs_slot.png"),
                                     tag=("clubs", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1270, 140, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                            "ace_of_diamonds_slot.png"),
                                     tag=("diamonds", "empty_ace_slot"), anchor=tk.NW)

            self.create_round_rectangle(
                22, 22, 98, 118, width=2, fill="#124f09", outline="#207c12", tag="empty_cardstack_slot")
            self.create_round_rectangle(
                122, 22, 198, 118, width=2, fill="#124f09", outline="#207c12", tag="empty_cardstack_slotb")
        else:
            self.canvas.create_image(1250, 20, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                           "ace_of_spades_slot.png"),
                                     tag=("spades", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1250, 170, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                            "ace_of_hearts_slot.png"),
                                     tag=("hearts", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1250, 320, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                            "ace_of_clubs_slot.png"),
                                     tag=("clubs", "empty_ace_slot"), anchor=tk.NW)
            self.canvas.create_image(1250, 470, image=self.convert_pictures(self.scaled_cards_prefix +
                                                                            "ace_of_diamonds_slot.png"),
                                     tag=("diamonds", "empty_ace_slot"), anchor=tk.NW)

            self.create_round_rectangle(
                22, 22, 118, 148, width=3, fill="#124f09", outline="#207c12", tag="empty_cardstack_slot")
            self.create_round_rectangle(
                136, 22, 233, 148, width=3, fill="#124f09", outline="#207c12", tag="empty_cardstack_slotb")

        if self.movetype == "Accessability Mode":
            self.canvas.tag_bind("empty_slot", "<Enter>", self.enter_card)
            self.canvas.tag_bind("empty_ace_slot", "<Enter>", self.enter_card)
            self.canvas.tag_bind("empty_cardstack_slot",
                                 "<Enter>", self.enter_refill)
            self.canvas.tag_bind("empty_slot", "<Leave>", self.leave_hover)
            self.canvas.tag_bind("empty_ace_slot", "<Leave>", self.leave_hover)
            self.canvas.tag_bind("empty_cardstack_slot",
                                 "<Leave>", self.leave_hover)
            self.canvas.tag_bind("empty_slot", "<Button-1>", self.card_onclick)
            self.canvas.tag_bind(
                "empty_ace_slot", "<Button-1>", self.card_onclick)
            self.canvas.tag_bind("empty_cardstack_slot",
                                 "<Button-1>", self.refill_card_stack)
        elif self.movetype == "Click":
            self.canvas.tag_bind("empty_slot", "<Button-1>", self.card_onclick)
            self.canvas.tag_bind(
                "empty_ace_slot", "<Button-1>", self.card_onclick)
            self.canvas.tag_bind("empty_cardstack_slot",
                                 "<Button-1>", self.refill_card_stack)
        else:
            self.canvas.tag_bind("empty_slot", "<Button-1>", self.end_onclick)
            self.canvas.tag_bind(
                "empty_ace_slot", "<Button-1>", self.end_onclick)
            self.canvas.tag_bind(
                "empty_slot", "<Button1-Motion>", self.move_card)
            self.canvas.tag_bind(
                "empty_slot", "<ButtonRelease-1>", self.drop_card)
            self.canvas.tag_bind(
                "empty_ace_slot", "<Button1-Motion>", self.move_card)
            self.canvas.tag_bind(
                "empty_ace_slot", "<ButtonRelease-1>", self.drop_card)
            self.canvas.tag_bind("empty_cardstack_slot",
                                 "<Button-1>", self.refill_card_stack)
        self.canvas.bind("<Button-1>", self.on_background)

        self_width = self.winfo_width()
        if self_width != 1:
            self.self_configure(event=None, width=self_width)

    def on_background(self, event):
        if (self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)) == ():
            self.canvas.delete("rect")
            self.last_active_card = ""
            self.card_stack_list = ""

    def create_rectangle(self, x1, y1, x2, y2, tag="rect", **kwargs):
        if "alpha" in kwargs:
            alpha = int(kwargs.pop("alpha") * 255)
            fill = kwargs.pop("fill")
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new("RGBA", (x2 - x1, y2 - y1), fill)
            self.rect_images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(
                x1, y1, image=self.rect_images[-1], anchor="nw", tag=tag)
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, tag="rect", **kwargs)

    def initiate_game(self):
        self.canvas_item_hover_time = self.canvas_default_item_hover_time
        self.restart_game_button.config(state="normal")
        self.redo_last_move_button.config(state="normal")
        try:
            last_move = self.history[-1]
        except:
            self.undo_last_move_button.disable()
            self.restart_game_button.disable()
        try:
            last_move = self.redo[-1]
        except:
            self.redo_last_move_button.disable()
        if self.game_started == False:
            self.stopwatch.start()
            self.game_started = True
            if self.total_redeals != "unlimited":
                self.redeal_label.pack(side="left", padx=6, pady=4)
            self.stock_label.pack(side="left", padx=6, pady=4)
            self.tribute.pack(side="right", padx=6, pady=4)
        else:
            self.game_started = True

    def enter_card(self, event):
        self.job = self.after(
            self.canvas_item_hover_time, lambda: self.card_onclick(event="Accessability Mode"))

    def enter_stack(self, event):
        self.job = self.after(
            self.canvas_item_hover_time + 800, lambda: self.stack_onclick(event="Accessability Mode"))

    def enter_refill(self, event):
        self.job = self.after(self.canvas_item_hover_time + 800,
                              lambda: self.refill_card_stack(event="Accessability Mode"))

    def leave_hover(self, event):
        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None

    def restart_game(self, *args):
        if self.move_flag:
            return
        self.reset_vars()
        self.redraw()

    def new_game(self, *args):
        if self.move_flag:
            return
        self.shuffle_cards()
        self.reset_vars()
        self.redraw()

    def reset_vars(self):
        if self.larger_cards_pending is not None:
            self.larger_cards = self.larger_cards_pending
            self.larger_cards_pending = None
            if self.larger_cards:
                self.scaled_cards_prefix = "scaled_"
            else:
                self.scaled_cards_prefix = ""
            self.back_of_card_file = os.path.dirname(os.path.abspath(
                __file__)) + "/resources/" + self.scaled_cards_prefix + self.card_back + ".png"
            self.dict_of_cards = {}
            card_dir = "cards"
            if self.larger_cards:
                card_dir = "scaled_cards"
                if not os.path.isdir("resources/scaled_cards"):
                    self.create_scaled_images()

            for card in self.cards:
                name_of_image = os.path.join(
                    "resources", card_dir, "{}.png".format(card))
                image = Image.open(os.path.dirname(
                    os.path.abspath(__file__)) + "/" + name_of_image)
                self.dict_of_cards[card] = (
                    ImageTk.PhotoImage(image))
            back_of_card = Image.open(self.back_of_card_file)
            self.back_of_card = (ImageTk.PhotoImage(back_of_card))

        self.card_drawing_count = 0

        if self.continuous_points:
            self.starting_points = (
                                           self.starting_points + (self.cards_on_ace * self.point_increment)) - 52

        self.cards_on_ace = 0
        self.card_moved_to_ace_by_sender = 0
        self.stock_left = 24
        self.last_active_card = ""
        self.card_stack_list = ""
        self.history = []
        self.redo = []
        self.game_started = False
        self.move_flag = False
        self.job = None

        self.redeals_left = 10

        self.canvas_item_hover_time = self.canvas_default_item_hover_time

        try:
            self.stopwatch.stop()
            self.stopwatch.config(text="Time: 00:00")
        except:
            pass

        self.restart_game_button.disable()
        self.undo_last_move_button.disable()
        self.redo_last_move_button.disable()
        if self.total_redeals != "unlimited":
            self.redeal_label.config(
                text="Redeals left: " + str(max(0, self.total_redeals + self.redeals_left - 1)))
        self.points_label.config(text="Points: " + str(self.starting_points))
        self.stock_label.config(text="Stock left: " + str(self.stock_left))
        self.tribute.config(text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj")
        self.deal_next_card_button.config(
            state="normal")
        self.deal_next_card_button.change_command(
            lambda event="deal_card_button": self.stack_onclick(event))
        if self.total_redeals != "unlimited":
            self.redeal_label.pack_forget()
        self.stock_label.pack_forget()
        self.tribute.pack_forget()
        self.canvas.delete("all")

    def redraw(self):
        self.draw_card_slots()
        self.generate_card_position()
        self.draw_remaining_cards()

    def find_available_cards(self):
        face_up_cards = list(reversed(self.canvas.find_withtag("face_up")))

        flipped_cards = []
        positions_of_ace_rects = []
        found_cards = []

        for card in (self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slotb"))):
            if card in face_up_cards:
                face_up_cards.remove(card)
            if "empty" not in str(self.canvas.gettags(card)):
                flipped_cards.append(card)
        if flipped_cards != []:
            del flipped_cards[:-1]
        ace_slots = self.canvas.find_withtag("empty_ace_slot")
        for slot in ace_slots:
            positions_of_ace_rects.append(self.canvas.bbox(slot))
        for position in positions_of_ace_rects:
            for card in self.canvas.find_overlapping(*position):
                if card in face_up_cards:
                    face_up_cards.remove(card)
                found_cards.append(card)
            if found_cards != []:
                flipped_cards.append(found_cards[-1])
            found_cards = []
        flipped_cards.extend(face_up_cards)
        face_up_cards = flipped_cards

        base_slots = self.canvas.find_withtag("empty_slot")
        for slot in base_slots:
            if len(self.canvas.find_overlapping(*self.canvas.bbox(slot))) == 1:
                face_up_cards.append(slot)

        return face_up_cards

    def create_wait_window(self, message, title, background, foreground):
        win = tk.Toplevel(self, background=background)
        win.transient()
        win.wm_overrideredirect(1)
        win.grab_set()
        win.update()
        win.title(title)
        width = win.winfo_width()
        height = win.winfo_height()
        xoffset = (self.winfo_geometry().split("+"))[-2]
        yoffset = (self.winfo_geometry().split("+"))[-1]
        x = (self.winfo_width() // 2) - (width // 2) + int(xoffset) - 50
        y = (self.winfo_height() // 2) - \
            (height // 2) + int(yoffset) + 100
        win.geometry("{}x{}+{}+{}".format(300, 40, x, y))
        self.win_label_var = tk.StringVar(value=message)
        win_label = tk.Label(
            win, textvariable=self.win_label_var, bg=background, fg=foreground)
        win_label.pack(expand=True, fill="both")
        return win

    def send_cards_up(self, *args):
        if self.move_flag:
            return
        self.initiate_game()
        self.card_stack_list = ""
        self.last_active_card = ""
        self.canvas.delete("rect")
        self.stopwatch.freeze(False)
        if self.win == None:
            self.win = self.create_wait_window(
                "Moving Cards... Please Wait.", "Please Wait", "#1c1c1b", "white")
        face_up_cards = list(reversed(self.canvas.find_withtag("face_up")))
        for card in face_up_cards:
            below_last = self.canvas.find_overlapping(*self.canvas.bbox(card))
            last_card_index_in_below = below_last.index(
                list(self.canvas.find_withtag(card))[0])
            below_last = str(self.canvas.gettags(
                below_last[last_card_index_in_below - 1]))
            if "face_up" in self.canvas.gettags(below_last):
                face_up_cards.remove(card)
        flipped_cards = []
        for card in (self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slotb"))):
            if card in face_up_cards:
                face_up_cards.remove(card)
            if "empty" not in str(self.canvas.gettags(card)):
                flipped_cards.append(card)
        if flipped_cards != []:
            del flipped_cards[:-1]
        flipped_cards.extend(face_up_cards)
        face_up_cards = flipped_cards
        cards_moved = self.card_moved_to_ace_by_sender
        over_ace = []
        temp_over_ace = []
        for item in self.canvas.find_withtag("empty_ace_slot"):
            temp_over_ace = []
            for card in self.canvas.find_overlapping(*self.canvas.bbox(item)):
                temp_over_ace.append(card)
                if card in face_up_cards:
                    face_up_cards.remove(card)
            over_ace.append(temp_over_ace[-1])
        self.cardsender_may_continue = True
        for pair in over_ace:
            for card in face_up_cards:
                if pair == card:
                    continue
                self.change_current(card)
                self.end_onclick(event="send_cards_to_ace")
                self.canvas.dtag("current")
                self.change_current(pair)
                self.card_onclick(event="send_cards_to_ace")
                self.canvas.dtag("current")
                self.card_stack_list = ""
                self.last_active_card = ""
                self.canvas.delete("cardsender_highlight")
                self.update_idletasks()
                if self.card_moved_to_ace_by_sender == 1:
                    self.win_label_var.set("Moved 1 Card.   Please Wait.")
                else:
                    self.win_label_var.set("Moved %s Cards.   Please Wait." % (
                        self.card_moved_to_ace_by_sender))

                if not self.cardsender_may_continue:
                    return
        if self.cardsender_may_continue:
            if cards_moved != self.card_moved_to_ace_by_sender:
                self.send_cards_up()
            else:
                self.card_moved_to_ace_by_sender = 0
                self.win.destroy()
                self.win = None
                self.stopwatch.freeze(True)

    def redo_move(self, *args):
        if self.move_flag:
            return
        try:
            last_move = self.redo[-1]
        except:
            return
        self.last_active_card = ""
        self.card_stack_list = ""
        self.canvas.delete("rect")
        del self.redo[-1]
        self.initiate_game()

        if "refill_card_stack" in last_move:
            self.refill_card_stack(event="redo")
        elif "stack_click_move" in last_move:
            self.stack_onclick(event="redo")
        else:
            if "move_card" in last_move:
                last_active_card = list(last_move[2])[0]
            else:
                last_active_card = last_move[3]
            self.change_current(last_active_card)
            self.end_onclick(event="redo")
            self.canvas.dtag("current")
            if "empty" in str(last_move[-1]):
                last_move[-1] = list(str(last_move[-1]).split("'"))[0]
            self.change_current(last_move[-1])
            self.card_onclick(event="redo")
            self.canvas.dtag("current")
        self.initiate_game()
        try:
            last_move = self.redo[-1]
            self.redo_last_move_button.config(state="normal")
            if self.redo_last_move_button.on_button:
                self.redo_last_move_button.config(
                    background=self.redo_last_move_button["activebackground"])
        except:
            self.redo_last_move_button.disable()
        self.update_deal_button()

    def change_current(self, tag):
        self.canvas.dtag("current")
        self.canvas.focus("")
        self.canvas.addtag_withtag("current", tag)

    def undo_move(self, *args):
        if self.move_flag:
            return
        self.last_active_card = ""
        self.card_stack_list = ""
        self.canvas.delete("rect")
        self.initiate_game()
        try:
            last_move = self.history[-1]
        except:
            return
        self.redo.append(last_move)
        del self.history[-1]
        if "refill_card_stack" in last_move:
            self.redeals_left += 1
            if self.total_redeals != "unlimited":
                self.redeal_label.config(
                    text="Redeals left: " + str(max(0, self.total_redeals + self.redeals_left - 1)))
            for card in reversed(list(self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slot")))):
                current_item_tags = self.canvas.gettags(card)
                tag_a = current_item_tags[0]
                if "empty_cardstack_slot" in (self.canvas.gettags(card)):
                    continue
                self.canvas.tag_unbind(tag_a, "<Enter>")
                self.canvas.tag_unbind(tag_a, "<Leave>")
                self.canvas.tag_unbind(tag_a, "<Button-1>")
                if self.movetype == "Accessability Mode":
                    self.canvas.tag_bind(tag_a, "<Enter>", self.enter_card)
                    self.canvas.tag_bind(tag_a, "<Leave>", self.leave_hover)
                    self.canvas.tag_bind(
                        tag_a, "<Button-1>", self.card_onclick)
                elif self.movetype == "Click":
                    self.canvas.tag_bind(
                        tag_a, "<Button-1>", self.card_onclick)
                else:
                    self.canvas.tag_bind(tag_a, "<Button-1>", self.end_onclick)
                    self.canvas.tag_bind(
                        tag_a, "<Button1-Motion>", self.move_card)
                    self.canvas.tag_bind(
                        tag_a, "<ButtonRelease-1>", self.drop_card)
                    self.canvas.tag_bind(
                        tag_a, "<Enter>", self.on_draggable_card)
                    self.canvas.tag_bind(
                        tag_a, "<Leave>", self.leave_draggable_card)
                self.canvas.tag_raise(card)
                if not self.larger_cards:
                    self.canvas.move(card, 100, 0)
                else:
                    self.canvas.move(card, 115, 0)
                self.canvas.itemconfig(
                    card, image=self.dict_of_cards[tag_a], tag=(tag_a, "face_up"))
                self.stock_left -= 1
            self.stock_label.config(text="Stock left: " + str(self.stock_left))
            self.tribute.config(text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj")
            self.undo_last_move_button.config(state="normal")
            self.restart_game_button.config(state="normal")
            self.redo_last_move_button.disable()

        elif "stack_click_move" in last_move:
            self.canvas.delete("rect")
            self.stock_left += 1
            self.stock_label.config(text="Stock left: " + str(self.stock_left))
            self.tribute.config(text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj")
            tag_a = last_move[0]
            if not self.larger_cards:
                self.canvas.move(tag_a, -100, 0)
            else:
                self.canvas.move(tag_a, -115, 0)
            self.canvas.itemconfig(
                tag_a, image=self.back_of_card, tag=(tag_a, "face_down"))
            self.canvas.tag_unbind(tag_a, "<Enter>")
            self.canvas.tag_unbind(tag_a, "<Leave>")
            self.canvas.tag_unbind(tag_a, "<Button-1>")
            if self.movetype == "Accessability Mode":
                self.canvas.tag_bind(tag_a, "<Enter>", self.enter_stack)
                self.canvas.tag_bind(tag_a, "<Leave>", self.leave_hover)
                self.canvas.tag_bind(tag_a, "<Button-1>", self.stack_onclick)
            else:
                self.canvas.tag_bind(tag_a, "<Button-1>", self.stack_onclick)
            self.canvas.tag_raise(self.canvas.find_withtag(tag_a))
            self.deal_next_card_button.config(state="normal")
            self.deal_next_card_button.change_command(
                lambda event="deal_card_button": self.stack_onclick(event))

        elif "move_card" in last_move:
            card_tags = last_move[-2]
            self.canvas.itemconfig(
                card_tags, image=self.back_of_card, tag=(card_tags, "face_down"))
            self.canvas.tag_unbind(card_tags, "<Enter>")
            self.canvas.tag_unbind(card_tags, "<Leave>")
            self.canvas.tag_unbind(card_tags, "<Button-1>")
            for i in last_move[2]:
                card_location = self.canvas.coords(i)
                current_location = last_move[2][i]
                xpos = int(current_location[0]) - int(card_location[0])
                ypos = (int(current_location[1]) - int(card_location[1]))
                self.canvas.move(i, xpos, ypos)
                if True in last_move:
                    self.canvas.tag_raise(i)
            if last_move[1] == 1:
                self.cards_on_ace -= 1
                for i in last_move[2]:
                    self.canvas.tag_raise(i)
                self.points_label["text"] = (
                        "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
            elif last_move[1] == 2:
                self.cards_on_ace += 1
                self.points_label["text"] = (
                        "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))

        elif "move_card_srv" in last_move:
            card_location = self.canvas.coords(last_move[3])
            current_image_location = last_move[-2]

            if last_move[1]:
                current_image_location = self.canvas.coords(last_move[1])

            xpos = int(current_image_location[0]) - int(card_location[0])
            ypos = (int(current_image_location[1]) - int(card_location[1]))
            self.canvas.move(last_move[3], xpos, ypos)
            self.canvas.tag_raise(last_move[3])

            if last_move[2] == 1:
                self.cards_on_ace -= 1
                self.points_label["text"] = (
                        "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
            elif last_move[2] == 2:
                self.cards_on_ace += 1
                self.points_label["text"] = (
                        "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
        self.canvas.tag_raise("face_up")
        self.restart_game_button.config(state="normal")
        self.redo_last_move_button.config(state="normal")
        try:
            last_move = self.history[-1]
        except:
            self.undo_last_move_button.disable()
            self.restart_game_button.disable()
        self.deal_next_card_button.config(state="normal")
        if self.total_redeals != "unlimited":
            if self.stock_left < 1 and (self.total_redeals + self.redeals_left - 1) == 0:
                self.deal_next_card_button.disable()
        if self.stock_left == 0:
            self.deal_next_card_button.change_command(
                lambda event=None: self.refill_card_stack(event))
        else:
            self.deal_next_card_button.change_command(
                lambda event="deal_card_button": self.stack_onclick(event))
        self.update_deal_button()

    def check_move_validity(self, current_card, last_card, ace_slot):
        if ace_slot:
            if "clubs" in current_card and "clubs" not in last_card:
                return False
            if "spades" in current_card and "spades" not in last_card:
                return False
            if "diamonds" in current_card and "diamonds" not in last_card:
                return False
            if "hearts" in current_card and "hearts" not in last_card:
                return False
        else:
            if (("clubs" in current_card) or ("spades" in current_card)) and (
                    ("clubs" in last_card) or ("spades" in last_card)):
                return False
            elif (("diamonds" in current_card) or ("hearts" in current_card)) and (
                    ("diamonds" in last_card) or ("hearts" in last_card)):
                return False
        if "empty_ace_slot" in current_card:
            return True
        else:
            if last_card[1] == "0":
                last_card = "10"
            else:
                last_card = last_card[0]

            if current_card[1] == "0":
                current_card = "10"
            else:
                current_card = current_card[0]

            if last_card == "j":
                last_card = "11"
            elif last_card == "q":
                last_card = "12"
            elif last_card == "k":
                last_card = "13"
            elif last_card == "a":
                last_card = "1"

            if current_card == "j":
                current_card = "11"
            elif current_card == "q":
                current_card = "12"
            elif current_card == "k":
                current_card = "13"
            elif current_card == "a":
                current_card = "1"

            last_card = int(last_card)
            current_card = int(current_card)

            if ace_slot:
                if last_card - 1 == current_card:
                    return True
                else:
                    return False
            else:
                if last_card + 1 == current_card:
                    return True
                else:
                    return False

    def stack_onclick(self, event):
        if self.move_flag:
            return
        self.initiate_game()
        current_item = list(self.canvas.find_overlapping(
            *self.canvas.bbox("empty_cardstack_slot")))[-1]
        current_item_tags = self.canvas.gettags(current_item)
        if event == "deal_card_button":
            if "rect" in str(current_item_tags):
                self.canvas.delete('rect')
                self.stack_onclick(event="deal_card_button")
                return
        tag_a = current_item_tags[0]
        if (event != "redo") and (event != "deal_card_button"):
            self.redo = []
            if "empty_cardstack_slot" in tag_a:
                return
            elif "rect" in tag_a:
                return
        else:
            if "empty_cardstack_slot" in tag_a:
                return

        self.canvas.delete("rect")
        self.stock_left -= 1
        self.stock_label.config(text="Stock left: " + str(self.stock_left))
        self.tribute.config(text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj")
        self.last_active_card = ""
        self.card_stack_list = ""

        history_to_add = [tag_a, "stack_click_move"]
        self.history.append(history_to_add)

        if not self.larger_cards:
            self.canvas.move(current_item, 100, 0)
        else:
            self.canvas.move(current_item, 115, 0)
        self.canvas.itemconfig(
            current_item, image=self.dict_of_cards[tag_a], tag=(tag_a, "face_up"))

        self.canvas.tag_unbind(tag_a, "<Button-1>")

        if self.movetype == "Accessability Mode":
            self.canvas.tag_unbind(tag_a, "<Enter>")
            self.canvas.tag_unbind(tag_a, "<Leave>")
            self.canvas.tag_bind(tag_a, "<Enter>", self.enter_card)
            self.canvas.tag_bind(tag_a, "<Leave>", self.leave_hover)
            self.canvas.tag_bind(tag_a, "<Button-1>", self.card_onclick)
        elif self.movetype == "Click":
            self.canvas.tag_bind(tag_a, "<Button-1>", self.card_onclick)
        else:
            self.canvas.tag_bind(tag_a, "<Button-1>", self.end_onclick)
            self.canvas.tag_bind(tag_a, "<Button1-Motion>", self.move_card)
            self.canvas.tag_bind(tag_a, "<ButtonRelease-1>", self.drop_card)
            self.canvas.tag_bind(tag_a, "<Enter>", self.on_draggable_card)
            self.canvas.tag_bind(tag_a, "<Leave>", self.leave_draggable_card)

        self.canvas.tag_raise(self.canvas.find_withtag(tag_a))

        self.undo_last_move_button.config(state="normal")
        self.restart_game_button.config(state="normal")
        self.redo_last_move_button.disable()

        self.update_deal_button()

    def refill_card_stack(self, event):
        if self.move_flag:
            return
        if event != "redo":
            self.redo = []
        self.initiate_game()
        self.canvas.delete("rect")
        ret = False
        if self.total_redeals != "unlimited":
            if (self.total_redeals + self.redeals_left - 1) <= 0:
                messagebox.showinfo(title="No Redeals Left",
                                    message="Sorry. You have no redeals left.")
                ret = True
        if not ret:
            history_to_add = ["refill_card_stack"]
            self.history.append(history_to_add)
            self.redeals_left -= 1
            if self.total_redeals != "unlimited":
                self.redeal_label.config(
                    text="Redeals left: " + str(max(0, self.total_redeals + self.redeals_left - 1)))

            for card in reversed(list(self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slotb")))):
                if "empty_cardstack_slotb" in self.canvas.gettags(card):
                    continue
                card = self.canvas.gettags(card)[0]

                self.canvas.tag_unbind(card, "<Button-1>")
                if self.movetype == "Accessability Mode":
                    self.canvas.tag_unbind(card, "<Enter>")
                    self.canvas.tag_unbind(card, "<Leave>")
                    self.canvas.tag_bind(card, "<Enter>", self.enter_stack)
                    self.canvas.tag_bind(card, "<Leave>", self.leave_hover)
                    self.canvas.tag_bind(
                        card, "<Button-1>", self.stack_onclick)
                else:
                    self.canvas.tag_unbind(card, "<Enter>")
                    self.canvas.tag_unbind(card, "<Leave>")
                    self.canvas.tag_bind(
                        card, "<Button-1>", self.stack_onclick)
                self.canvas.tag_raise(card)
                if not self.larger_cards:
                    self.canvas.move(card, -100, 0)
                else:
                    self.canvas.move(card, -115, 0)
                self.canvas.itemconfig(
                    card, image=self.back_of_card, tag=(card, "face_down"))
            self.stock_left -= 1
            for i in (self.canvas.find_overlapping(*self.canvas.bbox("empty_cardstack_slot"))):
                self.stock_left += 1
            self.stock_label.config(text="Stock left: " + str(self.stock_left))
            self.tribute.config(text="Made with ❤️ by Rajat, Anay, Tejas, Ntin & Rituraj")
            self.undo_last_move_button.config(state="normal")
            self.restart_game_button.config(state="normal")
            self.redo_last_move_button.config(state="disabled")
            self.update_deal_button()

    def update_deal_button(self):
        if self.total_redeals != "unlimited":
            if self.stock_left < 1 and (self.total_redeals + self.redeals_left - 1) == 0:
                self.deal_next_card_button.disable()
            else:
                self.deal_next_card_button.config(state="normal")
        else:
            self.deal_next_card_button.config(state="normal")
        if self.stock_left == 0:
            self.unbind_all("<Control-d>")
            self.bind_all("<Control-d>", lambda event=None: self.refill_card_stack(event))
            self.deal_next_card_button.change_command(
                lambda event=None: self.refill_card_stack(event))
        else:
            self.unbind_all("<Control-d>")
            self.bind_all("<Control-d>", lambda event: self.stack_onclick("deal_card_button"))
            self.deal_next_card_button.change_command(
                lambda event="deal_card_button": self.stack_onclick(event))

    def on_draggable_card(self, event):
        if self.canvas["cursor"] != "fleur":
            self.canvas.config(cursor="hand2")

    def leave_draggable_card(self, event):
        if self.canvas["cursor"] != "fleur":
            self.canvas.config(cursor="")

    def move_card(self, event):
        self.canvas.delete("available_card_rect")
        self.canvas.delete("rect")
        if self.move_flag:
            new_xpos, new_ypos = event.x, event.y
            self.canvas.move("moveable", new_xpos -
                             self.mouse_xpos, new_ypos - self.mouse_ypos)

            self.mouse_xpos = new_xpos
            self.mouse_ypos = new_ypos

            self.highlight_available_cards()
        else:
            for item in self.card_stack_list:
                card_tag = list(self.canvas.gettags(item))[0]
                if "empty" in str(self.canvas.gettags(item)):
                    continue
                elif "face_down" in str(self.canvas.gettags(item)):
                    continue
                else:
                    self.canvas.addtag_withtag("moveable", card_tag)
            self.move_flag = True
            self.canvas.tag_raise("moveable")
            self.mouse_xpos = event.x
            self.mouse_ypos = event.y

    def highlight_available_cards(self):
        try:
            last_image_location = self.current_image_location
            returnval = True
            bbox = list(self.canvas.bbox(self.canvas.find_withtag("current")))
            bbox[0] = int(bbox[0]) - 15
            bbox[1] = int(bbox[1]) - 15
            bbox[2] = int(bbox[2]) + 15
            bbox[3] = int(bbox[3]) + 15
            card_overlapping = self.canvas.find_overlapping(*tuple(bbox))
        except:
            return
        for card in card_overlapping:
            if (self.canvas.find_withtag("current")) == card:
                continue
            card_tag = str(self.canvas.gettags(card))
            if "face_down" in card_tag:
                continue
            elif "current" in card_tag:
                continue
            elif "empty_cardstack_slot" in card_tag:
                break
            else:
                current_image = self.canvas.find_withtag(card)
                current_image_bbox = self.canvas.bbox(current_image)
                returnval = self.generate_returnval(current_image)
                if returnval:
                    self.create_rectangle(
                        *current_image_bbox, fill="blue", alpha=.3, tag="available_card_rect")
                    for card in self.card_stack_list:
                        if "empty_slot" not in self.canvas.gettags(card):
                            self.canvas.tag_raise(card)
                    continue

    def drop_card(self, event):
        if self.canvas["cursor"] == "fleur":
            self.canvas.config(cursor="hand2")
        self.canvas.delete("available_card_rect")
        self.move_flag = False
        self.canvas.dtag("face_up", "moveable")
        try:
            last_image_location = self.current_image_location
            returnval = True
            bbox = list(self.canvas.bbox(self.canvas.find_withtag("current")))
            bbox[0] = int(bbox[0]) - 15
            bbox[1] = int(bbox[1]) - 15
            bbox[2] = int(bbox[2]) + 15
            bbox[3] = int(bbox[3]) + 15
            card_overlapping = self.canvas.find_overlapping(*tuple(bbox))
        except:
            moving_count = 0
            for item in self.card_stack_list:
                if "empty" in str(self.canvas.gettags(item)):
                    continue
                elif "face_down" in str(self.canvas.gettags(item)):
                    continue
                else:
                    xpos = int(last_image_location[0]) - \
                           int(self.canvas.coords(item)[0])
                    ypos = moving_count + \
                           (int(last_image_location[1]) -
                            int(self.canvas.coords(item)[1]))

                    self.canvas.move(item, xpos, ypos)
                    moving_count += 20
            return
        for card in card_overlapping:
            card_tag = str(self.canvas.gettags(card))
            if "face_down" in card_tag:
                continue
            elif "current" in card_tag:
                continue
            elif "empty_cardstack_slot" in card_tag:
                break
            else:
                self.current_image = current_image = self.canvas.find_withtag(
                    card)
                self.current_image_tags = current_image_tags = self.canvas.gettags(
                    current_image)
                self.current_image_location = self.canvas.coords(current_image)
                self.current_image_bbox = current_image_bbox = self.canvas.bbox(
                    current_image)
                bbox_list = list(current_image_bbox)
                current_image_overlapping = self.canvas.find_overlapping(
                    *bbox_list)
                self.tag_a = tag_a = str(current_image_tags).replace(", 'current')", "").replace(
                    ")", "").replace("('", "").replace("', 'face_down'", "").replace("', 'face_up'", "")
                overlapping = False
                ace_slot = False
                over_ace_slot = False
                for card in self.canvas.find_overlapping(*self.canvas.bbox(current_image)):
                    if "empty_ace_slot" in self.canvas.gettags(card):
                        over_ace_slot = True
                        break
                if (not over_ace_slot) and ("empty_slot" not in str(current_image_tags)):
                    csl = list(self.canvas.bbox(tag_a))
                    if self.larger_cards:
                        csl[1] = (int(csl[1])) + 135
                    else:
                        csl[1] = (int(csl[1])) + 110
                    csl[3] = (int(csl[3])) + 20
                    csl = tuple(csl)
                    csl = list(self.canvas.find_overlapping(*csl))
                    for card in csl:
                        if card in self.card_stack_list:
                            continue
                        elif "empty_cardstack_slot" in str(self.canvas.gettags(card)):
                            overlapping = True
                            break
                        elif "face_up" in self.canvas.gettags(card):
                            overlapping = True
                            break

                if "empty_slot" in str(self.current_image_tags):
                    if "king" in self.last_active_card:
                        for card in current_image_overlapping:
                            if card in self.card_stack_list:
                                continue
                            elif "face" in str(self.canvas.gettags(card)):
                                overlapping = True
                                break

                for item in current_image_overlapping:
                    if "empty_ace_slot" in self.canvas.gettags(self.canvas.find_withtag(item)):
                        ace_slot = True

                if ace_slot:
                    try:
                        for item in self.card_stack_list:
                            self.canvas.tag_raise(item)
                        item = self.canvas.find_overlapping(
                            *self.canvas.bbox(self.canvas.find_above(self.last_active_card)))
                        overlapping = True
                    except:
                        pass

                try:
                    if str(list(current_image)[0]) == str(self.last_active_card_over[self.last_active_card_over.index(
                            list(self.canvas.find_withtag(self.last_active_card))[0]) - 1]):
                        overlapping = True
                except (ValueError, IndexError):
                    pass

                if ("ace" not in self.last_active_card and "empty_ace_slot" in self.current_image_tags):
                    continue
                elif ("king" not in self.last_active_card and "empty_slot" in self.current_image_tags):
                    continue
                elif ("empty_slot" in self.last_active_card):
                    continue
                elif overlapping:
                    continue
                elif "king" in self.last_active_card and "empty_slot" in self.current_image_tags:
                    self.continue_onclick(ace_slot=ace_slot, event=event)
                    returnval = False
                    break
                elif self.check_move_validity(tag_a, self.last_active_card, ace_slot):
                    self.continue_onclick(ace_slot=ace_slot, event=event)
                    returnval = False
                    break
                else:
                    continue

        if returnval:
            moving_count = 0
            for item in self.card_stack_list:
                if "empty" in str(self.canvas.gettags(item)):
                    continue
                elif "face_down" in str(self.canvas.gettags(item)):
                    continue
                else:
                    xpos = int(last_image_location[0]) - \
                           int(self.canvas.coords(item)[0])
                    ypos = moving_count + \
                           (int(last_image_location[1]) -
                            int(self.canvas.coords(item)[1]))

                    self.canvas.move(item, xpos, ypos)
                    moving_count += 20
        self.card_stack_list = ""
        self.canvas.delete("rect")
        self.last_active_card = ""

    def generate_returnval(self, current_image, use_last_active_card=None):
        if use_last_active_card:
            last_active_card = use_last_active_card
        else:
            last_active_card = self.last_active_card
        current_image_tags = self.canvas.gettags(current_image)

        current_image_bbox = self.canvas.bbox(current_image)
        bbox_list = list(current_image_bbox)
        current_image_overlapping = self.canvas.find_overlapping(*bbox_list)

        tag_a = str(current_image_tags).replace(", 'current')", "").replace(")", "").replace(
            "('", "").replace("', 'face_down'", "").replace("', 'face_up'", "")
        overlapping = False
        ace_slot = False
        returnval = False

        over_ace_slot = False
        for card in self.canvas.find_overlapping(*self.canvas.bbox(current_image)):
            if "empty_ace_slot" in self.canvas.gettags(card):
                over_ace_slot = True
                break
        if (not over_ace_slot) and ("empty_slot" not in str(current_image_tags)):
            csl = list(self.canvas.bbox(current_image))
            if self.larger_cards:
                csl[1] = (int(csl[1])) + 135
            else:
                csl[1] = (int(csl[1])) + 110
            csl[3] = (int(csl[3])) + 20
            csl = tuple(csl)
            csl = list(self.canvas.find_overlapping(*csl))
            for card in csl:
                if card in self.card_stack_list:
                    continue
                elif "face_up" in self.canvas.gettags(card):

                    overlapping = True
                    break

        if "empty_slot" in str(current_image_tags):
            if "king" in last_active_card:
                for card in current_image_overlapping:
                    if card in self.card_stack_list:
                        continue
                    elif "face" in str(self.canvas.gettags(card)):
                        overlapping = True
                        break

        for item in current_image_overlapping:
            if "empty_ace_slot" in self.canvas.gettags(self.canvas.find_withtag(item)):
                ace_slot = True

        if ace_slot:
            try:
                for item in self.card_stack_list:
                    self.canvas.tag_raise(item)
                item = self.canvas.find_overlapping(
                    *self.canvas.bbox(self.canvas.find_above(last_active_card)))
                overlapping = True
            except:
                pass

        if ("ace" not in last_active_card and "empty_ace_slot" in current_image_tags):
            return returnval
        elif ("king" not in last_active_card and "empty_slot" in current_image_tags):
            return returnval
        elif ("empty_slot" in last_active_card):
            return returnval
        elif overlapping:
            return returnval
        elif "king" in last_active_card and "empty_slot" in current_image_tags:
            returnval = True
            return returnval
        elif self.check_move_validity(tag_a, last_active_card, ace_slot):
            returnval = True
            return returnval
        else:
            return returnval

    def card_onclick(self, event):
        self.initiate_game()
        self.current_image = current_image = self.canvas.find_withtag(
            "current")
        self.current_image_tags = current_image_tags = self.canvas.gettags(
            current_image)
        if self.movetype == "Accessability Mode":
            if "rect" in self.current_image_tags:
                return
            elif "()" in str(self.current_image_tags):
                return
        self.current_image_location = self.canvas.coords(current_image)

        self.current_image_bbox = current_image_bbox = self.canvas.bbox(
            current_image)
        bbox_list = list(current_image_bbox)
        current_image_overlapping = self.canvas.find_overlapping(*bbox_list)

        self.tag_a = tag_a = str(current_image_tags).replace(", 'current')", "").replace(
            "('", "").replace("', 'face_down'", "").replace("', 'face_up'", "")
        overlapping = False
        ace_slot = False
        if self.last_active_card != "":
            if ("empty_ace_slot" not in str(current_image_tags)) and ("empty_slot" not in str(current_image_tags)):
                csl = list(self.canvas.bbox(tag_a))
                if self.larger_cards:
                    csl[1] = (int(csl[1])) + 135
                else:
                    csl[1] = (int(csl[1])) + 110
                csl[3] = (int(csl[3])) + 20
                csl = tuple(csl)
                csl = list(self.canvas.find_overlapping(*csl))
                for i in csl:
                    if "face_up" in self.canvas.gettags(self.canvas.find_withtag(i)):
                        overlapping = True

            for item in current_image_overlapping:
                if "empty_ace_slot" in self.canvas.gettags(self.canvas.find_withtag(item)):
                    ace_slot = True

            if ace_slot:
                try:
                    for item in self.card_stack_list:
                        self.canvas.tag_raise(item)
                    item = self.canvas.find_overlapping(
                        *self.canvas.bbox(self.canvas.find_above(self.last_active_card)))
                    overlapping = True
                except:
                    pass
                self.canvas.tag_raise("rect")

            try:
                for card in self.canvas.find_overlapping(*self.canvas.bbox(self.tag_a)):
                    if "empty_cardstack" in str(self.canvas.gettags(card)):
                        overlapping = True
            except:
                pass
            if ("ace" not in self.last_active_card and "empty_ace_slot" in current_image_tags):
                if event != "send_cards_to_ace":
                    self.end_onclick(event=event)
            elif ("king" not in self.last_active_card and "empty_slot" in current_image_tags):
                if event != "send_cards_to_ace":
                    self.end_onclick(event=event)
            elif ("empty_slot" in self.last_active_card):
                if event != "send_cards_to_ace":
                    self.end_onclick(event=event)
            elif overlapping is True:
                if event != "send_cards_to_ace":
                    self.end_onclick(event=event)
            elif "king" in self.last_active_card and "empty_slot" in current_image_tags:
                self.continue_onclick(ace_slot=ace_slot, event=event)
            elif self.check_move_validity(tag_a, self.last_active_card, ace_slot) is True:
                if event == "send_cards_to_ace":
                    self.create_rectangle(
                        *self.canvas.bbox(self.last_active_card), fill="blue", tag="cardsender_highlight", alpha=.5)
                    self.canvas.tag_raise("cardsender_highlight")
                    self.update_idletasks()
                    self.canvas.after(self.default_cardsender_freeze_time)
                    self.update_idletasks()
                self.continue_onclick(ace_slot=ace_slot, event=event)
            else:
                if event != "send_cards_to_ace":
                    self.end_onclick(event=event)
        else:
            if event != "send_cards_to_ace":
                self.end_onclick(event=event)

    def end_onclick(self, event, current_tag_name="current", pass_variable_updates=False):
        self.initiate_game()
        self.canvas.tag_unbind("face_up", "<Enter>")
        self.canvas.tag_unbind("card_below_rect", "<Enter>")
        self.canvas.dtag("card_below_rect")

        self.current_image = current_image = self.canvas.find_withtag(
            current_tag_name)[0]
        self.current_image_tags = current_image_tags = self.canvas.gettags(
            current_image)
        self.current_image_location = self.canvas.coords(current_image)
        self.current_image_bbox = self.canvas.bbox(
            current_image)

        self.tag_a = current_image_tags[0]

        if (
                "empty_ace_slot" not in self.current_image_tags and "empty_slot" not in self.current_image_tags) or pass_variable_updates:
            self.card_stack_list = ""
            self.canvas.delete("rect")
            self.last_active_card = ""
            self.last_active_card = self.tag_a

            self.card_stack_list = list(
                self.canvas.bbox(self.last_active_card))
            if self.larger_cards:
                self.card_stack_list[1] = (int(self.card_stack_list[1])) + 129
            else:
                self.card_stack_list[1] = (int(self.card_stack_list[1])) + 99
            self.card_stack_list[3] = (int(self.card_stack_list[3])) + 350
            self.card_stack_list = tuple(self.card_stack_list)
            self.card_stack_list = list(
                self.canvas.find_overlapping(*self.card_stack_list))

            if (self.movetype == "Drag"):
                if event != "send_cards_to_ace":
                    self.canvas.config(cursor="fleur")
                for card in self.card_stack_list:
                    card_tag = self.canvas.gettags(card)
                    if ("cardstack" in str(card_tag)):
                        to_be_card_stack_list = self.card_stack_list[-1]
                        self.card_stack_list = []
                        self.card_stack_list.append(to_be_card_stack_list)
                        break
                    elif ("ace_slot" in str(card_tag)):
                        self.card_stack_list = []
                        for card in self.canvas.find_withtag(self.last_active_card):
                            self.card_stack_list.append(card)
                        break
            last_active_card_bbox_list = list(
                self.canvas.bbox(self.last_active_card))
            if self.larger_cards:
                last_active_card_bbox_list[1] = int(
                    last_active_card_bbox_list[1]) + 90
            else:
                last_active_card_bbox_list[1] = int(
                    last_active_card_bbox_list[1]) + 60
            last_active_card_bbox_list[3] = int(
                last_active_card_bbox_list[3]) - 25
            last_active_card_bbox_list = tuple(last_active_card_bbox_list)
            self.last_active_card_overlapping = self.canvas.find_overlapping(
                *last_active_card_bbox_list)

            self.last_active_card_over = self.canvas.find_overlapping(
                *self.canvas.bbox(self.last_active_card))
            self.last_active_card_coordinates = []
            for card in self.card_stack_list:
                self.last_active_card_coordinates.append(
                    self.canvas.coords(card))

            if (self.movetype != "Drag") and (event != "send_cards_to_ace"):
                first_item = list(self.canvas.bbox(self.last_active_card))
                last_item = list(self.canvas.bbox(
                    self.canvas.find_withtag(self.card_stack_list[-1])))

                tl = first_item[0]
                tr = first_item[1]
                bl = last_item[2]
                br = last_item[3]

                positionsb = []
                positionsb.append(tl)
                positionsb.append(tr)
                positionsb.append(bl)
                positionsb.append(br)
                positionsb = tuple(positionsb)

                positions = self.canvas.bbox(self.last_active_card)

                returnval = False
                for item in self.card_stack_list:
                    if "empty_ace_slot" in self.canvas.gettags(self.canvas.find_withtag(item)):
                        returnval = True
                        break
                if returnval is True:
                    self.create_rectangle(*positions, fill="blue", alpha=.3)
                else:
                    self.create_rectangle(*positionsb, fill="blue", alpha=.3)
                if self.movetype == "Accessability Mode":
                    self.canvas.tag_unbind("face_up", "<Enter>")
                    self.canvas.tag_bind(
                        "rect", "<Enter>", self.enter_hover_on_rect)
                    self.canvas.tag_bind("rect", "<Leave>", self.leave_hover)
                    self.canvas.tag_bind(
                        "rect", "<Button-1>", self.click_on_rect)
                elif self.movetype == "Click":
                    self.canvas.tag_bind(
                        "rect", "<Button-1>", self.click_on_rect)

    def enter_hover_on_rect(self, event):
        self.job = self.after(
            self.canvas_item_hover_time + 1000, lambda: self.click_on_rect(event=event))

    def click_on_rect(self, event):
        self.canvas.tag_bind("face_up", "<Enter>", self.end_onclick)
        self.canvas.delete("rect")

    def continue_onclick(self, ace_slot, event):
        self.update_idletasks()
        self.cardsender_may_continue = True
        if event != "redo":
            self.redo = []
        self.canvas.delete("rect")
        tag_list = []
        new_card_on_ace = 0
        self.card_drawing_count = 20

        for i in self.last_active_card_overlapping:
            tag_list.append(self.canvas.gettags(i))

        if "empty_ace_slot" in str(tag_list):
            self.cards_on_ace -= 1
            self.points_label["text"] = (
                    "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
            new_card_on_ace = 2
            check = self.generate_drawing_count(ace_slot=ace_slot)
            if self.movetype == "Drag":
                self.card_drawing_count = 20
                for i in self.canvas.find_overlapping(*self.canvas.bbox(self.current_image)):
                    tag_list.append(self.canvas.gettags(i))
                if "empty_ace_slot" in str(tag_list):
                    check = self.generate_drawing_count(ace_slot=ace_slot)
                    if check != None:
                        new_card_on_ace = check
        else:
            check = self.generate_drawing_count(ace_slot=ace_slot)
            if check != None:
                new_card_on_ace = check

        last_active_card_bbox_list = list(
            self.canvas.bbox(self.last_active_card))
        last_active_card_bbox_list[1] = int(
            last_active_card_bbox_list[1]) + 60
        last_active_card_bbox_list[3] = int(
            last_active_card_bbox_list[3]) - 25
        last_active_card_bbox_list = tuple(last_active_card_bbox_list)

        secondreturnval = False
        empty_ace_slot_found = False
        for i in list(self.last_active_card_overlapping):
            if "empty_ace_slot" in self.canvas.gettags(self.canvas.find_withtag(i)):
                secondreturnval = True
                empty_ace_slot_found = i
                break
            elif "empty_cardstack_slotb" in self.canvas.gettags(self.canvas.find_withtag(i)):
                secondreturnval = True
                break

        if secondreturnval:
            last_active_card = self.canvas.find_withtag(
                self.last_active_card)
            last_active_card_coordinates = self.canvas.coords(
                last_active_card)
            xpos = int(
                self.current_image_location[0]) - int(last_active_card_coordinates[0])
            ypos = self.card_drawing_count + \
                   (int(self.current_image_location[1]) -
                    int(last_active_card_coordinates[1]))
            self.canvas.move(last_active_card, xpos, ypos)
            self.canvas.tag_raise(last_active_card)
            if event == "send_cards_to_ace":
                self.canvas.tag_raise("cardsender_highlight")
                self.card_moved_to_ace_by_sender += 1
            if self.movetype != "Drag":
                history_to_add = ["move_card_srv", empty_ace_slot_found, new_card_on_ace,
                                  self.last_active_card, last_active_card_coordinates, self.tag_a]
            else:
                history_to_add = ["move_card_srv", empty_ace_slot_found, new_card_on_ace, self.last_active_card,
                                  self.last_active_card_coordinates[0], self.current_image]
        else:
            flipped_cards = []
            moved_cards = {}
            for card in list(self.last_active_card_overlapping):
                card_values = self.canvas.find_withtag(card)
                if "face_down" in self.canvas.gettags(card_values):
                    card_tags = str(self.canvas.gettags(card_values))
                    tag_a = card_tags.replace("('", "").replace(
                        "', 'face_down')", "").replace("', 'face_up')", "")
                    self.canvas.itemconfig(
                        card_values, image=self.dict_of_cards[tag_a], tag=(tag_a, "face_up"))
                    if self.movetype == "Accessability Mode":
                        self.canvas.tag_bind(
                            tag_a, "<Enter>", self.enter_card)
                        self.canvas.tag_bind(
                            tag_a, "<Leave>", self.leave_hover)
                        self.canvas.tag_bind(
                            tag_a, "<Button-1>", self.card_onclick)
                    elif self.movetype == "Click":
                        self.canvas.tag_bind(
                            tag_a, "<Button-1>", self.card_onclick)
                    else:
                        self.canvas.tag_bind(
                            tag_a, "<Button-1>", self.end_onclick)
                        self.canvas.tag_bind(
                            tag_a, "<Button1-Motion>", self.move_card)
                        self.canvas.tag_bind(
                            tag_a, "<ButtonRelease-1>", self.drop_card)
                        self.canvas.tag_bind(
                            tag_a, "<Enter>", self.on_draggable_card)
                        self.canvas.tag_bind(
                            tag_a, "<Leave>", self.leave_draggable_card)
                    flipped_cards.append(tag_a)
            for card in list(self.card_stack_list):
                if "face_up" in self.canvas.gettags(self.canvas.find_withtag(card)):
                    card_location = self.canvas.coords(card)
                    xpos = int(
                        self.current_image_location[0]) - int(card_location[0])
                    ypos = self.card_drawing_count + \
                           (int(
                               self.current_image_location[1]) - int(card_location[1]))
                    self.canvas.move(card, xpos, ypos)
                    self.canvas.tag_raise(card)
                    if event == "send_cards_to_ace":
                        self.canvas.tag_raise("cardsender_highlight")
                        self.card_moved_to_ace_by_sender += 1
                    self.card_drawing_count += 20
                    moved_cards[str(self.canvas.gettags(self.canvas.find_withtag(card))).replace("('", "").replace(
                        "', 'face_down')", "").replace(
                        "', 'face_up')", "").replace("', 'face_up', 'current')", "")] = \
                    self.last_active_card_coordinates[self.card_stack_list.index(card)]
            history_to_add = ["move_card", new_card_on_ace, moved_cards,
                              self.card_drawing_count, flipped_cards, self.current_image]
        self.card_stack_list = ""
        self.last_active_card = ""

        if self.cards_on_ace == 52:
            if self.win != None:
                self.canvas.delete("cardsender_highlight")
                self.win.destroy()
                self.win = None
                self.card_moved_to_ace_by_sender = 0
                self.stopwatch.freeze(True)
            self.history = []
            self.cardsender_may_continue = False
            after_game = messagebox.askquestion(
                "You've won!", "Congratulations! You've won the game! Do you want to play again?", icon="warning")
            if after_game == "yes":
                self.new_game()
            else:
                self.destroy()
                exit()

        self.history.append(history_to_add)
        self.undo_last_move_button.config(state="normal")
        self.restart_game_button.config(state="normal")
        self.redo_last_move_button.disable()
        self.update_idletasks()

    def generate_drawing_count(self, ace_slot):
        ace_slots = self.canvas.find_withtag("empty_ace_slot")
        positions_of_ace_rects = []
        for slot in ace_slots:
            positions_of_ace_rects.append(self.canvas.bbox(slot))
        returnval = False
        for i in positions_of_ace_rects:
            if str(self.current_image_bbox) == str(i):
                returnval = True
        if returnval is False:
            self.card_drawing_count = 20
        else:
            self.card_drawing_count = 0
        if "king" in self.last_active_card and "empty_slot" in self.current_image_tags:
            self.card_drawing_count = 0
        if ace_slot:
            self.cards_on_ace += 1
            self.points_label["text"] = (
                    "Points: " + str((self.cards_on_ace * self.point_increment) + self.starting_points))
            self.card_drawing_count = 0
            new_card_on_ace = 1
            self.canvas_item_hover_time += 300
            return new_card_on_ace


def main():
    window = SolitareGameWindow()
    window.mainloop()


if __name__ == "__main__":
    main()