"""Grammar-driven text generation with anti-repetition memory.

Template syntax
---------------
  {symbol}            expand a rule (or a context variable)
  {symbol.a.cap}      apply modifiers: a (article), s (plural), cap, lower, title
  {symbol>var}        expand and remember the raw result in ctx["var"]
  [one|two|three]     inline alternatives (an empty alternative makes it optional)

Rules are looked up through *scopes*: with scopes ("forest:autumn", "forest"),
the symbol "canopy" resolves to "forest:autumn:canopy", then "forest:canopy",
then plain "canopy" - so specific situations can override general phrasing.
"""
import re
import textwrap
from collections import deque

TOKEN = re.compile(r"\{([^{}]+)\}")
ALT = re.compile(r"\[([^\[\]]*\|[^\[\]]*)\]")

_AN_EXCEPTIONS = ("hour", "honest", "honour", "heir", "herb")
_A_EXCEPTIONS = ("one", "once", "uni", "use", "usu", "eu", "ewe", "uto", "ura", "ure")


def article(phrase):
    w = phrase.lstrip().lower()
    if not w:
        return phrase
    if w.startswith(_AN_EXCEPTIONS):
        return "an " + phrase
    if w.startswith(_A_EXCEPTIONS):
        return "a " + phrase
    return ("an " if w[0] in "aeiou" else "a ") + phrase


_IRREGULAR = {"wolf": "wolves", "thief": "thieves", "leaf": "leaves", "man": "men",
              "woman": "women", "foot": "feet", "tooth": "teeth", "mouse": "mice",
              "goose": "geese", "child": "children", "ox": "oxen", "elf": "elves",
              "sheep": "sheep", "deer": "deer", "fish": "fish", "knife": "knives",
              "staff": "staves", "calf": "calves", "loaf": "loaves", "yew": "yews",
              "reed": "reeds", "dwarf": "dwarves"}


def plural(phrase):
    head, _, last = phrase.rpartition(" ")
    low = last.lower()
    if low in _IRREGULAR:
        p = _IRREGULAR[low]
    elif low.endswith(("s", "x", "z", "ch", "sh")):
        p = last + "es"
    elif low.endswith("y") and len(low) > 1 and low[-2] not in "aeiou":
        p = last[:-1] + "ies"
    else:
        p = last + "s"
    return (head + " " + p) if head else p


def and_list(items, word="and"):
    """'A', 'A and B', 'A, B and C'."""
    items = [str(x) for x in items]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {word} " + items[-1]


def join_speech(a, b):
    """Two quoted lines from the same speaker, one after the other, become one speech:
    '"Hello." "Name?"' -> '"Hello. Name?"'. Anything else is joined with a space."""
    a, b = a.rstrip(), b.lstrip()
    if a.endswith('"') and b.startswith('"'):
        return a[:-1].rstrip() + " " + b[1:]
    return (a + " " + b).strip()


def one_voice(text):
    """Inside a passage spoken by one person, run back-to-back quotes together into one."""
    return re.sub(r'([^\s"])"\s+"(?=\S)', r"\1 ", text)


def cap(s):
    for i, ch in enumerate(s):
        if ch.isalpha():
            return s[:i] + ch.upper() + s[i + 1:]
    return s


def title(s):
    small = {"of", "the", "a", "an", "and", "in", "on", "at", "by"}
    words = s.split(" ")
    return " ".join(w if (i and w in small) else cap(w) for i, w in enumerate(words))


MODS = {"a": article, "s": plural, "cap": cap, "lower": str.lower, "title": title}


class Grammar:
    def __init__(self, rng, rules=None):
        self.rng = rng
        self.rules = {}
        self.recent = {}
        self.missing = set()
        if rules:
            self.add(rules)

    @staticmethod
    def _norm(value):
        if isinstance(value, (str, tuple)):
            value = [value]
        out = []
        for entry in value:
            if isinstance(entry, tuple):          # (weight, text)
                out.append((entry[1], float(entry[0])))
            else:
                out.append((entry, 1.0))
        return out

    def add(self, rules):
        for key, value in rules.items():
            self.rules[key] = self._norm(value)

    def extend(self, rules):
        """Append options to existing symbols (or create them)."""
        for key, value in rules.items():
            self.rules.setdefault(key, []).extend(self._norm(value))

    # -- choosing -----------------------------------------------------------
    def choose(self, key, options):
        """Weighted pick that avoids options used recently under the same key."""
        n = len(options)
        if n == 1:
            return options[0][0]
        mem = self.recent.get(key)
        if mem is None:
            mem = self.recent[key] = deque(maxlen=max(1, min(n - 1, int(n * 0.65))))
        pool = [(i, o) for i, o in enumerate(options) if i not in mem] or list(enumerate(options))
        total = sum(o[1] for _, o in pool)
        r = self.rng.random() * total
        pick_i, pick = pool[-1]
        for i, o in pool:
            r -= o[1]
            if r <= 0:
                pick_i, pick = i, o
                break
        mem.append(pick_i)
        return pick[0]

    def pick(self, items, key=None):
        """Anti-repetitive choice from a plain Python list."""
        items = list(items)
        return self.choose(key or ("list:" + "|".join(map(str, items))[:200]),
                           [(x, 1.0) for x in items])

    def lookup(self, name, scopes):
        for s in scopes:
            k = f"{s}:{name}"
            if k in self.rules:
                return k
        return name if name in self.rules else None

    # -- expansion ----------------------------------------------------------
    def expand(self, text, ctx=None, scopes=(), depth=0):
        if ctx is None:
            ctx = {}
        if depth > 30:
            return text

        def alt(m):
            body = m.group(1)
            return self.choose("alt:" + body, [(o, 1.0) for o in body.split("|")])

        while True:
            new = ALT.sub(alt, text)
            if new == text:
                break
            text = new

        def repl(m):
            spec = m.group(1)
            var = None
            if ">" in spec:
                spec, var = spec.split(">", 1)
            name, *mods = spec.split(".")
            if name in ctx:
                val = ctx[name]
                if callable(val):
                    val = val()
                if isinstance(val, (list, tuple)):
                    val = self.choose(f"ctx:{name}:{len(val)}:{val[0]}", self._norm(list(val)))
                val = str(val)
                if "{" in val or "[" in val:
                    val = self.expand(val, ctx, scopes, depth + 1)
            else:
                key = self.lookup(name, scopes)
                if key is None:
                    self.missing.add(name)
                    val = name.replace("_", " ")
                else:
                    val = self.expand(self.choose(key, self.rules[key]), ctx, scopes, depth + 1)
            if var:
                ctx[var] = val
            for mod in mods:
                val = MODS[mod](val)
            return val

        return TOKEN.sub(repl, text)


_ART = re.compile(r"\b([Aa])(n?) ([A-Za-z][\w'-]*)")


def fix_articles(text):
    """Re-derive a/an from the word that actually follows, after expansion."""
    def sub(m):
        fixed = article(m.group(3))
        if m.group(1) == "A":
            fixed = "A" + fixed[1:]
        return fixed
    return _ART.sub(sub, text)


def tidy(text):
    """Fix spacing/punctuation/capitalisation/articles in assembled prose."""
    text = re.sub(r"\s+", " ", text).strip()
    text = fix_articles(text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,;:])\s*([,.;:])", r"\2", text)
    text = re.sub(r"\.\s*\.", ".", text)
    # a new sentence starts after . ! ? - but not after a question or exclamation closed by a quote, where a
    # speech tag follows: '"Name?" she asks', not '"Name?" She asks'
    text = re.sub(r"(?:([.!?])|(\.\"))\s+([a-z])", lambda m: (m.group(1) or m.group(2)) + " " + m.group(3).upper(), text)
    text = cap(text)
    if text and text[-1] not in ".!?\"'—:":
        text += "."
    return text


def wrap(text, width=78):
    paras = [p for p in text.split("\n")]
    return "\n".join(textwrap.fill(p, width) if p.strip() else "" for p in paras)
