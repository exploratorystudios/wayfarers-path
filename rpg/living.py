"""A world that goes on without you, and remembers.

Each new day:
  * villages may develop a trouble (at most one at a time) - wolves at the folds, a
    fever, someone lost in the wilds, a haunting, a stolen heirloom, a fouled well.
    Troubles wait for you: they never fail or get worse while you're away. Their
    telling changes as days pass, and they stay until someone deals with them.
  * when the season turns, every village keeps its festival for two days
  * creatures drift back into empty wild country
  * news of what has happened travels as rumour

Solving a trouble is remembered: garlands, gratitude, better prices, gossip.
"""
from . import story as S
from .textgen import article, cap

FESTIVALS = {
    "spring": ("the Mayday garlanding", ["Garlands of hawthorn and cowslips hang over every door, and someone is dressing a pole with ribbons.",
                                         "Children run from house to house with green branches, and everyone is wearing a flower."]),
    "summer": ("the midsummer fires", ["A great bonfire is being built on the green, and the smell of roasting meat is everywhere.",
                                       "Folk are leaping the embers of last night's fire, laughing, for luck."]),
    "autumn": ("the harvest home", ["The last sheaf, dressed like a little woman, rides in state on a cart, and there is ale on every doorstep.",
                                    "Long tables stand in the lane, heaped with bread and apples, and anyone may sit."]),
    "winter": ("the midwinter wassail", ["Lanterns hang in the bare trees, and a bowl of hot spiced ale is going from hand to hand.",
                                         "Singers go door to door through the cold, and every hearth is banked high."]),
}

TROUBLES = {
    # kind: (weight, giver role preference, opening line, lines as days pass, request)
    "beast": (3, "folk", ["Something has been taking sheep from the folds at night. Folk walk in pairs, and look over their shoulders.",
                          "A hurdle by the lane is smashed and stained dark; something big got at the animals."],
              ["The sheep are penned every night now, and men sit up with them, yawning, with pitchforks.",
               "Children have been told not to go past the last house. Nobody says why."]),
    "fever": (2, "folk", ["A fever has gone through the houses. Doors are shut, and there's a smell of burnt herbs on the air.",
                          "Somebody is coughing behind every other door."],
              ["The fever lingers. Those on their feet look grey and tired from nursing the rest.",
               "A woman hurries past with an armful of linen, not stopping to look at you."]),
    "lost": (2, "folk", ["A knot of folk stand at the edge of the village calling a name into the wild, and getting no answer.",
                         "Someone hasn't come home. You hear their name called, again and again."],
             ["A lamp has been set in a window to guide the lost one home. It burns day and night.",
              "The searchers have come back with nothing. They are going out again tomorrow."]),
    "haunting": (2, "elder", ["Folk say something walks the lanes after dark. Salt lines every doorstep.",
                              "Every door has a sprig of rowan nailed over it, and the shutters are closed early."],
                 ["No one goes out after dark now, not even for the privy.", "Someone has painted eyes on the shutters to watch for it."]),
    "heirloom": (2, "elder", ["The village is in uproar: the old silver bell from the moot-stone has been stolen in the night.",
                              "Something precious has gone missing from the village, and everyone is looking at everyone else."],
                 ["They have searched every house twice. The bell is not in the village.", "Folk are still arguing over who took it."]),
    "well": (2, "folk", ["The water's gone bad. People are fetching it from a long way off, and grumbling.",
                         "A sign on the well says DO NOT DRINK, in letters a child could read."],
             ["The village is getting by on rainwater and ale. The ale is holding out better.", "Folk queue at a rain-barrel with jugs."]),
}

HEIRLOOMS = ["silver bell from the moot-stone", "old copper cup of the village", "carved oak saint from the chapel", "brass key to the tithe barn"]
LOST_NAMES = ["Wat", "Jory", "little Annet", "old Hob", "Tibbie", "young Cuthbert", "Marion", "Peronel"]


def new_day(g):
    """Advance the living world one day."""
    w = g.world
    S.ensure(g)
    S.expire(g)
    season = getattr(w, "last_season", w.season)
    if season != w.season:
        start_festivals(g)
    w.last_season = w.season
    for v in w.villages:
        site = w.tiles[v].site
        if site.get("trouble") or w.day < 2:
            continue
        cooldown = site.get("calm_until", 0)
        if w.day >= cooldown and g.rng.random() < 0.22:
            start_trouble(g, v)
    respawn(g)


# ------------------------------------------------------------------ festivals
def start_festivals(g):
    w = g.world
    name, _ = FESTIVALS[w.season]
    for v in w.villages:
        w.tiles[v].site["festival"] = dict(name=name, until=w.day + 1, gifted=[])
    S.record(g, f"The villages kept {name}.", "news")


def festival(site, world):
    f = site.get("festival")
    return f if f and f["until"] >= world.day else None


def festival_lines(narr, site):
    f = festival(site, narr.w)
    if not f:
        return []
    name, lines = FESTIVALS[narr.w.season] if narr.w.season in FESTIVALS else (f["name"], [])
    return [f"It is {f['name']} here.", narr.pick(lines, f"fest{site['name']}")] if lines else [f"It is {f['name']} here."]


def festival_gift(g, npc):
    """During a festival, the first talk with each villager comes with something."""
    site = g.world.tiles[g.pos].site
    f = festival(site, g.world) if site else None
    if not f or npc.name in f["gifted"]:
        return
    f["gifted"].append(npc.name)
    npc.like(1)
    from .world import Item
    gift = g.rng.choice([("food", "slice of festival cake", 5), ("food", "mug of spiced ale", 3), ("food", "honeyed oatcake", 4), ("herb", None, 0)])
    it = g.world.make_item(1, "herb") if gift[0] == "herb" else Item("food", gift[1], value=gift[2], heal=gift[2])
    g.player.inv.append(it)
    g.emit(f"{npc.name} presses {article(it.name)} on you. \"It's {f['name']}! Nobody goes without.\"")


# ------------------------------------------------------------------ troubles
def start_trouble(g, v):
    w = g.world
    site = w.tiles[v].site
    kinds = list(TROUBLES)
    weights = [TROUBLES[k][0] for k in kinds]
    kind = g.rng.choices(kinds, weights)[0]
    npcs = w.tiles[v].npcs
    pref = TROUBLES[kind][1]
    giver = next((n for n in npcs if n.role == pref), None) or next((n for n in npcs if n.role != "merchant"), npcs[0])
    t = dict(kind=kind, day=w.day, giver=giver.name, offered=False, accepted=False)
    if kind == "beast":
        sp = [s for s in w.species if s["key"] in ("wolf", "bear", "boar", "spider", "serpent")] or w.species
        spot = wild_near(g, v, 1, 3)
        if not spot:
            return
        c = w.make_creature(g.rng.choice(sp), max(2, min(4, w.day // 3 + 2)))
        c.aggressive = True
        w.tiles[spot].creatures.append(c)
        t.update(creature=c, target=spot)
    elif kind == "lost":
        spot = wild_near(g, v, 2, 4)
        if not spot:
            return
        gender = g.rng.choice(["female", "male"])
        who = w.new_name(w.culture_of(v), gender) if hasattr(w, "new_name") else g.rng.choice(LOST_NAMES)
        t.update(target=spot, who=g.rng.choice(["little ", "young ", "old ", "", "", ""]) + who, who_gender=gender)
    elif kind == "haunting":
        sp = next((s for s in w.species if s["arch"].get("undead")), None)
        spot = wild_near(g, v, 1, 2)
        if not sp or not spot:
            return
        c = w.make_creature(sp, 3)
        c.aggressive = True
        w.tiles[spot].creatures.append(c)
        t.update(creature=c, target=spot)
    elif kind == "heirloom":
        from .secrets import plant_cache
        old = g.pos
        g.pos = v
        target = plant_cache(g, 2, 5)
        g.pos = old
        if not target:
            return
        tp, tf = target
        thing = g.rng.choice(HEIRLOOMS)
        tf.state["secret"].update(key="heirloom", village=v, thing=thing)
        t.update(target=tp, thing=thing, noun=tf.noun)
    elif kind == "well":
        waters = [(p, f) for p in w.land for f in w.tiles[p].features
                  if f.archetype in ("stream", "holy well", "pool", "dew pond", "waterfall") and 1 <= abs(p[0] - v[0]) + abs(p[1] - v[1]) <= 4]
        if waters:
            tp, tf = g.rng.choice(waters)
            t.update(target=tp, noun=tf.noun)
        else:
            spot = wild_near(g, v, 1, 3)
            if not spot:
                return
            t.update(target=spot, noun="spring")
    site["trouble"] = t
    S.record(g, f"Trouble came to {site['name']}: {short(t)}.", "news", pos=v)


def short(t):
    return {"beast": "something is killing the sheep", "fever": "a fever is in the houses", "lost": f"{t.get('who', 'someone')} is lost in the wilds",
            "haunting": "something walks the lanes at night", "heirloom": f"the {t.get('thing', 'heirloom')} was stolen", "well": "the water has gone bad"}[t["kind"]]


def wild_near(g, v, lo, hi):
    w = g.world
    cands = [p for p in w.land if lo <= abs(p[0] - v[0]) + abs(p[1] - v[1]) <= hi and not w.tiles[p].site and p != g.pos]
    return g.rng.choice(cands) if cands else None


def trouble_lines(narr, site):
    """What you see of a village's trouble (it changes as the days pass, but never gets worse)."""
    t = site.get("trouble")
    if not t:
        if site.get("celebrate_until", -1) >= narr.w.day:
            return [narr.pick(["Garlands hang over the doors, and people smile at you as you pass.",
                               "There's a lightness in the lanes today; someone is even whistling.",
                               "Folk nod to you with real warmth. Word of what you did has got round."], f"celeb{site['name']}")]
        return []
    w = narr.w
    _, _, opening, later = TROUBLES[t["kind"]]
    lines = later if w.day - t["day"] >= 3 else opening
    return [narr.pick(lines, f"trouble{site['name']}{t['kind']}").replace("{who}", t.get("who", "someone"))]


def offer_trouble(g, npc):
    """Talking to a villager in a troubled village: they ask for help (once accepted, they leave you be)."""
    w = g.world
    site = w.tiles[g.pos].site
    t = site.get("trouble") if site else None
    if not t or t.get("accepted"):
        return False
    if npc.role == "merchant" and t["giver"] != npc.name:
        return False
    k = t["kind"]
    d = lambda: g.narr.dir_phrase(g.pos, t["target"])
    asks = {
        "beast": lambda: f"\"There's a beast out there taking our sheep. It lairs {d()}, we think. Will you deal with it?\"",
        "fever": lambda: "\"The fever's in half the houses. If you come across any healing herbs - anything - bring them here. Please.\"",
        "lost": lambda: f"\"{t['who']} went out and didn't come back. Somewhere {d()}, we think. Will you look?\"",
        "haunting": lambda: f"\"Something comes up from {d()} at night. It isn't alive. Can you put it down?\"",
        "heirloom": lambda: f"\"Our {t['thing']} - stolen! Somebody saw a magpie, or a thief, or both, heading {d()}. Find it?\"",
        "well": lambda: f"\"The water's gone foul. It comes down from the {t['noun']} {d()}. Something must be in it. Would you look?\"",
    }[k]()
    S.ask(g, f"{npc.name} catches your sleeve. {asks}",
          [("Agree to help", "trouble_yes", dict(village=g.pos, giver=npc.name)), ("Not now", "trouble_no", dict(giver=npc.name))], leave=1)
    return True


@S.choice_handler("trouble_yes")
def _trouble_yes(g, d):
    w = g.world
    v = tuple(d["village"])
    site = w.tiles[v].site
    t = site.get("trouble")
    if not t:
        return
    t["accepted"], t["giver"] = True, d["giver"]
    giver = S.find_npc(w, d["giver"])
    k, name = t["kind"], site["name"]
    reward = dict(gold=g.rng.randint(15, 35), xp=25, like=4, village_like=2, chronicle=f"You ended the trouble at {name}: {short(t)}.",
                  story=f"you saved {name} when {short(t)}", story_like=3)
    common = dict(giver=giver, source="trouble", on_done="trouble", data=dict(village=v))
    if k in ("beast", "haunting"):
        what = t["creature"].species["name"]
        S.new_quest(g, "slay", f"The {what} near {name}", f"Kill the {what} troubling {name}", reward, target=t["target"], creature=t["creature"], **common)
    elif k == "fever":
        q = S.new_quest(g, "bring", f"Fever in {name}", f"Bring a healing herb to {giver.name} in {name}", reward, item=None, **common)
        q["data"].update(any_kind="herb", done_text=f"{giver.name} takes the herb and is gone into a house before you can say a word. Later {giver.pronouns()['he']} comes back out, smiling for the first time in days.")
    elif k == "lost":
        S.new_quest(g, "find", f"{t['who']} is lost", f"Search the wilds for {t['who']}", reward, target=t["target"], **common)
    elif k == "heirloom":
        S.new_quest(g, "find", f"The stolen {t['thing']}", f"Find the {t['thing']} - the trail leads to the {t['noun']}", reward, target=t["target"],
                    giver=giver, source="trouble", on_done=None, data=dict(village=v, noun=t["noun"], search=True, heirloom=True))
    elif k == "well":
        S.new_quest(g, "find", f"Foul water at {name}", f"Find what is fouling the water at the {t['noun']}", reward, target=t["target"], **common)
    g.emit(f"{giver.name} lets out a long breath. \"Thank you.\"")


@S.choice_handler("trouble_no")
def _trouble_no(g, d):
    g.emit(f"{d['giver']} nods, and lets go of your sleeve. \"If you change your mind…\"")


def found(g, q):
    """Arriving where a 'find' quest points."""
    w = g.world
    if q["data"].get("search"):
        g.emit(f"(This is the place. Search the {q['data'].get('noun', 'landmark')}.)")
        return
    v = q["data"].get("village")
    site = w.tiles[v].site if v else None
    t = site.get("trouble") if site else None
    if t and t["kind"] == "lost":
        who = t["who"]
        from .world import PRONOUNS
        pr = PRONOUNS.get(t.get("who_gender"), PRONOUNS["female"])
        g.emit(f"You find {who} at last - cold, hungry, with a twisted ankle, sheltering as best {pr['he']} can. {cap(pr['he'])} nearly weeps at the sight of you.")
        q["kind"], q["target"] = "escort", v
        q["title"], q["desc"] = f"Bring {who} home", f"Lead {who} back to {site['name']}"
        comp = dict(name=who)
        q["companion"] = comp
        g.companions.append(comp)
        q["data"]["done_text"] = f"{who} limps into {site['name']} on your arm, and the whole village comes running."
        g.emit(f"(Journal: {who} will follow you home.)")
    elif t and t["kind"] == "well":
        g.pass_time(40)
        g.emit(f"At the {t['noun']} you find the cause: a dead sheep, bloated and stinking, wedged in the water. It takes you a foul half-hour to haul it out and drag it well away.")
        S.finish(g, q, "The water will run clean again by tomorrow.")


def quest_done(g, q):
    if q.get("on_done") != "trouble":
        return
    w = g.world
    v = tuple(q["data"]["village"])
    site = w.tiles[v].site
    if not site:
        return
    site["trouble"] = None
    site["celebrate_until"] = w.day + 2
    site["calm_until"] = w.day + 6
    S.add_mark(g, v, "Garlands still hang over a few doors, for the day the trouble ended.", days=5)


def heirloom_found(g, f, sec):
    """Searching where the stolen heirloom was hidden."""
    from .world import Item
    v = tuple(sec["village"])
    site = g.world.tiles[v].site
    it = Item("token", sec["thing"], value=0, facts=dict(material="old metal", glow="the shine of many hands"))
    g.player.inv.append(it)
    g.emit(f"Wedged out of sight at the {f.noun} is the {sec['thing']}, along with a scatter of shiny rubbish. A magpie's work, then - or a very odd thief.")
    t = site.get("trouble") if site else None
    for q in S.active(g):
        if q["data"].get("heirloom") and tuple(q["data"].get("village")) == v:
            q["status"] = "done"
    giver = S.find_npc(g.world, t["giver"]) if t else None
    if giver:
        q = S.new_quest(g, "bring", f"Return the {sec['thing']}", f"Take the {sec['thing']} back to {giver.name} in {site['name']}",
                        dict(gold=g.rng.randint(15, 30), xp=25, like=4, village_like=2, chronicle=f"You returned the {sec['thing']} to {site['name']}.",
                             story=f"you found {site['name']}'s stolen {sec['thing']}", story_like=3),
                        item=sec["thing"], giver=giver, source="trouble", on_done="trouble", data=dict(village=v))
        q["data"]["done_text"] = f"{giver.name} holds the {sec['thing']} up for everyone to see, and a cheer goes up."


# ------------------------------------------------------------------ creatures come back
def respawn(g):
    w = g.world
    total = sum(len(t.creatures) for t in w.tiles.values())
    if total > len(w.land) // 3 or g.rng.random() > 0.5:
        return
    empty = [p for p in w.land if not w.tiles[p].creatures and not w.tiles[p].site and abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) > 2]
    if not empty:
        return
    p = g.rng.choice(empty)
    t = w.tiles[p]
    natives = [s for s in w.species if s["home"] == t.biome and not s["arch"].get("undead")] or w.species
    t.creatures.append(w.make_creature(g.rng.choice(natives), max(1, t.danger)))


# ------------------------------------------------------------------ news travels
def news(world, here, day_span=6):
    """Recent happenings elsewhere, for rumours: [(key, text)]."""
    out = []
    for i, e in enumerate(world.chronicle):
        if e["kind"] != "news" or world.day - e["day"] > day_span:
            continue
        if abs(e["pos"][0] - here[0]) + abs(e["pos"][1] - here[1]) == 0:
            continue
        out.append((f"news{i}", e["text"]))
    return out
