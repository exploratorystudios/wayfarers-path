"""Telling a fight: the record it keeps and the lines it chooses.

The numbers are settled in game.py and arts.py; this only says what happened. A small record rides on the
creature's mind (c.mind["fight"]) so each line can know the fight so far: how many exchanges, which wounds
are already open on either side, how badly each of you is hurt, when the ground or the sky last had a say."""

from . import lex_fight as LF
from . import lex_temper as TEMPER
from . import mind

SETTING_GAP = 3        # exchanges, at least, between lines about the ground or the weather


def record(c):
    m = mind.ensure(c)
    f = m.get("fight")
    if f is None:
        f = m["fight"] = dict(turns=0, wounds={}, hurt={}, band=0, me_band=0, winded=False, low=False,
                              setting=0, opened=False, took=0)
    return f


def _band(hp, mx):
    r = hp / max(1, mx)
    return 0 if r > 0.6 else 1 if r > 0.3 else 2 if r > 0.15 else 3


def _beast(c):
    return LF.BEASTS.get(c.species.get("key"), LF.BEASTS[LF.BEAST_DEFAULT])


def _cls(g):
    w = g.player.weapon
    return w.cls if w else "fist"


def _weapon(g):
    w = g.player.weapon
    return f"your {w.facts.get('noun', w.name)}" if w else "your fist"


def _kinds(c):
    a, key = c.species["arch"], c.species.get("key")
    out = []
    if a.get("undead"):
        out.append("undead")
    if c.boss:
        out.append("boss")
    elif key in LF.SMALL:
        out.append("small")
    elif key in LF.BIG:
        out.append("big")
    return out


def _ctx(g, c, **kw):
    b = _beast(c)
    np = g.narr.creature_np(c, True)
    if np.startswith("The "):                     # a named one: "the Old Mother", capitalised only where a sentence starts
        np = "the " + np[4:]
    d = dict(the_c=np, weapon=_weapon(g),
             r_small=b["r_small"], r_mid=b["r_mid"], r_big=b["r_big"])
    d.update(kw)
    return d


def _scopes(g):
    t = g.world.tiles[g.pos]
    return [_cls(g)] + g.narr.scopes(t.biome, t.mood)


def _say(g, pool, ctx):
    return g.narr.say("{line}", dict(ctx, line=list(pool)), _scopes(g))


# ------------------------------------------------------------------ beats that ride after a line
def _setting(g, c, f):
    """Now and then, the ground underfoot or the weather overhead."""
    if f["turns"] < 2 or f["turns"] - f["setting"] < SETTING_GAP or g.rng.random() > 0.4:
        return ""
    w, t = g.world, g.world.tiles[g.pos]
    pools = []
    if t.biome in LF.GROUND:
        pools.append(LF.GROUND[t.biome])
    if w.is_dark:
        pools.append(LF.SKY["dark"])
    elif w.weather in LF.SKY:
        pools.append(LF.SKY[w.weather])
    elif w.weather == "clear" and w.time_of_day in ("morning", "midday", "afternoon"):
        pools.append(LF.SKY["sun"])
    if w.weather == "snow" or (w.season == "winter" and t.biome == "peaks"):
        pools.append(LF.SKY["snow"])
    if not pools:
        return ""
    f["setting"] = f["turns"]
    return _say(g, g.rng.choice(pools), _ctx(g, c))


def _foe_state(g, c, f):
    """When it crosses from fresh to hurt to failing, say so, once each."""
    if c.hp <= 0:
        return ""
    band = min(2, _band(c.hp, c.maxhp))
    if band <= f["band"]:
        return ""
    f["band"] = band
    b = _beast(c)
    return _say(g, b["hurt"] if band == 1 else b["fail"], _ctx(g, c, part=c.species["arch"]["parts"]))


def _my_state(g, c, f, bp):
    p = g.player
    band = _band(max(0, p.hp), p.maxhp)
    if p.hp <= 0:
        return ""
    if band > f["me_band"] and band >= 1:
        f["me_band"] = band
        return _say(g, LF.HURT if band == 1 else LF.DIRE, _ctx(g, c, bp=bp))
    if not f["winded"] and f["turns"] >= 5 and g.rng.random() < 0.5:
        f["winded"] = True
        return _say(g, LF.WINDED, _ctx(g, c))
    return ""


def _join(*parts):
    return " ".join(x for x in parts if x)


# ------------------------------------------------------------------ the opening
def opening(g, c):
    """The beat before the first blow, when you start it. Empty if the fight is already going."""
    f = record(c)
    if f["opened"]:
        return ""
    f["opened"] = True
    kinds = _kinds(c)
    key = "boss" if "boss" in kinds else "undead" if "undead" in kinds else TEMPER.temper(g.world, c)
    line = _say(g, LF.OPEN.get(key, LF.OPEN["brazen"]), _ctx(g, c))
    if g.rng.random() < 0.5:
        style = LF.OPEN_STYLE.get(getattr(g.player, "klass", None)) or LF.OPEN_STYLE[None]
        line = _join(line, _say(g, style, _ctx(g, c)))
    return line


# ------------------------------------------------------------------ your blows
def blow(g, c, tier):
    """Your weapon blow. tier: miss / graze / hit / crit. Call after the damage is dealt."""
    f = record(c)
    f["opened"] = True
    f["turns"] += 1
    parts, cls = c.species["arch"]["parts"], _cls(g)
    if c.hp <= 0 and tier != "miss":                       # the blow that ends it
        pool = list(LF.FINISH.get(cls, LF.FINISH["fist"]))
        for k in _kinds(c):
            pool += LF.FINISH_KIND.get(k, [])
        return _say(g, pool, _ctx(g, c, part=g.rng.choice(parts)))
    reopen = tier in ("hit", "crit") and f["wounds"] and g.rng.random() < 0.4
    if reopen:
        part = g.rng.choice(sorted(f["wounds"]))
        pool = LF.REOPEN[tier] + (LF.REOPEN_CLS.get(cls, []) if tier == "hit" else [])
    else:
        part = g.rng.choice(parts)
        pool = list(LF.BLOW[tier])
        style = LF.STYLE.get(getattr(g.player, "klass", None), {})
        if g.player.weapon or tier == "miss":              # a calling's way with a weapon; bare hands are bare hands
            pool += style.get(tier, []) * 2
        for k in _kinds(c):
            pool += LF.KIND.get(k, {}).get(tier, []) * 2
    if tier in ("hit", "crit"):
        f["wounds"][part] = f["wounds"].get(part, 0) + 1
    line = _say(g, pool, _ctx(g, c, part=part))
    return _join(line, _foe_state(g, c, f) or _setting(g, c, f))


def after_art(g, c, dealt, school):
    """What follows an art's own words: how the creature looks now, and whether your strength is running out."""
    p = g.player
    out = []
    if c is not None:
        f = record(c)
        f["opened"] = True
        f["turns"] += 1
        if dealt:
            out.append(_foe_state(g, c, f))
        res_max = getattr(p, "res_max", 0)
        if res_max and not f["low"] and p.res <= res_max // 4 and school in LF.LOW_POWER:
            f["low"] = True
            out.append(_say(g, LF.LOW_POWER[school], _ctx(g, c)))
    return _join(*out)


# ------------------------------------------------------------------ its blows
def foe(g, c, outcome, dmg=0):
    """Its attack. outcome: miss / block / hit / hard. Call after the damage is dealt."""
    f = record(c)
    f["opened"] = True
    b, p = _beast(c), g.player
    tool, hits, misses = g.rng.choice(b["tools"])
    bp = g.rng.choice(LF.BODY)
    ctx = _ctx(g, c, act=b["acts"][tool], tool=tool, toolhit=hits, bp=bp, bp_it="them" if bp.endswith("s") else "it",
               armour=p.armour.name.split()[-1] if p.armour else "skin")
    if outcome in ("hit", "hard"):
        f["took"] += dmg
        if bp in f["hurt"]:
            ctx["bp"] = f"{g.rng.choice(LF.RULES['f_hurt_adj'])} {bp}"
        if dmg > 0:                                # a blow the ward or shield swallowed leaves no mark
            f["hurt"][bp] = f["hurt"].get(bp, 0) + 1
    ctx["toolmiss"] = [f"{tool} {m}" for m in misses]
    if outcome == "block" and not p.armour:
        outcome = "block_bare"
    pool = list(LF.FOE[outcome])
    if c.boss:
        pool += LF.FOE_BOSS.get(outcome, []) * 2
    line = _say(g, pool, ctx)
    if outcome in ("hit", "hard"):
        return line, _my_state(g, c, f, bp) or _setting(g, c, f)
    return line, _setting(g, c, f)


# ------------------------------------------------------------------ the end
def death(g, c):
    return g.narr.say("{the_c.cap} {death}.", _ctx(g, c, death=c.species["arch"]["death"]))


def aftermath(g, c):
    """A line about how it went: quick, clean, long, close, or nothing much."""
    f = record(c)
    p = g.player
    if c.boss:
        key = "boss"
    elif p.hp <= p.maxhp * 0.3:
        key = "close"
    elif f["turns"] >= 6:
        key = "long"
    elif f["turns"] <= 1 and f["took"] == 0:
        key = "quick"
    elif f["took"] == 0 and f["turns"] >= 2 and g.rng.random() < 0.6:
        key = "clean"
    elif g.rng.random() < 0.4:
        key = "plain"
    else:
        return ""
    return _say(g, LF.AFTER[key], _ctx(g, c))
