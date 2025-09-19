import pynput.keyboard
import keyboard
import time
import random
import tkinter as tk
from tkinter import Frame, Label, Entry, Button, font
import threading
import ctypes
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

class SOCDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.key_left = 'a'
        self.key_right = 'd'

        self.is_simulating = False
        self.socd_enabled = True
        self.counter_strafe_enabled = False
        self.current_output = None
        self.min_delay = 0.030
        self.max_delay = 0.130
        self.key_states = {self.key_left: False, self.key_right: False}
        self.key_timestamps = {self.key_left: 0.0, self.key_right: 0.0}
        self.controller = pynput.keyboard.Controller()
        
        self.setup_ui()
        
        keyboard.hook(self._key_event_handler)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _pulse_key(self, key, pulse_time=0.05):
        self.is_simulating = True
        self.controller.press(key)
        time.sleep(pulse_time)
        self.controller.release(key)
        self.is_simulating = False

    def _update_socd_output(self):
        if not self.socd_enabled:
            return

        left_pressed = self.key_states[self.key_left]
        right_pressed = self.key_states[self.key_right]
        new_output = None

        if left_pressed and right_pressed:
            new_output = self.key_right if self.key_timestamps[self.key_right] > self.key_timestamps[self.key_left] else self.key_left
        elif left_pressed:
            new_output = self.key_left
        elif right_pressed:
            new_output = self.key_right

        if new_output != self.current_output:
            if self.current_output:
                self.is_simulating = True
                self.controller.release(self.current_output)
                self.is_simulating = False
            
            if new_output:
                delay = random.uniform(self.min_delay, self.max_delay)
                threading.Timer(delay, self._press_key, args=[new_output]).start()
            
            self.current_output = new_output
            
    def _press_key(self, key):
        self.is_simulating = True
        self.controller.press(key)
        self.is_simulating = False

    def _key_event_handler(self, event):
        if self.is_simulating or event.name not in (self.key_left, self.key_right):
            return True

        if event.event_type == 'down':
            if not self.key_states[event.name]:
                self.key_states[event.name] = True
                self.key_timestamps[event.name] = time.time()
        elif event.event_type == 'up':
            self.key_states[event.name] = False
            self.key_timestamps[event.name] = 0.0
            
            if self.counter_strafe_enabled:
                opposite_key = self.key_right if event.name == self.key_left else self.key_left
                if not self.key_states[opposite_key]:
                    threading.Thread(target=self._pulse_key, args=(opposite_key,), daemon=True).start()
        
        self._update_socd_output()
        return not self.socd_enabled

    def setup_ui(self):
        bg_color = "#2E2E2E"
        text_color = "#F5F5F5"
        entry_bg = "#3C3F41"
        accent_color = "#4A90E2"
        border_color = "#1E1E1E"
        error_color = "#FF5733"
        
        title_bar_bg = "#252525"
        button_bg = title_bar_bg
        button_hover_bg = "#3E3E3E"
        button_active_bg = "#555555"
        close_hover_bg = "#C81919"
        close_active_bg = "#A01414"

        self.geometry("420x300")
        self.configure(bg=bg_color)
        self.resizable(False, False)
        self.overrideredirect(True)

        title_bar = Frame(self, bg=title_bar_bg, relief='flat', bd=0, highlightthickness=0)
        title_bar.pack(fill=tk.X)

        title_label = Label(title_bar, text="SOCD Cleaner", bg=title_bar_bg, fg=text_color, font=("Segoe UI", 9, "bold"))
        title_label.pack(side=tk.LEFT, padx=10, pady=4)

        close_button = Button(title_bar, text='\u00D7', bg=button_bg, fg=text_color, relief='flat', bd=0,
                              activebackground=close_active_bg, activeforeground=text_color, 
                              command=self._on_closing, width=6, highlightthickness=0)
        close_button.pack(side=tk.RIGHT, fill=tk.Y)

        minimize_button = Button(title_bar, text='\u2212', bg=button_bg, fg=text_color, relief='flat', bd=0,
                                 activebackground=button_active_bg, activeforeground=text_color, 
                                 command=self.iconify, width=6, highlightthickness=0)
        minimize_button.pack(side=tk.RIGHT, fill=tk.Y)

        def on_enter_close(e): close_button.config(background=close_hover_bg)
        def on_leave_close(e): close_button.config(background=button_bg)
        def on_enter_minimize(e): minimize_button.config(background=button_hover_bg)
        def on_leave_minimize(e): minimize_button.config(background=button_bg)

        close_button.bind("<Enter>", on_enter_close)
        close_button.bind("<Leave>", on_leave_close)
        minimize_button.bind("<Enter>", on_enter_minimize)
        minimize_button.bind("<Leave>", on_leave_minimize)
        
        def start_move(event):
            self._offset_x = event.x
            self._offset_y = event.y
        def move_window(event):
            self.geometry(f'+{event.x_root - self._offset_x}+{event.y_root - self._offset_y}')
            
        title_bar.bind('<ButtonPress-1>', start_move)
        title_bar.bind('<B1-Motion>', move_window)
        title_label.bind('<ButtonPress-1>', start_move)
        title_label.bind('<B1-Motion>', move_window)

        try:
            icon_path = resource_path("uttanka.png") 
            if os.path.exists(icon_path):
                photo = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, photo)
        except tk.TclError:
            print("Warning: Could not load .png title bar icon.")

        label_font = font.Font(family="Segoe UI", size=10, weight="bold")
        entry_font = font.Font(family="Segoe UI", size=10)
        button_font = font.Font(family="Segoe UI", size=11, weight="bold")

        main_frame = Frame(self, bg=bg_color)
        main_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH)

        control_frame = Frame(main_frame, bg=bg_color)
        control_frame.pack(fill=tk.X, pady=5)
        control_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # --- MODIFICATION HERE: Added 'justify': 'center' ---
        common_entry_options = {
            'font': entry_font, 'width': 8, 'bg': entry_bg, 'fg': text_color, 
            'relief': 'flat', 'highlightbackground': border_color, 
            'highlightthickness': 1, 'insertbackground': text_color, 'justify': 'center'
        }
        
        Label(control_frame, text="LEFT KEY", font=label_font, bg=bg_color, fg=text_color).grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.left_key_entry = Entry(control_frame, **common_entry_options)
        self.left_key_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.left_key_entry.insert(0, self.key_left)
        
        Label(control_frame, text="RIGHT KEY", font=label_font, bg=bg_color, fg=text_color).grid(row=0, column=2, sticky=tk.W, padx=2, pady=2)
        self.right_key_entry = Entry(control_frame, **common_entry_options)
        self.right_key_entry.grid(row=0, column=3, sticky=tk.W, padx=2, pady=2)
        self.right_key_entry.insert(0, self.key_right)

        Label(control_frame, text="MIN DELAY (MS)", font=label_font, bg=bg_color, fg=text_color).grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.min_entry = Entry(control_frame, **common_entry_options)
        self.min_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.min_entry.insert(0, str(int(self.min_delay * 1000)))
        
        Label(control_frame, text="MAX DELAY (MS)", font=label_font, bg=bg_color, fg=text_color).grid(row=1, column=2, sticky=tk.W, padx=2, pady=2)
        self.max_entry = Entry(control_frame, **common_entry_options)
        self.max_entry.grid(row=1, column=3, sticky=tk.W, padx=2, pady=2)
        self.max_entry.insert(0, str(int(self.max_delay * 1000)))

        self.error_label = Label(main_frame, text="", font=label_font, bg=bg_color, fg=error_color)
        self.error_label.pack(pady=2)

        common_button_options = {'font': button_font, 'fg': text_color, 'relief': 'flat', 'activeforeground': text_color, 'bd': 0, 'cursor': "hand2"}

        self.toggle_button = Button(main_frame, text="SOCD: ON", **common_button_options, bg="#228B22", activebackground="#5C9E5C", command=self._toggle_socd)
        self.toggle_button.pack(fill=tk.X, pady=2, ipady=4)

        self.counter_strafe_button = Button(main_frame, text="COUNTER-STRAFE: OFF", **common_button_options, bg="#C70039", activebackground="#E57373", command=self._toggle_counter_strafe)
        self.counter_strafe_button.pack(fill=tk.X, pady=2, ipady=4)
        
        self.update_button = Button(main_frame, text="UPDATE SETTINGS", **common_button_options, bg=accent_color, activebackground="#5aaaff", command=self._update_settings_from_gui)
        self.update_button.pack(fill=tk.X, pady=2, ipady=4)

    def _update_settings_from_gui(self):
        try:
            min_val_ms = int(self.min_entry.get())
            max_val_ms = int(self.max_entry.get())
            if min_val_ms < 0 or max_val_ms < 0:
                self.error_label.config(text="Delays cannot be negative.")
                return
            if min_val_ms >= max_val_ms:
                self.error_label.config(text="Min delay must be less than Max.")
                return
            
            new_left_key = self.left_key_entry.get().lower().strip()
            new_right_key = self.right_key_entry.get().lower().strip()
            if len(new_left_key) != 1 or len(new_right_key) != 1:
                self.error_label.config(text="Keys must be a single character.")
                return
            if new_left_key == new_right_key:
                self.error_label.config(text="Left and Right keys cannot be the same.")
                return

            self.error_label.config(text="")
            self.min_delay = min_val_ms / 1000.0
            self.max_delay = max_val_ms / 1000.0
            
            if self.key_left != new_left_key or self.key_right != new_right_key:
                if self.current_output:
                    self.is_simulating = True
                    self.controller.release(self.current_output)
                    self.is_simulating = False
                
                self.key_left = new_left_key
                self.key_right = new_right_key
                self.key_states = {self.key_left: False, self.key_right: False}
                self.key_timestamps = {self.key_left: 0.0, self.key_right: 0.0}
                self.current_output = None

            self.update_button.config(text="UPDATED!")
            self.update_button.after(1000, lambda: self.update_button.config(text="UPDATE SETTINGS"))
        except ValueError:
            self.error_label.config(text="Please enter valid numbers for delays.")

    def _toggle_socd(self):
        self.socd_enabled = not self.socd_enabled
        if self.socd_enabled:
            self.toggle_button.config(text="SOCD: ON", bg="#228B22")
        else:
            self.toggle_button.config(text="SOCD: OFF", bg="#C70039")
            self.is_simulating = True
            if self.current_output:
                self.controller.release(self.current_output)
            self.is_simulating = False
            self.current_output = None
            self.key_states = {self.key_left: False, self.key_right: False}

    def _toggle_counter_strafe(self):
        self.counter_strafe_enabled = not self.counter_strafe_enabled
        if self.counter_strafe_enabled:
            self.counter_strafe_button.config(text="COUNTER-STRAFE: ON", bg="#228B22")
        else:
            self.counter_strafe_button.config(text="COUNTER-STRAFE: OFF", bg="#C70039")

    def _on_closing(self):
        keyboard.unhook_all()
        if self.current_output:
            self.controller.release(self.current_output)
        self.destroy()

if __name__ == "__main__":
    run_as_admin()
    app = SOCDApp()
    app.mainloop()