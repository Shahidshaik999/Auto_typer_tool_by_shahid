import pyperclip
import time
import keyboard
import pyautogui
import sys
import re
from settings import TYPING_SPEED, TRIGGER_KEY, STOP_KEY, START_DELAY

pyautogui.FAILSAFE = False

current_speed = [TYPING_SPEED]
MAX_SPEED     = 0.20
instant_mode  = [False]
syntax_mode   = [False]

def on_key(e):
    if e.name == 'f8':
        instant_mode[0] = True
        current_speed[0] = 0.0
        print("[+] INSTANT MODE ON")
    elif e.name == 'f7':
        instant_mode[0] = False
        current_speed[0] = max(0.01, min(MAX_SPEED, round(current_speed[0] + 0.02, 4)))
        print(f"[-] SLOWER → {current_speed[0]:.3f}s per char")
    elif e.name == 'f6':
        syntax_mode[0] = not syntax_mode[0]
        print(f"[*] Syntax-aware mode {'ON' if syntax_mode[0] else 'OFF'}")

keyboard.on_press(on_key, suppress=False)

# ── TYPING PRIMITIVES ────────────────────────────────────────────────────────

def type_str(text):
    if instant_mode[0]:
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        return True
    for ch in text:
        if keyboard.is_pressed(STOP_KEY):
            return False
        pyperclip.copy(ch)
        pyautogui.hotkey('ctrl', 'v')
        if current_speed[0] > 0:
            time.sleep(current_speed[0])
    return True

def press(key):
    pyautogui.press(key)
    if not instant_mode[0]:
        time.sleep(0.04)

def natural_pause():
    if not instant_mode[0]:
        time.sleep(0.2)

# ── LANGUAGE DETECTION ───────────────────────────────────────────────────────

def detect_language(code):
    c = code.strip()
    # HTML
    if re.search(r'<!DOCTYPE|<html|<head|<body|<div|<span|<p>', c, re.I):
        return 'html'
    # JSX / TSX / React
    if re.search(r'(import React|from [\'"]react[\'"]|useState|useEffect|<[A-Z]\w+|\.tsx|\.jsx)', c):
        return 'jsx'
    # Java
    if re.search(r'(public\s+class|public\s+static\s+void\s+main|System\.out|import\s+java\.)', c):
        return 'java'
    # C / C++
    if re.search(r'(#include\s*<|int\s+main\s*\(|std::|printf\s*\(|scanf\s*\(|cout\s*<<)', c):
        return 'c'
    # TypeScript
    if re.search(r'(:\s*(string|number|boolean|void|any|never)\b|interface\s+\w+|type\s+\w+\s*=|<T>|as\s+\w+)', c):
        return 'typescript'
    # CSS / SCSS / LESS
    if re.search(r'(^\s*[\.\#\*]?[\w\-]+\s*\{|@media|@keyframes|@import|margin:|padding:|color:|font-|background:)', c, re.M):
        return 'css'
    # Python
    if re.search(r'^\s*(def |class |import |from |if __name__|@\w+)', c, re.M):
        return 'python'
    # JS generic
    if re.search(r'(function\s+\w+\s*\(|const |let |var |=>|module\.exports|export default)', c):
        return 'javascript'
    # JSON
    if re.match(r'^\s*[\{\[]', c):
        return 'json'
    return 'generic'

# ── VOID / SELF-CLOSING TAGS ─────────────────────────────────────────────────

HTML_VOID = {'area','base','br','col','embed','hr','img','input',
             'link','meta','param','source','track','wbr'}

# ── BRACE-BASED TYPER (JS, TS, JSX, TSX, CSS, C, Java, JSON) ─────────────────

BRACE_OPEN_RE = re.compile(r'\{\s*$')

def syntax_type_braces(lines, jsx=False):
    i = 0
    while i < len(lines):
        if keyboard.is_pressed(STOP_KEY):
            return False
        line  = lines[i]
        strip = line.strip()

        # JSX: handle self-closing and paired tags inline
        if jsx and re.match(r'^\s*<[A-Za-z]', line):
            result, i = handle_jsx_line(lines, i)
            if not result:
                return False
            continue

        if BRACE_OPEN_RE.search(strip):
            if not type_str(line.rstrip()):
                return False
            press('enter')
            natural_pause()

            depth = 1
            body  = []
            i += 1
            closing = ''
            while i < len(lines) and depth > 0:
                l = lines[i]
                depth += l.count('{') - l.count('}')
                if depth == 0:
                    closing = l
                    break
                body.append(l)
                i += 1

            if body:
                if not syntax_type_braces(body, jsx=jsx):
                    return False

            if closing.strip():
                if not type_str(closing.rstrip()):
                    return False
                press('enter')
                natural_pause()
        else:
            if strip:
                if not type_str(line.rstrip()):
                    return False
                press('enter')
                natural_pause()
            else:
                press('enter')
            i += 1

    return True

# ── JSX TAG HANDLER ──────────────────────────────────────────────────────────

def handle_jsx_line(lines, i):
    line  = lines[i]
    strip = line.strip()

    # Self-closing JSX tag like <Component /> or <br />
    if re.search(r'/>\s*$', strip):
        if not type_str(line.rstrip()):
            return False, i
        press('enter')
        natural_pause()
        return True, i + 1

    # Opening JSX tag
    m = re.match(r'<([A-Za-z][\w\.]*)', strip)
    if m:
        tag = m.group(1)
        close_tag = f'</{tag}>'

        # Check if close tag is on same line
        if re.search(rf'</{re.escape(tag)}>', strip):
            if not type_str(line.rstrip()):
                return False, i
            press('enter')
            natural_pause()
            return True, i + 1

        # Type open tag + close tag together, cursor goes inside
        open_part = strip
        if not type_str(open_part + close_tag):
            return False, i
        natural_pause()

        for _ in range(len(close_tag)):
            pyautogui.press('left')
        natural_pause()

        # Collect body until </tag>
        body  = []
        i += 1
        depth = 1
        while i < len(lines) and depth > 0:
            l = lines[i]
            if re.search(rf'<{re.escape(tag)}[\s>/]', l):
                depth += 1
            if re.search(rf'</{re.escape(tag)}>', l):
                depth -= 1
                if depth == 0:
                    break
            body.append(l)
            i += 1

        if body:
            press('enter')
            if not syntax_type_braces(body, jsx=True):
                return False, i
            for _ in range(len(close_tag)):
                pyautogui.press('right')

        press('enter')
        natural_pause()
        return True, i + 1

    # Fallback
    if not type_str(line.rstrip()):
        return False, i
    press('enter')
    return True, i + 1

# ── PYTHON / INDENTED ────────────────────────────────────────────────────────

PYTHON_BLOCK_RE = re.compile(
    r'^\s*(def |class |if |elif |else\s*:|for |while |try\s*:|except|finally\s*:|with |async )'
)

def syntax_type_python(lines):
    i = 0
    while i < len(lines):
        if keyboard.is_pressed(STOP_KEY):
            return False
        line  = lines[i]
        strip = line.rstrip()

        if PYTHON_BLOCK_RE.match(strip):
            if not type_str(strip):
                return False
            press('enter')
            natural_pause()

            base_indent = len(line) - len(line.lstrip())
            body = []
            i += 1
            while i < len(lines):
                if lines[i].strip() == '':
                    body.append(lines[i])
                    i += 1
                    continue
                curr_indent = len(lines[i]) - len(lines[i].lstrip())
                if curr_indent > base_indent:
                    body.append(lines[i])
                    i += 1
                else:
                    break

            if body:
                if not syntax_type_python(body):
                    return False
        else:
            if strip.strip():
                if not type_str(strip):
                    return False
                press('enter')
                natural_pause()
            else:
                press('enter')
            i += 1

    return True

# ── HTML ─────────────────────────────────────────────────────────────────────

HTML_OPEN_RE = re.compile(r'^\s*<(\w[\w\-]*)([^>]*)>\s*$', re.I)

def syntax_type_html(lines):
    i = 0
    while i < len(lines):
        if keyboard.is_pressed(STOP_KEY):
            return False
        line  = lines[i]
        strip = line.strip()
        m     = HTML_OPEN_RE.match(strip)

        if m:
            tag = m.group(1).lower()
            if tag in HTML_VOID or tag.startswith('!'):
                if not type_str(strip):
                    return False
                press('enter')
                natural_pause()
                i += 1
                continue

            close_tag = f'</{tag}>'
            if not type_str(strip + close_tag):
                return False
            natural_pause()

            for _ in range(len(close_tag)):
                pyautogui.press('left')
            natural_pause()

            body  = []
            i += 1
            depth = 1
            while i < len(lines) and depth > 0:
                l = lines[i]
                s = l.strip()
                if re.match(rf'<{tag}[\s>]', s, re.I):
                    depth += 1
                if re.match(rf'</{tag}>', s, re.I):
                    depth -= 1
                    if depth == 0:
                        break
                body.append(l)
                i += 1

            if body:
                press('enter')
                if not syntax_type_html(body):
                    return False
                for _ in range(len(close_tag)):
                    pyautogui.press('right')

            press('enter')
            natural_pause()
        else:
            if strip:
                if not type_str(strip):
                    return False
                press('enter')
                natural_pause()
            else:
                press('enter')
            i += 1

    return True

# ── ROUTER ───────────────────────────────────────────────────────────────────

def syntax_type(code):
    lang  = detect_language(code)
    lines = code.split('\n')
    print(f"[*] Detected language: {lang}")

    if lang == 'html':
        return syntax_type_html(lines)
    elif lang == 'python':
        return syntax_type_python(lines)
    elif lang in ('jsx', 'typescript'):
        return syntax_type_braces(lines, jsx=True)
    else:
        # javascript, css, json, c, c++, java, generic — all brace-based
        return syntax_type_braces(lines, jsx=False)

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 45)
    print("   AutoTyper - YouTube Recording Tool")
    print("=" * 45)
    print(f"  F9  = Start typing")
    print(f"  F10 = Stop")
    print(f"  F8  = Instant speed (one press)")
    print(f"  F7  = Slow down")
    print(f"  F6  = Toggle syntax-aware mode")
    print(f"        (HTML / CSS / JS / TS / JSX / TSX")
    print(f"         Python / JSON / C / C++ / Java)")
    print(f"  Ctrl+C = Quit\n")
    print(f"  Syntax mode : {'ON' if syntax_mode[0] else 'OFF'}")
    print(f"  Speed       : {current_speed[0]:.3f}s per char\n")
    print("Ready! Copy code → click target window → press F9\n")

    while True:
        keyboard.wait(TRIGGER_KEY)

        text = pyperclip.paste()
        if not text.strip():
            print("[!] Clipboard is empty!")
            continue

        lang = detect_language(text)
        print(f"[>] {len(text)} chars | lang={lang} | syntax={'ON' if syntax_mode[0] else 'OFF'} | starting in {START_DELAY}s...")
        time.sleep(START_DELAY)
        print("[>] Typing... (F8=instant, F7=slower, F6=syntax toggle, F10=stop)\n")

        if syntax_mode[0]:
            result = syntax_type(text)
        else:
            result = type_str(text)

        if result is False:
            print("[!] Stopped\n")
        else:
            print("[✓] Done! Press F9 again.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
