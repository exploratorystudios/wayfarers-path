"""What someone says when you talk to them, after the greeting.

In order of what matters most to them:
  1. the errand they gave you: they ask after it, and nudge you about the step you're on
  2. your errands: what they know of the people, places and beasts you need
  3. on a return visit, the next piece of their inner life (inner.py, told by speech.py)
  4. fresh news from elsewhere
  5. their work this season, built from their trade's tasks, a word about the village, and a closing
     remark in their own temperament
  6. the older rumours (a beast seen somewhere, a ruin, a shrine), and then nothing new

Everything is built at the sentence level (sentences.py) from the shapes in lex_dialogue.py, then said
in the speaker's own voice (speech.voice).

Each topic is told once (per day, for the ones that change), so coming back brings something new.
"""
import re

from . import lex_life as LIFE
from . import inner as IN
from . import speech as SP
from . import sentences as SN
from . import lex_dialogue as DL
from .textgen import cap

TROUBLE_NOW = {"beast": "something killing the sheep", "fever": "the fever in the houses", "lost": "{who} lost out in the wilds",
               "haunting": "something walking the lanes at night", "heirloom": "the {thing} stolen", "well": "the water gone bad",
               "strayed": "the {animal} strayed", "letter": "the letter wanting carrying", "supplies": "the stores running short",
               "wedding": "a wedding and no gift for it", "blight": "the blight on the fields", "feud": "two neighbours at each other's throats",
               "labour": "the work and nobody to do it"}


def topic(g, npc):
    """The thing this person most wants to say to you today, as a spoken line (or None)."""
    for fn in (checkin, need, story, news, own):
        line = fn(g, npc)
        if line:
            return line
    return None


def _say(g, npc, line, ctx):
    return g.narr.say(line, dict(ctx, **npc.pronouns()), [npc.demeanour])


def _temper(npc):
    return npc.demeanour if npc.demeanour in LIFE.TAIL else "warm"


# ---------------------------------------------------------------- 1. the errand they gave you
def checkin(g, npc):
    w = g.world
    if npc.mem.get("checkin_day") == w.day:
        return None
    plot = next((p for p in getattr(g, "plots", []) if p["giver"] == npc.name and p["status"] == "active"), None)
    if not plot or plot["i"] >= len(plot["steps"]):
        return None
    npc.mem["checkin_day"] = w.day
    st = plot["steps"][plot["i"]]
    ctx = dict(plot["F"])
    ctx.update({k: v for k, v in st.items() if isinstance(v, str)})
    for k in ("fhe", "fhim", "fhis"):
        ctx.setdefault(k, "they")
    ctx.update(obj_cap=cap(str(ctx.get("obj", "it"))), dir_cap=cap(str(ctx.get("dir", "out there"))), **npc.pronouns())
    temper = _temper(npc)
    parts = [SN.say(g.narr, DL.CHECKIN_SHAPES.get(temper, DL.CHECKIN_SHAPES["warm"]), DL.LEX, ctx, f"checkin-{temper}")]
    nudge = DL.NUDGE_SHAPES.get("climax" if st.get("climax") else st["mech"])
    if nudge:
        parts.append(SN.say(g.narr, nudge, DL.LEX, ctx, f"nudge-{st['mech']}"))
    return '"' + SP.voice(g, npc, parts, ctx) + '"'


# ---------------------------------------------------------------- 2. what they know of your errands
def _needs(g, npc):
    """(key, kind, facts) for the people, places and beasts your errands need, nearest first."""
    w, here = g.world, npc.home
    out = []
    for p in getattr(g, "plots", []):
        if p["status"] != "active" or p["giver"] == npc.name or p["i"] >= len(p["steps"]):
            continue
        st = p["steps"][p["i"]]
        if st.get("npc") and st.get("npc") != npc.name and st["mech"] in ("ask", "deal", "bring"):
            out.append((f"need:p:{st['npc']}", "person", dict(name=st["npc"], home=st.get("npc_home"))))
    for q in getattr(g, "quests", []):
        if q["status"] != "active":
            continue
        t = q.get("target")
        if t and t != here and t in w.tiles:
            site = w.tiles[t].site
            if site and site.get("kind") == "village":
                out.append((f"need:v:{t}", "place", dict(pos=t)))
        c = q.get("creature")
        if q["kind"] == "slay" and c is not None and t:
            out.append((f"need:b:{c.species['name']}", "beast", dict(species=c.species, pos=t)))
    if getattr(g, "has_quest", False) and not w.quest.done:
        for t in w.quest.targets(g) or []:
            site = w.tiles[t].site if t in w.tiles else None
            if t != here and site and site.get("kind") == "village":
                out.append((f"need:v:{t}", "place", dict(pos=t)))
    seen, uniq = set(), []
    for k, kind, f in out:
        if k not in seen:
            seen.add(k)
            uniq.append((k, kind, f))
    return uniq


def need(g, npc):
    from . import story as S
    w, n, told = g.world, g.narr, npc.mem["told"]
    heard = g.__dict__.setdefault("heard_needs", [])     # what anyone has already told you: once is enough
    for key, kind, f in _needs(g, npc):
        if key in told or key in heard:
            continue
        if kind == "person":
            who = S.find_npc(w, f["name"])
            if not who or who is npc:
                continue
            pr = who.pronouns()
            ctx = dict(far=who.name, fjob=who.job, fvillage=w.tiles[who.home].site["name"], fhe=pr["he"], fhim=pr["him"], fhis=pr["his"])
            manners = DL.MANNER.get(who.demeanour, DL.MANNER["warm"]) + LIFE.PERSON_MORE.get(who.demeanour, [])
            ctx["manner"] = SN.say(n, manners, DL.LEX, ctx, f"manner-{who.demeanour}")
            shapes = DL.NEED_PERSON_SHAPES
        elif kind == "place":
            t = w.tiles[f["pos"]]
            here = w.tiles[npc.home]
            ctx = dict(place=t.site["name"], dir=n.dir_phrase(npc.home, f["pos"]), economy=t.site["economy"], economy_cap=cap(t.site["economy"]))
            ctx["how"] = SN.say(n, DL.HOW_ROAD if (t.road and here.road) else DL.HOW_WILD, DL.LEX, ctx, "needhow")
            ctx["about"] = SN.say(n, DL.ABOUT, DL.LEX, ctx, "needabout")
            shapes = DL.NEED_PLACE_SHAPES
        else:
            sp = f["species"]
            ctx = dict(beast=sp["name"], beast_cap=cap(sp["name"]), region=w.region_of(f["pos"])["name"], dir=n.dir_phrase(npc.home, f["pos"]),
                       mark=sp.get("mark", "its look"), mark_cap=cap(sp.get("mark", "its look")))
            shapes = DL.NEED_BEAST_SHAPES
        told.append(key)
        heard.append(key)
        return '"' + SP.voice(g, npc, [SN.say(n, shapes, DL.LEX, ctx, f"need-{kind}")], ctx) + '"'
    return None


# ---------------------------------------------------------------- 3. fresh news
def news(g, npc):
    from . import living as LV
    told = npc.mem["told"]
    heard = g.__dict__.setdefault("heard_news", set())     # news is news once: the next person won't repeat it
    for key, text in LV.news(g.world, npc.home)[::-1]:
        if key not in told and key not in heard:
            told.append(key)
            heard.add(key)
            import re
            said = g.narr.say("{rumour_frame}", dict(rumour=text[0].lower() + text[1:].rstrip(".")))
            return re.sub(r'(\w)"$', r'\1."', said)
    return None


# ---------------------------------------------------------------- 4. their own life
def story(g, npc):
    """On a return visit, a piece of their own story comes before second-hand news."""
    if npc.mem.get("met", 0) == 0 or npc.mem.get("inner_day") == g.world.day:
        return None
    fact = IN.next_fact(g.world, npc)
    if not fact or g.rng.random() < 0.25:
        return None
    said = SP.compose(g, npc, fact)
    fact["told"] = True
    if said:
        npc.mem["inner_day"] = g.world.day
    return said


def own(g, npc):
    """Something of their own: a piece of their inner life they're ready to tell you, or their work today."""
    w, m = g.world, npc.mem
    first = m.get("met", 0) == 0
    fact = IN.next_fact(w, npc)
    told_today = m.get("inner_day") == w.day
    life_left = f"life:{w.day}" not in m["told"]
    # a first meeting is mostly small talk; after that, they open up, a piece at a time (one a day, unless they've nothing else)
    want_fact = fact and not told_today and (g.rng.random() < (0.35 if first else 0.8) or not life_left)
    if want_fact:
        said = SP.compose(g, npc, fact)
        if said:
            fact["told"] = True
            m["inner_day"] = w.day
            return said
        fact["told"] = True          # can't be told here (the neighbour has gone): let it go
    return life(g, npc)


def life(g, npc):
    """Their work this season, put together from their trade's tasks; maybe a word about the village; a closing remark."""
    w, n = g.world, g.narr
    key = f"life:{w.day}"
    if key in npc.mem["told"]:
        return None
    npc.mem["told"].append(key)
    temper = _temper(npc)
    group = "elder" if npc.role == "elder" else LIFE.GROUP.get(npc.job, "road" if npc.role == "merchant" else "craft")
    site = w.tiles[npc.home].site or {}
    inner = IN.of(w, npc)
    ctx = dict(village=site.get("name", "the village"), economy=site.get("economy", "farming"), tool="", season=w.season,
               season_cap=cap(w.season), pkin=inner.get("pkin", "mother"))
    # their own trade's tasks this season first, then the kind of work's
    own = DL.JOB_TASKS.get(npc.job, {}).get(w.season, [])
    tasks = own + [x for x in DL.GROUP_TASKS.get(group, DL.GROUP_TASKS["craft"])[w.season] if x not in own]
    first = g.rng.choice(own) if own and g.rng.random() < 0.7 else g.rng.choice(tasks)
    ctx.update(task1=first, task2=g.rng.choice([x for x in tasks if x != first] or tasks))
    # the hand-written lines for the trade and season stay in the pool, among the built ones
    canned = LIFE.JOB_SEASON.get(npc.job, {}).get(w.season, []) + LIFE.WORK[group][w.season]
    if w.weather in ("fog", "rain", "storm", "drizzle", "snow", "overcast"):          # no fine-day talk on a foul one
        canned = [x for x in canned if not re.search(r"good weather|fine day|sunshine|in the sun|dry in a day|clear sky|see the sky|blue sky|bright day", x, re.I)]
    shapes = DL.WORK_SHAPES * 2 + canned
    parts = [SN.say(n, shapes, DL.LEX, ctx, f"work-{npc.job}-{w.season}")]
    if g.rng.random() < 0.25:
        parts.append(SN.say(n, DL.WORK_TAIL, DL.LEX, ctx, "worktail"))
    middle = []
    t = site.get("trouble")
    if t:
        ctx["trouble"] = TROUBLE_NOW.get(t["kind"], "the trouble").format(who=t.get("who", "someone"), thing=t.get("thing", "heirloom"),
                                                                          animal=t.get("animal", "cow"))
        middle += [("trouble", DL.TROUBLE_SHAPES)] * 2
    from . import living as LV
    fest = LV.festival(site, w) if site else None
    if fest:
        ctx["festival"] = fest["name"]
        middle.append(("fest", DL.FESTIVAL_SHAPES))
    middle.append(("village", DL.VILLAGE_SHAPES))
    said = w.__dict__.setdefault("reacted", set())          # the weather and the hour: one person per village per day
    if w.weather in LIFE.WEATHER_NOW and (npc.home, "lifeweather", w.day) not in said:
        middle.append((f"weather-{w.weather}", LIFE.WEATHER_NOW[w.weather]))
    if w.time_of_day in LIFE.TIME_NOW and (npc.home, "lifetime", w.day) not in said:
        middle.append((f"time-{w.time_of_day}", LIFE.TIME_NOW[w.time_of_day]))
    if g.rng.random() < 0.75:
        k, shapes = g.rng.choice(middle)
        if k.startswith(("weather-", "time-")):
            said.add((npc.home, "lifeweather" if k.startswith("weather-") else "lifetime", w.day))
        parts.append(SN.say(n, shapes, DL.LEX, ctx, f"life-{k}"))
    if g.rng.random() < 0.7:
        parts.append(SN.say(n, DL.TAIL_SHAPES.get(temper, DL.TAIL_SHAPES["warm"]), DL.LEX, ctx, f"tail-{temper}"))
    return '"' + SP.voice(g, npc, parts, ctx) + '"'
