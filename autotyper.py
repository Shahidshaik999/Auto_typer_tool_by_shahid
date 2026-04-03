import pyperclip
import time
import keyboard
import pyautogui
import sys
from settings import TYPING_SPEED, TRIGGER_KEY, STOP_KEY, START_DELAY

pyautogui.FAILSAFE = False

current_speed = [TYPING_SPEED]

MIN_SPEED = 0.0   # 0 = no delay = instant/infinite speed
MAX_SPEED = 0.20

def on_key(e):
    if e.name == 'f8':
        current_speed[0] = max(0.0, round(current_speed[0] - 0.01, 4))
        label = "INSTANT" if current_speed[0] == 0.0 else f"{current_speed[0]:.4f}s per char"
        print(f"[+] FASTER → {label}")
    elif e.name == 'f7':
        current_speed[0] = min(MAX_SPEED, round(current_speed[0] + 0.01, 4))
        print(f"[-] SLOWER → {current_speed[0]:.4f}s per char")

keyboard.on_press(on_key, suppress=False)

def type_char(char):
    if char == '\n':
        pyautogui.press('enter')
    elif char == '\t':
        pyautogui.press('tab')
    elif char == ' ':
        pyautogui.press('space')
    else:
        old_clip = pyperclip.paste()
        pyperclip.copy(char)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.01)
        pyperclip.copy(old_clip)

def main():
    print("=" * 40)
    print("   AutoTyper - YouTube Recording Tool")
    print("=" * 40)
    print(f"  F9  = Start typing from clipboard")
    print(f"  F10 = Stop typing mid-way")
    print(f"  F8  = Speed UP  (tap or hold)")
    print(f"  F7  = Slow DOWN (tap or hold)")
    print(f"  Ctrl+C = Quit\n")
    print(f"  Current speed: {current_speed[0]:.4f}s per char\n")
    print("Ready! Copy your code, click your target window, press F9\n")

    while True:
        keyboard.wait(TRIGGER_KEY)

        text = pyperclip.paste()
        if not text.strip():
            print("[!] Clipboard is empty, nothing to type!")
            continue

        print(f"[>] {len(text)} chars | speed: {current_speed[0]:.4f}s | starting in {START_DELAY}s... switch window!")
        time.sleep(START_DELAY)
        print("[>] Typing... (F8=faster, F7=slower, F10=stop)\n")

        stopped = False
        for char in text:
            if keyboard.is_pressed(STOP_KEY):
                stopped = True
                break
            type_char(char)
            if current_speed[0] > 0:
                time.sleep(current_speed[0])

        if stopped:
            print("[!] Stopped (F10)\n")
        else:
            print("[✓] Done! Press F9 again.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
