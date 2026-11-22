"""What someone says when you talk to them, after the greeting.

In order of what matters most to them:
  1. the errand they gave you: they ask after it, and nudge you about the step you're on
  2. your errands: what they know of the people, places and beasts you need
  3. fresh news from elsewhere
  4. their own life, put together from parts: their work this season, a word about a neighbour
     or the village, and a closing remark in their own temperament
  5. the older rumours (a beast seen somewhere, a ruin, a shrine), and then nothing new

Each topic is told once (per day, for the ones that change), so coming back brings something new.
"""
from . import lex_life as LIFE
from .textgen import cap

TROUBLE_NOW = {"beast": "something killing the sheep", "fever": "the fever in the houses", "lost": "{who} lost out in the wilds",
               "haunting": "something walking the lanes at night", "heirloom": "the {thing} stolen", "well": "the water gone bad",
               "strayed": "the {animal} strayed", "letter": "the letter wanting carrying", "supplies": "the stores running short",
               "wedding": "a wedding and no gift for it", "blight": "the blight on the fields", "feud": "two neighbours at each other's throats",
               "labour": "the work and nobody to do it"}


def topic(g, npc):
    """The thing this person most wants to say to you today, as a spoken line (or None)."""
    for fn in (checkin, need, news, life):
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
    ask = g.narr.pick(LIFE.CHECKIN[_temper(npc)], f"checkin-{_temper(npc)}")
    nudge = LIFE.STEP_NUDGE.get("climax" if st.get("climax") else st["mech"])
    text = ask + (" " + g.narr.pick(nudge, f"nudge-{st['mech']}") if nudge else "")
    return '"' + _say(g, npc, text, ctx) + '"'


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
            manners = [LIFE.PERSON.get(who.demeanour, LIFE.PERSON["warm"])] + LIFE.PERSON_MORE.get(who.demeanour, [])
            ctx["manner"] = n.say(n.pick(manners, f"manner-{who.demeanour}"), ctx)
            line = n.pick(LIFE.NEED_PERSON, "needperson")
        elif kind == "place":
            t = w.tiles[f["pos"]]
            here = w.tiles[npc.home]
            how = ("The road will take you there." if t.road and here.road else
                   "There's no road the whole way; you'll go across country for some of it.")
            ctx = dict(place=t.site["name"], dir=n.dir_phrase(npc.home, f["pos"]), how=how,
                       about=n.pick([f"They live by {t.site['economy']} there.", f"It's {t.site['economy']} country, that.",
                                     f"Good folk, mostly. {cap(t.site['economy'])}, and not much else."], "needabout"))
            line = n.pick(LIFE.NEED_PLACE, "needplace")
        else:
            sp = f["species"]
            ctx = dict(beast=sp["name"], region=w.region_of(f["pos"])["name"], dir=n.dir_phrase(npc.home, f["pos"]), mark=sp.get("mark", "its look"))
            line = n.pick(LIFE.NEED_BEAST, "needbeast")
        told.append(key)
        heard.append(key)
        return '"' + _say(g, npc, line, ctx) + '"'
    return None


# ---------------------------------------------------------------- 3. fresh news
def news(g, npc):
    from . import living as LV
    told = npc.mem["told"]
    for key, text in LV.news(g.world, npc.home)[::-1]:
        if key not in told:
            told.append(key)
            import re
            said = g.narr.say("{rumour_frame}", dict(rumour=text[0].lower() + text[1:].rstrip(".")))
            return re.sub(r'(\w)"$', r'\1."', said)
    return None


# ---------------------------------------------------------------- 4. their own life
def life(g, npc):
    w, n = g.world, g.narr
    key = f"life:{w.day}"
    if key in npc.mem["told"]:
        return None
    npc.mem["told"].append(key)
    temper = _temper(npc)
    group = "elder" if npc.role == "elder" else LIFE.GROUP.get(npc.job, "road" if npc.role == "merchant" else "craft")
    pool = LIFE.JOB_SEASON.get(npc.job, {}).get(w.season, []) * 2 + LIFE.WORK[group][w.season]    # their own trade first, then its kind
    parts = [n.pick(pool, f"work-{npc.job}-{w.season}")]
    site = w.tiles[npc.home].site or {}
    ctx = dict(village=site.get("name", "the village"), economy=site.get("economy", "farming"), tool="")
    middle = []
    t = site.get("trouble")
    if t:
        ctx["trouble"] = TROUBLE_NOW.get(t["kind"], "the trouble").format(who=t.get("who", "someone"), thing=t.get("thing", "heirloom"),
                                                                          animal=t.get("animal", "cow"))
        middle += [n.pick(LIFE.TROUBLE, "lifetrouble")] * 2
    from . import living as LV
    fest = LV.festival(site, w) if site else None
    if fest:
        ctx["festival"] = fest["name"]
        middle.append(n.pick(LIFE.FESTIVAL, "lifefest"))
    others = [x for x in w.tiles[npc.home].npcs if x is not npc]
    if others:
        o = g.rng.choice(others)
        op = o.pronouns()
        ctx.update(other=o.name, ojob=o.job, ohe=op["he"], ohim=op["him"], ohis=op["his"])
        middle.append(n.pick(LIFE.NEIGHBOUR + LIFE.NEIGHBOUR_TEMPER.get(temper, []), f"neigh-{temper}"))
    middle.append(n.pick(LIFE.VILLAGE, "lifevillage"))
    if w.weather in LIFE.WEATHER_NOW:
        middle.append(n.pick(LIFE.WEATHER_NOW[w.weather], f"lifeweather-{w.weather}"))
    if w.time_of_day in LIFE.TIME_NOW:
        middle.append(n.pick(LIFE.TIME_NOW[w.time_of_day], f"lifetime-{w.time_of_day}"))
    if g.rng.random() < 0.75:
        parts.append(g.rng.choice(middle))
    if g.rng.random() < 0.7:
        parts.append(n.pick(LIFE.TAIL[temper], f"tail-{temper}"))
    return '"' + _say(g, npc, " ".join(parts), ctx) + '"'
