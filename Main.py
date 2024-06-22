import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
from pynput import keyboard
import time
import os
import signal
import sys

class TypingSimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Typing Simulator")
        self.text_lists = {}
        self.typing_speed = 0.05  # Default typing speed
        self.last_execution_time = 0
        self.cooldown = 1  # 1 second cooldown between executions
        self.typing_active = False
        self.waiting_for_key = False
        self.default_texts = {
            '1': "Default text for key 1",
            '2': "Default text for key 2",
            '3': "Default text for key 3",
            '4': "Default text for key 4",
            '5': "Default text for key 5",
            '6': "Default text for key 6",
            '7': "Default text for key 7",
            '8': "Default text for key 8",
            '9': "Default text for key 9"
        }
        self.setup_gui()
        self.load_text_lists()
        self.setup_key_listener()

    def setup_gui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=20)
    
        self.textbox = tk.Text(self.frame, width=50, height=10)
        self.textbox.pack(pady=10)
    
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill="x", padx=10)
    
        self.add_button = tk.Button(button_frame, text="Add Text", command=self.add_text)
        self.add_button.pack(side=tk.LEFT, padx=5)
    
        self.show_keybinds_button = tk.Button(button_frame, text="Show Keybinds", command=self.show_keybinds)
        self.show_keybinds_button.pack(side=tk.BOTTOM, padx=5)
    
        self.config_button = tk.Button(self.frame, text="Settings", command=self.open_settings)
        self.config_button.pack(side=tk.LEFT, padx=5)

    def show_keybinds(self):
        # Close existing keybind window if it exists
        if hasattr(self, 'keybind_window') and self.keybind_window is not None:
         self.keybind_window.destroy()

        self.keybind_window = tk.Toplevel(self.master)
        self.keybind_window.title("Keybinds")
        self.keybind_window.geometry("400x300")

        # Create a canvas with a scrollbar
        canvas = tk.Canvas(self.keybind_window)
        scrollbar = tk.Scrollbar(self.keybind_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for key, text in self.text_lists.items():
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=5)

            button = tk.Button(frame, text=f"Change '{key}'", command=lambda k=key: self.change_keybind(k))
            button.pack(side="left")

            text_area = tk.Text(frame, height=3, width=30)
            text_area.insert(tk.END, text)
            text_area.config(state="disabled")
            text_area.pack(side="left", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def change_keybind(self, old_key):
        keybind_window = tk.Toplevel(self.master)
        keybind_window.title("Change Keybind")
        keybind_window.geometry("300x100")
    
        label = tk.Label(keybind_window, text=f"Press any key to change the keybind for '{old_key}'")
        label.pack(pady=10)
    
        def set_new_keybind(event):
            new_key = event.keysym
            text = self.text_lists.pop(old_key)
            self.text_lists[new_key] = text
            self.save_text_lists()
            print(f"Debug: Changed keybind from '{old_key}' to '{new_key}'")
            messagebox.showinfo("Success", f"Keybind changed from '{old_key}' to '{new_key}'")
            keybind_window.destroy()
            self.show_keybinds()  # Refresh the keybinds window

        keybind_window.bind('<KeyPress>', set_new_keybind)

    def simulate_typing(self):
        pass
    
    def add_text(self):
        text = self.textbox.get("1.0", tk.END).strip()
        if text:
            self.open_keybind_window(text)
        else:
            messagebox.showerror("Error", "Text cannot be empty.")

    def open_keybind_window(self, text):
        keybind_window = tk.Toplevel(self.master)
        keybind_window.title("Set Keybind")
        keybind_window.geometry("300x100")
    
        label = tk.Label(keybind_window, text="Press any key to set as keybind")
        label.pack(pady=10)
    
        keybind_window.bind('<KeyPress>', lambda event: self.set_keybind(event, text, keybind_window))

    def set_keybind(self, event, text, window):
        key = event.keysym
        self.text_lists[key.lower()] = text
        self.save_text_lists()
        print(f"Debug: Added keybind '{key}' for text: {text}")
        print(f"Debug: Updated text_lists: {self.text_lists}")
        messagebox.showinfo("Success", f"Text added for keybind '{key}'.")
        window.destroy()

    def on_key_press_for_binding(self, event):
        print(f"Debug: Key pressed for binding: {event.keysym}")
        if self.waiting_for_key:
            key = event.keysym
            text = self.textbox.get("1.0", tk.END).strip()
            self.text_lists[key] = text
            self.save_text_lists()
            print(f"Debug: Updated text_lists: {self.text_lists}")
            messagebox.showinfo("Success", f"Text added for keybind '{key}'.")
            self.waiting_for_key = False
            self.master.unbind('<KeyPress>')
        else:
            print("Debug: Not waiting for key, ignoring key press")
    
    def save_text_lists(self):
        with open("text_lists.txt", "w") as file:
            for key, text in self.text_lists.items():
                file.write(f"{key}:{text}\n")
        print("Debug: Saved text_lists to text_lists.txt")

    def load_text_lists(self):
        if not os.path.exists("text_lists.txt"):
            self.create_default_text_lists()
        else:
            try:
                with open("text_lists.txt", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        key, text = line.strip().split(":", 1)
                        self.text_lists[key] = text
                print(f"Debug: Loaded text_lists from file: {self.text_lists}")
            except FileNotFoundError:
                pass

    def create_default_text_lists(self):
        self.default_texts = {
            '1': "Default text for key 1",
            '2': "Default text for key 2",
            '3': "Default text for key 3",
            '4': "Default text for key 4",
            '5': "Default text for key 5",
        }
        with open("text_lists.txt", "w") as file:
            for key, text in self.default_texts.items():
                file.write(f"{key}:{text}\n")
        self.text_lists = self.default_texts.copy()
        print("Debug: Created default text_lists")

    def open_settings(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")
        
        speed_label = tk.Label(settings_win, text="Typing Speed (seconds per character):")
        speed_label.pack(pady=10)
        
        self.speed_entry = tk.Entry(settings_win)
        self.speed_entry.insert(0, str(self.typing_speed))
        self.speed_entry.pack(pady=5)
        
        save_button = tk.Button(settings_win, text="Save", command=self.save_settings)
        save_button.pack(pady=10)
    
    def save_settings(self):
        try:
            new_speed = float(self.speed_entry.get())
            if new_speed <= 0:
                raise ValueError("Typing speed must be a positive number.")
            self.typing_speed = new_speed
            messagebox.showinfo("Success", "Settings saved successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def setup_key_listener(self):
        def on_press(key):
            try:
                print(f"Debug: Key pressed in listener: {key}")
                key_char = key.char if hasattr(key, 'char') else key.name
                print(f"Debug: key char press is {key_char}")
                if key_char.lower() in self.text_lists:
                    print(f"Debug: key found in {self.text_lists.get(key_char)}")
                    current_time = time.time()
                    if (not self.typing_active and 
                    current_time - self.last_execution_time > self.cooldown):
                        self.typing_active = True
                        self.last_execution_time = current_time
                        text = self.text_lists[key_char]
                        print(f"Debug: Typing text for key {key_char}: {text}")
                        self.master.after(100, lambda t=text: self.type_text(t))
            except Exception as e:
                print(f"Debug: Error in key listener: {e}")
            return True

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        print("Debug: Key listener started")

    def type_text(self, text):
        print(f"Debug: Entering type_text method with text: {text}")
        self.master.after(100, lambda: self._perform_typing(text))

    def _perform_typing(self, text):
        pyautogui.press('enter')
        print(f"Debug: Typing text: {text}")
        pyautogui.typewrite(text, interval=self.typing_speed)
        pyautogui.press('enter')
        self.typing_active = False
        print("Debug: Finished typing, set typing_active to False")

    def setup_signal_handlers(self):
        def signal_handler(sig, frame):
            print("Exiting gracefully...")
            if hasattr(self, 'listener'):
                self.listener.stop()
                self.listener.join()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSimulatorApp(root)
    root.mainloop()
