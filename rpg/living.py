"""A world that goes on without you, and remembers.

Each new day:
  * villages may develop a trouble (at most one at a time) - thirteen kinds, from
    wolves at the folds to a wedding that wants a gift (see rpg/troubles.py).
    Troubles wait for you: they never fail or get worse while you're away. Their
    telling changes as days pass, and they stay until someone deals with them.
  * when the season turns (every 7 days), you notice, and every village keeps its festival for two days
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
    season_check(g)
    for v in w.villages:
        site = w.tiles[v].site
        if site.get("trouble") or w.day < 2:
            continue
        cooldown = site.get("calm_until", 0)
        if w.day >= cooldown and g.rng.random() < 0.22:
            start_trouble(g, v)
    respawn(g)
    from . import goods as GOODS
    GOODS.restock(g)


# ------------------------------------------------------------------ the turning year
TURN = {
    "spring": ["Overnight the wind has gone round to the south. The thaw has begun: spring is here.",
               "The birds are back, singing as if they'd never been away, and the air smells of wet earth. Spring has come.",
               "Somewhere in the night the cold let go. The streams are loud with meltwater, and it is spring."],
    "summer": ["The days have grown long and the nights warm, and the hedges are thick with green. It is summer now.",
               "The air has turned heavy and sweet, and the first hay is down in the meadows. Summer has come in."],
    "autumn": ["There's a new edge to the air, and the first leaves are turning. Autumn has come.",
               "The swallows are gone, all at once, and the light has gone low and gold. It is autumn."],
    "winter": ["There's a white rime on everything, and your breath smokes. Winter has come.",
               "The last leaves came down in the night's wind, and the puddles have skinned with ice. It is winter now."],
}


def season_check(g, quiet=False):
    """If the season has turned since we last looked: say so (unless the caller already has), note it, and start the festivals."""
    w = g.world
    if getattr(w, "last_season", w.season) != w.season:
        if not quiet:
            g.emit(g.rng.choice(TURN[w.season]))
        S.record(g, f"The season turned: {w.season} came.", "news")
        start_festivals(g)
    w.last_season = w.season


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


# ------------------------------------------------------------------ troubles (rpg/troubles.py)
from .troubles import (KINDS as TROUBLES, start_trouble, short, wild_near, trouble_lines, offer_trouble,   # noqa: E402,F401
                       found, quest_done, heirloom_found)


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
