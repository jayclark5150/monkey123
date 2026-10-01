# Building Monkey123 as a desktop app

Monkey123 is packaged with [PyInstaller](https://pyinstaller.org), which bundles Python,
Tkinter, the app and the word list into a single file. People running the result do not need
Python installed.

**Build on each operating system you want to support.** PyInstaller does not cross-compile:
a Windows `.exe` must be built on Windows, a macOS `.app` on macOS, and so on.

## 1. Install Python with Tkinter

Python 3.9 or newer is required.

- **Windows / macOS**: install from [python.org](https://www.python.org/downloads/) (Tkinter is included).
- **Linux (Debian/Ubuntu)**: `sudo apt install python3-tk python3-venv`
- **Linux (Fedora)**: `sudo dnf install python3-tkinter`

## 2. Build

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --windowed --name Monkey123 --icon ICON \
  --add-data "wordlist.txt:." --add-data "assets/icon.png:assets" passgen.py
```

Replace `ICON` with the file for your OS:

| OS | `--icon` value |
|---|---|
| Windows | `assets/icon.ico` |
| macOS | `assets/icon.icns` |
| Linux | `assets/icon.png` (PyInstaller ignores it on Linux; the launcher below sets the icon) |

On Windows (Command Prompt), put the whole command on one line instead of using `\`.

| Option | Purpose |
|---|---|
| `--onefile` | Produce a single file |
| `--windowed` | Don't open a terminal window alongside the app |
| `--icon` | Icon for the `.exe` / `.app` file itself |
| `--add-data "wordlist.txt:."` | Bundle the word list (the app finds it automatically when packaged) |
| `--add-data "assets/icon.png:assets"` | Bundle the icon shown in the app's window and taskbar |

PyInstaller 6+ accepts `:` as the `--add-data` separator on all platforms; older versions need
`;` on Windows.

On Windows, use `python` instead of `python3` if `python3` is not found.

## 3. Find the result

The app is written to `dist/`.

| OS | Output | Double-click notes |
|---|---|---|
| Windows | `dist\Monkey123.exe` | SmartScreen may warn about an unknown publisher. Click **More info → Run anyway**. |
| macOS | `dist/Monkey123.app` | The app is unsigned, so the first time right-click it and choose **Open**. Drag it to Applications. |
| Linux | `dist/Monkey123` | Many file managers won't launch a program on double-click. Add a launcher (below). |

## Linux launcher

Install the binary and create a menu entry:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons
cp dist/Monkey123 ~/.local/bin/
cp assets/icon.svg ~/.local/share/icons/monkey123.svg
cat > ~/.local/share/applications/monkey123.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Monkey123
Comment=Password generator
Exec=$HOME/.local/bin/Monkey123
Icon=$HOME/.local/share/icons/monkey123.svg
Terminal=false
Categories=Utility;Security;
StartupWMClass=Monkey123
EOF
```

Paste the whole block at once; don't type the lines between `cat` and `EOF` on their own.
`StartupWMClass` lets the dock match the running window to this launcher so it shows the icon.

Monkey123 then appears in your app menu and can be pinned to the dock. To launch it from the
desktop instead, copy `monkey123.desktop` to `~/Desktop`, then right-click it and choose
**Allow Launching**.

## Optional

- **Changing the icon**: edit `assets/icon.svg`, then regenerate `icon.png` (256×256), `icon.ico`
  and `icon.icns` from it (for example with Inkscape, or Python's `cairosvg` and Pillow).
- **No security warnings**: requires code signing, with a code-signing certificate on Windows
  and an Apple Developer ID on macOS.
