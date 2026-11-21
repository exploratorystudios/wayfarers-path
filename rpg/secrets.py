"""Things to do at landmarks, and the secrets some of them keep.

Verbs: search, climb, drink, touch, read, listen, forage (and `give X to <landmark>`
as an offering). Any landmark answers the verbs that suit it with something,
even if only a little colour; about half of them hide a secret, fixed when
the world is made, so a place is the same place each time you come back.

Secrets range over rewards (caches, old blades, healing springs), magic (fairy
rings, visions, ghosts, will-o'-wisps, hermits), hijinks (magpies, bees, falling
in) and quests (keepsakes that belong to real villagers, bones to bury, cursed
stones to return, treasure clues). Many only stir under certain conditions -
at night, under a full moon, in fog, at dawn - and the description hints when
something is waiting.
"""
import random

from . import story as S
from .lex_landmarks import TAG
from . import lex_looks as LK
from . import lex_talk_more as LK_TALK2
from .textgen import article, cap

VERBS = ["search", "climb", "drink", "touch", "read", "listen", "forage"]

FALLEN = {"fallen tree", "fallen beech"}      # lying down: you walk them, you don't climb them
CLIMBABLE = {"oak", "yew", "willow", "hawthorn", "rowan", "standing stone", "cairn", "outcrop", "stone circle", "eyrie",
             "sheepfold", "hunter's hide", "dovecote", "gibbet", "barrow", "hill fort", "chalk figure", "charcoal-burner's mound", "glacier",
             "bog oak", "hermit's cell", "reed island"}
READ_KINDS = {"standing stone", "stone circle", "cairn", "gibbet", "hermit's cell", "dovecote", "bog oak", "holy well", "causeway",
              "chalk figure", "oak", "yew", "sheepfold", "hill fort"}
READ_WORDS = ("carved", "inscri", "letters", "spirals", "marks", "name", "initials", "faces", "tally", "scratch", "painted", "cross")


def kind_of(f):
    return f.archetype


def tag_of(f):
    return TAG.get(kind_of(f), "stone")


def can(verb, f):
    k, t = kind_of(f), tag_of(f)
    if verb == "search" or verb == "touch" or verb == "listen":
        return True
    if verb == "climb":
        return k in CLIMBABLE
    if verb == "drink":
        return t == "water"
    if verb == "read":
        return k in READ_KINDS or any(w in d for d in f.details for w in READ_WORDS)
    if verb == "forage":
        return t in ("tree", "plant", "fungus", "water", "earth", "log")
    return False


# ------------------------------------------------------------------ the deck
# key: (verbs, where (tags or kinds), weight, condition)
DECK = {
    "cache":        ({"search"}, {"tree", "stone", "built", "earth", "log"}, 3, None),
    "old_blade":    ({"search"}, {"barrow", "cairn", "hill fort", "bog oak", "peat cutting", "cave mouth", "sunken punt", "old mine"}, 3, None),
    "nest":         ({"climb"}, {"oak", "yew", "willow", "rowan", "hawthorn", "eyrie", "dovecote", "gibbet"}, 2, None),
    "healing":      ({"drink"}, {"water"}, 3, None),
    "bad_water":    ({"drink"}, {"pool", "dew pond", "peat cutting", "stream"}, 1, None),
    "fairy":        ({"touch", "search", "listen"}, {"ring of toadstools", "glade", "stone circle", "hawthorn"}, 5, "night"),
    "wishing":      ({"drink", "touch"}, {"holy well", "dew pond", "tarn", "waterfall"}, 3, None),
    "vision":       ({"touch"}, {"standing stone", "stone circle", "chalk figure", "barrow", "glacier"}, 3, "dawn_or_moon"),
    "raven":        ({"listen"}, {"outcrop", "gibbet", "eyrie", "cairn", "hawthorn", "oak", "yew", "rowan"}, 2, None),
    "ghost":        ({"listen", "touch"}, {"barrow", "gibbet", "hermit's cell", "cave mouth", "sunken punt", "causeway", "old mine", "bog oak"}, 3, "dark"),
    "wisp":         ({"listen", "search"}, {"pool", "causeway", "reed island", "bog oak", "willow", "sunken punt", "peat cutting", "eel trap"}, 3, "dark_or_fog"),
    "hermit":       ({"touch", "search", "listen"}, {"hermit's cell"}, 6, None),
    "cursed_stone": ({"search"}, {"cairn", "barrow", "standing stone", "stone circle"}, 2, None),
    "magpie":       ({"search", "climb"}, {"oak", "yew", "hawthorn", "rowan", "gibbet", "dovecote", "willow"}, 2, None),
    "slip":         ({"drink"}, {"stream", "waterfall", "pool", "tarn", "hot spring"}, 2, None),
    "stuck":        ({"climb"}, {"oak", "yew", "rowan", "hawthorn", "willow"}, 1, None),
    "bees":         ({"search", "forage"}, {"oak", "yew", "fallen beech", "rowan", "hawthorn", "dovecote", "fallen tree"}, 2, "warm"),
    "badger":       ({"search"}, {"badger sett", "hunter's hide", "charcoal-burner's mound"}, 3, None),
    "keepsake":     ({"search"}, {"tree", "stone", "built", "earth", "water", "plant", "log"}, 1, None),
    "letter":       ({"search"}, {"oak", "yew", "hunter's hide", "dovecote", "sheepfold", "hermit's cell", "cairn", "gibbet"}, 1, None),
    "bones":        ({"search"}, {"barrow", "cave mouth", "peat cutting", "bog oak", "chasm", "old mine", "sunken punt", "fallen beech", "fallen tree"}, 2, None),
    "snared":       ({"search", "listen"}, {"hunter's hide", "track", "hawthorn", "glade", "sheepfold", "charcoal-burner's mound"}, 2, None),
    "clue":         ({"read", "search"}, {"standing stone", "cairn", "hermit's cell", "dovecote", "gibbet", "causeway", "stone circle", "bog oak"}, 2, None),
    "echo":         ({"listen"}, {"chasm", "old mine", "cave mouth", "waterfall", "holy well"}, 3, None),
    "chalk_walk":   ({"touch", "climb"}, {"chalk figure"}, 6, None),
    "hot_bath":     ({"drink", "touch"}, {"hot spring"}, 6, None),
    "ringing":      ({"touch"}, {"stone circle", "standing stone"}, 2, None),
    "heirloom":     ({"search"}, set(), 0, None),
    "plot":         ({"search"}, set(), 0, None),
    "magpie_nest":  ({"search", "climb"}, set(), 0, None),
    "hidden_door":  ({"search"}, {"outcrop", "barrow", "hill fort", "cave mouth", "old mine"}, 1, None),
}

HINTS = {
    "cache": ["The ground at the foot of the {noun} looks disturbed, as if someone dug there and filled it in.", "One part of the {noun} looks handled more than the rest."],
    "old_blade": ["Something long and dark is half-buried near the {noun}.", "Here and there around the {noun}, the earth has been turned over by rabbits, showing a glint of metal."],
    "nest": ["Something glints high up in the {noun}.", "A big untidy nest sits high in the {noun}."],
    "healing": ["The water of the {noun} looks unusually clear and inviting.", "Small offerings have been left by the {noun}, as if it had once healed someone."],
    "fairy": ["Faint music seems to drift from the {noun}, and stops when you listen for it.", "Tiny lights move around the {noun}, there and gone."],
    "wishing": ["Coins glint in the water of the {noun}.", "Someone has scratched 'wish' on a stone beside the {noun}."],
    "vision": ["The {noun} seems to hum, very faintly.", "Your skin prickles when you look at the {noun}."],
    "raven": ["A raven watches you from the {noun}, head cocked, as if waiting for you to say something.", "A raven on the {noun} makes a sound almost like a word."],
    "ghost": ["The air by the {noun} is colder than it should be.", "You think you hear someone weeping near the {noun}."],
    "wisp": ["A pale light bobs low over the ground beyond the {noun}, then winks out.", "A small blue flame drifts near the {noun}, though nothing is burning."],
    "hermit": ["A thread of smoke rises from the {noun}.", "Someone has swept the step of the {noun} recently."],
    "cursed_stone": ["One stone in the {noun} is carved with a sign that makes your eyes slide away.", "One stone of the {noun} is darker than the rest and feels watched."],
    "magpie": ["A magpie chatters at you from the {noun}, eyeing anything that shines.", "Magpies squabble in the {noun}."],
    "bees": ["Bees drone in and out of a crack in the {noun}.", "There's a smell of honey around the {noun}."],
    "badger": ["Something snuffles in the {noun}.", "Fresh bedding has been dragged into the {noun}."],
    "keepsake": ["Something small catches the light near the {noun}.", "There is a scrap of ribbon caught on the {noun}, as if something was dropped here."],
    "letter": ["A corner of folded paper pokes out of a gap in the {noun}.", "Someone has wedged something into a crack in the {noun}."],
    "bones": ["A pale shape lies half-hidden by the {noun}.", "Crows have been picking at something near the {noun}."],
    "snared": ["Something thrashes in the undergrowth near the {noun}.", "You hear a thin, frightened squealing near the {noun}."],
    "clue": ["Marks have been scratched into the {noun} - not old carvings, something newer.", "There's writing on the {noun}, half worn away."],
    "echo": ["You could swear something in the {noun} said your name.", "Sounds come back from the {noun} not quite as they went in."],
    "chalk_walk": ["A path is worn into the turf around the outline of the {noun}, as if people walk it.", "Old ribbons are pegged at the head of the {noun}."],
    "hot_bath": ["The warm water of the {noun} looks very inviting after the road.", "Someone has set a stone seat at the edge of the {noun} for bathing."],
    "ringing": ["When the wind blows, one of the stones of the {noun} hums like a struck bell.", "One stone of the {noun} is worn smooth on one side by many hands."],
    "hidden_door": ["Cold air seeps from a crack in the {noun}.", "One slab in the {noun} doesn't quite match the others."],
}


def rested(g, sec):
    """A place that can answer again - but not until tomorrow."""
    sec["found"] = False
    sec["used_day"] = g.world.day


def ready(w, sec):
    """An unfound secret whose moment has come (and which isn't resting after use today)."""
    return bool(sec) and not sec["found"] and sec.get("used_day") != w.day and cond_met(w, sec.get("cond"))


def cond_met(w, cond):
    if cond is None:
        return True
    if cond == "night":
        return w.is_dark
    if cond == "dark":
        return w.is_dark
    if cond == "dark_or_fog":
        return w.is_dark or w.weather == "fog"
    if cond == "dawn_or_moon":
        return w.time_of_day == "dawn" or (w.is_dark and "full" in w.moon_line)
    if cond == "warm":
        return w.season in ("spring", "summer")
    if cond == "fog":
        return w.weather == "fog"
    if cond == "fog_or_rain":
        return w.weather in ("fog", "rain", "drizzle", "storm")
    if cond == "dawn":
        return w.time_of_day == "dawn"
    if cond == "dusk":
        return w.time_of_day in ("dusk", "evening")
    if cond == "day":
        return not w.is_dark
    return True


COND_WORDS = {"night": "by night", "dark": "after dark", "dark_or_fog": "in darkness or fog", "dawn_or_moon": "at dawn, or under a full moon",
              "warm": "in the warm months", "fog": "in fog", "fog_or_rain": "in fog or rain", "dawn": "at dawn", "dusk": "at dusk",
              "day": "by daylight"}


# how many of each secret one world holds: the ones that start a story are kept rare, so they stay special
CAP = {"bones": 2, "keepsake": 3, "letter": 2, "ghost": 2, "vision": 2, "raven": 2, "clue": 2, "magpie": 2, "cursed_stone": 2,
       "hermit": 2, "hidden_door": 2, "old_blade": 3, "wishing": 3, "fairy": 4, "healing": 4, "snared": 3, "cache": 30}
# the dead traveller under the landmark: who they were, what they carried, where it should go
TRAVELLERS = [
    ("a pilgrim", "pilgrim's badge", "of lead, stamped with a worn saint", "shrine", "the shrine they never reached",
     "You hang the pilgrim's badge at the shrine among the other offerings. Somewhere a journey ends."),
    ("a soldier", "soldier's name-tag", "a tin tag stamped with a name you can just read", "village", "a village, so someone knows",
     "You leave the name-tag with the village elder, who promises to ask about. Someone, somewhere, will finally know."),
    ("a drover", "drover's tally-stick", "a notched hazel stick, every notch a beast brought safe to market", "village", "the drovers' village it came from",
     "You hand the tally-stick to an old drover, who turns it over and goes very quiet. \"I knew him,\" is all he says."),
    ("a pedlar", "pedlar's sealed licence", "a scrap of vellum with a wax seal, giving leave to trade the roads", "village", "the market it was sealed in",
     "You give the licence to the reeve. \"So that's where old Wat got to,\" someone murmurs."),
    ("a hermit", "hermit's prayer-rope", "a knotted cord, worn smooth by a lifetime of fingers", "shrine", "holy ground",
     "You lay the prayer-rope on the shrine. For a moment the air is very still."),
    ("a shepherd", "shepherd's horn", "a small horn, cracked, carved with a ram's head", "village", "the shepherd's people",
     "You give the horn to the shepherds by the village fold. One of them puts it to his lips, and it still sounds."),
]


def place_all(world):
    """Give about half of all landmarks a secret. Fixed per world (its own seeded RNG)."""
    r = random.Random(f"{world.seed}-secrets")
    feats = [(p, f) for p in world.land for f in world.tiles[p].features]
    npcs = [n for v in world.villages for n in world.tiles[v].npcs]
    shrines = [p for p in world.land if world.tiles[p].site and world.tiles[p].site["kind"] == "shrine"]
    placed = {}
    for p, f in feats:
        if f.state is None:
            f.state = {}
        if "secret" in f.state:
            continue
        if r.random() > 0.5:
            f.state["secret"] = None
            continue
        k, t = kind_of(f), tag_of(f)
        options = [(key, wt) for key, (verbs, where, wt, cond) in DECK.items() if (k in where or t in where) and placed.get(key, 0) < CAP.get(key, 4)]
        if not options:
            f.state["secret"] = None
            continue
        key = r.choices([o for o, _ in options], [w for _, w in options])[0]
        verbs, where, wt, cond = DECK[key]
        sec = dict(key=key, verbs=sorted(v for v in verbs if can(v, f)) or ["search"], cond=cond, found=False)
        if key in ("keepsake", "letter") and npcs:
            owner = r.choice(npcs)
            sec.update(owner=owner.name, home=owner.home,
                       thing=r.choice(["brass ring", "carved wooden bird", "silver thimble", "bone comb", "copper locket", "little knife with a horn handle", "child's rag doll", "string of blue beads"])
                       if key == "keepsake" else "sealed letter",
                       sender=r.choice([n.name for n in npcs if n is not owner] or ["someone"]))
        if key == "bones" and shrines:
            sec.update(shrine=min(shrines, key=lambda s: abs(s[0] - p[0]) + abs(s[1] - p[1])))
        if key == "ghost":
            sec.update(who=r.choice(["a drowned ferryman", "a hanged thief", "a shepherd lost in the snow", "a lady who waited for someone who never came",
                                     "a soldier who never got home", "a child who wandered off", "a miller who cheated his neighbours"]),
                       token=r.choice(["tarnished ring", "broken spur", "wooden token", "rusted key", "knot of red hair", "lead pilgrim's badge"]))
        f.state["secret"] = sec
        placed[key] = placed.get(key, 0) + 1


def hint(narr, f):
    """A line hinting at an unfound secret, when its moment has come (or None)."""
    sec = (f.state or {}).get("secret")
    if not sec or sec["key"] not in HINTS or not ready(narr.w, sec):
        return None
    return narr.say(narr.pick(HINTS[sec["key"]], f"hint{id(f)}"), dict(noun=f.noun))


# ------------------------------------------------------------------ the verbs
def act(g, verb, f):
    """Use a verb on a landmark."""
    if f.state is None:
        f.state = {}
    if not can(verb, f):
        return g.emit(cant(g, verb, f))
    done = f.state.setdefault("done", [])
    sec = f.state.get("secret")
    took = {"search": 20, "climb": 25, "drink": 5, "touch": 5, "read": 10, "listen": 10, "forage": 40}[verb]
    if sec and not sec["found"] and verb in sec["verbs"] and sec.get("used_day") != g.world.day:
        if cond_met(g.world, sec.get("cond")):
            sec["found"] = True
            with g.hush():
                g.pass_time(took)
                SECRET[sec["key"]](g, f, sec)
            for q in S.active(g):      # a clue, vision or magpie pointed here
                if q["kind"] == "find" and q["data"].get("search") and q["target"] == g.pos and not q["data"].get("heirloom"):
                    S.finish(g, q)
            return
        # the secret sleeps; say something that suggests coming back
        with g.hush():
            g.pass_time(took)
        return g.emit(asleep(g, verb, f, sec))
    if verb in done and verb in ("search", "forage") and not (verb == "forage" and f.state.get("forage_day") != g.world.day):
        return g.emit(g.narr.pick([x.format(noun=f.noun) for x in LK.SEARCHED], "searched"))
    if verb not in done:
        done.append(verb)
    with g.hush():
        g.pass_time(took)
        return PLAIN[verb](g, f)


def cant(g, verb, f):
    if verb == "climb" and kind_of(f) in FALLEN:
        return g.narr.pick([f"The {f.noun} is lying on its side - there's nothing to climb. Standing on its trunk wouldn't lift you above the trees around it.",
                            f"There's no climbing a tree that's already down. From the {f.noun}'s trunk you'd see no further than the bracken.",
                            f"The {f.noun} lies full length on the ground. You'd need a standing tree to see anything from."])
    return {
        "climb": g.narr.pick(LK.NO_CLIMB, "noclimb").format(noun=f.noun),
        "drink": f"There's nothing to drink at the {f.noun}.",
        "read": f"There's nothing written on the {f.noun}.",
        "forage": f"Nothing worth gathering grows on the {f.noun}.",
    }.get(verb, f"You can't do that with the {f.noun}.")


def asleep(g, verb, f, sec):
    when = COND_WORDS.get(sec.get("cond"), "another time")
    return g.narr.pick([f"You {verb} at the {f.noun}, and for a moment you feel you have nearly understood something. Perhaps {when}…",
                        f"Nothing answers. Yet you can't shake the feeling the {f.noun} is waiting - for something, or for a different hour.",
                        f"The {f.noun} keeps its own counsel. Folk say such places are different {when}."])


# ------------------------------------------------------------------ plain outcomes (no secret)
def small_find(g, chance=0.12):
    if g.rng.random() > chance:
        return ""
    r = g.rng.random()
    if r < 0.5:
        n = g.rng.randint(1, 4)
        g.player.gold += n
        return f" You turn up {n} coin{'s' if n > 1 else ''}, long lost."
    it = g.world.make_item(1, g.rng.choice(["herb", "food", "trinket"]))
    g.player.inv.append(it)
    return f" Tucked away, you find {article(it.name)}."


def _list(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def plain_search(g, f):
    """Searching with nothing hidden: what turns up, told in frames of different shapes."""
    pool = LK.FINDS.get(tag_of(f), LK.FINDS["stone"])
    def make():
        items = g.rng.sample(pool, min(len(pool), g.rng.choice([1, 2, 2, 3])))
        fr = g.narr.pick(LK.SEARCH, "search")
        return fr.format(noun=f.noun, finds=_list(items), Finds=cap(_list(items)), one=items[0])
    g.emit(g.narr.best_of(make) + small_find(g))


def plain_climb(g, f):
    """Climbing for a view: how you get up depends on what it is; what you see depends on the
    weather, the hour, how high it is, and what is really out there on the map."""
    w, narr = g.world, g.narr
    kind, tag = kind_of(f), tag_of(f)
    how = narr.pick([x.format(noun=f.noun) for x in LK.CLIMB_KIND.get(kind) or LK.CLIMB_HOW.get(tag, LK.CLIMB_HOW["stone"])], f"climb:{kind}")
    fog, dark = w.weather == "fog", w.is_dark
    found = reveal_places(g, 1 if fog else (3 if kind in LK.CLIMB_HIGH else 2))
    def where(pos):
        dist = abs(pos[0] - g.pos[0]) + abs(pos[1] - g.pos[1])
        far = "a short walk" if dist <= 3 else "a few hours" if dist <= 7 else "a long way"
        return narr.dir_phrase(g.pos, pos).split(" to the ")[-1], far
    parts = [how]
    villages = [p for k, p in found if k == "village"]
    if fog:
        parts.append(narr.pick(LK.VISTA_FOG, "vista:fog"))
        if villages:
            d, far = where(villages[0])
            parts.append(narr.pick(LK.HEARD, "heard").format(dir=d, far=far))
    elif dark:
        parts.append(narr.pick(LK.VISTA_DARK, "vista:dark"))
        if villages:
            d, far = where(villages[0])
            parts.append("You make out " + narr.pick(LK.SEEN_LIGHT, "seenlight").format(dir=d, far=far) + ".")
    elif found:
        bits = []
        for k, pos in found[:3]:
            d, far = where(pos)
            what = {"village": "a village", "ruin": "a ruin", "shrine": "a shrine"}[k]
            bits.append(narr.pick(LK.SEEN_FRAMES, "seenframe").format(what=what, dir=d, far=far))
        intro = narr.pick(LK.VISTA_CLEAR if w.weather_class == "bright" else LK.VISTA_DULL, "vista")
        parts.append(f"{intro} You make out {_list(bits)}.")
    else:
        regions = sorted({w.region_of(p)["name"] for p, t in w.tiles.items()
                          if getattr(t, "glimpsed", False) and abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) <= 2} - {w.region_of(g.pos)["name"]})
        if regions and g.rng.random() < 0.6:
            parts.append(narr.pick(LK.VISTA_CLEAR if w.weather_class == "bright" else LK.VISTA_DULL, "vista") +
                         f" You can see as far as {_list(regions[:2])}.")
        else:
            parts.append(narr.pick(LK.VISTA_NONE, "vista:none"))
    if not fog and not dark:                      # an errand's destination, if it's in sight
        for q in S.active(g):
            tq = q.get("target")
            if tq and tuple(tq) != tuple(g.pos) and abs(tq[0] - g.pos[0]) + abs(tq[1] - g.pos[1]) <= 3:
                t = w.tiles[tuple(tq)]
                place = t.site["name"] if t.site and t.site.get("name") else w.region_of(tuple(tq))["name"]
                d, far = where(tuple(tq))
                parts.append(narr.pick(LK.GOAL_SEEN, "goalseen").format(place=place, dir=d, far=far, title=q["title"]))
                break
    if g.rng.random() < 0.35:
        parts.append(narr.pick(LK.CLIMB_DOWN, "climbdown"))
    g.emit(" ".join(parts))


def reveal_places(g, radius):
    """Mark the land within reach as glimpsed; return the sites newly seen, nearest first, as (kind, pos)."""
    w = g.world
    out = []
    for (x, y), t in w.tiles.items():
        if (x, y) != tuple(g.pos) and abs(x - g.pos[0]) + abs(y - g.pos[1]) <= radius and not t.visited and not getattr(t, "glimpsed", False):
            t.glimpsed = True
            if t.site and t.site["kind"] in ("village", "ruin", "shrine"):
                t.site_seen = True
                out.append((t.site["kind"], (x, y)))
    out.sort(key=lambda kp: abs(kp[1][0] - g.pos[0]) + abs(kp[1][1] - g.pos[1]))
    return out


def reveal(g, radius):
    w = g.world
    names = []
    for (x, y), t in w.tiles.items():
        if (x, y) != tuple(g.pos) and abs(x - g.pos[0]) + abs(y - g.pos[1]) <= radius and not t.visited and not getattr(t, "glimpsed", False):
            t.glimpsed = True
            if t.site and t.site["kind"] in ("village", "ruin", "shrine"):
                t.site_seen = True
                names.append({"village": "a village", "ruin": "a ruin", "shrine": "a shrine"}[t.site["kind"]] + " " + g.narr.dir_phrase(g.pos, (x, y)))
    regions = {w.region_of(p)["name"] for p, t in w.tiles.items() if getattr(t, "glimpsed", False) and abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) <= radius}
    bits = names[:3] or ([f"the edges of {', '.join(sorted(regions)[:2])}"] if regions else [])
    return ", ".join(bits)


def plain_drink(g, f):
    p = g.player
    heal = min(p.maxhp - p.hp, g.rng.randint(1, 3))
    p.hp += heal
    g.emit(g.narr.pick([f"You cup your hands and drink from the {f.noun}. The water is cold enough to ache in your teeth.",
                        f"You kneel and drink from the {f.noun}. It tastes of stone and earth.",
                        f"The water of the {f.noun} is clean and cold. You drink your fill."]) + (f" (+{heal} HP)" if heal else ""))


def plain_touch(g, f):
    t = tag_of(f)
    feel = {"tree": "rough bark, and under it a slow, patient life", "stone": "cold stone, rough with lichen", "water": "cold water closing round your fingers",
            "earth": "damp earth that gives a little under your palm", "log": "soft, crumbling wood, cold and damp under the moss", "built": "old wood and stone, worn by other hands", "ice": "a cold that bites straight to the bone",
            "fungus": "soft caps, faintly greasy", "plant": "grass, cool and springy"}
    g.emit(g.narr.pick([f"You lay a hand on the {f.noun}: {feel.get(t, 'nothing out of the ordinary')}.",
                        f"You touch the {f.noun}. {cap(feel.get(t, 'Nothing happens'))}. Nothing more.",
                        f"You rest your palm against the {f.noun} for a while. {cap(feel.get(t, 'It is what it is'))}."]))


LORE = ["a list of names, the last few added in a cruder hand", "a prayer for safe roads, worn almost smooth", "a warning: 'Not after dark'",
        "the words 'I waited here three days' and a date no one uses any more", "a carved hand, palm out", "a tally of seven strokes, and then a cross",
        "a line of verse about a king who sleeps under a hill", "the words 'Remember Aldric', over and over", "a crude map of the stars",
        "two names inside a heart, one scratched out", "a mason's mark and the words 'for the dead of the hard winter'"]


def plain_read(g, f):
    g.emit(g.narr.pick([f"You trace the marks on the {f.noun} with a finger. It reads: {g.narr.pick(LORE)}.",
                        f"Worn into the {f.noun} you make out {g.narr.pick(LORE)}.",
                        f"The {f.noun} bears {g.narr.pick(LORE)}."]))


def plain_listen(g, f):
    w = g.world
    snd = ["wind", "a distant bird", "your own heartbeat", "water somewhere", "the creak of something settling"]
    if w.is_dark:
        snd += ["an owl", "a fox's scream, far off", "small things moving"]
    g.emit(g.narr.pick([f"You stand by the {f.noun} and listen. You hear {g.narr.pick(snd)}, and nothing else.",
                        f"You listen at the {f.noun} a long while: {g.narr.pick(snd)}.",
                        f"You close your eyes beside the {f.noun}. Only {g.narr.pick(snd)}."]))


FORAGE = {
    "spring": [("food", "handful of wild garlic", 2), ("herb", None, 0), ("food", "fistful of young nettle-tops", 2)],
    "summer": [("food", "handful of wild strawberries", 3), ("food", "cap full of bilberries", 3), ("herb", None, 0)],
    "autumn": [("food", "pocketful of hazelnuts", 3), ("food", "handful of blackberries", 3), ("food", "few field mushrooms", 3), ("herb", None, 0)],
    "winter": [("food", "few shrivelled rosehips", 1)],
}


def plain_forage(g, f):
    w = g.world
    if f.state.get("forage_day") == w.day:
        return g.emit(f"You've already picked the {f.noun} over today.")
    f.state["forage_day"] = w.day
    if w.is_dark:
        return g.emit("You grope about in the dark and come away with nothing but scratches.")
    if w.season == "winter" and g.rng.random() < 0.6:
        return g.emit(f"Winter has stripped the {f.noun} bare. There is nothing to gather.")
    if tag_of(f) == "fungus":
        return mushrooms(g, f)
    kind, name, heal = g.rng.choice(FORAGE[w.season])
    if kind == "herb":
        it = w.make_item(1, "herb")
    else:
        from .world import Item
        it = Item("food", name, value=heal, heal=heal)
    g.player.inv.append(it)
    g.emit(g.narr.pick([f"You forage around the {f.noun} and come away with {article(it.name)}.",
                        f"There's food here if you know where to look. You gather {article(it.name)}.",
                        f"After a patient search around the {f.noun} you have {article(it.name)}."]))


def mushrooms(g, f):
    from .world import Item
    p = g.player
    r = g.rng.random() * (0.4 if getattr(g, "knows_fungi", False) else 1)
    if r < 0.4:
        p.inv.append(Item("food", "handful of fairy-ring mushrooms", value=4, heal=5))
        g.emit(f"You pick a handful of mushrooms from the {f.noun}. They smell good - like the field ones, you're fairly sure.")
    elif r < 0.7:
        S.add_buff(g, "fae", 6)
        g.emit(f"You nibble one cap from the {f.noun} to test it. The world tilts gently and every colour sings for a while. (Fae favour for a few hours.)")
    else:
        S.add_buff(g, "queasy", 6)
        p.hp = max(1, p.hp - 2)
        g.emit(f"You try a cap from the {f.noun}. It tastes of nothing, and then of regret. Your stomach rolls. (-2 HP, queasy for a few hours.)")


PLAIN = {"search": plain_search, "climb": plain_climb, "drink": plain_drink, "touch": plain_touch,
         "read": plain_read, "listen": plain_listen, "forage": plain_forage}


# ------------------------------------------------------------------ secrets
def s_cache(g, f, sec):
    w, p = g.world, g.player
    gold = g.rng.randint(8, 25)
    p.gold += gold
    where = LK.CACHE_WHERE.get(tag_of(f), "tucked out of sight")
    extra = ""
    if g.rng.random() < 0.5:
        it = w.make_item(2, g.rng.choice(["potion", "weapon", "armour", "trinket"]))
        p.inv.append(it)
        extra = f", and {article(it.name)} wrapped in oiled cloth"
    loot = f"{gold} coins{extra}"
    g.emit(g.narr.pick(LK.CACHE, "cache").format(where=where, Where=cap(where), noun=f.noun, loot=loot, Loot=cap(loot)))
    S.record(g, f"You found a hidden cache at the {f.noun}.", "find", mark=f"The ground by the {f.noun} has been dug, where you found the cache.", mark_days=6)


def s_old_blade(g, f, sec):
    S.ask(g, f"Half-buried at the {f.noun} lies a blade, dark with age but whole. Whoever laid it here meant it to stay.",
          [("Take it", "blade_take", dict(pos=g.pos, noun=f.noun)), ("Leave it with the dead, and say a word for them", "blade_leave", dict(noun=f.noun))],
          leave=1)


@S.choice_handler("blade_take")
def _blade_take(g, d):
    it = g.world.make_item(3, "weapon")
    g.player.inv.append(it)
    g.emit(f"You work the blade free. It is {article(it.name)}, and it fits your hand as if it remembered one.")
    if g.rng.random() < 0.5 and d["noun"] in ("barrow", "burial mound", "cairn", "pile of stones"):
        sp = next((s for s in g.world.species if s["arch"].get("undead")), None)
        if sp:
            c = g.world.make_creature(sp, max(2, g.world.tiles[g.pos].danger))
            c.aggressive = True
            g.world.tiles[g.pos].creatures.append(c)
            g.emit("The ground shudders. Something rises from beneath, and it wants its blade back.")
            g.combat = c
            g.enemy_turn(committed=True)
    S.record(g, f"You took an old blade from the {d['noun']}.", "find")


@S.choice_handler("blade_leave")
def _blade_leave(g, d):
    S.add_buff(g, "lucky", 24)
    g.emit(f"You leave the blade where it lies and speak a few words for whoever it belonged to. The air feels lighter. (Luck for a day.)")
    S.record(g, f"You left an old blade with the dead at the {d['noun']}.", "deed", story="you left a dead warrior's blade where it lay, out of respect", like=1)


def s_nest(g, f, sec):
    p = g.player
    if f.archetype == "eyrie" and g.klass() not in ("ranger", "rogue"):
        dmg = g.rng.randint(3, 6)
        p.hp = max(1, p.hp - dmg)
        g.emit(f"As you reach the eyrie an eagle stoops on you out of nowhere, all talons and fury. You grab what you can and half-climb, half-fall back down. ({dmg} damage)")
    it = g.world.make_item(2, "trinket")
    p.inv.append(it)
    gold = g.rng.randint(2, 9)
    p.gold += gold
    g.emit(f"Woven into the nest in the {f.noun} you find {article(it.name)} and {gold} coins - a thieving bird's hoard.")


def s_healing(g, f, sec):
    p = g.player
    holy = f.archetype == "holy well"
    heal = p.maxhp - p.hp if holy else min(p.maxhp - p.hp, g.rng.randint(8, 15))
    p.hp += heal
    if holy:
        S.add_buff(g, "blessed", 12)
    g.emit(g.narr.pick([f"The water of the {f.noun} tastes of nothing at all, and then of every good thing. Warmth spreads through you.",
                        f"You drink from the {f.noun}. The cold goes in, and your aches go out."]) + f" (+{heal} HP" + (", blessed for half a day)" if holy else ")"))
    rested(g, sec)               # a healing spring heals again - tomorrow


def s_bad_water(g, f, sec):
    S.add_buff(g, "queasy", 8)
    g.player.hp = max(1, g.player.hp - 2)
    g.emit(f"The water of the {f.noun} tastes of rot. You spit, but too late. Your stomach turns over. (-2 HP; you won't heal on the road for a while.)")
    S.record(g, f"You drank bad water at the {f.noun}.", "mishap", story=f"you drank from the {f.noun} out in {g.world.region_of(g.pos)['name']}, of all the fool things", like=0)


def s_fairy(g, f, sec):
    ring = "Small lights wheel in a ring" if f.archetype in ("ring of toadstools", "stone circle") else f"Small lights wheel around the {f.noun}"
    S.ask(g, f"The {f.noun} is alight. {ring}, and music you can almost hear pulls at your feet. A voice, very close: \"Dance with us?\"",
          [("Step into the ring and dance", "fairy_dance", dict(noun=f.noun)),
           ("Leave an offering of food at the edge", "fairy_offer", dict(noun=f.noun)),
           ("Step back and keep your feet", "fairy_refuse", dict(noun=f.noun))], leave=2)


@S.choice_handler("fairy_dance")
def _fairy_dance(g, d):
    r = g.rng.random()
    if r < 0.4:
        it = g.world.make_item(4, g.rng.choice(["weapon", "armour", "potion"]))
        g.player.inv.append(it)
        hours = g.rng.randint(4, 9)
        g.pass_time(hours * 60)
        g.emit(f"You dance. You can't stop. When you can, it is {hours} hours later, your feet are bleeding, and in your hands is {article(it.name)} you have never seen before.")
    elif r < 0.75:
        S.add_buff(g, "fae", 48)
        g.pass_time(120)
        g.emit("You dance until you are laughing, and the lights laugh with you. When it ends you feel quick and light, as if the ground had stopped holding on. (Fae favour for two days.)")
    else:
        w = g.world
        far = [p for p in w.land if 3 <= abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) <= 6 and not (w.tiles[p].site and w.tiles[p].site.get("quest"))]
        if far:
            g.pos, g.combat = g.rng.choice(far), None
        g.pass_time(g.rng.randint(5, 10) * 60)
        g.emit("You dance, and the ring spins, and the stars spin, and then you are lying in wet grass somewhere else entirely, with a terrible thirst.")
        g.show_location()
    S.record(g, f"You danced in the {d['noun']} with the fair folk.", "magic", story="you danced with the fair folk and came back", like=1, reach=10)


@S.choice_handler("fairy_offer")
def _fairy_offer(g, d):
    food = next((i for i in g.player.inv if i.kind == "food"), None)
    if not food:
        g.emit("You pat your pockets - you have no food to offer. The lights dim, disappointed, and are gone.")
        return
    g.player.inv.remove(food)
    S.add_buff(g, "fae", 24)
    S.add_buff(g, "lucky", 24)
    g.emit(f"You set the {food.name} at the edge of the ring. Small hands that aren't there take it. Something brushes your cheek like a thank-you. (Fae favour and luck for a day.)")
    S.record(g, f"You left an offering for the fair folk at the {d['noun']}.", "magic")


@S.choice_handler("fairy_refuse")
def _fairy_refuse(g, d):
    g.emit("You plant your feet. The music sours, then stops. When you look again the ring is just toadstools and grass, and you are alone.")


def s_wishing(g, f, sec):
    if g.player.gold < 1:
        rested(g, sec)
        return g.emit(f"Coins glint at the bottom of the {f.noun}. You have none to add.")
    S.ask(g, f"The {f.noun} is full of other people's wishes, glinting. It seems to wait for yours.",
          [("Toss in a coin and wish for luck", "wish", dict(kind="luck", noun=f.noun)),
           ("Toss in a coin and wish to know the way", "wish", dict(kind="way", noun=f.noun)),
           ("Toss in a coin and wish to be well", "wish", dict(kind="health", noun=f.noun)),
           ("Keep your coin", "wish_none", {})], leave=3)


@S.choice_handler("wish")
def _wish(g, d):
    g.player.gold -= 1
    w = g.world
    if d["kind"] == "luck":
        S.add_buff(g, "lucky", 48)
        g.emit("The coin turns over and over as it sinks, and lands face up. (Luck for two days.)")
    elif d["kind"] == "health":
        g.player.maxhp += 1
        g.player.hp = g.player.maxhp
        g.emit("The water shivers. You feel a warmth settle in your chest and stay there. (+1 max HP, fully healed.)")
    else:
        if g.has_quest:
            g.emit(f"In the ripples you see a ruin {g.narr.dir_phrase(g.pos, w.quest_pos)}, and something huge asleep in it.")
        else:
            v = w.tiles[w.start].site["name"]
            g.emit(f"In the ripples you see {v}, and an old face waiting there for you.")
    S.record(g, f"You made a wish at the {d['noun']}.", "magic")


@S.choice_handler("wish_none")
def _wish_none(g, d):
    g.emit("You keep your coin. The water goes still.")


def s_vision(g, f, sec):
    w, n = g.world, g.narr
    g.emit(f"You lay your hand on the {f.noun} and the world drops away.")
    r = g.rng.random()
    if r < 0.45 or not g.has_quest:
        target = plant_cache(g, 4, 9)
        if target:
            tp, tf = target
            g.emit(f"You see, as clearly as if you stood there, {article(tf.noun)} {n.dir_phrase(g.pos, tp)}, and something hidden at its foot.")
            S.new_quest(g, "find", f"The vision at the {f.noun}", f"Search the {tf.noun} you saw in a vision", dict(gold=0), target=tp, source="vision",
                        data=dict(noun=tf.noun, search=True))
            return
    if g.has_quest:
        g.emit(f"You see the {w.relic.name}, lying in the dark in a broken place {n.dir_phrase(g.pos, w.quest_pos)}. Something breathes beside it.")
    else:
        g.emit(f"You see an old face in {w.tiles[w.start].site['name']}, waiting at a window for someone who hasn't come yet.")
    S.add_buff(g, "blessed", 12)


def plant_cache(g, lo, hi):
    """Hide a fresh cache at a landmark some distance away, for clues and visions to point to."""
    w = g.world
    cands = [(p, f) for p in w.land for f in w.tiles[p].features
             if lo <= abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) <= hi and not (f.state or {}).get("secret")]
    if not cands:
        return None
    p, f = g.rng.choice(cands)
    f.state = f.state or {}
    f.state["secret"] = dict(key="cache", verbs=["search"], cond=None, found=False, planted=True)
    return p, f


def s_raven(g, f, sec):
    riddles = [("What has roots that nobody sees, is taller than trees, up it goes, and yet never grows?", ["A mountain", "An oak", "A river"], 0),
               ("Thirty white horses on a red hill; first they champ, then they stamp, then they stand still. What are they?", ["Teeth", "Gravestones", "Hailstones"], 0),
               ("Voiceless it cries, wingless flutters, toothless bites, mouthless mutters. What is it?", ["The wind", "A ghost", "A bat"], 0),
               ("The more you take, the more you leave behind. What are they?", ["Footsteps", "Coins", "Years"], 0)]
    q, answers, right = g.rng.choice(riddles)
    order = list(range(len(answers)))
    g.rng.shuffle(order)
    opts = [(answers[i], "raven_answer", dict(right=(i == right), noun=f.noun)) for i in order]
    S.ask(g, f"A raven drops onto the {f.noun} beside you and fixes you with a black eye. \"Riddle,\" it croaks, quite clearly. \"{q}\"",
          opts + [("Shoo it away", "raven_shoo", {})], leave=len(opts))


@S.choice_handler("raven_answer")
def _raven_answer(g, d):
    if d["right"]:
        target = plant_cache(g, 3, 7)
        if target:
            tp, tf = target
            g.emit(f"\"Clever,\" says the raven, sounding put out. \"Clever, clever. Look under the {tf.noun}, {g.narr.dir_phrase(g.pos, tp)}.\" It flaps off, laughing.")
            S.new_quest(g, "find", "The raven's secret", f"Search the {tf.noun} the raven spoke of", dict(gold=0), target=tp, source="raven",
                        data=dict(noun=tf.noun, search=True))
        else:
            g.emit("\"Clever,\" says the raven, and flies off.")
    else:
        lost = min(g.player.gold, g.rng.randint(1, 4))
        g.player.gold -= lost
        g.emit(f"\"Wrong!\" The raven cackles, snatches {lost} coin{'s' if lost != 1 else ''} from your purse, and is gone before you can grab it.")
        S.record(g, "A raven beat you at riddles and robbed you.", "mishap", story="a raven beat you at riddles and took your coin", like=0)


@S.choice_handler("raven_shoo")
def _raven_shoo(g, d):
    g.emit("You flap your arms. The raven gives you a look of deep contempt and flies off.")


def s_ghost(g, f, sec):
    S.ask(g, f"The cold thickens by the {f.noun} into a shape: {sec['who']}, grey and faint. It holds out a {sec['token']} that you can see right through. "
             "\"Take it to holy ground,\" it whispers. \"Let me rest.\"",
          [("Promise to take it", "ghost_yes", dict(who=sec["who"], token=sec["token"], noun=f.noun)),
           ("Refuse", "ghost_no", dict(who=sec["who"]))], leave=1)


@S.choice_handler("ghost_yes")
def _ghost_yes(g, d):
    from .world import Item
    w = g.world
    shrines = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "shrine"]
    target = min(shrines, key=lambda s: abs(s[0] - g.pos[0]) + abs(s[1] - g.pos[1])) if shrines else w.start
    it = Item("token", d["token"], value=0, facts=dict(material="something cold", glow="a chill that never warms"))
    g.player.inv.append(it)
    g.emit(f"Your fingers close on the {d['token']}, and it is solid, and cold as river ice. The shape fades with a sigh.")
    where = w.tiles[target].site
    S.new_quest(g, "deliver", f"Rest for {d['who']}", f"Carry the {d['token']} to holy ground - the nearest is the shrine of {where['spirit']}" if where and where.get("spirit") else f"Carry the {d['token']} to holy ground",
                dict(maxhp=2, xp=20, buff=("blessed", 24), chronicle=f"You laid {d['who']} to rest.",
                     story=f"you laid the ghost of {d['who']} to rest", story_like=2),
                target=target, item=d["token"], source="ghost",
                data=dict(done_text=f"You lay the {d['token']} at the shrine. For a moment you see {d['who']} standing beside you, no longer grey. Then there is only sunlight, or moonlight, and peace."))


@S.choice_handler("ghost_no")
def _ghost_no(g, d):
    S.add_buff(g, "cursed", 8)
    g.emit("The shape's face crumples. Its wail follows you a long way, and cold sits on your shoulders like a hand. (Cursed for a while.)")


def s_wisp(g, f, sec):
    S.ask(g, f"A pale light rises from beyond the {f.noun} and bobs away over the bog, slow, as if waiting for you to follow.",
          [("Follow the light", "wisp_follow", dict(noun=f.noun)), ("Turn your back on it", "wisp_no", {})], leave=1)


@S.choice_handler("wisp_follow")
def _wisp_follow(g, d):
    w, p = g.world, g.player
    if g.rng.random() < 0.5:
        gold = g.rng.randint(10, 30)
        p.gold += gold
        it = w.make_item(3, g.rng.choice(["potion", "trinket", "weapon"]))
        p.inv.append(it)
        g.emit(f"The light leads you to a hummock where it sinks into the ground and goes out. Digging, you find a drowned man's purse: {gold} coins, and {article(it.name)}.")
    else:
        dmg = g.rng.randint(3, 6)
        p.hp = max(1, p.hp - dmg)
        S.add_buff(g, "soaked", 4)
        g.emit(f"The light dances ahead, and ahead, and then the ground isn't there and you are up to your chest in black water. You drag yourself out, the light long gone. ({dmg} damage)")
        S.record(g, "A will-o'-the-wisp led you into the bog.", "mishap", story="a will-o'-the-wisp led you into the bog and you came out black to the neck", like=0)
    g.pass_time(60)


@S.choice_handler("wisp_no")
def _wisp_no(g, d):
    g.emit("You turn away. Behind you, the light flickers, uncertain, and goes out.")


def s_hermit(g, f, sec):
    from .world import PRONOUNS
    sec.setdefault("gender", random.Random(f"{g.world.seed}-hermit-{f.noun}").choice(["female", "male"]))   # the same hermit every visit
    pr = PRONOUNS[sec["gender"]]
    S.ask(g, f"The door of the {f.noun} creaks open. An old hermit peers out, wrapped in a blanket, eyes bright as a bird's. \"A visitor! What do you want of me?\"",
          [("Ask for a blessing", "hermit", dict(kind="bless", g=sec["gender"])), (f"Ask what {pr['he']} knows", "hermit", dict(kind="know", g=sec["gender"])),
           (f"Share your food with {pr['him']}", "hermit", dict(kind="share", g=sec["gender"])),
           (f"Apologise and leave {pr['him']} in peace", "hermit", dict(kind="leave", g=sec["gender"]))], leave=3)


@S.choice_handler("hermit")
def _hermit(g, d):
    p, w, n = g.player, g.world, g.narr
    k = d["kind"]
    if k == "bless":
        p.hp = p.maxhp
        if hasattr(p, "res_max"):
            p.res = p.res_max
        g.emit("The hermit puts two dry fingers on your forehead and mutters. You feel scoured clean. (Fully restored.)")
    elif k == "know":
        if g.has_quest:
            g.emit(f"\"The {w.relic.name}? Aye. It lies {n.dir_phrase(g.pos, w.quest_pos)}. The thing that guards it is old and slow and does not forgive. Go strong, or don't go.\"")
        else:
            elder = next((n for n in w.tiles[w.start].npcs if n.role == "elder"), None)
            g.emit(f"\"There's an old one in {w.tiles[w.start].site['name']} who's been waiting a long while for someone like you. Go and see {elder.pronouns()['him'] if elder else 'them'}.\"")
    elif k == "share":
        food = next((i for i in p.inv if i.kind == "food"), None)
        if food:
            p.inv.remove(food)
            p.maxhp += 2
            p.hp += 2
            g.emit(f"You share your {food.name}. The hermit eats like a sparrow and talks like a river, and when you go you feel oddly stronger. (+2 max HP.)")
            S.record(g, "You shared a meal with the hermit.", "deed", story="you shared your food with the mountain hermit", like=1)
        else:
            g.emit(f"You have nothing to share. The hermit laughs and shares {'hers' if d.get('g') == 'female' else 'his'} instead: one cold, wonderful potato.")
            p.hp = min(p.maxhp, p.hp + 3)
    else:
        g.emit("\"Peace, then,\" says the hermit, and shuts the door.")


def s_cursed_stone(g, f, sec):
    S.ask(g, f"Tucked into the {f.noun} is a stone carved with a sign that hurts to look at. It's small enough to pocket, and it looks valuable.",
          [("Take the carved stone", "curse_take", dict(pos=g.pos, noun=f.noun)), ("Leave it alone", "curse_leave", {})], leave=1)


@S.choice_handler("curse_take")
def _curse_take(g, d):
    from .world import Item
    it = Item("trinket", "carved curse-stone", value=30, facts=dict(detail="cut with a sign that hurts to look at"))
    g.player.inv.append(it)
    S.add_buff(g, "cursed", 24 * 30)
    g.emit("You pocket the stone. At once the day seems darker, and your hands clumsier. Something has noticed you. (Cursed.)")
    S.new_quest(g, "deliver", "The carved stone", f"Put the curse-stone back in the {d['noun']} where you found it", dict(chronicle="You returned the curse-stone."),
                target=tuple(d["pos"]), item=it.name, source="curse",
                data=dict(done_text="You push the stone back into its place. The weight lifts from your shoulders all at once.", lift="cursed"))


@S.choice_handler("curse_leave")
def _curse_leave(g, d):
    g.emit("You leave it. Some things are carved for a reason.")


def s_magpie(g, f, sec):
    p = g.player
    lost = min(p.gold, g.rng.randint(3, 8))
    if lost <= 0:
        return g.emit(f"A magpie in the {f.noun} looks you over, finds nothing worth stealing, and says so loudly.")
    p.gold -= lost
    target = plant_cache(g, 2, 5)
    g.emit(f"While you're busy at the {f.noun}, a magpie drops onto your pack, flips open your purse with its beak and is away with {lost} coins before you can swat it.")
    if target:
        tp, tf = target
        tf.state["secret"].update(key="magpie_nest", verbs=["search"] + (["climb"] if can("climb", tf) else []), gold=lost * 2)
        g.emit(f"You watch where it goes: toward {article(tf.noun)}, {g.narr.dir_phrase(g.pos, tp)}.")
        S.new_quest(g, "find", "The thieving magpie", f"Get your coins back from the magpie's hoard at the {tf.noun}", dict(gold=0), target=tp, source="magpie",
                    data=dict(noun=tf.noun, search=True))
    S.record(g, f"A magpie stole {lost} coins from you.", "mishap", story="a magpie robbed you blind in broad daylight", like=0)


def s_magpie_nest(g, f, sec):
    gold = sec.get("gold", 10)
    g.player.gold += gold
    it = g.world.make_item(1, "trinket")
    g.player.inv.append(it)
    g.emit(f"There it is - the magpie's hoard, at the {f.noun}: your coins and plenty of other people's. {gold} coins all told, and {article(it.name)}. The magpie screams at you from a branch.")


def s_slip(g, f, sec):
    p = g.player
    lost = next((i for i in p.inv if i.kind in ("food", "herb")), None)
    if lost:
        p.inv.remove(lost)
    S.add_buff(g, "soaked", 4)
    p.hp = max(1, p.hp - 1)
    g.emit(f"You lean out to drink from the {f.noun}, the stone under your hand turns, and you go in headfirst. "
           + (f"You come up spluttering; your {lost.name} does not come up at all." if lost else "You come up spluttering and soaked to the skin.")
           + " (Soaked: a little easier to hit for a while.)")
    S.record(g, f"You fell into the {f.noun}.", "mishap", story=f"you fell headfirst into the {f.noun} trying to get a drink", like=0)


def s_stuck(g, f, sec):
    g.pass_time(120)
    g.emit(f"You climb the {f.noun} easily enough. Getting down is another matter. It takes you two undignified hours, a torn sleeve, and a lot of language.")
    S.record(g, f"You got stuck up the {f.noun}.", "mishap", story=f"you got stuck up a {f.noun} for half the afternoon", like=0, reach=8)


def s_bees(g, f, sec):
    from .world import Item
    dmg = g.rng.randint(2, 4)
    g.player.hp = max(1, g.player.hp - dmg)
    g.player.inv.append(Item("food", "comb of wild honey", value=8, heal=8))
    g.emit(f"You find the bees' nest in the {f.noun} the hard way. Through the stings ({dmg} damage) you manage to break off a dripping comb of wild honey.")


def s_badger(g, f, sec):
    dmg = g.rng.randint(1, 3)
    g.player.hp = max(1, g.player.hp - dmg)
    g.emit(f"You reach into the {f.noun} and something inside bites you, hard, and does not let go for a long and educational moment. ({dmg} damage) A badger glares out at you, then retreats.")
    S.record(g, f"A badger bit you at the {f.noun}.", "mishap", story="a badger bit you when you stuck your hand in its sett", like=0)


def s_keepsake(g, f, sec):
    from .world import Item
    owner = S.find_npc(g.world, sec.get("owner"))
    if not owner:
        return s_cache(g, f, sec)
    w = g.world
    home = w.tiles[owner.home].site["name"] if w.tiles[owner.home].site else "somewhere"
    if sec["key"] == "letter":
        name = f"letter for {owner.name}"
        it = Item("trinket", name, value=1, facts=dict(detail=f"sealed with wax and addressed to {owner.name} of {home}, from {sec['sender']}"))
        g.emit(f"Wedged into the {f.noun} is a letter, damp but sealed, addressed in a careful hand to {owner.name} of {home}.")
        title, desc = f"A letter for {owner.name}", f"Deliver the letter you found to {owner.name} in {home}"
        done = f"{owner.name} turns the letter over, sees the hand, and goes very still. \"From {sec['sender']}… I thought {S.find_npc(g.world, sec['sender']).pronouns()['he'] if S.find_npc(g.world, sec['sender']) else 'they'}'d forgotten me.\""
    else:
        name = f"{sec['thing']} engraved '{owner.name}'"
        it = Item("trinket", name, value=6, facts=dict(detail=g.rng.choice(["worn smooth by years of handling", "small enough to lose in a pocket",
                                                                               "a little chipped, but clearly cared for", "the letters cut with a careful hand"])))
        g.emit(f"In the grass by the {f.noun} you find a {sec['thing']}, lost a long time. Someone has engraved a name on it: {owner.name}.")
        title, desc = f"{owner.name}'s {sec['thing']}", f"Return the {sec['thing']} to {owner.name}"
        pr = owner.pronouns()
        done = f"{owner.name} stares at the {sec['thing']}. \"Where did you - I lost this years ago!\" {cap(pr['he'])} holds it to {pr['his']} chest and won't let go."
    g.player.inv.append(it)
    q = S.new_quest(g, "bring", title, desc, dict(gold=g.rng.randint(5, 15), like=5, chronicle=f"You returned a lost {sec['thing']} to {owner.name}.",
                                                   story=f"you brought {owner.name} back something {owner.pronouns()['he']} had lost", story_like=1),
                    item=name, source="keepsake", data=dict(done_text=done))
    q["giver"], q["giver_home"] = owner.name, owner.home


s_letter = s_keepsake


def s_bones(g, f, sec):
    if "who" not in sec:
        sec["who"] = g.rng.randrange(len(TRAVELLERS))
    who, token, look, dest, where, _ = TRAVELLERS[sec["who"] % len(TRAVELLERS)]
    S.ask(g, f"Under the {f.noun} lie the bones of {who}, long dead. In the rags is a {token} - {look}.",
          [(f"Take the {token} to {where}", "bones_take", dict(shrine=sec.get("shrine"), noun=f.noun, who=sec["who"])),
           ("Cover the bones and leave them be", "bones_cover", dict(noun=f.noun)), ("Leave them", "bones_leave", {})], leave=2)


@S.choice_handler("bones_take")
def _bones_take(g, d):
    from .world import Item
    w = g.world
    who, token, look, dest, where, done = TRAVELLERS[d.get("who", 0) % len(TRAVELLERS)]
    if dest == "shrine":
        target = tuple(d["shrine"]) if d.get("shrine") else w.start
    else:      # a village other than the nearest you came from, if there is one
        vs = sorted(w.villages, key=lambda v: abs(v[0] - g.pos[0]) + abs(v[1] - g.pos[1]))
        target = g.rng.choice(vs[:3]) if vs else w.start
    place = w.tiles[target].site["name"] if w.tiles[target].site and w.tiles[target].site.get("name") else "holy ground"
    it = Item("trinket", token, value=1, facts=dict(detail=look))
    g.player.inv.append(it)
    S.new_quest(g, "deliver", f"The {token}", f"Carry the dead {who.split()[-1]}'s {token.split(' ', 1)[-1] if token.startswith(who.split()[-1]) else token} to {place}",
                dict(xp=15, buff=("blessed", 24), chronicle=f"You finished a dead {who.split()[-1]}'s last journey for them.",
                     story=f"you carried a dead {who.split()[-1]}'s {token} home", story_like=2),
                target=target, item=it.name, source="bones", data=dict(done_text=done))
    g.emit(g.narr.pick([f"You take the {token} gently. It weighs almost nothing.", f"You wrap the {token} in a scrap of cloth and put it away carefully."]))


@S.choice_handler("bones_cover")
def _bones_cover(g, d):
    g.pass_time(30)
    S.add_buff(g, "lucky", 12)
    g.emit("You scrape earth and stones over the bones and say what words you know. It feels like the right thing. (Luck for half a day.)")
    S.record(g, f"You buried a stranger's bones at the {d['noun']}.", "deed", mark=f"A low mound of stones by the {d['noun']} covers the bones you buried.",
             story="you buried a stranger's bones out in the wild", like=1)


@S.choice_handler("bones_leave")
def _bones_leave(g, d):
    g.emit("You leave the dead to their rest.")


def s_snared(g, f, sec):
    beast = g.rng.choice(["fox", "hare", "young deer", "badger cub"])
    S.ask(g, f"Near the {f.noun} a {beast} is caught in a wire snare, half-strangled, eyes rolling.",
          [(f"Free the {beast}", "snare_free", dict(beast=beast)), (f"Take the {beast} for food", "snare_take", dict(beast=beast)),
           ("Leave it", "snare_leave", dict(beast=beast))], leave=2)


@S.choice_handler("snare_free")
def _snare_free(g, d):
    S.add_buff(g, "lucky", 24)
    g.emit(g.narr.pick(LK_TALK2.SNARE_FREE, "snarefree").format(beast=d["beast"]) + " (Luck for a day.)")
    S.record(g, f"You freed a {d['beast']} from a snare.", "deed", story=f"you freed a {d['beast']} from a poacher's snare", like=1)


@S.choice_handler("snare_take")
def _snare_take(g, d):
    from .world import Item
    g.player.inv.append(Item("food", f"brace of {d['beast']} meat", value=7, heal=7))
    g.emit(f"It's quick, at least. You'll eat well tonight.")


@S.choice_handler("snare_leave")
def _snare_leave(g, d):
    g.emit(f"You leave the {d['beast']} to whoever set the snare.")


def s_clue(g, f, sec):
    target = plant_cache(g, 3, 8)
    if not target:
        return plain_read(g, f)
    tp, tf = target
    g.emit(f"Scratched into the {f.noun}, newer than the rest: an arrow, a crude drawing of {article(tf.noun)}, and the word 'BENEATH'. "
           f"By the arrow, it lies {g.narr.dir_phrase(g.pos, tp)}.")
    S.new_quest(g, "find", f"The mark on the {f.noun}", f"Search beneath the {tf.noun} the scratched clue points to", dict(gold=0), target=tp, source="clue",
                data=dict(noun=tf.noun, search=True))


def s_echo(g, f, sec):
    S.ask(g, f"From deep in the {f.noun} a voice says your name. Not an echo - you didn't speak.",
          [("Answer it", "echo_answer", dict(noun=f.noun)), ("Back away slowly", "echo_leave", {})], leave=1)


@S.choice_handler("echo_answer")
def _echo_answer(g, d):
    w, n = g.world, g.narr
    if g.rng.random() < 0.6:
        g.emit(f"\"Listen,\" says the voice. \"The thing that guards the {w.relic.name} cannot abide fire, nor holy words. Go to it by daylight.\" Then nothing, however long you wait.")
        S.add_buff(g, "warded", 24)
    else:
        S.add_buff(g, "cursed", 6)
        g.emit("\"Come down,\" it says, sweetly. \"Come down to us.\" You find yourself at the very edge before you can stop. You stagger back, shaking. (Cursed for a while.)")


@S.choice_handler("echo_leave")
def _echo_leave(g, d):
    g.emit("You back away. The voice says your name once more, sadly, and then is silent.")


def s_chalk_walk(g, f, sec):
    g.pass_time(90)
    S.add_buff(g, "strong", 24)
    g.emit(g.narr.pick(LK_TALK2.CHALK_WALK, "chalkwalk").format(noun=f.noun) + " (Strength for a day.)")
    rested(g, sec)


def s_hot_bath(g, f, sec):
    p = g.player
    p.hp = p.maxhp
    if hasattr(p, "res_max"):
        p.res = p.res_max
    g.pass_time(60)
    g.emit(f"You strip off and sink into the {f.noun}. It stinks of rotten eggs and it is the best thing that has happened to you in weeks. Every ache dissolves. (Fully restored.)")
    rested(g, sec)


def s_ringing(g, f, sec):
    t = g.world.tiles[g.pos]
    S.add_buff(g, "lucky", 12)
    from . import lex_compose as COMPOSE
    g.emit(g.narr.pick(COMPOSE.RING, "ring") + " (Luck for half a day.)")
    for c in list(t.creatures):
        if not c.boss and c is not g.combat:
            t.creatures.remove(c)
            g.emit(f"The {c.species['name']} flinches at the sound and bolts.")


def s_hidden_door(g, f, sec):
    w, p = g.world, g.player
    gold = g.rng.randint(15, 40)
    p.gold += gold
    it = w.make_item(4, g.rng.choice(["weapon", "armour"]))
    p.inv.append(it)
    g.emit(f"Your fingers find a seam in the {f.noun}. You heave, and a slab grinds aside on a narrow dark space: a forgotten smuggler's hole, or a robber's. Inside: {gold} coins and {article(it.name)}.")
    S.record(g, f"You found a hidden chamber in the {f.noun}.", "find", mark=f"A slab of the {f.noun} stands askew where you opened the hidden chamber.",
             story=f"you found a robbers' hoard hidden in the {f.noun}", like=1)


SECRET = {"cache": s_cache, "old_blade": s_old_blade, "nest": s_nest, "healing": s_healing, "bad_water": s_bad_water, "fairy": s_fairy,
          "wishing": s_wishing, "vision": s_vision, "raven": s_raven, "ghost": s_ghost, "wisp": s_wisp, "hermit": s_hermit,
          "cursed_stone": s_cursed_stone, "magpie": s_magpie, "magpie_nest": s_magpie_nest, "slip": s_slip, "stuck": s_stuck, "bees": s_bees,
          "badger": s_badger, "keepsake": s_keepsake, "letter": s_letter, "bones": s_bones, "snared": s_snared, "clue": s_clue, "echo": s_echo,
          "chalk_walk": s_chalk_walk, "hot_bath": s_hot_bath, "ringing": s_ringing, "hidden_door": s_hidden_door,
          "heirloom": lambda g, f, sec: __import__("rpg.living", fromlist=["x"]).heirloom_found(g, f, sec),
          "plot": lambda g, f, sec: __import__("rpg.plots", fromlist=["x"]).searched(g, f, sec)}


def offer(g, f, it):
    """`give X to <landmark>`: leave an offering."""
    sec = (f.state or {}).get("secret")
    g.player.inv.remove(it)
    if it is g.player.weapon:
        g.player.weapon = None
    if it is g.player.armour:
        g.player.armour = None
    if sec and not sec["found"] and sec["key"] in ("fairy", "wishing", "ghost", "hermit", "vision") and cond_met(g.world, sec.get("cond")):
        sec["found"] = True
        S.add_buff(g, "lucky", 24)
        g.emit(f"You leave the {it.name} at the {f.noun}. When you look again it is gone, and the air smells of rain and honey. (Luck for a day.)")
        return
    g.emit(g.narr.pick([f"You leave the {it.name} at the {f.noun} as an offering. Nothing happens - that you can see.",
                        f"You set the {it.name} down at the {f.noun}. Perhaps someone, or something, will be glad of it."]))
