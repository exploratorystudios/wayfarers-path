"""A name generator built from the sound patterns of a name list, not its pieces.

Training (tools/name_analysis.py) reads the source lists and learns, per culture
and gender:

  * how many syllables names have
  * which consonants and consonant clusters may begin a word, sit between
    vowels, or end a word, letter by letter, by position
  * which vowels form a syllable's nucleus, and which vowel may follow which
  * how gender is marked on the last syllable (its vowel, then its coda)

Generation builds a name one *letter* at a time from those positional
distributions. Each letter depends on the letter before it, backed off to that
letter's phonological class (stop, fricative, nasal, liquid, glide; front, back
or low vowel) and then to its position alone. So names follow the same
phonotactics without copying chunks of real ones. Every candidate is checked
against the corpus's legal letter pairs, scored for how typical it sounds, and
rejected if it is a known name or too close to one.

Cultures are also related by **sound changes**, learned by aligning names that
appear in several lists (Westron Abigail ~ Archaic Abigayl ~ Northish Abyiga ~
Southron Abigala). `evolve()` applies a culture's changes to any name, so one
invented proto-name can be given its Archaic, Northish and Southron forms.

The learned model is stored in rpg/data/names_model.json, so the game does not
need the source list at run time.
"""
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "data" / "names_model.json"

VOWELS = set("aeiou")
DIGRAPHS = ("th", "ch", "sh", "ph", "ck")

# phonological classes, used to generalise ("after a stop..." rather than "after a d...")
CLASS = {}
for ch in "pbtdkcgq":
    CLASS[ch] = "stop"
for ch in "fvszxh":
    CLASS[ch] = "fric"
for d in ("th", "ch", "sh", "ph"):
    CLASS[d] = "fric"
CLASS["ck"] = "stop"
for ch in "mn":
    CLASS[ch] = "nasal"
for ch in "lr":
    CLASS[ch] = "liquid"
for ch in "wj":
    CLASS[ch] = "glide"
CLASS["y_c"] = "glide"
for ch in "ie":
    CLASS[ch] = "front"
for ch in "ou":
    CLASS[ch] = "back"
CLASS["a"] = "low"
CLASS["y"] = "front"


# ------------------------------------------------------------------ phonology
def units(name):
    """Split a lower-case name into graphemes, each tagged V or C.
    'y' is a vowel unless it stands before a vowel (Maya, Yanna: a glide)."""
    s = name.lower()
    out = []
    i = 0
    while i < len(s):
        if s[i:i + 2] in DIGRAPHS:
            out.append((s[i:i + 2], "C"))
            i += 2
            continue
        ch = s[i]
        if ch == "y":
            nxt = s[i + 1] if i + 1 < len(s) else ""
            out.append(("y", "C" if nxt in VOWELS or nxt == "y" else "V"))
        elif ch in VOWELS:
            out.append((ch, "V"))
        else:
            out.append((ch, "C"))
        i += 1
    return out


def skeleton(name):
    return "".join(k for _, k in units(name))


def cls(u, kind):
    if u == "y" and kind == "C":
        return "glide"
    return CLASS.get(u, "other")


def syllables(name, onsets):
    """Divide into (onset, nucleus, coda) by the maximal-onset principle:
    a consonant run between vowels gives the next syllable the longest onset
    that can also begin a word."""
    us = units(name)
    runs = []          # alternating runs of C and V
    for u, k in us:
        if runs and runs[-1][0] == k:
            runs[-1][1].append(u)
        else:
            runs.append([k, [u]])
    sylls = []
    i = 0
    onset = []
    if runs and runs[0][0] == "C":
        onset = runs[0][1]
        i = 1
    while i < len(runs):
        nucleus = runs[i][1]
        i += 1
        if i >= len(runs):
            sylls.append((tuple(onset), tuple(nucleus), ()))
            break
        cons = runs[i][1]
        i += 1
        if i >= len(runs):                       # word-final consonants
            sylls.append((tuple(onset), tuple(nucleus), tuple(cons)))
            break
        split = len(cons)                         # everything is coda unless an onset fits
        for k in range(len(cons)):
            if "".join(cons[k:]) in onsets or len(cons[k:]) == 1:
                split = k
                break
        sylls.append((tuple(onset), tuple(nucleus), tuple(cons[:split])))
        onset = cons[split:]
    return sylls


# ------------------------------------------------------------------ training
def _ctx_counts():
    return defaultdict(Counter)


def train(first):
    """first: {culture: {gender: [names]}} -> a JSON-able model."""
    all_names = [n for c in first.values() for g in c.values() for n in g]
    initial_clusters = Counter()
    for n in all_names:
        lead = []
        for u, k in units(n):
            if k == "V":
                break
            lead.append(u)
        if lead:
            initial_clusters["".join(lead)] += 1
    onsets = {o for o, c in initial_clusters.items() if c >= 2}
    legal_pairs = Counter()
    for n in all_names:
        s = n.lower()
        legal_pairs.update(s[i:i + 2] for i in range(len(s) - 1))

    def table(names):
        t = dict(sylls=Counter(), lead=_ctx_counts(), lead_len=Counter(), bridge=_ctx_counts(), bridge_len=Counter(),
                 nuc=_ctx_counts(), nuc_len=Counter(), last_nuc=_ctx_counts(), coda_len=Counter(), coda=_ctx_counts(),
                 nucu=_ctx_counts(), n=len(names))
        for n in names:
            ss = syllables(n, onsets)
            t["sylls"][len(ss)] += 1
            onset0 = ss[0][0]
            t["lead_len"][len(onset0)] += 1
            prev = "^"
            for u in onset0:
                t["lead"][prev][u] += 1
                prev = u
            for i, (on, nu, co) in enumerate(ss):
                last = i == len(ss) - 1
                if i > 0:          # the consonants between the previous nucleus and this one
                    bridge = list(ss[i - 1][2]) + list(on)
                    t["bridge_len"][len(bridge)] += 1
                    prev = "^"
                    for u in bridge:
                        t["bridge"][prev][u] += 1
                        prev = u
                key = "last_nuc" if last else "nuc"
                t["nuc_len"][len(nu)] += 1
                t["nucu"]["f" if last else ("i" if i == 0 else "m")]["".join(nu)] += 1
                prev = "^" if i == 0 else ("^m" if not last else "^f")
                for u in nu:
                    t[key][prev][u] += 1
                    prev = u
                if last:
                    t["coda_len"][len(co)] += 1
                    prev = "v:" + nu[-1]
                    for u in co:
                        t["coda"][prev][u] += 1
                        prev = u
        return t

    bridges, finals = Counter(), Counter()
    for n in all_names:
        ss = syllables(n, onsets)
        for i in range(1, len(ss)):
            bridges["".join(ss[i - 1][2] + ss[i][0])] += 1
        finals["".join(ss[-1][2])] += 1
    codas = set()
    for b in bridges:          # a bridge is a coda plus an onset; any coda seen that way may join any onset
        for k in range(len(b) + 1):
            if b[k:] in onsets or len(b[k:]) <= 1:
                codas.add(b[:k])
                break
    model = dict(onsets=sorted(onsets), pairs=sorted(p for p, c in legal_pairs.items() if c >= 1), tables={}, known=sorted(set(all_names)),
                 bridges=sorted(bridges), codas=sorted(codas), finals=sorted(finals))
    pooled = defaultdict(list)
    for culture, gs in first.items():
        for gender, names in gs.items():
            model["tables"][f"{culture}/{gender}"] = jsonable(table(names))
            pooled[gender] += names
            pooled["any"] += names
        # the "combined" list: both genders' sound patterns learned together
        both = [n for names in gs.values() for n in names]
        model["tables"][f"{culture}/any"] = jsonable(table(both))
        first[culture]["any"] = both
    for gender, names in pooled.items():
        model["tables"][f"*/{gender}"] = jsonable(table(names))
    model["changes"] = learn_changes({c: {g: v for g, v in gs.items() if g != "any"} for c, gs in first.items()})
    # how typical training names sound under their own culture's model: the bar new names must clear
    gen = NameGen(model)
    for key in list(model["tables"]):
        c, g = key.split("/")
        names = first[c][g] if c != "*" else pooled[g]
        scores = sorted(gen.score(n, c, g) for n in names)
        model["tables"][key]["floor"] = scores[max(0, int(len(scores) * 0.25) - 1)]
    return model


def jsonable(t):
    out = {}
    for k, v in t.items():
        if isinstance(v, defaultdict):
            out[k] = {a: dict(b) for a, b in v.items()}
        elif isinstance(v, Counter):
            out[k] = {str(a): b for a, b in v.items()}
        else:
            out[k] = v
    return out


# ------------------------------------------------------------------ sound changes between cultures
def edit_ops(a, b):
    """Levenshtein alignment of two strings as a list of (a_piece, b_piece)."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    ops, i, j = [], n, m
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            ops.append((a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            ops.append((a[i - 1], ""))
            i -= 1
        else:
            ops.append(("", b[j - 1]))
            j -= 1
    return ops[::-1], d[n][m]


def cognates(src, dst):
    """Pair each source name with its closest relative in another list (if close enough)."""
    pairs = []
    for s in src:
        best, bd = None, 9
        for t in dst:
            if t[0].lower() != s[0].lower() and abs(len(t) - len(s)) > 2:
                continue
            _, dist = edit_ops(s.lower(), t.lower())
            if dist < bd:
                best, bd = t, dist
        if best and bd <= max(1, len(s) // 2) and best.lower() != s.lower():
            pairs.append((s.lower(), best.lower()))
    return pairs


def final_class(word):
    ch = word[-1]
    if ch in VOWELS or (ch == "y" and len(word) > 1 and word[-2] not in VOWELS):
        return "vowel"
    return CLASS.get(word[-2:], CLASS.get(ch, "other")) if word[-2:] in DIGRAPHS else CLASS.get(ch, "other")


def learn_changes(first, hub="Westron"):
    """For each culture, the sound changes that turn hub-culture names into its own:
      * letter substitutions (i -> y, c -> k, a -> ae...), with the rate at which they apply
      * how endings change, as a distribution per gender and final sound class:
        "strip k letters, add X" (no change included), e.g. Southron men's names ending
        in a nasal: Adam -> Adamo (strip 0, add -o), Bradyn -> Brado (strip 2, add -o)."""
    out = {}
    for culture in first:
        if culture == hub:
            continue
        subs, opp = Counter(), Counter()
        ends = defaultdict(Counter)
        for gender in first[culture]:
            for a, b in cognates(first[hub][gender], first[culture][gender]):
                ops, _ = edit_ops(a, b)
                k = 0
                while k < min(len(a), len(b)) and a[k] == b[k]:
                    k += 1
                strip, add = len(a) - k, b[k:]
                if strip <= 3 and len(add) <= 4:
                    ends[f"{gender}/{final_class(a)}"][f"{strip}|{add}"] += 1
                # letter changes anywhere before the last two letters (the ending is handled above)
                pos = 0
                for x, y in ops:
                    if pos >= len(a) - 2:
                        break
                    if x and y and x != y:
                        subs[(x, y)] += 1
                    elif x and not y:
                        subs[(x, "")] += 1
                    elif y and not x and pos > 0:
                        subs[(a[pos - 1], a[pos - 1] + y)] += 1
                    if x:
                        pos += 1
                for ch in a[:-2]:
                    opp[ch] += 1
        rules = []
        for (x, y), c in subs.items():
            rate = c / max(1, opp[x[0]])
            if not y and (c < 6 or rate < 0.2):     # a lost letter must be a real habit, not alignment noise
                continue
            if c >= 4 and rate >= 0.06:
                rules.append(dict(src=x, dst=y, rate=round(min(0.9, rate), 3), support=c))
        rules.sort(key=lambda r: -r["support"])
        endings = {}
        for key, dist in ends.items():
            total = sum(dist.values())
            if total < 3:
                continue
            kept = [(o, c) for o, c in dist.items() if c >= 2 or o == "0|"]
            endings[key] = [dict(strip=int(o.split("|")[0]), add=o.split("|")[1], p=round(c / total, 3)) for o, c in
                            sorted(kept, key=lambda x: -x[1])]
        out[culture] = dict(subs=rules[:16], endings=endings)
    return out


# ------------------------------------------------------------------ generation
class NameGen:
    def __init__(self, model=None):
        if model is None:
            model = json.loads(MODEL_PATH.read_text())
        self.m = model
        self.onsets = set(model["onsets"])
        self.pairs = set(model["pairs"])
        self.known = set(n.lower() for n in model["known"])
        self.known_list = sorted(self.known)
        self.bridges = set(model.get("bridges", []))
        self.codas = set(model.get("codas", []))
        self.finals = set(model.get("finals", []))

    # -- drawing ------------------------------------------------------------
    @staticmethod
    def _draw(rng, counter, temp=1.0):
        items = list(counter.items())
        if not items:
            return None
        weights = [c ** (1 / temp) for _, c in items]
        return rng.choices([k for k, _ in items], weights)[0]

    def _letter(self, rng, tables, key, prev, kind):
        """A letter given the previous one; backs off to the previous letter's class, then to
        the slot's overall frequencies. Blending in the class level lets new pairs appear."""
        mix = Counter()
        for t, w in tables:
            dist = t[key]
            exact = dist.get(prev, {})
            by_class = Counter()
            pc = CLASS.get(prev[2:] if prev.startswith("v:") else prev, None)
            for p, d in dist.items():
                if p != prev and CLASS.get(p[2:] if p.startswith("v:") else p) == pc and pc:
                    by_class.update(d)
            overall = Counter()
            for d in dist.values():
                overall.update(d)
            for src, lam in ((exact, 0.70), (by_class, 0.22), (overall, 0.08)):
                tot = sum(src.values())
                if tot:
                    for u, c in src.items():
                        mix[u] += w * lam * c / tot
        return self._draw(rng, mix, temp=1.15)

    def _len(self, rng, tables, key):
        mix = Counter()
        for t, w in tables:
            tot = sum(t[key].values())
            for k, c in t[key].items():
                mix[int(k)] += w * c / tot
        return self._draw(rng, mix)

    def _tables(self, culture, gender):
        own = self.m["tables"].get(f"{culture}/{gender}")
        pooled = self.m["tables"][f"*/{gender}"]
        return [(own, 0.8), (pooled, 0.2)] if own else [(pooled, 1.0)]

    def _cluster(self, rng, T, key, length, start, ok):
        """Consonants built letter by letter, kept only if the whole run is legal in its position."""
        for _ in range(10):
            s, prev = "", start
            for _ in range(length):
                u = self._letter(rng, T, key, prev, "C")
                if u is None:
                    break
                s += u
                prev = u
            if ok(s):
                return s
        return None

    def _nucleus(self, rng, T, pos):
        mix = Counter()
        for t, w in T:
            d = t.get("nucu", {}).get(pos, {})
            tot = sum(d.values())
            for k, c in d.items():
                mix[k] += w * c / tot
        return self._draw(rng, mix, temp=1.1) or "a"

    def raw(self, rng, culture="Westron", gender="female"):
        T = self._tables(culture, gender)
        n = max(1, self._len(rng, T, "sylls"))
        lead = self._cluster(rng, T, "lead", self._len(rng, T, "lead_len"), "^", lambda c: c == "" or c in self.onsets)
        s = lead or ""
        for i in range(n):
            last = i == n - 1
            if i > 0:
                k = max(1, self._len(rng, T, "bridge_len"))
                b = self._cluster(rng, T, "bridge", k, "^", lambda c: c in self.bridges or self._splits(c))
                if b is None:
                    b = self._cluster(rng, T, "bridge", 1, "^", lambda c: c in self.bridges)
                s += b or "l"
            nuc = self._nucleus(rng, T, "f" if last else ("i" if i == 0 else "m"))
            s += nuc
            if last:
                k = self._len(rng, T, "coda_len")
                c = self._cluster(rng, T, "coda", k, "v:" + nuc[-1], lambda c: c in self.finals)
                s += c or ""
        return s

    def _splits(self, c):
        """A new medial cluster is fine if it is a known coda followed by a known onset."""
        return any(c[:k] in self.codas and c[k:] in self.onsets for k in range(1, len(c)))

    # -- judging ------------------------------------------------------------
    def legal(self, s):
        if len(s) < 3 or len(s) > 11:
            return False
        if any(s[i:i + 2] not in self.pairs for i in range(len(s) - 1)):
            return False
        sk = skeleton(s)
        if "CCCC" in sk or "VVV" in sk or re.search(r"(.)\1\1", s) or re.search(r"([aeiouy])\1", s.replace("ee", "")):
            return False
        if re.search(r"[^aeiouy]([^aeiouy])\1", s) or re.search(r"(..).?\1\1", s):   # no 'ndd', no 'lylyly'
            return False
        if re.search(r"(...).*\1", s) or s.count("y") > 2 or len(re.findall(r"[aeiouy]+", s)) > 4:   # no 'ialial', no stutter
            return False
        if sk.startswith("CCC") and s[:3] not in self.onsets:
            return False
        return True

    def score(self, s, culture, gender):
        """Average log-probability per letter under the positional letter model (higher = more typical)."""
        T = self._tables(culture, gender)
        total, n = 0.0, 0
        prev = "^"
        for u, k in units(s):
            p = 0.0
            for t, w in T:
                for key in (("lead", "bridge", "coda") if k == "C" else ("nuc", "last_nuc")):
                    d = t[key]
                    row = d.get(prev, {})
                    tot = sum(row.values())
                    allc = sum(sum(r.values()) for r in d.values()) or 1
                    col = sum(r.get(u, 0) for r in d.values())
                    p = max(p, w * (0.7 * (row.get(u, 0) / tot if tot else 0) + 0.3 * col / allc))
            total += math.log(p + 1e-4)
            n += 1
            prev = u
        return total / max(1, n)

    def too_close(self, s):
        if s in self.known:
            return True
        for k in self.known_list:
            if abs(len(k) - len(s)) <= 1 and k[:2] == s[:2]:
                if edit_ops(s, k)[1] <= (1 if len(s) <= 6 else 2):
                    return True
        return False

    def generate(self, rng=None, culture="Westron", gender="female", tries=400, allow_close=False, pick_of=2):
        """A new name: legal, typical-sounding, and not a copy of (or one letter from) a known name.
        Makes `pick_of` acceptable candidates and keeps the most natural-sounding."""
        rng = rng or random.Random()
        floor = self.m["tables"].get(f"{culture}/{gender}", self.m["tables"][f"*/{gender}"]).get("floor", -9)
        good, best = [], None
        for _ in range(tries):
            s = self.raw(rng, culture, gender)
            if not self.legal(s) or (not allow_close and self.too_close(s)):
                continue
            sc = self.score(s, culture, gender)
            if sc >= floor:
                good.append((sc, s))
                if len(good) >= pick_of:
                    break
            elif best is None or sc > best[0]:
                best = (sc, s)
        if good:
            return max(good)[1].capitalize()
        return (best[1] if best else "Ash").capitalize()

    # -- sound change ---------------------------------------------------------
    def evolve(self, name, culture, gender="female", rng=None):
        """Give a (Westron-style) name another culture's sound changes: first its ending,
        drawn from the learned distribution for that gender and final sound, then letter changes."""
        rng = rng or random.Random(f"{name}-{culture}")
        ch = self.m["changes"].get(culture)
        s = name.lower()
        if not ch:
            return name
        opts = ch["endings"].get(f"{gender}/{final_class(s)}", [])
        if opts:
            r, acc = rng.random(), 0.0
            for o in opts:
                acc += o["p"]
                if r <= acc:
                    if len(s) - o["strip"] >= 2:
                        s = s[: len(s) - o["strip"]] + o["add"]
                    break
        out = []
        i = 0
        while i < len(s):
            done = False
            for rl in ch["subs"]:
                src = rl["src"]
                if s.startswith(src, i) and rng.random() < rl["rate"]:
                    out.append(rl["dst"])
                    i += len(src)
                    done = True
                    break
            if not done:
                out.append(s[i])
                i += 1
        s = "".join(out)
        s = re.sub(r"(.)\1\1+", r"\1\1", s)
        if not self.legal(s) and getattr(rng, "_retry", 0) < 6:
            r2 = random.Random(f"{name}-{culture}-{rng.random()}")
            r2._retry = getattr(rng, "_retry", 0) + 1
            return self.evolve(name, culture, gender, r2)
        return s.capitalize() if self.legal(s) else name

    def family(self, rng=None, gender="female", hub="Westron"):
        """One invented name and its relatives in every culture."""
        rng = rng or random.Random()
        proto = self.generate(rng, hub, gender)
        out = {hub: proto}
        for c in self.m["changes"]:
            out[c] = self.evolve(proto, c, gender, random.Random(f"{proto}-{c}-{rng.random()}"))
        return out


_GEN = None


def gen():
    global _GEN
    if _GEN is None:
        _GEN = NameGen()
    return _GEN
