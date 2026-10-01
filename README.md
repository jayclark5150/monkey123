# Monkey123

Version 1.1.0

A small cross-platform desktop app (Windows, macOS, Linux) for generating random
passwords and passphrases. Uses Python's `secrets` module (cryptographically secure RNG)
and the EFF large diceware wordlist (7,776 words). No network access, no dependencies
beyond Python's standard library.

## Features
- **Password**: character count 4–128; toggle lowercase, uppercase, numbers, special characters
  (at least one of each selected type is guaranteed)
- **Passphrase**: word count 3–20; separator (hyphen, space, period, underscore, comma, none,
  or custom); optional capitalization, number, and special character
- Color-coded strength meter (Weak / Fair / Strong / Very strong) next to the Generate button
- Length and entropy estimate, one-click copy, Enter to regenerate

## Run
Requires Python 3.9+ with Tkinter.

```
python3 passgen.py
```

- **Windows / macOS**: the python.org installer includes Tkinter.
- **Linux (Debian/Ubuntu)**: `sudo apt install python3-tk`  (Fedora: `sudo dnf install python3-tkinter`)

## Build a double-click desktop app
See [BUILDING.md](BUILDING.md) for step-by-step instructions for Windows, macOS and Linux.
Quick version (run on each target OS):

```
pip install pyinstaller
pyinstaller --onefile --windowed --name Monkey123 --add-data "wordlist.txt:." passgen.py
```

## Changelog

### 1.1.0
- Added a color-coded strength meter beside the Generate button
- Removed the character-count slider; set length with the number box
- Renamed the app to Monkey123

### 1.0.0
- Initial release: password and passphrase generation

## Credits
Wordlist: [EFF Large Wordlist](https://www.eff.org/dice) by the Electronic Frontier Foundation,
licensed under [CC BY 3.0 US](https://creativecommons.org/licenses/by/3.0/us/).
