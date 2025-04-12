import tkinter as tk
from tkinter import ttk
from tkinter import font
import time

# sample test
SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog."

class TypingSpeedTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Tester")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#333", font=("Helvetica", 14))
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TButton", font=("Helvetica", 12))

        self.start_time = None
        self.elapsed_time = 0
        self.test_running = False
        
        self.main_frame = ttk.Frame(root, padding="20 20 20 20")
        self.main_frame.pack(expand=True, fill="both")
        
        self.title_label = ttk.Label(self.main_frame, text="Typing Speed Tester", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))

        self.sample_frame = ttk.Frame(self.main_frame)
        self.sample_frame.pack(fill="x", pady=(0, 10))
        
        self.sample_label = ttk.Label(self.sample_frame, text=SAMPLE_TEXT, wraplength=650, justify="center")
        self.sample_label.pack(pady=10)

        self.timer_label = ttk.Label(self.main_frame, text="Time: 0 sec")
        self.timer_label.pack(pady=(0, 10))

        self.input_text = tk.Text(self.main_frame, height=8, wrap="word", font=("Helvetica", 14))
        self.input_text.config(state="disabled") 
        self.input_text.pack(fill="both", pady=(0, 10))

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=(0, 10))
        
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_test)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.submit_button = ttk.Button(self.button_frame, text="Submit", command=self.submit_test, state="disabled")
        self.submit_button.grid(row=0, column=1, padx=10)
        
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_test)
        self.reset_button.grid(row=0, column=2, padx=10)

        self.result_frame = ttk.Frame(self.main_frame)
        self.result_frame.pack(pady=10, fill="x")
        self.result_label = ttk.Label(self.result_frame, text="", font=("Helvetica", 14))
        self.result_label.pack()
    
    def start_test(self):
        """Begin the typing test by resetting timers and enabling input."""
        self.input_text.config(state="normal")
        self.input_text.delete("1.0", tk.END)
        self.start_time = time.time()
        self.test_running = True
        self.result_label.config(text="")
        self.start_button.config(state="disabled")
        self.submit_button.config(state="normal")
        self.update_timer()

    def update_timer(self):
        """Update the displayed timer every 100 ms."""
        if self.test_running:
            self.elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {int(self.elapsed_time)} sec")
            self.root.after(100, self.update_timer)

    def submit_test(self):
        """Stop the test and calculate speed and accuracy."""
        if not self.test_running:
            return
        
        self.test_running = False
        self.input_text.config(state="disabled")
        total_time = time.time() - self.start_time
        typed_text = self.input_text.get("1.0", tk.END).strip()
        
        wpm = (len(typed_text) / 5) / (total_time / 60) if total_time > 0 else 0

        sample = SAMPLE_TEXT
        total_chars = len(sample)
        correct_chars = sum(1 for i in range(min(len(typed_text), len(sample))) if typed_text[i] == sample[i])
        accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0

        result_text = (
            f"Results:\n"
            f"Time Taken: {total_time:.1f} seconds\n"
            f"Words Per Minute (WPM): {wpm:.1f}\n"
            f"Accuracy: {accuracy:.1f}%"
        )
        self.result_label.config(text=result_text)
        self.start_button.config(state="normal")
        self.submit_button.config(state="disabled")
    
    def reset_test(self):
        """Reset the test to its initial state."""
        self.test_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.timer_label.config(text="Time: 0 sec")
        self.input_text.config(state="normal")
        self.input_text.delete("1.0", tk.END)
        self.input_text.config(state="disabled")
        self.result_label.config(text="")
        self.start_button.config(state="normal")
        self.submit_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTester(root)
    root.mainloop()
