"""Phrases you have read in earlier runs, so a new run can steer away from them.

The narrator already avoids phrasing it used recently within a game. This remembers, across every
character and world on this machine (or in this browser), the four-word runs of words you've been
shown, as small hashes in saves/phrases.bin (capped at LIMIT, oldest forgotten first). When the
narrator weighs candidate sentences, ones that echo an earlier run score a little worse, so a second
or third playthrough leans toward wording you haven't seen. It never changes what happens, only how
it is told.

Set RPG_PHRASEBOOK=0 to turn it off (tools/repeats.py does, unless asked, to measure the text itself).
"""
import array
import os
import zlib
from pathlib import Path

LIMIT = 100000         # about 400 KB: a few whole runs


def enabled():
    return os.environ.get("RPG_PHRASEBOOK", "1") != "0"


def _path():
    base = os.environ.get("RPG_SAVE_DIR") or Path(__file__).resolve().parent.parent / "saves"
    return Path(base) / "phrases.bin"


FILLER = set("a an the of and to in on at it is was you your his her its their with for from by as that this but or "
              "there here one some more into out up down over all not no be are were has have had".split())


def telling(shingle):
    """Worth remembering: a phrase with at least two words that aren't filler ("you can see the" isn't)."""
    return sum(w not in FILLER for w in shingle.split()) >= 2


def key(shingle):
    return zlib.crc32(shingle.encode())


def _read():
    a = array.array("I")
    try:
        data = _path().read_bytes()
        a.frombytes(data[: len(data) - len(data) % a.itemsize])
    except (OSError, ValueError):
        pass
    return a


def load():
    """The phrases of earlier runs, as a set of hashes (empty when turned off or never saved)."""
    return frozenset(_read()) if enabled() else frozenset()


def add(shingles):
    """Remember these phrases for future runs."""
    if not enabled() or not shingles:
        return
    a = _read()
    have = set(a)
    a.extend(k for k in dict.fromkeys(key(s) for s in shingles if telling(s)) if k not in have)
    if len(a) > LIMIT:
        a = a[-LIMIT:]
    p = _path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_bytes(a.tobytes())
        os.replace(tmp, p)
    except OSError:
        pass
