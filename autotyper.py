import pyperclip
import time
import keyboard
import sys
from settings import TYPING_SPEED, TRIGGER_KEY, STOP_KEY, START_DELAY

# Mutable speed so hotkeys can change it mid-typing
current_speed = [TYPING_SPEED]

SPEED_STEP = 0.01
MIN_SPEED = 0.01
MAX_SPEED = 0.20

def increase_speed():
    current_speed[0] = max(MIN_SPEED, round(current_speed[0] - SPEED_STEP, 3))
    print(f"[+] Speed increased → {current_speed[0]:.2f}s per char")

def decrease_speed():
    current_speed[0] = min(MAX_SPEED, round(current_speed[0] + SPEED_STEP, 3))
    print(f"[-] Speed decreased → {current_speed[0]:.2f}s per char")

keyboard.add_hotkey('F7', decrease_speed)
keyboard.add_hotkey('F8', increase_speed)

def main():
    print("=" * 40)
    print("   AutoTyper - YouTube Recording Tool")
    print("=" * 40)
    print(f"  F9  = Start typing from clipboard")
    print(f"  F10 = Stop typing mid-way")
    print(f"  F8  = Speed up typing")
    print(f"  F7  = Slow down typing")
    print(f"  Ctrl+C = Quit\n")
    print(f"  Current speed: {current_speed[0]:.2f}s per char\n")
    print("Ready! Copy your code, click your target window, press F9\n")

    while True:
        keyboard.wait(TRIGGER_KEY)

        text = pyperclip.paste()
        if not text.strip():
            print("[!] Clipboard is empty, nothing to type!")
            continue

        print(f"[>] {len(text)} chars queued | speed: {current_speed[0]:.2f}s | starting in {START_DELAY}s... switch window!")
        time.sleep(START_DELAY)
        print("[>] Typing started... (F8=faster, F7=slower, F10=stop)")

        stopped = False
        for char in text:
            if keyboard.is_pressed(STOP_KEY):
                stopped = True
                break
            keyboard.write(char, delay=0)
            time.sleep(current_speed[0])

        if stopped:
            print("[!] Stopped by user (F10)\n")
        else:
            print("[✓] Done! Press F9 again for next text.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
