"""Crafting new arts, each craft in its own school only (no mixing schools).

Spellcraft (arcane): an element + a shape (+ a twist) -> a new spell. You know
  the runes of the spells you've learned: Firebolt teaches fire and bolt, Ward
  teaches ward, Fear teaches shadow, and so on. Costs a pot of ink and hours.
Prayer composing (divine): a virtue + a form (+ a twist) -> a new prayer, from
  the prayers you know. Costs beeswax candles and hours.
Technique honing (martial, wild, cant): use a technique often enough and you can
  hone it into one of two refinements. With the school's stat high enough you can
  join two of its techniques into a combination.

Every crafted art is ordinary data for arts.run(), registered under a short
command word and kept on the player (p.crafted), so it survives saving.
"""
from .textgen import cap
from . import ui


def _typed(cmd):
    """ ('hone bash ringing') after an option in the terminal; nothing on the web, where it's a menu choice."""
    return "" if ui.web else f" ('{cmd}')"


def _named(key):
    """The command for a newly made art, in the terminal; on the web it simply appears in its menu."""
    return "" if ui.web else f" Command: '{key}'."


# ------------------------------------------------------------------ spellcraft and composing
WEAVES = {
    "arcane": dict(
        craft="Spellcraft", verb="craft", material="pot of oak-gall ink", hours=3,
        primary={   # element: fx it adds, words
            "fire":   dict(fx=[("bonus", 2)], word="Fire", lingering=("dot", (3, 3, "burns"))),
            "frost":  dict(fx=[("weaken", 1)], word="Frost", lingering=("dot", (2, 3, "shivers, rimed with frost"))),
            "storm":  dict(fx=[("stun", 0.35)], word="Storm", lingering=("stun", 0.2)),
            "stone":  dict(fx=[("expose", 2)], word="Stone", lingering=("expose", 1)),
            "shadow": dict(fx=[("flee", dict(turns=2, base=0.5))], word="Shadow", lingering=("dot", (2, 3, "is gnawed by shadow"))),
        },
        shape={
            "bolt":  dict(fx=[("dmg", dict(base=4, per=1, pierce=True))], cost=2, circle=1, word="Bolt", target=True),
            "burst": dict(fx=[("dmg", dict(base=3, per=1, pierce=True)), ("stun", 0.15)], cost=3, circle=2, word="Burst", target=True),
            "lance": dict(fx=[("dmg", dict(base=8, per=2, pierce=True))], cost=4, circle=3, word="Lance", target=True),
            "ward":  dict(fx=[("ward", dict(base=6, per=2))], cost=2, circle=1, word="Ward", self_only=True),
            "veil":  dict(fx=[("escape", 2)], cost=3, circle=3, word="Veil", combat_only=True, self_only=True),
        },
        twist={
            "lingering": dict(cost=1, circle=1, word="Lingering"),
            "twin":      dict(cost=2, circle=1, word="Twinned"),
            "quiet":     dict(cost=-1, circle=0, word="Quiet"),
            "great":     dict(cost=2, circle=1, word="Great"),
        },
        sources={"firebolt": ["fire", "bolt"], "frost": ["frost", "bolt"], "thunder": ["storm", "burst"], "lance": ["fire", "lance", "lingering"],
                 "ward": ["ward"], "blink": ["veil"], "fear": ["shadow"], "unmake": ["stone", "great"], "farsight": ["quiet"]},
        say=["You shape the working the way you wrote it out: {name} leaps from your hands at {the_c}.",
             "The new spell comes easily now - {name}, straight into {the_c}'s {part}.",
             "You speak your own words, and {name} answers."],
        say_self=["You weave {name} around yourself, just as you worked it out by candlelight.", "Your own spell, {name}, settles about you."],
    ),
    "divine": dict(
        craft="Prayer composing", verb="compose", material="bundle of beeswax candles", hours=2,
        primary={   # virtue
            "mercy": dict(fx=[("heal", dict(base=7, per=2))], word="Mercy", lingering=("heal", dict(base=4, per=1)), self_only=True),
            "wrath": dict(fx=[("dmg", dict(base=4, per=1, pierce=True, undead=2))], word="Wrath", lingering=("dot", (2, 3, "smoulders with holy fire")), target=True),
            "vigil": dict(fx=[("ward", dict(base=6, per=2))], word="Vigil", lingering=("guard", 1), self_only=True),
            "light": dict(fx=[("stun", 0.5)], word="Light", lingering=("stun", 0.15), target=True),
            "peace": dict(fx=[("flee", dict(turns=2, base=0.7))], word="Peace", lingering=("flee", dict(turns=1, base=0.2)), target=True),
        },
        shape={   # form
            "word":     dict(fx=[], cost=2, circle=1, word="Word"),
            "litany":   dict(fx=[("strength", 1.6)], cost=4, circle=3, word="Litany"),
            "blessing": dict(fx=[("lasting", None)], cost=3, circle=2, word="Blessing", peace_only=True, self_only=True),
        },
        twist={
            "lasting": dict(cost=1, circle=1, word="Lasting"),
            "humble":  dict(cost=-1, circle=0, word="Humble"),
            "twinned": dict(cost=2, circle=2, word="Twinned"),
        },
        sources={"heal": ["mercy", "word"], "smite": ["wrath", "word"], "turn": ["peace"], "bless": ["blessing"], "sanctuary": ["vigil"],
                 "purify": ["mercy", "humble"], "radiance": ["light", "litany"], "miracle": ["litany", "lasting", "twinned"]},
        say=["You pray the words you wrote yourself, and {name} falls on {the_c}.", "Your own prayer - {name} - and it is answered against {the_c}."],
        say_self=["You speak {name}, your own prayer, and feel it heard.", "{name}: you wrote it by candlelight, and now it holds you up."],
    ),
}
# blessings: what a lasting form of each virtue leaves on you
BLESSING_BUFF = {"mercy": ("blessed", 12, 1), "wrath": ("strong", 12, 1), "vigil": ("warded", 12, 1), "light": ("lucky", 12, 1), "peace": ("warded", 8, 1)}


def known_parts(p, school):
    """The runes or virtues/forms you know, from the arts you have."""
    w = WEAVES[school]
    parts = set()
    for k in p.known:
        parts |= set(w["sources"].get(k, []))
    return parts


def recipes(p, school):
    """Every (primary, shape, twist, second) you could weave now, with its art spec."""
    from . import arts as ARTS
    w = WEAVES[school]
    have = known_parts(p, school)
    out = []
    for pr in sorted(have & set(w["primary"])):
        for sh in sorted(have & set(w["shape"])):
            for tw in [None] + sorted(have & set(w["twist"])):
                seconds = [None]
                if tw in ("twinned",):
                    seconds = [x for x in sorted(have & set(w["primary"])) if x > pr]     # each pair once
                    if not seconds:
                        continue
                for sec in seconds:
                    spec = build(school, pr, sh, tw, sec)
                    if spec and ARTS.circle_ok(p, school, spec["circle"]):
                        out.append((pr, sh, tw, sec, spec))
    return out


def build(school, pr, sh, tw=None, sec=None):
    """Put the parts together into an art (dict like arts.ARTS entries), or None if they don't fit."""
    w = WEAVES[school]
    P, S, T = w["primary"][pr], w["shape"][sh], (w["twist"][tw] if tw else None)
    fx = []
    mult = 1.0
    for kind, arg in S["fx"]:
        if kind == "strength":
            mult = arg
        elif kind != "lasting":
            fx.append((kind, dict(arg) if isinstance(arg, dict) else arg))
    if sh == "blessing":
        scale = 2 if tw == "lasting" else 0.5 if tw == "humble" else 1
        fx = []
        for v in [pr] + ([sec] if sec else []):
            name, hours, power = BLESSING_BUFF[v]
            if not any(a[0] == name for k, a in fx):
                fx.append(("buff", (name, max(2, int(hours * scale)), power)))
        if pr == "mercy" or sec == "mercy":
            fx.append(("heal", dict(base=4, per=1)))
    else:
        if school == "arcane" and S.get("self_only"):     # a ward or veil takes only the element's colour, and a little strength
            if sh == "ward":
                fx += [("ward_bonus", {"stone": 4, "frost": 2, "fire": 1}.get(pr, 0))] + ([("guard", 1)] if pr == "storm" else [])
        else:
            fx += [(k, dict(a) if isinstance(a, dict) else a) for k, a in P["fx"]]
        if sec:
            fx += [(k, dict(a) if isinstance(a, dict) else a) for k, a in w["primary"][sec]["fx"]]
        if tw == "lingering" or tw == "lasting":
            if S.get("self_only") and P["lingering"][0] in ("dot", "stun", "expose", "flee"):
                return None
            fx.append(P["lingering"])
        if tw == "twin":
            for kind, arg in fx:
                if kind == "dmg":
                    arg["hits"] = 2
                    arg["base"] = max(1, arg["base"] - 1)
            if not any(k == "dmg" for k, _ in fx):
                return None
        if tw == "quiet" or tw == "humble":
            for kind, arg in fx:
                if isinstance(arg, dict) and "base" in arg:
                    arg["base"] = max(1, arg["base"] - 2)
        if tw == "great":
            for kind, arg in fx:
                if isinstance(arg, dict) and "base" in arg:
                    arg["base"] += 4
        if mult != 1.0:
            for kind, arg in fx:
                if isinstance(arg, dict) and "base" in arg:
                    arg["base"] = round(arg["base"] * mult)
                    arg["per"] = round(arg.get("per", 0) * mult)
    # fold the element's flat bonus into the damage
    bonus = sum(a for k, a in fx if k == "bonus")
    fx = [(k, a) for k, a in fx if k != "bonus"]
    for k, a in fx:
        if k == "dmg":
            a["base"] += bonus
    wb = sum(a for k, a in fx if k == "ward_bonus")
    fx = [(k, a) for k, a in fx if k != "ward_bonus"]
    for k, a in fx:
        if k == "ward":
            a["base"] += wb
    targeted = any(k in ("dmg", "stun", "weaken", "expose", "dot", "flee") for k, _ in fx)
    if targeted and S.get("self_only"):
        return None
    cost = max(1, S["cost"] + (T["cost"] if T else 0) + (1 if sec else 0))
    circle = max(1, min(5, S["circle"] + (T["circle"] if T else 0) + (1 if sec else 0)))
    words = ([T["word"]] if T else []) + [P["word"]] + ([f"and {w['primary'][sec]['word']}"] if sec else []) + [S["word"]]
    if school == "arcane":
        name = " ".join(words)
    else:
        virtues = ([T["word"]] if T else []) + [P["word"]] + ([f"and {w['primary'][sec]['word']}"] if sec else [])
        name = f"{S['word']} of {' '.join(virtues)}"
    desc = describe_fx(fx)
    spec = dict(label=name, school=school, circle=circle, cost=cost, desc=desc, fx=fx, crafted=True,
                target=targeted, say=[], parts=[pr, sh, tw, sec])
    if S.get("combat_only"):
        spec["combat_only"] = True
    if S.get("peace_only") or sh == "blessing":
        spec["peace_only"] = True
    sayk = "say" if targeted else "say_self"
    spec["say"] = [s.replace("{name}", name) for s in w[sayk]]
    return spec


def describe_fx(fx):
    """A plain account of what an art does, from its effects."""
    bits = []
    for k, a in fx:
        if k == "dmg":
            hits = a.get("hits", 1)
            many = "two " if hits == 2 else "three " if hits == 3 else ""
            if a.get("weapon"):
                what = (f"{many}weapon blows" if many else "a weapon blow") + (f" harder by {a['base']}" if a.get("base") else "") + \
                       (" that slips past armour" if a.get("pierce") else "")
            else:
                what = (f"{many}strikes of " if many else "") + ("damage that ignores armour" if a.get("pierce") else "damage") + \
                       f" (about {a.get('base', 0) + a.get('per', 0)}{'+' if a.get('per') else ''}{' each' if many else ''})"
            bits.append(what + (", doubled on the dead" if a.get("undead") else ""))
        elif k == "stun":
            bits.append(f"a {'good' if a >= 0.6 else 'fair' if a >= 0.35 else 'small'} chance to stun")
        elif k == "weaken":
            bits.append("its blows weakened")
        elif k == "expose":
            bits.append("its armour cracked")
        elif k == "dot":
            bits.append(f"lingering harm ({a[0]} a turn for {a[1]} turns)")
        elif k == "flee":
            bits.append("a chance to send it fleeing")
        elif k == "heal":
            bits.append("healing" if a["base"] < 50 else "every wound closed")
        elif k == "ward":
            bits.append(f"a ward that soaks about {a['base']} damage")
        elif k == "guard":
            bits.append(f"guard for {a} blows")
        elif k == "escape":
            bits.append("an escape from the fight, hidden")
        elif k == "buff":
            from . import story as S
            bits.append(f"{S.BUFF_NAMES.get(a[0], a[0])} for {a[1]} hours")
        elif k == "ambush":
            bits.append(f"{a}x damage against anything not yet fighting you, or while hidden")
        elif k == "execute":
            bits.append("a killing stroke against the badly hurt")
        elif k == "cleanse":
            bits.append("curses and sickness lifted")
    return cap(", ".join(bits)) + "." if bits else "A small working."


def command_for(p, label):
    """A one-word command for a crafted art: its most telling word, made unique."""
    from . import classes as K
    base = "".join(ch for ch in label.lower().split()[-1] if ch.isalpha())
    first = "".join(ch for ch in label.lower().split()[0] if ch.isalpha())
    for cand in (first + base, first[:4] + base, base + str(len(p.crafted) + 1)):
        if cand not in K.ABILITIES and cand not in p.crafted:
            return cand
    return base + str(len(p.crafted) + 7)


def register(p):
    """Make a player's crafted arts usable (after creating them, or after loading a save)."""
    from . import classes as K
    from . import arts as ARTS
    for key, spec in getattr(p, "crafted", {}).items():
        ARTS.ARTS[key] = spec
        K.ABILITIES[key] = spec


def weave(g, school, rest):
    """'craft fire burst', 'compose lasting mercy word', or with nothing: what you could make."""
    from . import arts as ARTS
    from . import classes as K
    p = g.player
    ARTS.ensure(p)
    w = WEAVES[school]
    if not ARTS.literate(p, school):
        return g.emit(f"{w['craft']} needs {ARTS.SCHOOLS[school]['trait']}, and you haven't got it.")
    opts = recipes(p, school)
    if not rest:
        have = known_parts(p, school)
        if not opts:
            return g.emit(f"You know too little of the {school} art to make anything new yet. "
                          f"(Parts you know: {', '.join(sorted(have)) or 'none'}. Learn more {ARTS.SCHOOLS[school]['art']}s to learn more parts.)")
        shown = "; ".join(f"{s['label']} ({s['cost']}): {s['desc']}" for *_, s in opts[:12])
        return g.emit(f"{w['craft']}: you know {', '.join(sorted(have))}. You could make: {shown} "
                      + (f"(Use Craft › {w['craft']}… to choose one." if ui.web else f"('{w['verb']} <parts>', e.g. '{w['verb']} {' '.join(x for x in opts[0][:3] if x)}'.")
                      + f" Each takes a {w['material']} and {w['hours']} hours.)")
    words = [x.lower() for x in rest if x not in ("and", "of", "a", "an")]
    match = None
    for pr, sh, tw, sec, spec in opts:
        need = {pr, sh} | ({tw} if tw else set()) | ({sec} if sec else set())
        if need == set(words) or need == {x.rstrip("s") for x in words}:
            match = (pr, sh, tw, sec, spec)
            break
    if not match:
        unknown = [x for x in words if x not in known_parts(p, school)]
        if unknown:
            return g.emit(f"You don't know how to work '{unknown[0]}' into anything. (You know: {', '.join(sorted(known_parts(p, school)))}.)")
        return g.emit(f"Those don't go together - or not yet, for you. ('{w['verb']}' alone lists what you could make.)")
    *_, spec = match
    if any(s["label"] == spec["label"] for s in p.crafted.values()):
        return g.emit(f"You've already made {spec['label']}.")
    mat = next((it for it in p.inv if it.name == w["material"]), None)
    if mat is None:
        return g.emit(f"You'll need a {w['material']} for that. Chandlers and pedlars sell them.")
    if g.combat:
        return g.emit("Not now!")
    p.inv.remove(mat)
    with g.hush():
        g.pass_time(w["hours"] * 60)
    key = command_for(p, spec["label"])
    p.crafted[key] = spec
    p.known.append(key)
    register(p)
    g.emit(g.narr.pick([f"You spend {w['hours']} hours by candlelight, writing, crossing out and trying again. At last it holds: {spec['label']}.",
                        f"It takes {w['hours']} hours and {'every drop of the ink' if 'ink' in mat.name else 'the candles burned down to stubs'}. But it's yours now: {spec['label']}."])
           + f" ({spec['desc']} Costs {spec['cost']} {K.res_name(p)}.{_named(key)})")


# ------------------------------------------------------------------ technique honing
HONE_SCHOOLS = ("martial", "wild", "cant")
PRACTICE = 5        # uses before a technique can be honed
# technique -> two refinements: (key, label, desc, fx, extra)
HONES = {
    "bash": [("ringbash", "Ringing Bash", "A bash placed to ring the skull: damage, and a very good chance to stun.", [("dmg", dict(weapon=True, base=0, per=0)), ("stun", 0.85)], {}),
             ("shieldrush", "Shield Rush", "Drive in behind the shield: a heavy blow, and a fair chance to stun.", [("dmg", dict(weapon=True, base=4, per=1)), ("stun", 0.35)], {})],
    "guard": [("ironguard", "Iron Guard", "Your guard holds for three blows instead of two.", [("guard", 3)], dict(combat_only=True)),
              ("turnguard", "Turning Guard", "Guard two blows, and a shell of will soaks a little more.", [("guard", 2), ("ward", dict(base=4, per=1))], dict(combat_only=True))],
    "cleave": [("sunder", "Sundering Cleave", "A great blow that splits its armour too.", [("dmg", dict(weapon=True, base=3, per=1)), ("expose", 2)], {}),
               ("widecleave", "Wide Cleave", "Everything into one even greater blow.", [("dmg", dict(weapon=True, base=6, per=1))], {})],
    "disarm": [("ironbind", "Iron Bind", "Wrench its weapon or limb so it barely hurts you again.", [("dmg", dict(weapon=True, base=0, per=0)), ("weaken", 3)], {}),
               ("bindstrike", "Bind and Strike", "Bind it, then hit it while it's tangled.", [("dmg", dict(weapon=True, base=2, per=1)), ("weaken", 2)], {})],
    "rally": [("battlebreath", "Battle Breath", "A deeper second wind.", [("heal", dict(base=10, per=2))], {}),
              ("stubborn", "Stubborn Heart", "Heal a little and harden yourself against what comes next.", [("heal", dict(base=6, per=1)), ("ward", dict(base=4, per=1))], {})],
    "shoot": [("longshot", "Long Shot", "A patient, heavy shot.", [("dmg", dict(base=5, per=1))], {}),
              ("pinshot", "Pinning Shot", "An arrow that pins a limb: damage, and a fair chance it loses its turn.", [("dmg", dict(base=2, per=1)), ("stun", 0.5)], {})],
    "snare": [("strangle", "Strangle-Snare", "A cruel snare: it almost always holds, and it chafes.", [("stun", 0.9), ("dot", (1, 3, "strains against the cord"))], {}),
              ("quicksnare", "Quick Snare", "A snare thrown in a heartbeat. Cheaper, a little less sure.", [("stun", 0.7)], dict(cost=1))],
    "volley": [("tripleshot", "Triple Shot", "Three arrows, nearly as one.", [("dmg", dict(base=3, per=1, hits=3))], {}),
               ("huntvolley", "Hunter's Volley", "Two arrows, the second where the first opened it up.", [("expose", 1), ("dmg", dict(base=3, per=1, hits=2))], {})],
    "poultice": [("hedgedoctor", "Hedge-Doctor's Poultice", "A poultice that heals more and draws out poison and ill luck.", [("heal", dict(base=12, per=1)), ("cleanse", None)], dict(peace_only=True)),
                 ("fieldpoultice", "Field Poultice", "A rough poultice you can slap on mid-fight.", [("heal", dict(base=7, per=1))], {})],
    "backstab": [("assassin", "Assassin's Cut", "Four times the damage against anything not yet fighting you, or while hidden.", [("ambush", 4), ("dmg", dict(weapon=True, base=1, per=0))], {}),
                 ("bleedcut", "Bleeding Cut", "Triple damage from hiding, and the wound keeps bleeding.", [("ambush", 3), ("dmg", dict(weapon=True, base=1, per=0)), ("dot", (2, 3, "bleeds"))], {})],
    "vanish": [("smokemirror", "Smoke and Mirrors", "Vanish, every time, and stay hidden longer.", [("escape", 4)], dict(combat_only=True)),
               ("slip", "Slip Away", "Vanish for less effort.", [("escape", 2)], dict(combat_only=True, cost=1))],
    "trick": [("pocketsand", "Pocket Sand", "The dirtiest trick there is: it nearly always works.", [("dmg", dict(base=1, per=0)), ("stun", 0.85)], {}),
              ("lowblow", "Low Blow", "A trick that leaves it hurting and weaker.", [("dmg", dict(base=2, per=0)), ("stun", 0.55), ("weaken", 1)], {})],
    "venom": [("blackvenom", "Black Venom", "A stronger poison, longer lasting.", [("dmg", dict(base=1, per=0)), ("dot", (4, 4, "sickens"))], {}),
              ("numbvenom", "Numbing Venom", "Poison that also slows its limbs.", [("dmg", dict(base=1, per=0)), ("dot", (2, 3, "sickens")), ("weaken", 1)], {})],
    "feint": [("doublefeint", "Double Feint", "Two lies and then the truth: a heavy cut past its armour.", [("dmg", dict(weapon=True, base=4, per=1, pierce=True))], {}),
              ("feintvanish", "Feint and Vanish", "Cut, and be gone before it turns.", [("dmg", dict(weapon=True, base=1, per=1, pierce=True)), ("escape", 2)], {})],
}
# the original class techniques, described as effects, so they can be joined in combinations
FX_EQUIV = {
    "bash": [("dmg", dict(weapon=True, base=0, per=0)), ("stun", 0.6)], "guard": [("guard", 2)],
    "shoot": [("dmg", dict(base=2, per=1))], "backstab": [("ambush", 3), ("dmg", dict(weapon=True, base=1, per=0))],
    "vanish": [("escape", 3)],
}
HONED_FROM = {v[0]: k for k, vs in HONES.items() for v in vs}
COMBO_STAT = 7      # the school's stat it takes to join two techniques


def practise(p, key):
    """Count a use of a technique toward honing it."""
    from . import arts as ARTS
    if ARTS.school_of(key)[0] in HONE_SCHOOLS:
        p.practice[key] = p.practice.get(key, 0) + 1


def fx_of(key):
    from . import arts as ARTS
    a = ARTS.ARTS.get(key)
    return a["fx"] if a else FX_EQUIV.get(key)


def honeable(p):
    """[(technique, [options])] you could hone right now."""
    return [(k, HONES[k]) for k in p.known if k in HONES and p.practice.get(k, 0) >= PRACTICE]


def make_hone(p, src, opt):
    from . import arts as ARTS
    key, label, desc, fx, extra = opt
    a = ARTS.ARTS.get(src) or {}
    from . import classes as K
    base = K.ABILITIES[src]
    school, circle = ARTS.school_of(src)
    spec = dict(label=label, school=school, circle=circle, cost=extra.get("cost", base["cost"]), desc=desc,
                fx=[(k, dict(v) if isinstance(v, dict) else v) for k, v in fx], crafted=True, honed_from=src,
                target=any(k in ("dmg", "stun", "weaken", "expose", "dot", "flee", "ambush") for k, _ in fx),
                say=a.get("say") or [f"You do it the way you've honed it: {label}, into {{the_c}}'s {{part}}." if any(k == "dmg" for k, _ in fx) else f"{label}, just as you've practised it."])
    for flag in ("combat_only", "peace_only"):
        if extra.get(flag) or base.get(flag):
            spec[flag] = True
    if not spec["target"] and not any(k == "escape" for k, _ in fx):
        spec["say"] = [f"{label}: the way you've drilled it a hundred times."]
    return key, spec


def combos(p):
    """Pairs of techniques in one school you could join now."""
    from . import arts as ARTS
    from . import classes as K
    out = []
    ks = [k for k in p.known if ARTS.school_of(k)[0] in HONE_SCHOOLS and fx_of(k) and not ARTS.ARTS.get(k, {}).get("combo")
          and not K.ABILITIES[k].get("peace_only")]
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            sa, sb = ARTS.school_of(a)[0], ARTS.school_of(b)[0]
            if sa != sb or ARTS.stat(p, ARTS.SCHOOLS[sa]["stat"]) < COMBO_STAT:
                continue
            fa, fb = fx_of(a), fx_of(b)
            ta = any(k in ("dmg", "stun", "weaken", "expose", "dot", "ambush") for k, _ in fa)
            tb = any(k in ("dmg", "stun", "weaken", "expose", "dot", "ambush") for k, _ in fb)
            if not (ta or tb):
                continue
            if not (HONED_FROM.get(a) or HONED_FROM.get(b) or p.practice.get(a, 0) >= PRACTICE or p.practice.get(b, 0) >= PRACTICE):
                continue
            out.append((a, b))
    return out


def make_combo(p, a, b):
    from . import arts as ARTS
    from . import classes as K
    A, B = K.ABILITIES[a], K.ABILITIES[b]
    fx = []
    for k, v in fx_of(a) + fx_of(b):
        if k == "escape" and any(x == "escape" for x, _ in fx):
            continue
        fx.append((k, dict(v) if isinstance(v, dict) else v))
    # an escape belongs at the end, or the second half never lands
    fx = [f for f in fx if f[0] != "escape"] + [f for f in fx if f[0] == "escape"]
    school = ARTS.school_of(a)[0]
    label = f"{A['label']} into {B['label']}"
    spec = dict(label=label, school=school, circle=max(ARTS.school_of(a)[1], ARTS.school_of(b)[1]), cost=max(1, A["cost"] + B["cost"] - 1),
                desc=describe_fx(fx), fx=fx, crafted=True, combo=[a, b],
                target=any(k in ("dmg", "stun", "weaken", "expose", "dot", "flee", "ambush") for k, _ in fx),
                say=[f"{A['label']}, and before {{the_c}} has recovered, {B['label']}.", f"You flow from {A['label'].lower()} straight into {B['label'].lower()}; {{the_c}} can't follow it."])
    if A.get("combat_only") or B.get("combat_only"):
        spec["combat_only"] = True
    return spec


def hone(g, rest):
    """'hone' lists; 'hone bash ringing' refines; 'hone feint with deathblow' joins two."""
    from . import arts as ARTS
    from . import classes as K
    p = g.player
    ARTS.ensure(p)
    words = [x.lower() for x in rest]
    if not words:
        ready = honeable(p)
        prog = [f"{K.ABILITIES[k]['label']} {min(p.practice.get(k, 0), PRACTICE)}/{PRACTICE}" for k in p.known if k in HONES and k not in dict(ready)]
        bits = []
        if ready:
            bits.append("Ready to hone: " + "; ".join(f"{K.ABILITIES[k]['label']} -> " + " or ".join(f"{o[1]}{_typed(f'hone {k} ' + o[1].split()[0].lower())}" for o in opts) for k, opts in ready))
        if prog:
            bits.append("Still practising: " + ", ".join(prog) + ". Use them in earnest and they'll come.")
        cs = combos(p)
        if cs:
            bits.append("You could join: " + "; ".join(f"{K.ABILITIES[a]['label']} into {K.ABILITIES[b]['label']}{_typed(f'hone {a} with {b}')}" for a, b in cs[:6]))
        if not bits:
            return g.emit("You have no techniques to hone. Knights, rangers and rogues hone what they practise; so can anyone who learns their ways.")
        return g.emit(" ".join(bits))
    if g.combat:
        return g.emit("Not now!")
    if "with" in words or "into" in words:
        cut = words.index("with") if "with" in words else words.index("into")
        a = next((k for k in p.known if k == "".join(words[:cut]) or K.ABILITIES[k]["label"].lower() == " ".join(words[:cut])), None)
        b = next((k for k in p.known if k == "".join(words[cut + 1:]) or K.ABILITIES[k]["label"].lower() == " ".join(words[cut + 1:])), None)
        if not a or not b:
            return g.emit(f"You'd need to know both techniques. ({ui.ref('hone')} lists what you could join.)")
        if (a, b) not in combos(p) and (b, a) not in combos(p):
            sa, sb = ARTS.school_of(a)[0], ARTS.school_of(b)[0]
            if sa != sb:
                return g.emit("Those come from different traditions. They don't join.")
            if ARTS.stat(p, ARTS.SCHOOLS[sa]["stat"]) < COMBO_STAT:
                return g.emit(f"Joining techniques takes someone {ARTS.STAT_WORDS[ARTS.SCHOOLS[sa]['stat']][3][0]}. Not yet.")
            return g.emit("You haven't practised either enough to join them, or they don't fit together.")
        spec = make_combo(p, a, b)
        if any(s["label"] == spec["label"] for s in p.crafted.values()):
            return g.emit(f"You already have {spec['label']}.")
        with g.hush():
            g.pass_time(180)
        key = command_for(p, spec["label"])
        p.crafted[key] = spec
        p.known.append(key)
        register(p)
        return g.emit(g.narr.pick([f"Three hours of drilling until your arms shake, and the two moves become one: {spec['label']}.",
                                   f"You work the join over and over until it stops being two things. {spec['label']}."])
                      + f" ({spec['desc']} Costs {spec['cost']} {K.res_name(p)}.{_named(key)})")
    src = next((k for k in p.known if k == words[0] or K.ABILITIES[k]["label"].lower().startswith(words[0])), None)
    if not src or src not in HONES:
        return g.emit(f"That isn't a technique you can hone. ({ui.ref('hone')} lists what you can.)")
    if p.practice.get(src, 0) < PRACTICE:
        return g.emit(f"You need more practice with {K.ABILITIES[src]['label']} first ({p.practice.get(src, 0)}/{PRACTICE}). Use it in earnest.")
    opts = HONES[src]
    choice = next((o for o in opts if len(words) > 1 and (o[0] == words[1] or o[1].lower().split()[0].startswith(words[1]))), None)
    if not choice:
        return g.emit(f"Hone {K.ABILITIES[src]['label']} into what? " + " or ".join(f"{o[1]} - {o[2]}{_typed(f'hone {src} ' + o[1].split()[0].lower())}" for o in opts))
    key, spec = make_hone(p, src, choice)
    with g.hush():
        g.pass_time(120)
    p.crafted[key] = spec
    p.known[p.known.index(src)] = key
    register(p)
    g.emit(g.narr.pick([f"You spend two hours working {K.ABILITIES[src]['label'].lower()} over and over, until it turns into something better: {spec['label']}.",
                        f"Two hours of drill, and {K.ABILITIES[src]['label'].lower()} is not what it was. It's {spec['label']} now."])
           + f" ({spec['desc']}{_named(key)})")


def forget(g, rest):
    """Let go of a crafted art you no longer want (the original, if it was honed, comes back)."""
    from . import classes as K
    p = g.player
    key = next((k for k in p.crafted if rest and (k == rest[0] or p.crafted[k]["label"].lower() == " ".join(rest))), None)
    if not key:
        mine = ", ".join(f"{s['label']} ({k})" for k, s in p.crafted.items())
        return g.emit("You can only let go of arts you made yourself." + (f" (Yours: {mine}.)" if mine else ""))
    spec = p.crafted.pop(key)
    i = p.known.index(key) if key in p.known else None
    if spec.get("honed_from") and i is not None:
        p.known[i] = spec["honed_from"]
    elif i is not None:
        p.known.pop(i)
    g.emit(f"You let {spec['label']} slip from your mind." + (f" You still have plain {K.ABILITIES[spec['honed_from']]['label']}." if spec.get("honed_from") else ""))
