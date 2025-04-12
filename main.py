import tkinter as tk
from tkinter import ttk
import time

SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog."

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
        style.configure("TFrame", background="#2f2f2f")
        style.configure("TLabel", background="#2f2f2f", foreground="#fff", font=("Helvetica", 14))
        style.configure("Title.TLabel", background="#2f2f2f", foreground="#f1c40f", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 12))
        
        self.start_time = None
        self.test_running = False
        self.finished = False
        self.tab_pressed_flag = False
        self.sample_words = SAMPLE_TEXT.split()

        self.keysym_map = {
            'q': 'q', 'w': 'w', 'e': 'e', 'r': 'r', 't': 't', 'y': 'y', 
            'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p',
            'bracketleft': '[', 'bracketright': ']',

            'a': 'a', 's': 's', 'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 
            'j': 'j', 'k': 'k', 'l': 'l',
            'semicolon': ';', 'apostrophe': "'",

            'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b', 'n': 'n', 
            'm': 'm', 'comma': ',', 'period': '.', 'slash': '/',

            'space': ' ', 
        }

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        self.build_test_page()

    def build_test_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.title_label = ttk.Label(self.main_frame, text="Burger Type", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))

        self.sample_label = ttk.Label(self.main_frame, text=SAMPLE_TEXT, wraplength=650, justify="center")
        self.sample_label.pack(pady=10)

        self.progress_label = ttk.Label(self.main_frame, text="Start typing to begin the test.")
        self.progress_label.pack(pady=10)

        self.input_text = tk.Text(self.main_frame, height=5, wrap="word", font=("Helvetica", 14), bg="#222", fg="#fff", insertbackground="#fff")
        self.input_text.pack(fill="x", pady=10)
        self.input_text.focus_set()

        self.keyboard_frame = ttk.Frame(self.main_frame)
        self.keyboard_frame.pack(pady=10)

        self.build_keyboard()

        self.restart_button = ttk.Button(self.main_frame, text="Restart", command=self.reset_test)
        self.restart_button.pack(pady=10)

        self.input_text.bind("<KeyRelease>", self.on_key_release)
        self.root.bind_all("<KeyPress>", self.on_key_press)
        self.root.bind_all("<KeyRelease>", self.on_key_release)

    def build_keyboard(self):
        self.key_labels = {} 

        keyboard_rows = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
            ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
        ]
        
        for row_keys in keyboard_rows:
            row_frame = tk.Frame(self.keyboard_frame, bg="#2f2f2f")
            row_frame.pack(pady=2)

            for key in row_keys:
                lbl = tk.Label(row_frame, text=key, bg="#333", fg="#f1c40f", width=3, height=1, font=("Helvetica", 14), padx=5, pady=5)
                lbl.pack(side="left", padx=2)
                self.key_labels[key] = lbl

        space_frame = tk.Frame(self.keyboard_frame, bg="#2f2f2f")
        space_frame.pack(pady=2)

        space_lbl = tk.Label(space_frame, text="space", bg="#333", fg="#f1c40f", width=10, height=1, font=("Helvetica", 14), padx=5, pady=5)
        space_lbl.pack(side="left", padx=2)
        self.key_labels[" "] = space_lbl  

    def highlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl:
            lbl.config(bg="#555")  

    def unhighlight_key(self, key):
        lbl = self.key_labels.get(key)
        if lbl:
            lbl.config(bg="#333")

    def on_key_press(self, event):
        if event.keysym == "Tab":
            self.tab_pressed_flag = True
        elif event.keysym == "Return" and self.tab_pressed_flag:
            self.reset_test()
            self.tab_pressed_flag = False
        else:
            self.tab_pressed_flag = False

        ks = event.keysym.lower()
        if ks in self.keysym_map:
            real_char = self.keysym_map[ks]
            self.highlight_key(real_char)

    def on_key_release(self, event):
        if not self.test_running and not self.finished:
            content = self.input_text.get("1.0", "end-1c")
            if content.strip():
                self.start_test()

        if self.test_running and not self.finished:
            self.update_progress()
            content = self.input_text.get("1.0", "end-1c")
            if len(content) >= len(SAMPLE_TEXT):
                self.finish_test()

        ks = event.keysym.lower()
        if ks in self.keysym_map:
            real_char = self.keysym_map[ks]
            self.unhighlight_key(real_char)

    def start_test(self):
        self.start_time = time.time()
        self.test_running = True

    def update_progress(self):
        text = self.input_text.get("1.0", "end-1c")
        if not text:
            finished_count = 0
        else:
            if text.endswith(" "):
                finished_count = len(text.split())
            else:
                words = text.split()
                finished_count = max(len(words) - 1, 0)
        self.progress_label.config(text=f"Words: {finished_count}/{len(self.sample_words)}")

    def finish_test(self):
        self.finished = True
        self.test_running = False
        end_time = time.time()
        elapsed = end_time - self.start_time

        content = self.input_text.get("1.0", "end-1c")
        typed_text = content[:len(SAMPLE_TEXT)]

        raw_wpm = (len(SAMPLE_TEXT) / 5) / (elapsed / 60) if elapsed > 0 else 0
        correct_chars = sum(1 for i in range(len(SAMPLE_TEXT)) if typed_text[i] == SAMPLE_TEXT[i])
        incorrect_chars = len(SAMPLE_TEXT) - correct_chars
        accuracy = (correct_chars / len(SAMPLE_TEXT)) * 100
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
        CreateToolTip(raw_label, text=f"Raw WPM (actual): {raw_wpm:.1f}")

        adjusted_label = ttk.Label(self.main_frame, text=f"Adjusted WPM: {adjusted_wpm_round}")
        adjusted_label.pack(pady=10)
        CreateToolTip(adjusted_label, text=f"Adjusted WPM (actual): {adjusted_wpm:.1f}")

        accuracy_label = ttk.Label(
            self.main_frame,
            text=f"Accuracy: {accuracy:.1f}% (Correct: {correct_chars}, Incorrect: {incorrect_chars})"
        )
        accuracy_label.pack(pady=10)

        self.restart_button = ttk.Button(self.main_frame, text="Restart", command=self.reset_test)
        self.restart_button.pack(pady=10)

    def reset_test(self):
        self.test_running = False
        self.finished = False
        self.start_time = None
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.build_test_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTester(root)
    root.mainloop()
