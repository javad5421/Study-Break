import pyautogui
import time
import threading
import signal
import ctypes
import os
import sys
import tkinter as tk

event = threading.Event()

# variables
awakeT = 600
breakT = 1800
delayT = 300
mouseT = 30
safe_margin = 10
def move_mouse():
    while not event.is_set():
        x, y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()

        if x < safe_margin:
            x += 1  # Move right if too close to the left
        elif x > screen_width - safe_margin:
            x -= 1  # Move left if too close to the right

        if y < safe_margin:
            y += 1  # Move down if too close to the top
        elif y > screen_height - safe_margin:
            y -= 1  # Move up if too close to the bottom
        pyautogui.moveTo(x + 1, y)
        event.wait(mouseT)  # Move every 5 seconds

def wake_pc():
    time.sleep(awakeT)  # Wait for 10 minutes
    os.system("powercfg -h off")  
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,0,0")

def countdown_timer():
    def update_timer(count):
        if count >= 0:
            label.config(text=f"Sleeping in {count} seconds...")
            root.after(1000, update_timer, count - 1)
        else:
            root.destroy()
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            threading.Thread(target=wake_pc, daemon=True).start()
    
    root = tk.Tk()
    root.title("Countdown")
    root.geometry("300x100")
    label = tk.Label(root, text="Sleeping in 10 seconds...", font=("Arial", 14))
    label.pack(expand=True)
    
    update_timer(10)
    root.mainloop()

def show_break_notification():
    user32 = ctypes.windll.user32
    response = user32.MessageBoxW(0, "It's time for a break!", "Break Reminder", 1 | 0x40 | 0x1000)
    if response == 1:  
        threading.Thread(target=countdown_timer, daemon=True).start()
    elif response == 2:  
        return
    elif response == 3:  #delay 
        time.sleep(delayT)
        show_break_notification()

def break_reminder():
    while not event.is_set():
        event.wait(breakT)  
        if not event.is_set():
            show_break_notification()

def run_in_background():
    threading.Thread(target=move_mouse, daemon=True).start()
    threading.Thread(target=break_reminder, daemon=True).start()

def signal_handler(sig, frame):
    print("Stopping script...")
    event.set()

def is_already_in_startup():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_path, 'mouse_mover.lnk')
    return os.path.exists(shortcut_path)

def add_to_startup():
    if is_already_in_startup():
        print("Already in startup, skipping addition.")
        return
    
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    script_path = os.path.abspath(sys.argv[0])
    shortcut_path = os.path.join(startup_path, 'mouse_mover.lnk')
    
    import winshell
    from win32com.client import Dispatch
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = sys.executable
    shortcut.Arguments = script_path
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.Save()
    print("Added to startup successfully.")

def main():
    signal.signal(signal.SIGINT, signal_handler)  
    add_to_startup()
    run_in_background()
    event.wait()  

if __name__ == "__main__":
    main()
