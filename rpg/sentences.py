"""Sentence-level construction: meaning in, words out.

A fact is stored as *roles* (the person's bad knee, what broke it, what sets it off). A *frame* is a
handful of sentence shapes for saying one thing about it. A shape is built from slots, and each slot is
filled from a shared word list or from the roles, so the same meaning comes out a different way each
time while every mention agrees with the facts:

    "{part.subj.cap} {ache.v} whenever {foul} {~is|are} on the way."
        -> "My knee aches whenever a storm is on the way."
        -> "My joints throb whenever the east wind is on the way."
    "When {foul} [is coming|is brewing], {part.subj} {ache.v}."
        -> "When rain is brewing, the old break in my wrist starts up."

Slot syntax  {name.mod.mod>var}
  name     a role (from the fact), a word list in LEX, or a special word (see below)
  .subj    this is the subject: verbs after it agree with it
  .v       a verb lemma, made to agree with the subject ('ache' -> 'aches' / 'ache')
  .past    a verb lemma in the past tense ('break' -> 'broke')
  .ing     a verb lemma as '-ing' ('brew' -> 'brewing')
  .cap .a .lower .title   as in the description grammar
  >var     remember what was chosen as {var}, to say it again the same way
  {~one|many}   pick by the subject's number: '{~is|are}', '{~was|were}', '{~has|have}'
  {it}     'it' or 'them' for the last subject; {its} 'its' or 'their'
  [a|b|c]  inline choice; [a|] makes something optional

Word-list entries are strings, or (text, "pl") for a plural, and may contain slots themselves.
"""
import re

from . import coherence as C
from .textgen import MODS, tidy, fix_articles

SLOT = re.compile(r"\{([^{}]+)\}")
ALT = re.compile(r"\[([^\[\]]*)\]")

_THIRD = {"be": "is", "have": "has", "do": "does", "go": "goes"}
_PAST = {"be": "was", "have": "had", "do": "did", "go": "went", "know": "knew", "feel": "felt", "tell": "told", "take": "took", "come": "came",
         "see": "saw", "say": "said", "get": "got", "keep": "kept", "leave": "left", "sit": "sat", "lie": "lay", "break": "broke", "fall": "fell",
         "give": "gave", "make": "made", "find": "found", "think": "thought", "bring": "brought", "buy": "bought", "sell": "sold", "hear": "heard",
         "run": "ran", "set": "set", "put": "put", "let": "let", "stand": "stood", "lose": "lost", "pay": "paid", "send": "sent", "swear": "swore",
         "wake": "woke", "write": "wrote", "drive": "drove", "ride": "rode", "freeze": "froze", "sing": "sang", "steal": "stole", "throw": "threw",
         "catch": "caught", "dig": "dug", "hold": "held", "lend": "lent", "mean": "meant", "meet": "met", "shake": "shook", "slide": "slid",
         "spend": "spent", "split": "split", "stick": "stuck", "strike": "struck", "swim": "swam", "teach": "taught", "tear": "tore", "win": "won",
         "wear": "wore", "weep": "wept", "creep": "crept", "sweep": "swept", "bite": "bit", "blow": "blew", "grow": "grew", "fly": "flew",
         "forget": "forgot", "hang": "hung", "hide": "hid", "light": "lit", "rise": "rose", "shine": "shone", "sink": "sank", "speak": "spoke",
         "spin": "spun", "spring": "sprang", "stink": "stank", "draw": "drew", "drink": "drank", "eat": "ate", "begin": "began", "feed": "fed"}


def _split(lemma):
    head, _, rest = lemma.partition(" ")
    return head, (" " + rest if rest else "")


def third(lemma):
    a, _, b = lemma.partition(" and ")
    if b and len(a.split()) <= 2 and len(b.split()) <= 2:           # 'toss and turn' -> 'tosses and turns' (not 'day and night')
        return third(a) + " and " + third(b)
    head, rest = _split(lemma)
    if head in _THIRD:
        return _THIRD[head] + rest
    if re.search(r"[^aeiou]y$", head):
        return head[:-1] + "ies" + rest
    if re.search(r"(s|sh|ch|x|z|o)$", head):
        return head + "es" + rest
    return head + "s" + rest


def past(lemma):
    a, _, b = lemma.partition(" and ")
    if b and len(a.split()) <= 2 and len(b.split()) <= 2:           # 'toss and turn' -> 'tosses and turns' (not 'day and night')
        return past(a) + " and " + past(b)
    head, rest = _split(lemma)
    if head in _PAST:
        return _PAST[head] + rest
    if head.endswith("e"):
        return head + "d" + rest
    if re.search(r"[^aeiou]y$", head):
        return head[:-1] + "ied" + rest
    if re.search(r"^[^aeiou]*[aeiou][^aeiouwxy]$", head):          # stop -> stopped
        return head + head[-1] + "ed" + rest
    return head + "ed" + rest


def gerund(lemma):
    a, _, b = lemma.partition(" and ")
    if b and len(a.split()) <= 2 and len(b.split()) <= 2:           # 'toss and turn' -> 'tosses and turns' (not 'day and night')
        return gerund(a) + " and " + gerund(b)
    head, rest = _split(lemma)
    if head.endswith("ie"):
        return head[:-2] + "ying" + rest
    if head.endswith("e") and not head.endswith(("ee", "ye", "oe")):
        return head[:-1] + "ing" + rest
    if re.search(r"^[^aeiou]*[aeiou][^aeiouwxy]$", head):
        return head + head[-1] + "ing" + rest
    return head + "ing" + rest


class Realiser:
    """Fills sentence shapes. Uses the narrator's grammar for its no-repeats choosing."""

    def __init__(self, narr, lex, roles=None, key=""):
        self.narr, self.lex, self.key = narr, lex, key
        self.roles = dict(roles or {})
        self.num = "sg"

    def choose(self, key, options):
        return self.narr.g.choose(key, [(o, 1.0) for o in options])

    def _alts(self, text):
        while True:
            new = ALT.sub(lambda m: self.choose("salt:" + m.group(1), m.group(1).split("|")), text)
            if new == text:
                return text
            text = new

    def fill(self, text, depth=0):
        text = self._alts(text)
        out, pos = [], 0
        for m in SLOT.finditer(text):
            out.append(text[pos:m.start()])
            out.append(self.slot(m.group(1), depth))
            pos = m.end()
        out.append(text[pos:])
        return "".join(out)

    def slot(self, spec, depth):
        if spec.startswith("~"):                                   # {~is|are}
            one, _, many = spec[1:].partition("|")
            return one if self.num == "sg" else many
        var = None
        if ">" in spec:
            spec, var = spec.split(">", 1)
        name, *mods = spec.split(".")
        num = "sg"
        if name == "it":
            val = "it" if self.num == "sg" else "them"
        elif name == "its":
            val = "its" if self.num == "sg" else "their"
        elif name in self.roles:
            val = self.roles[name]
            if isinstance(val, dict):
                num, val = val.get("num", "sg"), val["text"]
            elif isinstance(val, (list, tuple)) and val and isinstance(val[0], str) and len(val) == 2 and val[1] in ("sg", "pl"):
                val, num = val
            if "{" in str(val) or "[" in str(val):
                val = self.fill(str(val), depth + 1) if depth < 12 else str(val)
        elif name in self.lex:
            opt = self.choose(f"lex:{self.key}:{name}" if name.startswith("_") else f"lex:{name}", self.lex[name])
            if isinstance(opt, tuple):
                opt, num = opt
            val = self.fill(opt, depth + 1) if depth < 12 else opt
        else:
            self.narr.g.missing.add(name)
            val = name.replace("_", " ")
        val = str(val)
        for mod in mods:
            if mod == "subj":
                self.num = num
            elif mod == "v":
                val = third(val) if self.num == "sg" else val
            elif mod == "past":
                val = past(val)
            elif mod == "ing":
                val = gerund(val)
            elif mod in MODS:
                val = MODS[mod](val)
        if var:
            self.roles[var] = {"text": val, "num": num}
        return val


def say(narr, shapes, lex, roles=None, key=""):
    """One sentence from a frame: try a few shapes and fillings, keep the one that best fits the moment
    (no snow in summer), repeats itself least, and echoes recent phrasing least."""
    w = narr.w
    best, best_score = "", None
    for _ in range(6):
        r = Realiser(narr, lex, roles, key)
        shape = narr.g.choose(f"shape:{key}", [(s, 1.0) for s in shapes])
        s = tidy(fix_articles(r.fill(shape)))
        score = (10 * len(C.context_clashes(s, w.season, w.weather, w.time_of_day, None))
                 + (3 if s in narr.recent else 0) + len(C.repeated_words(s)) + narr.echo(s))
        if best_score is None or score < best_score:
            best, best_score = s, score
        if score == 0:
            break
    narr.recent.append(best)
    narr.remember_phrases(best)
    return best


def expand(narr, text, lex=None, roles=None, key="x"):
    """Fill [a|b] choices and word-list slots in text that's otherwise finished (no tidying)."""
    return fix_articles(Realiser(narr, lex or {}, roles, key).fill(text))
