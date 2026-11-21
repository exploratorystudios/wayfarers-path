"""Village troubles: thirteen kinds, each told many ways, rotated so they don't repeat.

A village gets at most one trouble at a time. Troubles wait for you: they never
fail or get worse while you're away. Kinds:

  beast     something is taking the animals: kill it
  fever     a sickness in the houses: bring a healing herb
  lost      someone hasn't come home: find them, bring them back
  haunting  something dead walks at night: put it down
  heirloom  something precious was stolen: find it, return it
  well      the water's gone bad: find what's fouling it
  strayed   an animal has wandered off: find it, lead it home
  letter    a letter or parcel needs carrying to another village
  supplies  the village needs something a trader sells
  wedding   a wedding wants a gift
  blight    the crops are failing: bring a charm or holy water
  feud      two neighbours at each other's throats: take a side, or make peace
  labour    hands needed: harvest, lambing, haymaking, storm repairs

Which kind comes next leans away from what's been seen lately and toward what
you haven't met yet.
"""
from . import story as S
from .textgen import article, cap

# kind: weight, who asks (role preferred), openings, later lines (the village a few days on)
KINDS = {
    "beast": (3, "folk",
              ["Something has been taking sheep from the folds at night. Folk walk in pairs, and look over their shoulders.",
               "A hurdle by the lane is smashed and stained dark; something big got at the animals.",
               "A dog was found torn open by the pond this morning. The other dogs won't go near it.",
               "There are tracks in the mud by the byre, bigger than any dog's, and a calf missing.",
               "Folk are bringing the goats in at noon, and nailing the byre doors shut."],
              ["The sheep are penned every night now, and men sit up with them, yawning, with pitchforks.",
               "Children have been told not to go past the last house. Nobody says why.",
               "Someone has hung a wolf-charm over the fold gate. It hasn't helped."]),
    "fever": (2, "folk",
              ["A fever has gone through the houses. Doors are shut, and there's a smell of burnt herbs on the air.",
               "Somebody is coughing behind every other door.",
               "A sweating sickness is in the village; the well is busy with folk fetching cold water for the sick.",
               "The children have the spotted fever, and their mothers look half-dead from sitting up."],
              ["The fever lingers. Those on their feet look grey and tired from nursing the rest.",
               "A woman hurries past with an armful of linen, not stopping to look at you.",
               "Straw has been laid in the lane outside one house, to quiet the carts."]),
    "lost": (2, "folk",
             ["A knot of folk stand at the edge of the village calling a name into the wild, and getting no answer.",
              "Someone hasn't come home. You hear their name called, again and again.",
              "A mother stands at the last gate with a lantern, though it's broad day.",
              "Men are being split into search parties by the green, arguing over which way to go."],
             ["A lamp has been set in a window to guide the lost one home. It burns day and night.",
              "The searchers have come back with nothing. They are going out again tomorrow.",
              "Nobody says the word 'drowned', but you can see them thinking it."]),
    "haunting": (2, "elder",
                 ["Folk say something walks the lanes after dark. Salt lines every doorstep.",
                  "Every door has a sprig of rowan nailed over it, and the shutters are closed early.",
                  "The church bell rang itself at midnight, folk say, and something answered from the fields.",
                  "Iron nails have been driven into every threshold, and nobody will say why."],
                 ["No one goes out after dark now, not even for the privy.", "Someone has painted eyes on the shutters to watch for it.",
                  "The dogs howl every night, all at once, and then stop all at once."]),
    "heirloom": (2, "elder",
                 ["The village is in uproar: the {thing} has been stolen in the night.",
                  "Something precious has gone missing from the village, and everyone is looking at everyone else.",
                  "There's shouting on the green: the {thing} is gone, and someone is getting blamed for it."],
                 ["They have searched every house twice. It is not in the village.", "Folk are still arguing over who took it.",
                  "Two families aren't speaking over the theft. It's spoiling everything."]),
    "well": (2, "folk",
             ["The water's gone bad. People are fetching it from a long way off, and grumbling.",
              "A sign on the well says DO NOT DRINK, in letters a child could read.",
              "The water comes up brown and smelling of rot. Three folk were sick from it.",
              "The geese won't drink from the pond, and now nobody else will either."],
             ["The village is getting by on rainwater and ale. The ale is holding out better.", "Folk queue at a rain-barrel with jugs.",
              "Somebody has started boiling everything twice, just in case."]),
    "strayed": (3, "folk",
                ["Somebody's {animal} has got out and wandered off into the wild, and its owner is beside {self}.",
                 "There's a broken hurdle by the lane and an empty pen behind it: the {animal} is gone.",
                 "A {owner_job} is stamping about the village, swearing at a gap in a hedge. The {animal} is out."],
                ["The gap in the hedge has been mended, too late.", "The {animal}'s owner keeps looking off toward the wild."]),
    "letter": (3, "any",
               ["Someone here has a letter that needs carrying, and no one going that way.",
                "A parcel sits waiting on a windowsill, addressed to someone in another village.",
                "There's talk of news that needs taking to another village - and nobody wants to walk that far."],
               ["The parcel is still waiting.", "Nobody has gone that way yet."]),
    "supplies": (3, "any",
                 ["The village is short of something it can't make for itself.",
                  "Folk are making do without: {need_why}.",
                  "Someone is asking every traveller the same thing: has anyone got {a_need}?"],
                 ["They're still making do.", "No trader has come through with what they need."]),
    "wedding": (2, "any",
                ["There's a wedding in a few days, and the whole village is busy with it.",
                 "Bunting is going up and there's baking on every hearth: a wedding is coming.",
                 "Two families are joining, and everyone's talking about it, and about the gifts."],
                ["The wedding preparations go on.", "Somebody is practising a fiddle tune, badly, over and over."]),
    "blight": (2, "elder",
               ["Something has got into the fields: the crop is blackening on the stalk, and folk say it's a curse.",
                "The wheat has come up grey and twisted. The old people are muttering about ill-wishing.",
                "There's a blight in the orchards; the fruit rots before it ripens."],
               ["The blight is still spreading, row by row.", "Someone has buried an egg at the field's corner, against the curse."]),
    "feud": (2, "any",
             ["Two neighbours here are at each other's throats over a boundary stone, and the whole village has taken sides.",
              "There's a quarrel in the village - about a pig, or a debt, or a wife, depending who you ask - and it's turning ugly.",
              "Raised voices on the green: two households have fallen out, and fists are being made."],
             ["The feud simmers on.", "The two families walk the long way round to avoid each other."]),
    "labour": (3, "folk",
               ["The village needs every pair of hands it can get: {work_what}.",
                "Everyone who can stand is out working: {work_what}. They look exhausted.",
                "A shout goes up as you arrive - another pair of hands! - {work_what}."],
               ["The work goes on, slowly.", "They're still short of hands."]),
}
SEASON_WORK = {
    "spring": ["the lambing has come all at once", "the ploughing is behind and the rain is coming", "a flood has broken the bank of the mill-leat"],
    "summer": ["the hay has to be in before the weather breaks", "the sheep need shearing and the shearers haven't come", "a barn is to be raised before harvest"],
    "autumn": ["the harvest has to be in before the storms", "the apples are falling faster than anyone can pick them", "the turves have to be cut and stacked for winter"],
    "winter": ["a storm has torn the thatch off half the roofs", "the snow has buried the sheep on the fell and they must be dug out",
               "the firewood is running low and the copse needs felling"],
}
HEIRLOOMS = ["silver bell from the moot-stone", "old copper cup of the village", "carved oak saint from the chapel", "brass key to the tithe barn",
             "bridal crown of braided straw and silver", "headman's chain of office", "great horn that calls the village to moot",
             "embroidered banner from the hall", "pewter christening bowl", "iron-bound book of village rights", "old sword that hangs above the hearth",
             "silver-mounted drinking horn", "carved boundary-staff", "bronze weathercock off the chapel roof"]
CULPRITS = ["Somebody saw a magpie, or a thief, or both, heading {d}.", "There were small, clawed prints in the dust, heading {d}.",
            "A pedlar was through yesterday and left in a hurry, {d}.", "Children were dared to take it, folk think - they ran off {d}.",
            "Something with a long shadow was seen slinking off {d} before dawn."]
ANIMALS = ["brindled cow", "old ram", "goat", "pony", "best sow", "geese", "plough-ox", "nanny goat and her kid", "donkey", "black heifer"]
NEEDS = [  # (item name or None, any_kind, a_need, why)
    ("whetstone", None, "a whetstone", "the smith's stone cracked, and every blade in the village is going dull"),
    ("flask of holy water", None, "a flask of holy water", "there's a burying soon, and no priest to bless the ground"),
    ("bundle of beeswax candles", None, "beeswax candles", "there's a vigil to keep for the dead, and only rushlights to keep it by"),
    ("antidote", None, "an antidote", "a child was bitten by an adder in the long grass"),
    (None, "potion", "a healing draught", "the miller fell from the loft and won't wake properly"),
    ("draught of strength", None, "a draught of strength", "the strongest man in the village is laid up, and the millstone needs shifting"),
    ("smoke pot", None, "a smoke pot", "there's a wild swarm in the chapel roof, and they need smoking out"),
]
LETTERS = [("sealed letter", "a letter"), ("small wrapped parcel", "a parcel"), ("knotted cord message", "a knotted-cord message"),
           ("bundle of seed-corn", "a bundle of seed-corn"), ("bolt of dyed wool", "a bolt of dyed wool")]
BLIGHT_CURES = ["rowan cross", "flask of holy water", "witch-stone"]

TITLES = {
    "beast": ["The {what} near {village}", "A beast at the folds of {village}", "What's taking {village}'s sheep"],
    "fever": ["Fever in {village}", "Sickness at {village}", "A cure for {village}"],
    "lost": ["{who} is lost", "Searching for {who}", "Where is {who}?"],
    "haunting": ["The {what} that walks at {village}", "Lay the dead of {village}", "Night terrors at {village}"],
    "heirloom": ["The stolen {thing}", "{village}'s lost {thing}", "Who took the {thing}?"],
    "well": ["Foul water at {village}", "The bad water of {village}", "What's in the water?"],
    "strayed": ["The strayed {animal}", "{owner}'s {animal}", "After the {animal}"],
    "letter": ["{a_thing} for {recipient}", "A message to {rvillage}", "Carry it to {recipient}"],
    "supplies": ["{a_need_cap} for {village}", "What {village} needs", "Fetching {a_need}"],
    "wedding": ["A gift for the wedding", "Wedding at {village}", "Something for the bride and groom"],
    "blight": ["The blight at {village}", "The ill-wished fields", "Lift the blight"],
}
ASKS = {
    "beast": ["\"There's a beast out there taking our sheep. It lairs {d}, we think. Will you deal with it?\"",
              "\"We've lost three ewes and a dog to it. It's {d}, somewhere. I'd pay to see it dead.\"",
              "\"You've a weapon. We've pitchforks. It's {d} - a {what}, by the tracks. Help us?\""],
    "fever": ["\"The fever's in half the houses. If you come across any healing herbs - anything - bring them here. Please.\"",
              "\"Herbs. Any healing herb. Our wise-woman's run out, and the children are burning up.\"",
              "\"If you can find something green and bitter that eases a fever, bring it. I'll see you're paid.\""],
    "lost": ["\"{who} went out and didn't come back. Somewhere {d}, we think. Will you look?\"",
             "\"{who} went {why}, and that was yesterday. {d_cap}, maybe. Please - you know the wild better than us.\"",
             "\"It's {who}. Gone since dawn, {d}. We've looked till we're dropping.\""],
    "haunting": ["\"Something comes up from {d} at night. It isn't alive. Can you put it down?\"",
                 "\"There's a dead thing walking, {d}. It came to my window. Please.\"",
                 "\"Salt and rowan aren't holding it. It's out {d}. You look like you've seen worse.\""],
    "heirloom": ["\"Our {thing} - stolen! {culprit} Find it?\"", "\"The {thing} is gone. {culprit} We'll never hear the end of it if it's lost.\""],
    "well": ["\"The water's gone foul. It comes down from the {noun} {d}. Something must be in it. Would you look?\"",
             "\"Something's got into the {noun}, {d}. The water stinks. Would you see what?\""],
    "strayed": ["\"My {animal}'s got out. It'll be {d}, if the wolves haven't had it. Would you bring it back?\"",
                "\"Have you seen a {animal}? It's wandered off {d}. I can't leave the others to look.\""],
    "letter": ["\"Would you carry {a_thing} to {recipient} in {rvillage}? It's {rdir}. I'd go myself, but…\"",
               "\"You're travelling. {recipient} in {rvillage} is waiting on {a_thing}. Take it?\""],
    "supplies": ["\"We need {a_need} - {need_why}. Any trader in the bigger places might have one. Would you fetch it?\"",
                 "\"If you come by {a_need}, bring it here. {need_why_cap}.\""],
    "wedding": ["\"My {kin} is getting wed, and we've nothing fine to give. If you come by a trinket - something pretty - would you bring it?\"",
                "\"A gift for the wedding, that's all I ask. Something nice. A ring, a brooch, a comb. I'll pay you back.\""],
    "blight": ["\"The fields are ill-wished. The old cure is a rowan cross, or holy water on the furrows - or a hag-stone, if you can find one. Bring one?\"",
               "\"Bring me something to lift a curse - a rowan cross, holy water, a witch-stone. Anything.\""],
}
LOST_WHY = ["after a strayed goat", "berrying", "to the old ruin on a dare", "to cut withies by the water", "to check the traps", "after a dog that ran off"]
FOUND_LOST = ["You find {who} at last - cold, hungry, with a twisted ankle, sheltering as best {he} can. {he_cap} nearly weeps at the sight of you.",
              "{who} is up a tree, of all places, and has been since something big went by in the night. {he_cap} climbs down shaking.",
              "You find {who} in a ditch, soaked and shivering, with a gash on {his} leg and a very sorry look.",
              "{who} is sitting by a dead fire, quite calm, and says {he} knew someone would come. {his_cap} feet are bloody from walking."]
FOUND_STRAYED = ["You find the {animal} grazing peacefully in a hollow as if nothing had happened.",
                 "The {animal} is tangled in brambles and very glad, for once, to see a person.",
                 "The {animal} has found a patch of sweet grass and is in no hurry to leave it."]
FOUND_WELL = ["At the {noun} you find the cause: a dead sheep, bloated and stinking, wedged in the water. It takes you a foul half-hour to haul it out and drag it well away.",
              "A rotten tree has come down into the {noun}, and the water's backing up green behind it. You lever it free with a branch and a lot of swearing.",
              "Someone has been dumping a tanner's waste upstream of the {noun}. You clear what you can and scatter the rest.",
              "A drowned badger has fouled the {noun}. You fish it out with a stick, holding your breath."]


def wild_near(g, v, lo, hi):
    w = g.world
    cands = [p for p in w.land if lo <= abs(p[0] - v[0]) + abs(p[1] - v[1]) <= hi and not w.tiles[p].site and p != g.pos]
    return g.rng.choice(cands) if cands else None


def choose_kind(g, v):
    """Lean away from recent troubles and toward kinds you haven't met yet."""
    w = g.world
    recent = getattr(w, "trouble_log", [])[-5:]
    active = {w.tiles[x].site["trouble"]["kind"] for x in w.villages if (w.tiles[x].site or {}).get("trouble")}
    seen = getattr(w, "troubles_seen", set())
    kinds, weights = [], []
    for k, (wt, *_rest) in KINDS.items():
        if k == "letter" and len(w.villages) < 2:
            continue
        if k == "haunting" and not any(s["arch"].get("undead") for s in w.species):
            continue
        f = wt
        f *= 0.15 if k in recent[-2:] else 0.4 if k in recent else 1
        f *= 0.3 if k in active else 1
        f *= 1.6 if k not in seen else 1
        kinds.append(k)
        weights.append(f)
    return g.rng.choices(kinds, weights)[0]


def start_trouble(g, v):
    w = g.world
    site = w.tiles[v].site
    kind = choose_kind(g, v)
    npcs = w.tiles[v].npcs
    pref = KINDS[kind][1]
    giver = next((n for n in npcs if n.role == pref), None) or next((n for n in npcs if n.role != "merchant"), npcs[0])
    t = dict(kind=kind, day=w.day, giver=giver.name, offered=False, accepted=False, village=site["name"])
    pick = g.rng.choice
    if kind in ("beast", "haunting"):
        if kind == "beast":
            sp = [s for s in w.species if s["key"] in ("wolf", "bear", "boar", "spider", "serpent")] or w.species
        else:
            sp = [s for s in w.species if s["arch"].get("undead")]
        spot = wild_near(g, v, 1, 3)
        if not spot or not sp:
            return
        c = w.make_creature(pick(sp), 3 if kind == "haunting" else max(2, min(4, w.day // 3 + 2)))
        c.aggressive = True
        w.tiles[spot].creatures.append(c)
        t.update(creature=c, target=spot, what=c.species["name"])
    elif kind == "lost":
        spot = wild_near(g, v, 2, 4)
        if not spot:
            return
        gender = pick(["female", "male"])
        who = w.new_name(w.culture_of(v), gender)
        t.update(target=spot, who=pick(["little ", "young ", "old ", "", "", ""]) + who, who_gender=gender, why=pick(LOST_WHY))
    elif kind == "heirloom":
        from .secrets import plant_cache
        old = g.pos
        g.pos = v
        target = plant_cache(g, 2, 5)
        g.pos = old
        if not target:
            return
        tp, tf = target
        thing = pick(HEIRLOOMS)
        tf.state["secret"].update(key="heirloom", village=v, thing=thing)
        t.update(target=tp, thing=thing, noun=tf.noun, culprit=pick(CULPRITS))
    elif kind == "well":
        waters = [(p, f) for p in w.land for f in w.tiles[p].features
                  if f.archetype in ("stream", "holy well", "pool", "dew pond", "waterfall") and 1 <= abs(p[0] - v[0]) + abs(p[1] - v[1]) <= 4]
        if waters:
            tp, tf = pick(waters)
            t.update(target=tp, noun=tf.noun)
        else:
            spot = wild_near(g, v, 1, 3)
            if not spot:
                return
            t.update(target=spot, noun="spring")
        t["found_text"] = pick(FOUND_WELL)
    elif kind == "strayed":
        spot = wild_near(g, v, 1, 3)
        if not spot:
            return
        t.update(target=spot, animal=pick(ANIMALS), owner=giver.name, owner_job=giver.job)
    elif kind == "letter":
        others = [x for x in w.villages if x != v and any(n.role != "merchant" or True for n in w.tiles[x].npcs) and w.tiles[x].npcs]
        if not others:
            return
        rv = pick(others)
        rec = pick(w.tiles[rv].npcs)
        thing, a_thing = pick(LETTERS)
        t.update(recipient=rec.name, rvillage=w.tiles[rv].site["name"], rpos=rv, thing=f"{thing} for {rec.name}", a_thing=a_thing)
    elif kind == "supplies":
        item, any_kind, a_need, why = pick(NEEDS)
        t.update(need=item, need_kind=any_kind, a_need=a_need, need_why=why)
    elif kind == "wedding":
        t.update(kin=pick(["daughter", "son", "sister", "brother", "niece", "nephew", "cousin"]))
    elif kind == "labour":
        t.update(work_what=pick(SEASON_WORK.get(w.season, SEASON_WORK["autumn"])))
    elif kind == "feud":
        folk = [n for n in npcs if n.role != "merchant" and n is not giver]      # the one asking you is a go-between, not a party
        a = folk[0].name if folk else w.new_name(w.culture_of(v), "male")
        b = folk[1].name if len(folk) > 1 else w.new_name(w.culture_of(v), pick(["female", "male"]))
        t.update(a=a, b=b, over=pick(["a boundary stone that moved in the night", "a pig that got into a garden", "a debt from three winters back",
                                       "who has the right to the spring", "a broken promise of marriage", "an insult at the harvest feast"]))
    site["trouble"] = t
    w.trouble_log = getattr(w, "trouble_log", []) + [kind]
    S.record(g, f"Trouble came to {site['name']}: {short(t)}.", "news", pos=v)


def short(t):
    k = t["kind"]
    return {"beast": "something was killing the sheep", "fever": "a fever was in the houses", "lost": f"{t.get('who', 'someone')} was lost in the wilds",
            "haunting": "something walked the lanes at night", "heirloom": f"the {t.get('thing', 'heirloom')} was stolen", "well": "the water went bad",
            "strayed": f"the {t.get('animal', 'cow')} strayed", "letter": f"{t.get('a_thing', 'a letter')} needed carrying to {t.get('rvillage', 'another village')}",
            "supplies": f"they needed {t.get('a_need', 'supplies')}", "wedding": "a wedding wanted a gift", "blight": "a blight was on the fields",
            "feud": "two neighbours were feuding", "labour": "they needed hands for the work"}.get(k, "there was trouble")


def _fill(t, text, g=None, here=None):
    """Put a trouble's facts into a line of text."""
    from .world import PRONOUNS
    d = g.narr.dir_phrase(here, t["target"]) if g and t.get("target") and here else "out there"
    rdir = g.narr.dir_phrase(here, t["rpos"]) if g and t.get("rpos") and here else "some way off"
    pr = PRONOUNS.get(t.get("who_gender"), PRONOUNS["female"])
    vals = dict(t, d=d, d_cap=cap(d), rdir=rdir, self="themselves", he=pr["he"], he_cap=cap(pr["he"]), his=pr["his"], his_cap=cap(pr["his"]),
                a_need_cap=cap(t.get("a_need", "")), need_why_cap=cap(t.get("need_why", "")), a_thing=t.get("a_thing", "a letter"),
                village=t.get("village", "the village"))
    vals["culprit"] = (t.get("culprit") or "").replace("{d}", d)
    out = text
    for k, v in vals.items():
        if isinstance(v, str):
            out = out.replace("{" + k + "}", v)
    return out


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
    _, _, opening, later = KINDS.get(t["kind"], KINDS["beast"])
    lines = later if w.day - t["day"] >= 3 else opening
    return [_fill(t, narr.pick(lines, f"trouble{site['name']}{t['kind']}"))]


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
    w.troubles_seen = getattr(w, "troubles_seen", set()) | {k}
    if k == "feud":
        return _feud(g, npc, t)
    if k == "labour":
        S.ask(g, f"{npc.name} waves you over. \"{cap(_fill(t, '{work_what}'))} - will you lend a hand? Half a day, no more.\"",
              [("Lend a hand (about four hours)", "trouble_labour", dict(village=g.pos, giver=npc.name)), ("Not now", "trouble_no", dict(giver=npc.name))], leave=1)
        return True
    ask = _fill(t, g.rng.choice(ASKS[k]), g, g.pos)
    S.ask(g, f"{npc.name} catches your sleeve. {ask}",
          [("Agree to help", "trouble_yes", dict(village=g.pos, giver=npc.name)), ("Not now", "trouble_no", dict(giver=npc.name))], leave=1)
    return True


def _reward(g, t, name):
    from . import arts as ARTS
    return dict(gold=g.rng.randint(15, 35), xp=25, like=4, village_like=2, **({"item": "book", "danger": 3} if g.rng.random() < 0.35 else {}),
                chronicle=f"You helped {name}: {short(t)}.", story=f"you helped {name} when {short(t)}", story_like=3)


def _title(g, t):
    return _fill(t, g.rng.choice(TITLES[t["kind"]]))


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
    t.setdefault("village", name)
    reward = _reward(g, t, name)
    common = dict(giver=giver, source="trouble", on_done="trouble", data=dict(village=v))
    title = _title(g, t)
    if k in ("beast", "haunting"):
        what = t["creature"].species["name"]
        S.new_quest(g, "slay", title, f"Kill the {what} troubling {name}", reward, target=t["target"], creature=t["creature"], **common)
    elif k == "fever":
        q = S.new_quest(g, "bring", title, f"Bring a healing herb to {giver.name} in {name}", reward, item=None, **common)
        q["data"].update(any_kind="herb", done_text=f"{giver.name} takes the herb and is gone into a house before you can say a word. Later {giver.pronouns()['he']} comes back out, smiling for the first time in days.")
    elif k in ("lost", "strayed"):
        what = t.get("who") if k == "lost" else f"the {t['animal']}"
        S.new_quest(g, "find", title, f"Search the wilds for {what}", reward, target=t["target"], **common)
    elif k == "heirloom":
        S.new_quest(g, "find", title, f"Find the {t['thing']} - the trail leads to the {t['noun']}", reward, target=t["target"],
                    giver=giver, source="trouble", on_done=None, data=dict(village=v, noun=t["noun"], search=True, heirloom=True))
    elif k == "well":
        S.new_quest(g, "find", title, f"Find what is fouling the water at the {t['noun']}", reward, target=t["target"], **common)
    elif k == "letter":
        from .world import Item
        rec = S.find_npc(w, t["recipient"])
        it = Item("token", t["thing"], value=0, facts=dict(material="cloth and string", glow="someone else's business"))
        g.player.inv.append(it)
        q = S.new_quest(g, "bring", title, f"Carry the {t['thing'].split(' for ')[0]} to {t['recipient']} in {t['rvillage']}",
                        dict(reward, gold=g.rng.randint(8, 20)), item=t["thing"], giver=rec, source="trouble", on_done="trouble", data=dict(village=v))
        q["data"]["done_text"] = (f"{t['recipient']} takes it, reads the hand on the outside, and smiles. \"From {name}! I'd given up.\"")
        g.emit(f"(You take {t['a_thing']} for {t['recipient']}.)")
    elif k == "supplies":
        q = S.new_quest(g, "bring", title, f"Bring {t['a_need']} to {giver.name} in {name}", reward, item=t.get("need"), **common)
        if t.get("need_kind"):
            q["data"]["any_kind"] = t["need_kind"]
        q["data"]["done_text"] = f"{giver.name} takes the {{thing}} with real relief. \"You don't know what this means.\""
    elif k == "wedding":
        q = S.new_quest(g, "bring", title, f"Bring a trinket - a ring, a brooch, something fine - to {giver.name} in {name}", reward, item=None, **common)
        q["data"].update(any_kind="trinket", done_text=f"{giver.name} turns the {{thing}} over in the light. \"Oh, that's lovely. That's just right.\"")
    elif k == "blight":
        q = S.new_quest(g, "bring", title, f"Bring a rowan cross, holy water or a witch-stone to {giver.name} in {name}", reward, item=None, **common)
        q["data"].update(any_name=list(BLIGHT_CURES), done_text=f"{giver.name} takes the {{thing}} out to the fields at once. By evening the grey has stopped spreading.")
    g.emit(f"{giver.name} lets out a long breath. \"Thank you.\"")


@S.choice_handler("trouble_no")
def _trouble_no(g, d):
    g.emit(f"{d['giver']} nods, and lets go of your sleeve. \"If you change your mind…\"")


@S.choice_handler("trouble_labour")
def _trouble_labour(g, d):
    w = g.world
    v = tuple(d["village"])
    site = w.tiles[v].site
    t = site.get("trouble")
    if not t:
        return
    giver = S.find_npc(w, d["giver"])
    with g.hush():
        g.pass_time(240)
    g.emit(g.narr.pick([f"You work alongside them until your back aches and your hands are raw: {_fill(t, '{work_what}')}. By the end, it's done.",
                        f"Four hours of hard labour, shoulder to shoulder with folk who've done it all their lives. They don't say much, but they share their bread.",
                        f"It's backbreaking work, but with one more pair of hands it gets finished before dark. Someone starts singing on the way home."]))
    q = S.new_quest(g, "bring", "A hand with the work", "Lend a hand", dict(gold=g.rng.randint(6, 14), xp=20, like=3, village_like=3,
                    chronicle=f"You worked a long day for {site['name']}.", story=f"you worked shoulder to shoulder with {site['name']}", story_like=3),
                    giver=giver, source="trouble", on_done="trouble", data=dict(village=v))
    S.finish(g, q, f"{giver.name} claps you on the shoulder. \"You'll eat with us tonight, and no argument.\"" if giver else None)


def _feud(g, npc, t):
    S.ask(g, f"{npc.name} pulls you aside. \"It's {t['a']} and {t['b']} - at it again, over {t['over']}. Somebody's going to get hurt. You're a stranger; they might listen to you.\"",
          [(f"Side with {t['a']}", "trouble_feud", dict(village=g.pos, side="a")),
           (f"Side with {t['b']}", "trouble_feud", dict(village=g.pos, side="b")),
           ("Try to make peace between them", "trouble_feud", dict(village=g.pos, side="peace")),
           ("Stay out of it", "trouble_no", dict(giver=npc.name))], leave=3)
    return True


@S.choice_handler("trouble_feud")
def _trouble_feud(g, d):
    from . import arts as ARTS
    w = g.world
    v = tuple(d["village"])
    site = w.tiles[v].site
    t = site.get("trouble")
    if not t:
        return
    p = g.player
    side = d["side"]
    if side == "peace":
        chance = 0.25 + 0.1 * (ARTS.stat(p, "spirit") - 4) + 0.05 * (ARTS.stat(p, "wits") - 4)
        if g.rng.random() < chance:
            g.emit(f"You get {t['a']} and {t['b']} in the same room, and keep them there. It takes an hour, a jug of ale and a great deal of patience, "
                   f"but by the end they're grudgingly shaking hands over {t['over']}.")
            for n in w.tiles[v].npcs:
                n.like(2)
            S.record(g, f"You made peace between {t['a']} and {t['b']} at {site['name']}.", "deed", pos=v, story=f"you made peace in {site['name']}", like=3)
            g.emit("(+25 experience.)")
            for m in p.gain_xp(25):
                g.emit(m)
        else:
            g.emit(f"You try. They both turn on you instead, and you leave them to it, ears ringing. Perhaps someone steadier of spirit would have done better.")
            return
    else:
        win, lose = (t["a"], t["b"]) if side == "a" else (t["b"], t["a"])
        g.emit(f"You hear them both out, then say plainly that {win} has the right of it. {lose} storms off. {win} wrings your hand.")
        for n in w.tiles[v].npcs:
            if n.name == win:
                n.like(4)
            elif n.name == lose:
                n.like(-3)
        S.record(g, f"You took {win}'s side against {lose} at {site['name']}.", "deed", pos=v)
        p.gold += 8
        g.emit("(8 coins, pressed on you by a grateful party.)")
    site["trouble"] = None
    site["calm_until"] = w.day + 6


def found(g, q):
    """Arriving where a 'find' quest points."""
    w = g.world
    if q["data"].get("search"):
        g.emit(f"(This is the place. Search the {q['data'].get('noun', 'landmark')}.)")
        return
    v = q["data"].get("village")
    site = w.tiles[v].site if v else None
    t = site.get("trouble") if site else None
    if t and t["kind"] in ("lost", "strayed"):
        if t["kind"] == "lost":
            who = t["who"]
            g.emit(_fill(t, g.rng.choice(FOUND_LOST)))
            title, desc, done = f"Bring {who} home", f"Lead {who} back to {site['name']}", f"{who} limps into {site['name']} on your arm, and the whole village comes running."
            note = f"{who} will follow you home."
        else:
            who = f"the {t['animal']}"
            g.emit(_fill(t, g.rng.choice(FOUND_STRAYED)))
            title, desc, done = f"Lead {who} home", f"Lead {who} back to {site['name']}", f"You lead {who} back into {site['name']}. {t['owner']} runs out to meet you, half-laughing."
            note = f"{cap(who)} plods after you."
        q["kind"], q["target"] = "escort", v
        q["title"], q["desc"] = title, desc
        comp = dict(name=who)
        q["companion"] = comp
        g.companions.append(comp)
        q["data"]["done_text"] = done
        g.emit(f"(Journal: {note})")
    elif t and t["kind"] == "well":
        g.pass_time(40)
        g.emit(_fill(t, t.get("found_text") or FOUND_WELL[0]))
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
    g.emit(g.narr.pick([f"Wedged out of sight at the {f.noun} is the {sec['thing']}, along with a scatter of shiny rubbish. A magpie's work, then - or a very odd thief.",
                        f"Under a flat stone by the {f.noun}, wrapped in a rag, is the {sec['thing']}. Whoever hid it meant to come back.",
                        f"The {sec['thing']} is at the {f.noun}, half-buried, as if dropped in a hurry by someone running."]))
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
