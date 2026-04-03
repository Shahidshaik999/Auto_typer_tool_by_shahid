# AutoTyper Tool by Shahid

A simple auto-typing tool for  recording videos. Copy any code or text, switch to your terminal/editor, press F9 and it types it out character by character like a human!

## Features
- Auto-types clipboard content character by character
- Adjustable typing speed
- Stop mid-typing with F10
- 3 second delay to switch windows before typing starts
- Syntax-aware mode (F6) — types like a real developer for:
  - HTML (opens tag + closing tag, cursor goes inside)
  - Python (types block header first, then body)
  - JavaScript / TypeScript
  - React JSX / TSX (handles components naturally)
  - CSS / SCSS
  - JSON
  - C / C++ / Java

## Requirements
- Python 3.x
- Windows OS

## Installation & Run

1. Right-click `run.bat` → **Run as Administrator**
2. It will auto-install dependencies and launch the tool

## How to Use

1. Copy your code or text (`Ctrl+C`)
2. Click into your terminal or editor window
3. Press `F9` to start auto-typing
4. Press `F6` to toggle syntax-aware mode (real-dev style typing)
5. Press `F8` for instant speed
6. Press `F7` to slow down
7. Press `F10` to stop mid-way

## Settings

Edit `settings.py` to customize:

| Setting | Default | Description |
|---|---|---|
| `TYPING_SPEED` | `0.05` | Seconds between each character |
| `TRIGGER_KEY` | `F9` | Key to start typing |
| `STOP_KEY` | `F10` | Key to stop typing |
| `START_DELAY` | `3` | Seconds before typing starts |

## Speed Guide
- `0.02` = Fast
- `0.05` = Natural (recommended)
- `0.10` = Slow / dramatic

## Made by Shahid
