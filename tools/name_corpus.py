"""Parse ../fantasy_names.txt into {culture: {gender: [names]}} and {category: [surnames]}."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent.parent / "fantasy_names.txt"
CULTURES = ["Archaic", "Westron", "Northish", "Southron"]


def parse(path=SRC):
    text = path.read_text()
    first, last = {}, {}
    culture = None
    in_surnames = False
    # split into "Label. a, b, c" segments; labels are capitalised words before a full stop
    for m in re.finditer(r"([A-Z][A-Za-z/ ]+?)\.\s+((?:[A-Z][A-Za-z' -]*(?:,\s*|\s+(?=[A-Z][a-z]+,)|$)?)+)", text):
        label, body = m.group(1).strip(), m.group(2)
        label = label.replace("Surname Lists", "").replace("First Name Lists", "").strip()
        names = [n.strip() for n in re.split(r",\s*|\s+(?=[A-Z])", body) if n.strip() and n.strip()[0].isupper()]
        if label in CULTURES:
            culture = label
            continue
        if label in ("Female", "Male") and culture and not in_surnames:
            first.setdefault(culture, {}).setdefault(label.lower(), [])
            first[culture][label.lower()] += names
        elif label not in ("Female", "Male"):
            last.setdefault(label, [])
            last[label] += names
    return first, last


def parse_strict(path=SRC):
    """Only the clean top part of the file (the tail repeats lists out of order)."""
    lines = [l.strip() for l in path.read_text().splitlines()]
    first, last, culture, mode = {}, {}, None, "first"
    for l in lines:
        if not l:
            continue
        if l.startswith("Surname Lists"):
            mode = "last"
            continue
        if l.rstrip(".") in CULTURES:
            culture = l.rstrip(".")
            continue
        m = re.match(r"^([A-Za-z/ ]+?)\.\s+(.*)$", l)
        if not m:
            continue
        label, body = m.groups()
        names = [n.strip().rstrip(".") for n in re.split(r",\s*", body) if n.strip()]
        names = [n for n in names if re.fullmatch(r"[A-Z][a-z]+", n)]
        if mode == "first" and label in ("Female", "Male") and culture:
            first.setdefault(culture, {}).setdefault(label.lower(), [])
            first[culture][label.lower()] += names
        elif mode == "last":
            last.setdefault(label, [])
            last[label] += names
        if len(first.get("Southron", {})) == 2 and mode == "first" and culture == "Southron" and label == "Male":
            pass
    for c in first:
        for g in first[c]:
            first[c][g] = list(dict.fromkeys(first[c][g]))
    for k in last:
        last[k] = list(dict.fromkeys(last[k]))
    return first, last


if __name__ == "__main__":
    f, l = parse_strict()
    for c, gs in f.items():
        print(c, {g: len(v) for g, v in gs.items()})
    print({k: len(v) for k, v in l.items()})
