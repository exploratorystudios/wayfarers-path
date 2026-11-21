"""Creature minds: persistent intents with decaying support.

Each creature holds a support level for five intents. Whenever it acts, every
intent's support decays and is topped up by fresh evidence from the situation
(its health, yours, how a fight would go, the dark, its temperament):

    support = DECAY * support + GAIN * evidence

The strongest intent governs. Because support decays rather than resetting, an
intent persists until the evidence clearly turns - creatures commit, then change
their minds visibly, instead of flickering. After each exchange in a fight, the
governing intent is reinforced if it is going well and demoted if it isn't.
(Utility AI with hysteresis; the decay/reinforce shape follows the plan layer of
exploratorystudios/neuro-go, reimplemented here.)
"""

INTENTS = ("wander", "stalk", "hunt", "hold", "flee")
DECAY, GAIN = 0.72, 0.42
CAP = 1.2

# Temperament by body plan: bold (presses attacks), cunning (stalks, waits for
# weakness), territorial (guards ground), skittish (quick to bolt).
TEMPER = {
    "wolf":    dict(bold=.55, cunning=.85, territorial=.25, skittish=.20),
    "boar":    dict(bold=.75, cunning=.15, territorial=.80, skittish=.10),
    "spider":  dict(bold=.45, cunning=.80, territorial=.55, skittish=.25),
    "serpent": dict(bold=.35, cunning=.55, territorial=.70, skittish=.45),
    "toad":    dict(bold=.40, cunning=.15, territorial=.65, skittish=.30),
    "crow":    dict(bold=.30, cunning=.65, territorial=.10, skittish=.75),
    "stag":    dict(bold=.50, cunning=.20, territorial=.85, skittish=.55),
    "bear":    dict(bold=.85, cunning=.30, territorial=.70, skittish=.05),
    "goat":    dict(bold=.45, cunning=.20, territorial=.75, skittish=.45),
    "wraith":  dict(bold=.70, cunning=.75, territorial=.40, skittish=.00),
}
# The individual's trait nudges the species' temperament.
TRAIT = {
    "young": dict(bold=-.20, skittish=.25, cunning=-.15), "old": dict(cunning=.20, bold=-.10),
    "scarred": dict(bold=.15, cunning=.10), "battle-torn": dict(bold=.20, skittish=-.10),
    "gaunt": dict(bold=.15, hungry=.30), "mangy": dict(hungry=.20, skittish=.10),
    "huge": dict(bold=.20, skittish=-.15), "limping": dict(skittish=.20, cunning=.10),
    "restless": dict(skittish=.10, bold=.05), "sleek": dict(cunning=.10), "colossal": dict(bold=.30),
}


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def temperament(c):
    t = dict(TEMPER.get(c.species["key"], TEMPER["wolf"]), hungry=0.0)
    # the species' generated aggression shades boldness
    t["bold"] += (c.species.get("aggression", 0.5) - 0.5) * 0.5
    for k, v in TRAIT.get(c.trait, {}).items():
        t[k] = t.get(k, 0) + v
    return {k: _clamp(v) for k, v in t.items()}


def ensure(c):
    """Give a creature a mind if it doesn't have one yet (older saves included)."""
    m = getattr(c, "mind", None)
    if m:
        return m
    t = temperament(c)
    support = {"wander": .1 + .3 * (1 - t["bold"]), "stalk": .3 * t["cunning"], "hunt": .3 * t["bold"],
               "hold": .35 * t["territorial"], "flee": .15 * t["skittish"]}
    if c.aggressive:
        support["hunt"] += .25
    if c.boss:
        support = {"wander": 0, "stalk": 0, "hunt": .3, "hold": .6, "flee": 0}
    c.mind = dict(temper=t, support=support, intent=max(support, key=support.get),
                  warned=False, feint=False, last_shift=None)
    return c.mind


def advantage(c, player):
    """0..1 from the creature's side: above 0.5 means it expects to win."""
    to_die = c.hp / max(0.5, player.atk + 1.5 - c.df)
    to_kill = player.hp / max(0.5, c.atk - 0.5 - player.df)
    return _clamp(to_die / (to_die + to_kill))


def evidence(c, player, world, in_combat):
    t = ensure(c)["temper"]
    hp, php = c.hp / c.maxhp, player.hp / player.maxhp
    adv = advantage(c, player)
    dark = 1.0 if world.is_dark else 0.0
    ev = {
        "hunt": .55 * t["bold"] + .7 * adv + .35 * (1 - php) + .15 * dark + t["hungry"] - .55,
        "stalk": .65 * t["cunning"] + (.3 if .3 <= adv <= .65 else 0) + .15 * dark + (.2 if php > .6 else 0)
                 - .3 * (1 - hp) - (.25 if in_combat else 0),
        "hold": .7 * t["territorial"] + .1 - (.15 if in_combat and adv > .6 else 0),
        "wander": 0.0 if in_combat else .5 * (1 - t["bold"]) + .2 - .25 * adv,
        "flee": 1.25 * (1 - hp) * (1 - .5 * t["bold"]) + .55 * (1 - adv) + .3 * t["skittish"] - .55,
    }
    if c.boss:   # the relic's guardian never wanders off or runs
        ev.update(wander=0.0, flee=0.0, stalk=0.0)
    return {k: _clamp(v) for k, v in ev.items()}


def update(c, player, world, in_combat=False):
    """Fold in fresh evidence. Returns (old_intent, new_intent)."""
    m = ensure(c)
    if m.get("locked", 0) > 0:          # under a spell: its own judgement is suspended
        m["locked"] -= 1
        return m["intent"], m["intent"]
    ev = evidence(c, player, world, in_combat)
    s = m["support"]
    for k in INTENTS:
        # overwhelming evidence (near death, an easy kill) cuts through hesitation: panic and bloodlust
        gain = GAIN if ev[k] < 0.75 else 0.8
        s[k] = _clamp(DECAY * s[k] + gain * ev[k], 0, CAP)
    if not in_combat:   # a little rest between encounters
        c.hp = min(c.maxhp, c.hp + max(1, c.maxhp // 12))
    old = m["intent"]
    m["intent"] = max(INTENTS, key=lambda k: s[k])
    if m["intent"] != old:
        m["last_shift"] = (old, m["intent"])
        if m["intent"] != "hold":
            m["warned"] = False
    return old, m["intent"]


def reinforce(c, going_well):
    """After an exchange: back the governing intent if it's paying off, else demote it."""
    m = ensure(c)
    k = m["intent"]
    m["support"][k] = _clamp(m["support"][k] + (.12 if going_well else -.18), 0, CAP)


def commit(c, to="hunt", turns=0):
    """Force a decision (an ambush, a chase, a spell). With `turns`, the intent is
    locked for that many updates before the creature's own mind resumes."""
    m = ensure(c)
    m["support"][to] = max(m["support"].values()) + 0.15
    m["intent"] = to
    m["locked"] = turns


def intent(c):
    return ensure(c)["intent"]
