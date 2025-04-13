import tkinter as tk
from tkinter import ttk
import time

SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog."

CORRECT_COLOR = "#FFFFFF"  
INCORRECT_COLOR = "#FF0000"
EXTRA_COLOR   = "#FFA500"   
BG_COLOR = "#2C2E34"
KB_BG_COLOR = "#232429"
TXT_COLOR = "#E7C664"

class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.waittime = 500  
        self.wraplength = 180  
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
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + cy + 25
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, wraplength=self.wraplength, font=("Helvetica", 10))
        label.pack(ipadx=1)

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
        style.configure("TButton", font=("Helvetica", 12))
        
        self.start_time = None
        self.test_running = False
        self.finished = False
        self.tab_pressed_flag = False
        self.sample_words = SAMPLE_TEXT.split()
        
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
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        self.build_test_page()

        self.root.focus_set()

        self.root.bind("<Key>", self.on_key)

    def build_test_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.title_label = ttk.Label(self.main_frame, text="Burger Type", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))

        self.display = tk.Text(self.main_frame, height=5, wrap="word", font=("Helvetica", 14), 
                               bg="#222", bd=0, relief="flat", highlightthickness=0)
        self.display.pack(fill="x", pady=10)
        self.display.tag_config("correct", foreground=CORRECT_COLOR)
        self.display.tag_config("incorrect", foreground=INCORRECT_COLOR)
        self.display.tag_config("not_typed", foreground=TXT_COLOR)
        self.display.tag_config("extra", foreground=EXTRA_COLOR)
        self.display.config(state="disabled")

        self.progress_label = ttk.Label(self.main_frame, text="Start typing to begin the test.")
        self.progress_label.pack(pady=10)

        self.build_keyboard()

        self.restart_button = ttk.Button(self.main_frame, text="Restart", command=self.reset_test)
        self.restart_button.pack(pady=10)

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
                lbl = tk.Label(row_frame, text=key, bg=KB_BG_COLOR, fg=TXT_COLOR, width=3, height=1, 
                               font=("Helvetica", 14), padx=5, pady=5)
                lbl.pack(side="left", padx=2)
                self.key_labels[key] = lbl

        space_frame = tk.Frame(self.keyboard_frame, bg=BG_COLOR)
        space_frame.pack(pady=2)
        space_lbl = tk.Label(space_frame, text="space", bg=KB_BG_COLOR, fg=TXT_COLOR, width=10, height=1, 
                             font=("Helvetica", 14), padx=5, pady=5)
        space_lbl.pack(side="left", padx=2)
        self.key_labels[" "] = space_lbl  

    def highlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl:
            lbl.config(bg="#555")
    
    def unhighlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl:
            lbl.config(bg=KB_BG_COLOR)

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
            if event.char.isprintable() or event.keysym == "space":
                self.start_test()

        if event.keysym == "BackSpace":
            self.user_input = self.user_input[:-1]
        elif event.char and event.char.isprintable():
            self.user_input += event.char

        self.update_display()
        self.update_progress()

        typed_words = self.user_input.split(" ")
        if len(typed_words) > len(self.sample_words) or (
           len(typed_words) == len(self.sample_words) and len(typed_words[-1]) >= len(self.sample_words[-1])):
            self.finish_test()

        self.root.after(100, lambda: self.unhighlight_key(self.keysym_map.get(ks, "")))

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

    def update_progress(self):
        """Update the progress label to show words attempted."""
        typed_words = self.user_input.split(" ")
        finished_count = 0
        for i, word in enumerate(typed_words):
            if i < len(self.sample_words) and len(word) >= len(self.sample_words[i]):
                finished_count += 1
        self.progress_label.config(text=f"Words: {finished_count}/{len(self.sample_words)}")

    def start_test(self):
        self.start_time = time.time()
        self.test_running = True

    def finish_test(self):
        if self.finished: 
            return
        self.finished = True
        self.test_running = False
        end_time = time.time()
        elapsed = end_time - self.start_time if self.start_time else 0

        typed_text = self.user_input[:len(SAMPLE_TEXT)]
        correct_chars = sum(1 for i in range(len(SAMPLE_TEXT)) if i < len(typed_text) and typed_text[i] == SAMPLE_TEXT[i])
        incorrect_chars = len(SAMPLE_TEXT) - correct_chars
        accuracy = (correct_chars / len(SAMPLE_TEXT)) * 100
        raw_wpm = (len(SAMPLE_TEXT) / 5) / (elapsed / 60) if elapsed > 0 else 0
        adjusted_wpm = raw_wpm * (accuracy / 100)

        self.show_result_page(elapsed, raw_wpm, adjusted_wpm, accuracy, correct_chars, incorrect_chars)

    def show_result_page(self, elapsed, raw_wpm, adjusted_wpm, accuracy, correct_chars, incorrect_chars):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        result_title = ttk.Label(self.main_frame, text="Test Results", style="Title.TLabel")
        result_title.pack(pady=(0, 20))

        time_label = ttk.Label(self.main_frame, text=f"Time: {elapsed:.1f} sec")
        time_label.pack(pady=10)

        raw_wpm_round = round(raw_wpm)
        adjusted_wpm_round = round(adjusted_wpm)
        raw_label = ttk.Label(self.main_frame, text=f"Raw WPM: {raw_wpm_round}")
        raw_label.pack(pady=10)
        CreateToolTip(raw_label, text=f"{raw_wpm:.2f} wpm")

        adjusted_label = ttk.Label(self.main_frame, text=f"Adjusted WPM: {adjusted_wpm_round}")
        adjusted_label.pack(pady=10)
        CreateToolTip(adjusted_label, text=f"{adjusted_wpm:.2f} wpm")

        accuracy_round = round(accuracy)
        accuracy_label = ttk.Label(self.main_frame, text=f"Accuracy: {accuracy_round}%")
        accuracy_label.pack(pady=10)
        CreateToolTip(accuracy_label, text=f"{accuracy:.2f}%\n{correct_chars} correct\n{incorrect_chars} incorrect")

        self.restart_button = ttk.Button(self.main_frame, text="Restart", command=self.reset_test)
        self.restart_button.pack(pady=10)

    def reset_test(self):
        self.test_running = False
        self.finished = False
        self.start_time = None
        self.user_input = ""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.build_test_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTester(root)
    root.mainloop()
