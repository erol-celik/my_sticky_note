# My Sticky Note

A lightweight, always-on-top desktop sticky-notes app for Windows, built with Python and Tkinter.

## Features

- Multiple notes ("pages"), each saved to its own plain-text file
- Global hotkey (`Alt+"`) to show/hide the note window from anywhere
- Paste and manage inline images directly in a note
- In-note search with match highlighting and next/prev navigation
- Automatic saving with periodic backups and safe (atomic) file writes
- Page rename/delete with soft-delete (archived, not immediately erased)
- Remembers window position, size, last opened page, and zoom level
- Packaged as a single standalone `.exe` via PyInstaller (no Python install required to run it)

## Requirements

- Python 3.12+ (only needed to run from source; the packaged `.exe` needs nothing)
- Windows (the app uses Windows-specific APIs for the global hotkey and clipboard image support)
- Third-party packages used by the code:
  - [`Pillow`](https://pypi.org/project/Pillow/) (image handling)
  - [`keyboard`](https://pypi.org/project/keyboard/) (global hotkey)
  - [`pyinstaller`](https://pypi.org/project/pyinstaller/) (only for building the `.exe`)

> Note: this repository does not currently ship a `requirements.txt` / `pyproject.toml`. Install the packages above manually until one is added.

## Installation

```bash
git clone <this-repo-url>
cd my_sticky_note
pip install pillow keyboard pyinstaller
```

## Usage

Run from source:

```bash
python my_sticky_note.py
```

Press `Alt+"` at any time to show or hide the note window.

Notes and images are stored under a `my_sticky_data/` folder that is created next to the script (or next to the `.exe` when packaged), so your data always travels with the app.

### Building the standalone executable

```bash
pyinstaller my_sticky_note.spec
```

The resulting executable is written to `dist/my_sticky_note.exe`.

## Project structure

```
my_sticky_note.py          Entry point
my_sticky_note.spec        PyInstaller build spec
sticky_note_app/
  app.py                   Main application class
  config.py                Colors/appearance constants
  logging_setup.py         Rotating file logger setup
  platform_win/            Windows-specific integrations (clipboard)
  storage/                 Page/settings/backup/image persistence
  ui/                      Tkinter UI mixins (window, pages, text editor, images, search, hotkeys)
```

## License

No license file is currently included in this repository. All rights are reserved by the author unless a license is added.
