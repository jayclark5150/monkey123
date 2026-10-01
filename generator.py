"""Password and passphrase generation using a cryptographically secure RNG."""

import math
import secrets
import string
import sys
from pathlib import Path

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/~"

_rng = secrets.SystemRandom()


def resource_dir() -> Path:
    # When bundled with PyInstaller, data files live in sys._MEIPASS.
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def load_wordlist() -> list[str]:
    path = resource_dir() / "wordlist.txt"
    words = [w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip()]
    if not words:
        raise RuntimeError(f"Wordlist is empty: {path}")
    return words


def generate_password(length=16, lower=True, upper=True, digits=True, symbols=True):
    """Return (password, entropy_bits). Guarantees at least one char from each chosen set."""
    pools = [p for p, on in ((LOWER, lower), (UPPER, upper), (DIGITS, digits), (SYMBOLS, symbols)) if on]
    if not pools:
        raise ValueError("Select at least one character type.")
    if length < len(pools):
        raise ValueError(f"Length must be at least {len(pools)} for the selected character types.")

    alphabet = "".join(pools)
    chars = [secrets.choice(p) for p in pools]
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    _rng.shuffle(chars)
    return "".join(chars), length * math.log2(len(alphabet))


def generate_passphrase(words, count=5, separator="-", capitalize=False, add_number=False, add_symbol=False):
    """Return (passphrase, entropy_bits). Number/symbol are appended to a random word."""
    if count < 1:
        raise ValueError("Word count must be at least 1.")

    chosen = [secrets.choice(words) for _ in range(count)]
    if capitalize:
        chosen = [w.capitalize() for w in chosen]

    entropy = count * math.log2(len(words))
    if add_number:
        i = secrets.randbelow(count)
        chosen[i] += secrets.choice(DIGITS)
        entropy += math.log2(len(DIGITS)) + math.log2(count)
    if add_symbol:
        i = secrets.randbelow(count)
        chosen[i] += secrets.choice(SYMBOLS)
        entropy += math.log2(len(SYMBOLS)) + math.log2(count)

    return separator.join(chosen), entropy


def strength_label(bits: float) -> str:
    if bits < 40:
        return "Weak"
    if bits < 60:
        return "Fair"
    if bits < 80:
        return "Strong"
    return "Very strong"
