"""Speech, put together piece by piece and spoken in a person's own voice.

compose()  turns one of their inner-life facts into a speech: a way of saying each beat (what happened,
           the proof of it, what they do about it), filled with the real names and places.
voice()    then says it as they would: a gruff one clips it short, a warm one runs on with 'and', a
           melancholy one trails off, a nervous one stumbles, a shrewd one leans in. Each person also
           has a saying, an oath, and a word for you that are theirs alone, used now and then.
react()    what they notice about you before anything else: blood, rain on your cloak, the hour, the
           look of your trade.
"""
import random
import re

from . import inner as IN
from . import sentences as SN
from .textgen import cap

_SKIP_LOWER = {"I", "I'm", "I've", "I'd", "I'll"}
# a sentence that starts with one of these can be run on after 'and' without losing its subject
SUBJECTS = {"I", "I'm", "I've", "I'd", "He", "She", "They", "It", "There", "My", "Our", "The", "That", "Folk", "Nobody", "Everyone",
            "His", "Her", "Their", "Someone", "Everything"}
# facts a cheerful soul may exclaim over; the rest are not for exclaiming
LIGHT = {"sea", "slate", "dog", "winter", "place_memory", "dance", "lean_year"}


# only these are lowered when a sentence is run on after an opener or 'and'; anything else capitalised
# might be a name ('Chipping Alasgarth', 'Old Bracca') and keeps its capital
_LOWERABLE = {"the", "a", "an", "it", "it's", "its", "there", "there's", "my", "our", "we", "we're", "we've", "you", "you'll", "you're", "you've",
              "he", "he's", "she", "she's", "they", "they're", "that", "that's", "this", "these", "those", "folk", "nobody", "everyone", "every",
              "some", "someone", "something", "everything", "not", "no", "his", "her", "their", "if", "when", "what", "how", "once", "one", "all",
              "ask", "never", "still", "then", "here", "here's", "now", "last", "next", "today", "tomorrow", "yesterday", "since", "before", "after",
              "half", "most", "come", "go", "look", "keep", "don't", "do", "did", "have", "has", "had", "is", "was", "can", "could", "would",
              "will", "so", "but", "and", "or", "at", "in", "on", "by", "for", "with", "every", "each", "two", "three", "four", "few", "many",
              "out", "up", "down", "over", "off", "into", "from", "who", "why", "where", "which", "while", "until", "till", "though", "even",
              "just", "only", "always", "sometimes", "mostly", "maybe", "perhaps", "good", "bad", "poor", "rain", "frost", "snow", "winter",
              "spring", "summer", "autumn", "harvest", "nothing", "anything", "anyone", "everybody", "somebody", "nights", "night", "days", "day",
              "years", "year", "word", "news", "people", "children", "work", "trade", "money", "blame", "weigh", "near", "close", "across",
              "like", "long", "funny", "dust", "long", "hay", "quiet", "busy", "thatch", "ha", "well", "oh"}


def _lower_first(s, names):
    """Lower-case the first word of a sentence being run on, if it's an ordinary word (never a name)."""
    if not s:
        return s
    first = s.split(" ", 1)[0]
    bare = re.sub(r"[^\w'-]", "", first).lower()
    if first in _SKIP_LOWER or bare not in _LOWERABLE:
        return s
    return s[0].lower() + s[1:]


def _names(ctx):
    out = set()
    for k in ("o", "kname", "far", "region", "spirit", "village", "creditor", "dogname", "lover"):
        v = ctx.get(k)
        if isinstance(v, str):
            out |= set(v.replace("'s", "").split())
    return out


def context(g, npc, fact=None):
    """Everything a speech about this person's life might name."""
    w = g.world
    inner = IN.of(w, npc)
    site = w.tiles[npc.home].site or {}
    ctx = dict(village=site.get("name", "the village"), economy=site.get("economy", "farming"), job=npc.job, pkin=inner.get("pkin", "mother"),
               **{k: inner.get(k, "") for k in ("kin", "kname", "far", "region", "spirit", "water", "fest", "job2", "dogname", "creditor", "creditor_v")})
    kg = inner["kgender"]
    if fact and fact["kind"] in ("dance", "promised"):
        ctx["kname"], kg = inner["lover"], inner["lgender"]
    ctx.update(dict(khe="she" if kg == "female" else "he", khim="her" if kg == "female" else "him", khis="her" if kg == "female" else "his"))
    if fact and fact["kind"] in ("tie", "gossip"):
        other = next((x for x in w.tiles[npc.home].npcs if x.name == fact["other"]), None)
        if other:
            op = other.pronouns()
            ctx.update(o=other.name, oj=other.job, ohe=op["he"], ohim=op["him"], ohis=op["his"], tool=fact.get("tool", "spade"), _other=other)
    else:
        # someone they'd mention in passing
        others = [x for x in w.tiles[npc.home].npcs if x is not npc]
        if others:
            ctx["o"] = sorted(others, key=lambda x: x.name)[0].name
    if fact and fact["kind"] == "saw_beast":
        sps = sorted(w.species, key=lambda s: s["name"])
        if sps:
            sp = IN._rng(w, "beast", npc.name).choice(sps)
            from .textgen import article
            mark = sp.get("mark", "its eyes")
            ctx.update(a_beast=article(sp["name"]), mark=cap(mark), mark_cap=cap(mark))
    return ctx


def _lex():
    from . import lex_dialogue as DL
    return DL.LEX


def compose(g, npc, fact):
    """One of their facts as a speech in their voice, quoted. None if it can't be told here."""
    ctx = context(g, npc, fact)
    if fact["kind"] in ("tie", "gossip") and "oj" not in ctx:
        return None
    if fact["kind"] == "saw_beast" and "a_beast" not in ctx:
        return None
    beats = IN.beats_for(fact, g.world, ctx.pop("_other", None))
    key = fact["kind"] + ":" + fact.get("inc", "") + fact.get("side", "") + (str(IN.quirk_of(g.world, next(x for x in g.world.tiles[npc.home].npcs if x.name == fact["other"]))) if fact["kind"] == "gossip" else "")
    n, r = g.narr, g.rng
    if "roles" not in fact:                  # a fact from an older save: choose its roles now, and keep them
        spec = (IN.INCIDENTS[fact["inc"]] if fact["kind"] == "tie" else IN.OWN.get(fact["kind"], {})).get("roles", {})
        fact["roles"] = IN._roles(IN._rng(g.world, "roles", npc.name, key), spec)
    roles = dict(ctx, **fact["roles"])
    parts = []
    for i, shapes in enumerate(beats):
        if i == 1 and len(beats) > 2 and r.random() < 0.12:       # sometimes they leave out the proof
            continue
        parts.append(SN.say(n, shapes, _lex(), roles, f"{key}:{i}"))
    asks = IN.ASK_BACK.get(fact["kind"])
    light = fact["kind"] in LIGHT or (fact["kind"] == "tie" and fact["inc"] in ("storm", "loan", "rivals", "courting"))
    opinion = fact["kind"] == "tie" and fact["side"] == "a" and fact["inc"] in ("boundary", "weights", "rivals")
    return '"' + voice(g, npc, parts, ctx, asks, light, opinion) + '"'


def voice(g, npc, sentences, ctx=None, asks=None, light=True, opinion=False):
    """Say these sentences the way this person talks."""
    ctx = ctx or {}
    inner = IN.of(g.world, npc)
    openers, clip, ramble, hedge, trail, stammer, ask, exclaim = IN.VOICES.get(inner["voice"], IN.VOICES["warm"])
    bend = inner.get("bend", 0.0)
    ramble, ask = max(0.0, ramble + bend), max(0.0, ask + bend / 2)
    r, names = g.rng, _names(ctx)
    s = [x.strip() for x in sentences if x and x.strip()]
    if not s:
        return ""
    # clipped: a gruff one drops the 'I've' and 'It's been'
    if clip:
        for i, x in enumerate(s):
            m = re.match(r"(I've|It's been|I'm|It was) (\w+)(.*)", x)
            if m and r.random() < clip and (m.group(1) != "I've" or m.group(2) in ("said", "been", "had", "seen", "asked", "got", "told", "never", "started", "stopped", "heard", "counted")):
                rest = (m.group(2) + m.group(3)) if m.group(1) in ("I've", "I'm") else ("Been " if m.group(1) == "It's been" else "Was ") + m.group(2) + m.group(3)
                s[i] = cap(rest)
        if r.random() < clip * 0.5 and len(s) > 2:
            s = s[:-1]                                   # and doesn't bother with the last word on it
    # rambling: run the first two sentences together with 'and'
    if ramble and len(s) > 1 and r.random() < ramble:
        i = 0
        a, b = s[i], s[i + 1]
        head = b.split(" ", 1)[0].strip(",.!?").replace("'s", "")
        subject = head in SUBJECTS
        if a.endswith(".") and subject and len(b.split(".")[0].split()) >= 3 and not b.endswith("?") and len(a) + len(b) < 190:
            s[i:i + 2] = [a[:-1] + r.choice([", and ", " - and ", ", and "]) + _lower_first(b, names)]
    # hedged: only an opinion can be hedged ('seems to me {o}'s weights are light'), not a plain fact
    if hedge and opinion and r.random() < hedge:
        i = 0
        if not s[i].endswith("?") and not s[i].startswith(("I think", "If ")):
            s[i] = cap(r.choice(IN.HEDGES)) + _lower_first(s[i], names)
    # stumbling
    if stammer and r.random() < stammer:
        for i, x in enumerate(s):
            if re.match(r"I\b", x):
                s[i] = "I - " + x
                break
    # exclaiming
    if exclaim and light and r.random() < exclaim:
        i = r.randrange(len(s))
        if s[i].endswith("."):
            s[i] = s[i][:-1] + "!"
    # a word for you, or their oath - one flourish at most
    roll = r.random()
    word = inner["address"]
    if word == "stranger" and npc.tier in ("friendly", "devoted"):
        word = "friend"
    if word and word != "you" and roll < 0.16:
        i = r.randrange(len(s))
        if s[i][-1] in ".!?" and len(s[i]) < 120:
            s[i] = s[i][:-1] + ", " + word + s[i][-1]
    elif roll > 0.95 and len(s) > 1:
        s.insert(1, cap(inner["oath"]) + "!")
    # asking you something back
    if asks and r.random() < ask:
        s.append(g.narr.say(r.choice(asks), ctx))
    # their saying, once in a while (and not every time you see them)
    m = npc.mem
    if r.random() < 0.12 and m.get("said_saying", -9) < g.world.day - 2:
        m["said_saying"] = g.world.day
        s.append(inner["saying"])
    # an opener
    confiding = s[0].startswith(tuple(x.split(",")[0] for x in IN.LEX["confide"])) or ":" in s[0][:45]
    if openers and not confiding and r.random() < 0.45:
        op = r.choice(openers)
        s[0] = op + (_lower_first(s[0], names) if op.endswith((", ", "- ", ": ")) else s[0])
    # trailing off
    if trail and r.random() < trail and s[-1].endswith("."):
        s[-1] = s[-1][:-1] + "..."
    return " ".join(s)


# --------------------------------------------------------------------------------------------- noticing you
def react(g, npc, first):
    """What they notice about you, once a day: a short spoken line, or None. Shapes in lex_dialogue.REACT."""
    from . import lex_dialogue as DL
    w, p, m = g.world, g.player, npc.mem
    if m.get("react_day") == w.day:
        return None
    tone = npc.demeanour if npc.demeanour in DL.REACT["hurt"] else "warm"
    kind = None
    if p.hp < p.maxhp * 0.45:
        kind = "hurt"
    elif w.weather == "snow":
        kind = "snow"
    elif w.weather in ("rain", "storm", "drizzle") and w.time_of_day not in ("night", "deepnight"):
        kind = "wet"
    elif w.time_of_day in ("night", "deepnight"):
        kind = "late"
    elif first and getattr(p, "klass", None) in DL.REACT["class"] and g.rng.random() < 0.6:
        kind = "class"
    if not kind or (kind != "hurt" and g.rng.random() < 0.35):
        return None
    # one person in a village remarks on the weather or the hour each day, and on your trade only once;
    # what they notice about your wounds, each says for themselves
    seen = w.__dict__.setdefault("reacted", set())
    key = (npc.home, kind) if kind == "class" else (npc.home, kind, w.day) if kind != "hurt" else None
    if key in seen:
        return None
    if key:
        seen.add(key)
    m["react_day"] = w.day
    table = DL.REACT[kind]
    shapes = table.get(p.klass) if kind == "class" else table.get("*") or table.get(tone) or table.get("warm")
    return SN.say(g.narr, shapes, DL.LEX, {}, f"react-{kind}-{tone if kind in ('hurt', 'wet', 'late') else ''}")
