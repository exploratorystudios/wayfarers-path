"""Inner lives: what each person carries about with them, decided once and kept.

Everyone has a few *facts*: how they stand with a neighbour (and the neighbour has their own side of
the same story), a worry, a memory tied to a real place nearby, a want, and - for those who come to
trust you - a secret. Each fact is told in *beats*: what happened, the detail that proves it, and what
they do about it. Each beat has several ways of being said, so a fact is put together piece by piece,
never pulled out whole.

Facts come out in layers. Strangers hear the surface; come back and you hear more; win their trust and
they tell you what they've told no one else.

  layer 0  anyone, any time
  layer 1  your second conversation onward, or once they like you
  layer 2  once they're friendly
  layer 3  once they'd do anything for you

Nothing here is stored at world-building time: a person's inner life is worked out the first time it's
needed, from the world's seed and their name, so it is the same every time and older saves get one too.
"""
import random

from . import names as NAMES

FESTS = ["the Mayday garlanding", "the midsummer fires", "the harvest home", "the midwinter wassail"]
KIN_PARENT = [("mother", "female"), ("father", "male"), ("grandmother", "female"), ("grandfather", "male"), ("aunt", "female"), ("uncle", "male")]
KIN_CHILD = [("son", "male"), ("daughter", "female"), ("nephew", "male"), ("niece", "female"), ("youngest", None), ("eldest", None)]
KIN_MATE = [("husband", "male"), ("wife", "female"), ("brother", "male"), ("sister", "female")]
TOOLS = ["good spade", "best saw", "ladder", "handcart", "billhook", "big copper pan", "whetstone", "pair of shears", "mattock", "auger"]
THINGS = ["a horseshoe", "a stone the size of a fist", "my thumb", "an iron key", "a spoon"]
LAYER_AT = {"cold": 0, "neutral": 1, "friendly": 2, "devoted": 3}


# The facts themselves - roles and sentence frames - live in lex_speech.py.
from .lex_speech import INCIDENTS, OWN, LEX      # noqa: E402


def _roles(r, spec):
    """Choose this person's roles for a fact, once: which knee, which remedy."""
    return {k: r.choice(v) for k, v in sorted(spec.items())}


# Something everyone knows about a person: whoever mentions it, it's the same thing. (claim, detail) beats.
QUIRKS = [
    (["{o} the {oj} keeps a jackdaw that steals spoons.", "You'll meet {o}'s jackdaw before you meet {o}.", "Mind your spoons round {o}'s [jackdaw|bird]."],
     ["Nobody's [brave enough|got the heart] to tell {ohim}.", "Half the village's spoons are in that bird's nest. We've seen them glinting.",
      "It said '[Morning|Hello|Thief]' to me once. I've not been right since."]),
    (["{o} the {oj} can tell you the weather [three days off|a week ahead|before the sky knows].", "Ask {o} if it'll rain. Go on.",
      "If you want to know the weather, [ask|watch] {o}."],
     ["Always right, too. It's [unsettling|uncanny|a bit much].", "{ohe.cap} says it's {ohis} [knees|bones|nose]. I think it's something else.",
      "We plan the [haymaking|washing|harvest] round {ohim}."]),
    (["{o} tells the best stories at the alehouse.", "Buy {o} the {oj} a drink and you'll hear a tale.", "Get {o} talking, [some night|one evening]. Just once."],
     ["And the least true. Nobody minds.", "Last time it was a [fish|pike|eel] the size of a cart. It grows every winter.",
      "{ohe.cap} once kept the whole room up till cock-crow."]),
    (["{o} came here a stranger, years back.", "{o} the {oj}'s not from {village}, not really.", "{o} isn't one of ours. Not by birth."],
     ["[Twenty|Fifteen|Thirty] years, and folk still call {ohim} the newcomer.", "Came up the road one autumn with a bundle and stayed.",
      "Never says where from. Nobody asks any more."]),
    (["{o} the {oj} has a cousin in every village from here to the hills.", "If you're lost, ask {o}. {ohe.cap}'ll have kin there.",
      "{o} is related to [half the valley|everyone|every second soul you'll meet]."],
     ["Weddings take {ohim} a month.", "{ohe.cap} sends letters by every carter.", "There's not a door between here and the hills {ohe} can't knock on."]),
    (["{o} sang at the last wedding.", "Have you heard {o} the {oj} sing?", "If {o} starts singing, [stay|sit down|don't run]."],
     ["The dogs joined in. Best night of the year.", "Folk stop in the lane to listen.", "Badly. Loudly. Every word of every verse."]),
    (["{o} the {oj} swears {ohe} saw lights on the hill at midsummer.", "{o} sees things. Lights, mostly.", "Ask {o} about the lights on the hill."],
     ["I believe {ohim}. Most don't.", "[Blue|Green|Pale] ones, {ohe} says, moving against the wind.", "{ohe.cap} goes up there every year now, to look."]),
    (["{o} the {oj} will feed you if you let {ohim}.", "Never go to {o}'s door hungry. Or do.", "You won't leave {o}'s house hungry. You won't be let."],
     ["Let {ohim}. You'll not regret it.", "There's always a pot on. Always.", "You come away with [bread|a pie|half a cheese] under your arm whether you wanted it or not."]),
    (["{o} the {oj} grows the biggest marrows in the valley.", "Don't mention marrows to {o}.", "{o} and {ohis} marrows. [Lord.|Don't get {ohim} started.]"],
     ["Sits up with them at night, in case of slugs. Or neighbours.", "Won the ribbon at {fest} [four|five|six] years running.", "{ohe.cap} talks to them. They seem to like it."]),
    (["{o} the {oj} has never once been late.", "You could set the sun by {o}.", "{o} is the most punctual soul [in {village}|alive|I know]."],
     ["Not once. Not in thirty years.", "Up before the birds, every morning, winter or summer.", "It's a bit much, if I'm honest."]),
]


def quirk_of(w, npc):
    return _rng(w, "quirk", npc.name, npc.home).randrange(len(QUIRKS))


# what someone asks you back, after telling you something of theirs
ASK_BACK = {
    "sick_kin": ["Have you anyone at home yourself?", "You've not got a cure in that pack, I suppose?"],
    "child_going": ["Did you leave someone, to be out here?", "Is it so much better, out there?"],
    "debt": ["You'll not be going to {creditor_v}, will you?"],
    "place_memory": ["Have you been out that way?", "Is it still the same out there?"],
    "winter": ["Do they get winters like that where you're from?"],
    "saw_beast": ["You've not seen it yourself? Out there?"],
    "sea": ["Have you seen it? The sea?", "Is it true it never stops?"],
    "dog": ["Do you keep a dog, on the road?"],
    "leaving": ["What's it like, out there? Really?"],
    "lean_year": ["How's trade where you've been?"],
    "tie": ["You've met {o}? What did you make of {ohim}?", "You'll not repeat that to {o}?"],
}

# --------------------------------------------------------------------------------------------- voice
VOICES = {
    #             openers                                         clip  ramble hedge trail stammer ask  exclaim
    "warm":       (["Oh, ", "Well, ", "Now, ", "Ah, "],             0.0, 0.45, 0.10, 0.05, 0.0, 0.40, 0.1),
    "cheerful":   (["Ha! ", "Oh, ", "Well! ", "Here's a thing: "],  0.0, 0.50, 0.00, 0.00, 0.0, 0.40, 0.4),
    "gruff":      (["Hm. ", "Look. ", "Right. ", "Aye. "],          0.6, 0.00, 0.00, 0.00, 0.0, 0.05, 0.0),
    "melancholy": (["Ah. ", "Well. ", "You know, "],               0.1, 0.20, 0.30, 0.22, 0.0, 0.15, 0.0),
    "suspicious": (["Listen. ", "Mind, ", "Between us, "],          0.4, 0.00, 0.10, 0.10, 0.0, 0.20, 0.0),
    "nervous":    (["Oh - ", "Sorry - ", "Um. ", "Well - "],         0.0, 0.25, 0.40, 0.15, 0.35, 0.20, 0.0),
    "dreamy":     (["You know, ", "Oh, ", "Funny thing - "],         0.0, 0.35, 0.20, 0.18, 0.0, 0.30, 0.0),
    "shrewd":     (["Now, ", "Between us, ", "Mark this: ", "Here's the thing. "], 0.2, 0.15, 0.10, 0.00, 0.0, 0.25, 0.0),
}
HEDGES = ["I think ", "seems to me ", "if you ask me, ", "I'd say "]
ASIDES = {"warm": ["- bless {ohim} -", "- and I say this kindly -"], "cheerful": ["- you'll laugh -", "- swear on my hat -"],
          "dreamy": ["- the swallows knew, I think -", "- it was a blue sort of day -"], "nervous": ["- I shouldn't say -", "- sorry -"],
          "shrewd": ["- and this is worth knowing -", "- mark it -"], "melancholy": ["- well -", "- these things happen -"]}
OATHS = ["by the wells", "spirits keep us", "on my mother's bones", "by the old stones", "saints and stones", "by the black oak", "by fire and frost",
         "salt and iron", "bless the bees"]
SAYINGS = ["Water finds its own level.", "What the frost takes, the frost keeps.", "Old rope holds.", "The crow always knows.", "It all comes out in the wash.",
           "There's no hurry in a graveyard.", "A creaking gate hangs longest.", "You can't hurry a pear.", "Every dog has its mud.", "Tomorrow's a long word.",
           "Bread first, then talk.", "Mist in the hollow, fine to follow.", "No use crying at a closed door.", "The wind doesn't argue.",
           "Short roads have long mud.", "Mend the roof when it's dry."]
ADDRESS = {"warm": ["love", "my dear", "pet"], "cheerful": ["friend", "traveller", "my friend"], "gruff": ["", ""], "melancholy": ["friend", ""],
           "suspicious": ["stranger", ""], "nervous": ["", ""], "dreamy": ["wanderer", "friend"], "shrewd": ["friend", "my friend"]}
DOGNAMES = ["Bess", "Nell", "Tess", "Fly", "Moss", "Jess", "Bramble", "Smudge", "Patch", "Gyp"]


def _rng(w, *salt):
    return random.Random(":".join(str(s) for s in (w.seed,) + salt))


def _name(w, r, home, gender):
    gender = gender or r.choice(["female", "male"])
    try:
        return NAMES.gen().generate(r, w.culture_of(home), gender), gender
    except (OSError, ValueError, AttributeError):
        return r.choice(["Edda", "Tam", "Wenna", "Rook", "Hild", "Bran"]), gender


def _sells(n):
    from . import goods as GOODS
    return n.role == "merchant" or GOODS.sells(n)


def _ties(w, v):
    """The village's web of grudges, kindnesses and secrets, made once per village and kept on the site."""
    site = w.tiles[v].site
    if site.get("ties") is not None:
        return site["ties"]
    folk = list(w.tiles[v].npcs)
    r = _rng(w, "ties", v)
    out = []
    pairs = [(a, b) for a in folk for b in folk if a is not b]
    r.shuffle(pairs)
    used = {}
    for a, b in pairs:
        if used.get(a.name, 0) >= 2 or used.get(b.name, 0) >= 2:
            continue
        if any({a.name, b.name} == {t["a"], t["b"]} for t in out):
            continue
        kinds = [k for k, d in INCIDENTS.items()
                 if not (d.get("needs_b") == "seller" and not _sells(b)) and not (d.get("needs") == "both_sell" and not (_sells(a) and _sells(b)))]
        if not kinds:
            continue
        k = r.choice(kinds)
        if any(t["kind"] == k for t in out) and r.random() < 0.7:     # variety within a village
            continue
        out.append(dict(kind=k, a=a.name, b=b.name, tool=r.choice(TOOLS), roles=dict(_roles(r, INCIDENTS[k].get("roles", {})), fest=r.choice(FESTS))))
        used[a.name] = used.get(a.name, 0) + 1
        used[b.name] = used.get(b.name, 0) + 1
        if len(out) >= max(1, len(folk) - 1):
            break
    site["ties"] = out
    return out


def _nearby(w, home, r, used=()):
    """Real things near a village to remember: a region beyond its own, a shrine's spirit, water, another village."""
    hx, hy = home
    own = w.region_of(home)["name"]
    near = sorted((p for p in w.land if 1 <= abs(p[0] - hx) + abs(p[1] - hy) <= 6), key=lambda p: (abs(p[0] - hx) + abs(p[1] - hy), p))
    regions = list(dict.fromkeys(w.region_of(p)["name"] for p in near if w.region_of(p)["name"] != own))[:6]
    fresh = [x for x in regions if x not in used] or regions
    region = r.choice(fresh) if fresh else own
    shrines = [w.tiles[p].site["spirit"] for p in w.tiles if w.tiles[p].site and w.tiles[p].site.get("kind") == "shrine"]
    shrines.sort(key=lambda s: s)
    lake = any(w.tiles[p].biome == "lake" for p in w.tiles if abs(p[0] - hx) + abs(p[1] - hy) <= 3)
    marsh = any(w.tiles[p].biome == "marsh" for p in w.tiles if abs(p[0] - hx) + abs(p[1] - hy) <= 3)
    water = r.choice(["mere", "lake"]) if lake else "fen" if marsh else r.choice(["mill-pond", "river", "ford"])
    villages = [x for x in w.villages if x != home]
    villages.sort(key=lambda x: abs(x[0] - hx) + abs(x[1] - hy))
    far = w.tiles[r.choice(villages[:4])].site["name"] if villages else "the next valley"
    creditor_v = w.tiles[r.choice(villages[:5])].site["name"] if villages else far
    return dict(region=region, spirit=r.choice(shrines) if shrines else "the old spirit of the hill", water=water, far=far, creditor_v=creditor_v)


def of(w, npc):
    """This person's inner life: facts (each with its layer and told-flag) and voice. Made once, then kept.
    A whole village is made at once, in a fixed order, so neighbours don't share the same worry or memory."""
    got = npc.mem.get("inner")
    if got is not None:
        return got
    folk = sorted(w.tiles[npc.home].npcs, key=lambda x: x.name) if npc.home in w.tiles else []
    if npc not in folk:
        folk.append(npc)
    used = set()
    for x in folk:
        if x.mem.get("inner"):
            i = x.mem["inner"]
            used |= {f["kind"] for f in i["facts"]} | {i.get("region"), i.get("saying"), i.get("oath")}
    for x in folk:
        if not x.mem.get("inner"):
            x.mem["inner"] = _make(w, x, used)
    return npc.mem["inner"]


def _make(w, npc, used):
    r = _rng(w, "inner", npc.name, npc.home)
    site = w.tiles[npc.home].site or {}
    near = _nearby(w, npc.home, r, used)
    used.add(near["region"])
    facts = []
    # ties with neighbours: both sides of each story
    for t in _ties(w, npc.home) if site else []:
        if npc.name not in (t["a"], t["b"]):
            continue
        side = "a" if t["a"] == npc.name else "b"
        other = t["b"] if side == "a" else t["a"]
        layer = INCIDENTS[t["kind"]]["layers"][0 if side == "a" else 1]
        facts.append(dict(kind="tie", inc=t["kind"], side=side, other=other, tool=t["tool"], layer=layer, told=False, roles=dict(t.get("roles", {}))))
    # a bit of gossip about someone they've no particular tie with: what everyone knows about them
    tied = {f["other"] for f in facts}
    loose = sorted((x for x in w.tiles[npc.home].npcs if x is not npc and x.name not in tied), key=lambda x: x.name)
    if loose:
        facts.append(dict(kind="gossip", other=r.choice(loose).name, layer=0, told=False))
    # their own: one worry or hardship, one memory, one want, one secret, one deep thing
    groups = [["sick_kin", "child_going", "lean_year", "old_hurt"], ["place_memory", "winter", "saw_beast", "dance"],
              ["sea", "slate", "dog"], ["cant_read", "offerings", "leaving", "broke_it", "debt"], ["promised"]]
    for grp in groups:
        if grp == ["promised"] and r.random() < 0.5:
            continue
        if npc.age_band == "young":
            grp = [k for k in grp if k not in ("promised", "old_hurt")] or grp
        k = r.choice([k for k in grp if k not in used] or grp)
        used.add(k)
        facts.append(dict(kind=k, layer=OWN[k]["layer"], told=False, roles=_roles(r, OWN[k]["roles"])))
    # the people in their life
    if any(f["kind"] in ("child_going",) for f in facts):
        kin, g = r.choice(KIN_CHILD)
    elif any(f["kind"] in ("dance", "promised") for f in facts):
        kin, g = r.choice(KIN_PARENT)
    else:
        kin, g = r.choice(KIN_PARENT + KIN_MATE)
    kname, kg = _name(w, r, npc.home, g)
    lover, lg = _name(w, r, npc.home, None)
    creditor, _ = _name(w, r, npc.home, None)
    from . import lex_entities as E
    jobs2 = [j for j in E.OCCUPATIONS.get("folk", []) if j != npc.job and j != "midwife"] or ["smith"]
    inner = dict(
        facts=facts,
        kin=kin, kname=kname, kgender=kg, lover=lover, lgender=lg, creditor=f"{creditor} the moneylender" if r.random() < 0.5 else creditor,
        job2=r.choice(jobs2), dogname=r.choice(DOGNAMES), **near,
        fest=r.choice(FESTS), pkin=r.choice(["mother", "father", "grandmother", "grandfather"]),
        oath=r.choice([x for x in OATHS if x not in used] or OATHS), saying=r.choice([x for x in SAYINGS if x not in used] or SAYINGS),
        address=r.choice(ADDRESS.get(npc.demeanour, ["friend"])),
        # a little of everyone's own: one stays chattier, one terser, than their temperament
        bend=r.choice([-0.15, 0.0, 0.0, 0.15]),
        voice=npc.demeanour if npc.demeanour in VOICES else "warm",
        visits=0,
    )
    used |= {inner["oath"], inner["saying"]}
    return inner


def allowed_layer(npc):
    lay = LAYER_AT.get(npc.tier, 1)
    if npc.mem.get("met", 0) >= 1:
        lay = max(lay, 1)
    return lay


def next_fact(w, npc):
    """The next thing they're ready to tell you, or None: surface first, deeper as trust grows."""
    inner = of(w, npc)
    lay = allowed_layer(npc)
    ready = [f for f in inner["facts"] if not f["told"] and f["layer"] <= lay]
    if not ready:
        return None
    ready.sort(key=lambda f: (f["layer"], f["kind"] != "tie"))
    # mostly the shallowest; now and then a deeper one ahead of its turn
    r = _rng(w, "pick", npc.name, w.day, len([f for f in inner["facts"] if f["told"]]))
    return ready[0] if r.random() < 0.7 or len(ready) == 1 else ready[1]


def beats_for(fact, w=None, other=None):
    if fact["kind"] == "tie":
        return INCIDENTS[fact["inc"]][fact["side"]]
    if fact["kind"] == "gossip":
        return list(QUIRKS[quirk_of(w, other)])
    return OWN[fact["kind"]]["beats"]
