from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import tkinter as tk
import time
import os
import random
import string

WORDS_FILE = os.path.join(os.path.dirname(__file__), "assets", "words.txt")

CORRECT_COLOR = "#E2E2E3"
INCORRECT_COLOR = "#FC5D7C"
EXTRA_COLOR = "#ECAC6A"
BG_COLOR = "#2C2E34"
KB_BG_COLOR = "#232429"
TXT_COLOR = "#E7C664"
TXT2_COLOR = "#8ED05D"


class CreateToolTip:
    def __init__(self, widget, text='widget info', position="above", arrow=True):
        self.widget = widget
        self.text = text
        self.waittime = 500     
        self.wraplength = 180   
        self.position = position
        self.has_arrow = arrow
        self.id = None
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = None

    def showtip(self, event=None):
        if self.tw or not self.text:
            return

        widget = self.widget
        widget.update_idletasks()
        wx = widget.winfo_rootx()
        wy = widget.winfo_rooty()
        ww = widget.winfo_width()
        wh = widget.winfo_height()

        self.tw = tk.Toplevel(widget)
        self.tw.wm_overrideredirect(True)

        frame = tk.Frame(self.tw, bg="#000", borderwidth=1, relief="solid")
        frame.pack()

        self.label_widget = tk.Label(
            frame, text=self.text, justify='left',
            background="#000", foreground="#fff",
            wraplength=self.wraplength, font=("Helvetica", 10)
        )
        self.label_widget.pack(padx=4, pady=(4, 2))

        arrow_height = 6
        if self.has_arrow:
            if self.position == "above":
                canvas = tk.Canvas(frame, bg="#000", width=20, height=arrow_height, highlightthickness=0)
                canvas.pack()
                canvas.create_polygon(10 - 5, 0, 10 + 5, 0, 10, arrow_height, fill="#000", outline="#000")
            elif self.position == "below":
                canvas = tk.Canvas(frame, bg="#000", width=20, height=arrow_height, highlightthickness=0)
                canvas.pack(side="top")
                canvas.create_polygon(10 - 5, arrow_height, 10 + 5, arrow_height, 10, 0, fill="#000", outline="#000")

        self.tw.update_idletasks()
        tip_width = self.tw.winfo_width()
        tip_height = self.tw.winfo_height()

        widget_center = wx + ww / 2
        if self.position == "above":
            tip_x = int(widget_center - tip_width / 2)
            tip_y = int(wy - tip_height - 5)
        else:
            tip_x = int(widget_center - tip_width / 2)
            tip_y = int(wy + wh + 5)
        self.tw.wm_geometry(f"+{tip_x}+{tip_y}")

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
        self.tw = None


class TypingSpeedTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Tester")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.config(bg="#464646")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground="#fff", font=("Helvetica", 14))
        style.configure("Title.TLabel", background=BG_COLOR, foreground=TXT_COLOR, font=("Helvetica", 18, "bold"))
        style.configure("Progress.TLabel", background=BG_COLOR, foreground=TXT2_COLOR)
        style.configure("TButton", font=("Helvetica", 12))

        self.mode = "time"       
        self.selected_time = 15  
        self.selected_words = 0
        self.countdown_running = False
        self.custom_prompt = None 

        self.start_time = None
        self.test_running = False
        self.finished = False
        self.tab_pressed_flag = False

        self.sample_words = []  
        self.user_input = ""

        self.keysym_map = {
            'q': 'q', 'w': 'w', 'e': 'e', 'r': 'r', 't': 't', 'y': 'y', 
            'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p',
            'bracketleft': '[', 'bracketright': ']',
            'a': 'a', 's': 's', 'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 
            'j': 'j', 'k': 'k', 'l': 'l',
            'semicolon': ';', 'apostrophe': "'",
            'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b', 'n': 'n', 
            'm': 'm', 'comma': ',', 'period': '.', 'slash': '/',
            'space': ' '
        }

        self.allow_commas = False

        redo_img_path = os.path.join(os.path.dirname(__file__), "assets", "redo-alt-solid.png")
        redo_img_hover_path = os.path.join(os.path.dirname(__file__), "assets", "redo-alt-solid-hover.png")
        redo_img = Image.open(redo_img_path).convert("RGBA").resize((25, 25), Image.Resampling.LANCZOS)
        redo_img_hover = Image.open(redo_img_hover_path).convert("RGBA").resize((26, 26), Image.Resampling.LANCZOS)
        self.redo_icon = ImageTk.PhotoImage(redo_img)
        self.redo_icon_hover = ImageTk.PhotoImage(redo_img_hover)

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        self.build_menu_bar()

        self.build_test_page()

        self.root.bind("<Key>", self.on_key)


    def build_menu_bar(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        mode_menu = tk.Menu(menu_bar, tearoff=0)
        mode_menu.add_command(label="Time Mode: 15s", command=lambda: self.set_mode("time", 15))
        mode_menu.add_command(label="Time Mode: 30s", command=lambda: self.set_mode("time", 30))
        mode_menu.add_command(label="Time Mode: 60s", command=lambda: self.set_mode("time", 60))
        mode_menu.add_command(label="Time Mode: 120s", command=lambda: self.set_mode("time", 120))
        mode_menu.add_separator()
        mode_menu.add_command(label="Words Mode: 10", command=lambda: self.set_mode("words", 10))
        mode_menu.add_command(label="Words Mode: 25", command=lambda: self.set_mode("words", 25))
        mode_menu.add_command(label="Words Mode: 50", command=lambda: self.set_mode("words", 50))
        mode_menu.add_command(label="Words Mode: 100", command=lambda: self.set_mode("words", 100))
        menu_bar.add_cascade(label="Mode", menu=mode_menu)

        custom_menu = tk.Menu(menu_bar, tearoff=0)
        custom_menu.add_command(label="Set Custom Prompt", command=self.set_custom_prompt)
        menu_bar.add_cascade(label="Custom", menu=custom_menu)

        punctuation_menu = tk.Menu(menu_bar, tearoff=0)
        self.allow_commas_var = tk.BooleanVar(value=self.allow_commas)
        punctuation_menu.add_checkbutton(
            label="Allow Commas",
            variable=self.allow_commas_var,
            command=lambda: self.set_allow_commas(self.allow_commas_var.get())
        )
        menu_bar.add_cascade(label="Punctuation", menu=punctuation_menu)


    def set_allow_commas(self, value):
        self.allow_commas = value
        self.reset_test()


    def set_mode(self, mode, value):
        self.mode = mode
        if mode == "time":
            self.selected_time = value
            self.selected_words = 0
        else:
            self.selected_time = 0
            self.selected_words = value
        self.custom_prompt = None
        self.reset_test()


    def set_custom_prompt(self):
        custom = simpledialog.askstring("Custom Prompt", "Enter your custom prompt (words separated by spaces):")
        if custom:
            self.custom_prompt = custom
            self.mode = "words"
            self.selected_words = len(custom.split())
            self.reset_test()


    def build_test_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.title_label = ttk.Label(self.main_frame, text="Burger Type", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))

        self.progress_label = ttk.Label(self.main_frame, text="Start typing to begin the test!", style="Progress.TLabel")
        self.progress_label.pack(pady=10)

        self.load_random_words()

        self.text_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.text_frame.pack(fill="both", expand=True, pady=10)

        self.display = tk.Text(self.text_frame, height=5, wrap="word", font=("Helvetica", 14), bg=BG_COLOR,  bd=0, relief="flat", highlightthickness=0)
        self.display.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.text_frame, bg=BG_COLOR, activebackground=BG_COLOR, bd=0, highlightthickness=0)
        self.scrollbar.pack(side="right", fill="y")

        self.display.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.display.yview)
        self.display.pack(fill="both", expand=True, pady=10)
        self.display.tag_config("correct", foreground=CORRECT_COLOR)
        self.display.tag_config("incorrect", foreground=INCORRECT_COLOR)
        self.display.tag_config("not_typed", foreground=TXT_COLOR)
        self.display.tag_config("extra", foreground=EXTRA_COLOR)
        self.display.config(state="disabled")

        self.build_keyboard()

        self.restart_button = tk.Button(self.main_frame, image=self.redo_icon, command=self.reset_test, bg=BG_COLOR, activebackground=BG_COLOR, bd=0, highlightthickness=0)
        self.restart_button.pack(pady=10)
        CreateToolTip(self.restart_button, text="Restart test", position="below", arrow=True)
        self.restart_button.bind("<Enter>", lambda e: self.restart_button.config(image=self.redo_icon_hover))
        self.restart_button.bind("<Leave>", lambda e: self.restart_button.config(image=self.redo_icon))

        self.update_display()


    def build_keyboard(self):
        self.key_labels = {}
        self.keyboard_frame = ttk.Frame(self.main_frame)
        self.keyboard_frame.pack(pady=10)

        keyboard_rows = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
            ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
        ]

        for row_keys in keyboard_rows:
            row_frame = tk.Frame(self.keyboard_frame, bg=BG_COLOR)
            row_frame.pack(pady=2)
            for key in row_keys:
                lbl = tk.Label(
                    row_frame, text=key, bg=KB_BG_COLOR, fg=TXT_COLOR,
                    width=3, height=1, font=("Helvetica", 14), padx=5, pady=5
                )
                lbl.pack(side="left", padx=2)
                self.key_labels[key] = lbl

        space_frame = tk.Frame(self.keyboard_frame, bg=BG_COLOR)
        space_frame.pack(pady=2)
        space_lbl = tk.Label(space_frame, text="space", bg=KB_BG_COLOR, fg=TXT_COLOR, width=10, height=1, font=("Helvetica", 14), padx=5, pady=5)
        space_lbl.pack(side="left", padx=2)
        self.key_labels[" "] = space_lbl


    def load_random_words(self):
        if self.custom_prompt is not None:
            all_words = self.custom_prompt.split()
        elif not os.path.isfile(WORDS_FILE):
            all_words = "The quick brown fox jumps over the lazy dog".split()
        else:
            with open(WORDS_FILE, "r") as f:
                content = f.read()
            all_words = content.split()

        if not self.allow_commas:
            all_words = [word.replace(",", "") for word in all_words]

        random.shuffle(all_words)

        if self.custom_prompt is not None:
            self.sample_words = all_words
        elif self.mode == "time":
            self.sample_words = all_words[:200] if len(all_words) > 200 else all_words
        else:
            self.sample_words = all_words[:self.selected_words] if len(all_words) >= self.selected_words else all_words
        if self.sample_words:
            self.sample_words[-1] = self.sample_words[-1].rstrip(string.punctuation)


    def on_key(self, event):
        if event.keysym == "Tab":
            self.tab_pressed_flag = True
            return
        elif event.keysym == "Return" and self.tab_pressed_flag:
            self.reset_test()
            self.tab_pressed_flag = False
            return
        else:
            self.tab_pressed_flag = False

        ks = event.keysym.lower()
        if ks in self.keysym_map:
            real_char = self.keysym_map[ks]
            self.highlight_key(real_char)

        if not self.test_running and not self.finished:
            if event.char and event.char.isprintable():
                self.start_test()

        if event.keysym == "BackSpace":
            self.user_input = self.user_input[:-1]
        elif event.char and event.char.isprintable():
            self.user_input += event.char

        self.update_display()

        if self.test_running and self.mode == "words":
            typed_words = self.user_input.split()
            if len(typed_words) >= len(self.sample_words):
                self.finish_test()

        self.root.after(100, lambda: self.unhighlight_key(self.keysym_map.get(ks, "")))


    def highlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl:
            lbl.config(bg="#555")


    def unhighlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl and lbl.winfo_exists():
            try:
                lbl.config(bg=KB_BG_COLOR)
            except tk.TclError:
                pass


    def start_test(self):
        self.start_time = time.time()
        self.test_running = True
        self.finished = False

        if self.mode == "time":
            self.countdown_running = True
            self.update_timer()


    def update_timer(self):
        if self.test_running and self.countdown_running:
            elapsed = time.time() - self.start_time
            remaining = self.selected_time - elapsed
            if remaining <= 0:
                self.finish_test()
                return
            else:
                self.progress_label.config(text=f"Time Left: {int(remaining)} s")
                self.root.after(500, self.update_timer)


    def update_display(self):
        self.display.config(state="normal")
        self.display.delete("1.0", tk.END)

        typed_words = self.user_input.split(" ")

        for i, expected_word in enumerate(self.sample_words):
            typed_word = typed_words[i] if i < len(typed_words) else ""
            for j, char in enumerate(expected_word):
                if j < len(typed_word):
                    if typed_word[j] == char:
                        self.display.insert(tk.END, char, "correct")
                    else:
                        self.display.insert(tk.END, char, "incorrect")
                else:
                    self.display.insert(tk.END, char, "not_typed")
            if len(typed_word) > len(expected_word):
                extra = typed_word[len(expected_word):]
                self.display.insert(tk.END, extra, "extra")

            if i < len(self.sample_words) - 1:
                if i < len(typed_words) - 1:
                    self.display.insert(tk.END, " ", "correct")
                else:
                    self.display.insert(tk.END, " ", "not_typed")

        self.display.config(state="disabled")

        if self.mode == "words" and self.test_running:
            typed_count = len([w for w in typed_words if w.strip()])
            total = len(self.sample_words)
            self.progress_label.config(text=f"Words: {typed_count}/{total}")


    def finish_test(self):
        if self.finished:
            return
        self.finished = True
        self.test_running = False
        self.countdown_running = False

        end_time = time.time()
        elapsed = end_time - self.start_time if self.start_time else 0

        full_sample_text = " ".join(self.sample_words)
        typed_text = self.user_input[:len(full_sample_text)]
        correct_chars = sum(1 for i in range(len(typed_text))
                            if typed_text[i] == full_sample_text[i])
        total_chars = len(typed_text)
        incorrect_chars = total_chars - correct_chars

        accuracy = (correct_chars / total_chars * 100) if total_chars else 0

        time_in_minutes = elapsed / 60 if elapsed > 0 else 1
        raw_wpm = (total_chars / 5) / time_in_minutes if elapsed > 0 else 0
        adjusted_wpm = raw_wpm * (accuracy / 100)

        self.show_result_page(elapsed, raw_wpm, adjusted_wpm, accuracy, correct_chars, incorrect_chars)


    def show_result_page(self, elapsed, raw_wpm, adjusted_wpm, accuracy, correct_chars, incorrect_chars):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        result_title = ttk.Label(self.main_frame, text="Test Results", style="Title.TLabel")
        result_title.pack(pady=(0, 20))

        time_label = ttk.Label(self.main_frame, text=f"Time: {elapsed:.1f} sec")
        time_label.pack(pady=10)

        raw_frame = ttk.Frame(self.main_frame)
        raw_frame.pack(pady=10)
        raw_text_label = ttk.Label(raw_frame, text="Raw WPM: ", font=("Helvetica", 14))
        raw_text_label.pack(side="left")
        raw_number_label = ttk.Label(raw_frame, text=f"{int(round(raw_wpm))}", font=("Helvetica", 14))
        raw_number_label.pack(side="left")
        CreateToolTip(raw_number_label, text=f"{raw_wpm:.2f} wpm", position="above", arrow=True)

        adjusted_frame = ttk.Frame(self.main_frame)
        adjusted_frame.pack(pady=10)
        adjusted_text_label = ttk.Label(adjusted_frame, text="Adjusted WPM: ", font=("Helvetica", 14))
        adjusted_text_label.pack(side="left")
        adjusted_number_label = ttk.Label(adjusted_frame, text=f"{int(round(adjusted_wpm))}", font=("Helvetica", 14))
        adjusted_number_label.pack(side="left")
        CreateToolTip(adjusted_number_label, text=f"{adjusted_wpm:.2f} wpm", position="above", arrow=True)

        accuracy_frame = ttk.Frame(self.main_frame)
        accuracy_frame.pack(pady=10)
        accuracy_text_label = ttk.Label(accuracy_frame, text="Accuracy: ", font=("Helvetica", 14))
        accuracy_text_label.pack(side="left")
        accuracy_number_label = ttk.Label(accuracy_frame, text=f"{accuracy:.1f}%", font=("Helvetica", 14))
        accuracy_number_label.pack(side="left")
        CreateToolTip(accuracy_number_label, text=f"{accuracy:.2f}%\n{correct_chars} correct\n{incorrect_chars} incorrect", position="above", arrow=True)

        self.restart_button = tk.Button(self.main_frame, image=self.redo_icon, command=self.reset_test, bg=BG_COLOR, activebackground=BG_COLOR, bd=0, highlightthickness=0)
        self.restart_button.pack(pady=10)
        CreateToolTip(self.restart_button, text="Restart test", position="below", arrow=True)
        self.restart_button.bind("<Enter>", lambda e: self.restart_button.config(image=self.redo_icon_hover))
        self.restart_button.bind("<Leave>", lambda e: self.restart_button.config(image=self.redo_icon))


    def reset_test(self):
        self.test_running = False
        self.finished = False
        self.start_time = None
        self.user_input = ""
        self.countdown_running = False
        self.build_test_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTester(root)
    root.mainloop()
