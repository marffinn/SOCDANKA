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
import hashlib
# // hashta
VALID_KEY_HASH = "94e23b1329f62da47588e48188cb10b8af5dbe0415273e5430d38d7d44361f2d" 
# passw


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


is_simulating = False
socd_enabled = True
counter_strafe_enabled = False
current_output = None
min_delay = 0.030
max_delay = 0.130
key_states = {'a': False, 'd': False}
key_timestamps = {'a': 0.0, 'd': 0.0}
controller = pynput.keyboard.Controller()


def pulse_key(key, pulse_time=0.05):
    global is_simulating
    is_simulating = True
    controller.press(key)
    time.sleep(pulse_time)
    controller.release(key)
    is_simulating = False


def key_event_handler(event):
    global is_simulating, counter_strafe_enabled
    if not socd_enabled or is_simulating: return True
    if event.name in ['a', 'd']:
        if event.event_type == 'down':
            if not key_states[event.name]: key_timestamps[event.name] = time.time()
            key_states[event.name] = True
        elif event.event_type == 'up':
            key_states[event.name] = False
            key_timestamps[event.name] = 0.0
            if counter_strafe_enabled:
                opposite_key = 'd' if event.name == 'a' else 'a'
                if not key_states[opposite_key]:
                    threading.Thread(target=pulse_key, args=(opposite_key,), daemon=True).start()
        return False
    return True


def ad_socd_last_input(root):
    global is_simulating, current_output
    while True:
        try:
            if not root.winfo_exists(): break
            if not socd_enabled:
                time.sleep(0.1);
                continue
            a_pressed = key_states['a'];
            d_pressed = key_states['d']
            new_output = None
            if a_pressed and d_pressed:
                new_output = 'd' if key_timestamps['d'] > key_timestamps['a'] else 'a'
            elif a_pressed:
                new_output = 'a'
            elif d_pressed:
                new_output = 'd'
            if new_output != current_output:
                is_simulating = True
                if new_output:
                    delay = random.uniform(min_delay, max_delay)
                    time.sleep(delay);
                    controller.press(new_output)
                if current_output:
                    controller.release(current_output)
                is_simulating = False
                current_output = new_output
            time.sleep(0.01)
        except (tk.TclError, RuntimeError):
            is_simulating = False;
            break


def launch_main_app():
    bg_color = "#2E2E2E";
    text_color = "#F5F5F5";
    entry_bg = "#3C3F41"
    accent_color = "#4A90E2";
    border_color = "#1E1E1E";
    error_color = "#FF5733"

    root = tk.Tk()
    root.title("A/D SOCD Cleaner");
    root.geometry("420x300")
    root.configure(bg=bg_color);
    root.resizable(False, False)

    try:
        icon_path = resource_path("uttanka.png")
        if os.path.exists(icon_path):
            photo = tk.PhotoImage(file=icon_path);
            root.iconphoto(False, photo)
    except tk.TclError:
        print("Warning: Could not load .png title bar icon.")

    label_font = font.Font(family="Segoe UI", size=10, weight="bold")
    entry_font = font.Font(family="Segoe UI", size=10)
    button_font = font.Font(family="Segoe UI", size=11, weight="bold")

    main_frame = Frame(root, bg=bg_color)
    main_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

    def update_delays_from_gui(min_entry, max_entry, button, error_label):
        global min_delay, max_delay
        try:
            min_val_ms = int(min_entry.get());
            max_val_ms = int(max_entry.get())
            if min_val_ms < 0 or max_val_ms < 0:
                error_label.config(text="Delays cannot be negative.");
                return
            if min_val_ms >= max_val_ms:
                error_label.config(text="Min delay must be less than Max.");
                return

            error_label.config(text="")
            min_delay = min_val_ms / 1000.0;
            max_delay = max_val_ms / 1000.0
            button.config(text="UPDATED!");
            button.after(1000, lambda: button.config(text="UPDATE"))
        except ValueError:
            error_label.config(text="Please enter valid numbers.")

    def toggle_socd(button):
        global socd_enabled, current_output, is_simulating
        socd_enabled = not socd_enabled
        if socd_enabled:
            button.config(text="SOCD: ON", bg="#228B22")
        else:
            button.config(text="SOCD: OFF", bg="#C70039")
            if current_output:
                is_simulating = True;
                controller.release(current_output)
                is_simulating = False;
                current_output = None
                key_states['a'], key_states['d'] = False, False

    def toggle_counter_strafe(button):
        global counter_strafe_enabled
        counter_strafe_enabled = not counter_strafe_enabled
        if counter_strafe_enabled:
            button.config(text="COUNTER-STRAFE: ON", bg="#228B22")
        else:
            button.config(text="COUNTER-STRAFE: OFF", bg="#C70039")

    control_frame = Frame(main_frame, bg=bg_color)
    control_frame.pack(fill=tk.X, pady=(5, 10))
    control_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    common_entry_options = {'font': entry_font, 'width': 8, 'bg': entry_bg, 'fg': text_color, 'relief': 'flat',
                            'highlightbackground': border_color, 'highlightthickness': 1,
                            'insertbackground': text_color}
    Label(control_frame, text="MIN DELAY (MS)", font=label_font, bg=bg_color, fg=text_color).grid(row=0, column=0,
                                                                                                  sticky=tk.W, padx=5,
                                                                                                  pady=5)
    min_entry = Entry(control_frame, **common_entry_options);
    min_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5);
    min_entry.insert(0, str(int(min_delay * 1000)))
    Label(control_frame, text="MAX DELAY (MS)", font=label_font, bg=bg_color, fg=text_color).grid(row=0, column=2,
                                                                                                  sticky=tk.W, padx=5,
                                                                                                  pady=5)
    max_entry = Entry(control_frame, **common_entry_options);
    max_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5);
    max_entry.insert(0, str(int(max_delay * 1000)))

    error_label = Label(main_frame, text="", font=label_font, bg=bg_color, fg=error_color)
    error_label.pack(pady=(0, 10))

    common_button_options = {'font': button_font, 'fg': text_color, 'relief': 'flat', 'activeforeground': text_color,
                             'bd': 0, 'cursor': "hand2"}

    toggle_button = Button(main_frame, text="SOCD: ON", **common_button_options, bg="#228B22",
                           activebackground="#5C9E5C", command=lambda: toggle_socd(toggle_button))
    toggle_button.pack(fill=tk.X, expand=True, pady=5, ipady=8)

    counter_strafe_button = Button(main_frame, text="COUNTER-STRAFE: OFF", **common_button_options, bg="#C70039",
                                   activebackground="#E57373", command=lambda: toggle_counter_strafe(counter_strafe_button))
    counter_strafe_button.pack(fill=tk.X, expand=True, pady=5, ipady=8)

    update_button = Button(main_frame, text="UPDATE", **common_button_options, bg=accent_color,
                           activebackground="#5aaaff",
                           command=lambda: update_delays_from_gui(min_entry, max_entry, update_button, error_label))
    update_button.pack(fill=tk.X, expand=True, pady=5, ipady=8)

    keyboard.hook(key_event_handler)
    threading.Thread(target=ad_socd_last_input, args=(root,), daemon=True).start()

    def on_closing():
        keyboard.unhook_all();
        controller.release('a');
        controller.release('d');
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


def validate_key(key_entry, error_label, window):
    entered_key = key_entry.get().strip().upper()
    hashed_key = hashlib.sha256(entered_key.encode('utf-8')).hexdigest()
    if hashed_key == VALID_KEY_HASH:
        window.destroy();
        launch_main_app()
    else:
        error_label.config(text="Invalid key. Please try again.")


def create_activation_window():
    bg_color = "#2E2E2E";
    text_color = "#F5F5F5";
    entry_bg = "#3C3F41"
    accent_color = "#4A90E2"

    act_window = tk.Tk()
    act_window.title("Activation Required")
    act_window.configure(bg=bg_color);
    act_window.geometry("400x180")
    act_window.resizable(False, False);
    act_window.eval('tk::PlaceWindow . center')

    label_font = font.Font(family="Segoe UI", size=10)
    button_font = font.Font(family="Segoe UI", size=11, weight="bold")
    entry_font = font.Font(family="Segoe UI", size=11)

    Label(act_window, text="Please enter your license key to continue:", font=label_font, bg=bg_color,
          fg=text_color).pack(pady=(15, 10))

    key_entry = Entry(act_window, font=entry_font, width=40, bg=entry_bg, fg=text_color, relief='flat',
                      justify='center')
    key_entry.pack(pady=5, padx=20);
    key_entry.focus_set()

    error_label = Label(act_window, text="", font=label_font, bg=bg_color, fg="#FF5733")
    error_label.pack(pady=5)

    activate_button = Button(act_window, text="ACTIVATE", font=button_font, bg=accent_color, fg=text_color,
                             command=lambda: validate_key(key_entry, error_label, act_window),
                             relief='flat', cursor="hand2", bd=0, activebackground="#5aaaff",
                             activeforeground=text_color)

    activate_button.pack(pady=10, ipady=5, padx=15)

    act_window.mainloop()


if __name__ == "__main__":
    run_as_admin()
    create_activation_window()
