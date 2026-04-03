import pyperclip
import time
import keyboard
import sys
from settings import TYPING_SPEED, TRIGGER_KEY, STOP_KEY, START_DELAY

def main():
    print("=" * 40)
    print("   AutoTyper - YouTube Recording Tool")
    print("=" * 40)
    print(f"  F9  = Start typing from clipboard")
    print(f"  F10 = Stop typing mid-way")
    print(f"  Ctrl+C = Quit\n")
    print("Ready! Copy your code, click your target window, press F9\n")

    while True:
        keyboard.wait(TRIGGER_KEY)

        text = pyperclip.paste()
        if not text.strip():
            print("[!] Clipboard is empty, nothing to type!")
            continue

        print(f"[>] {len(text)} characters queued. Typing in {START_DELAY} seconds... switch to your window!")
        time.sleep(START_DELAY)
        print("[>] Typing started...")

        stopped = False
        for char in text:
            if keyboard.is_pressed(STOP_KEY):
                stopped = True
                break
            keyboard.write(char, delay=0)
            time.sleep(TYPING_SPEED)

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
