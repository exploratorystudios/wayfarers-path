"""Player classes: stats, starting kit, a resource, abilities and a passive.

Abilities are commands (`firebolt`, `bash`, ...). Each one spends the class's
resource, is narrated from generated text (lex_classes.py), and plugs into the
same combat flow as an ordinary attack - including creature minds: Fear and Turn
override a creature's intent, Track reads intents on neighbouring tiles.
"""
from . import mind

CLASSES = {
    "knight": dict(
        name="Knight", difficulty="easy", menu="Feats", res="stamina", res_max=6, res_gain=2,
        hp=36, atk=2, df=1, hp_gain=7, atk_every=1, df_every=2,
        weapon=["sword", "mace", "axe"], armour="mail",
        abilities=["bash", "guard"],
        passive=("Armoured", "Heavy armour sits easily on you: +1 defence."),
        blurb="Sworn steel and a stubborn heart. Hard to kill, hard to move.",
        past=["a knight whose lord died owing you a year's pay", "a hedge knight with a dented shield and a long memory",
              "the last sworn knight of an order that no longer exists"]),
    "ranger": dict(
        name="Ranger", difficulty="medium", menu="Skills", res="stamina", res_max=6, res_gain=2,
        hp=30, atk=3, df=0, hp_gain=6, atk_every=1, df_every=3,
        weapon=["spear", "dagger"], armour="jerkin",
        abilities=["shoot", "track"],
        passive=("Woodwise", "Ambushes rarely catch you, and marsh and mountain slow you less."),
        blurb="A bow, a sharp eye, and the wild as a second home.",
        past=["a border scout who stopped reporting back", "a forester whose woods were sold out from under you",
              "a tracker hired to find someone who did not want finding"]),
    "wizard": dict(
        name="Wizard", difficulty="hard", menu="Spells", res="mana", res_max=12, res_gain=3,
        hp=25, atk=0, df=0, hp_gain=5, atk_every=2, df_every=4,
        weapon=["staff"], armour=None,
        abilities=["firebolt", "ward", "fear"],
        passive=("Attuned", "Mana returns quickly as you travel."),
        blurb="Frail in body, terrible in will. Fire, wards, and fear itself.",
        past=["an apprentice whose master vanished mid-sentence", "a scholar expelled for reading the wrong shelf",
              "a hedge-mage who finally outgrew the hedge"]),
    "rogue": dict(
        name="Rogue", difficulty="tricky", menu="Tricks", res="stamina", res_max=6, res_gain=2,
        hp=26, atk=2, df=0, hp_gain=5, atk_every=1, df_every=3,
        weapon=["dagger", "sword"], armour="jerkin",
        abilities=["backstab", "vanish"],
        passive=("Light-fingered", "Better prices from merchants, more coin from the fallen, and sharper criticals."),
        blurb="Quick hands, quiet feet. Strike first, or not at all.",
        past=["a cutpurse who robbed the wrong magistrate", "a smuggler whose boat is now at the bottom of a lake",
              "a spy whose employers have stopped paying and started looking"]),
    "cleric": dict(
        name="Cleric", difficulty="easy", menu="Prayers", res="faith", res_max=8, res_gain=2,
        hp=28, atk=1, df=1, hp_gain=6, atk_every=2, df_every=2,
        weapon=["mace", "staff"], armour="jerkin",
        abilities=["heal", "smite", "turn"],
        passive=("Blessed", "Shrines give you more, and the undead strike you more softly."),
        blurb="Faith that mends, and faith that burns.",
        past=["a priest whose temple burned with the old god still in it", "a pilgrim who heard an answer and followed it",
              "a field-chaplain who has buried too many friends"]),
}

# combat: usable in a fight (and may start one if it targets a creature); peace: not mid-fight
ABILITIES = {
    "bash":     dict(cost=2, label="Shield bash", desc="Batter it with your shield: damage, and a good chance to stun.", target=True),
    "guard":    dict(cost=1, label="Guard", desc="Raise your shield: the next two blows are halved.", combat_only=True),
    "shoot":    dict(cost=2, label="Shoot", desc="Loose an arrow. Opening a fight from range, it can't strike back this turn.", target=True),
    "track":    dict(cost=1, label="Track", desc="Read the signs: what lurks on the neighbouring tiles, and what it intends.", peace_only=True),
    "firebolt": dict(cost=3, label="Firebolt", desc="Hurl fire. Ignores armour and hits hard.", target=True),
    "ward":     dict(cost=2, label="Ward", desc="Weave a shield that soaks up damage until it breaks."),
    "fear":     dict(cost=2, label="Fear", desc="Fill a creature's mind with terror so that it flees. The strong-willed may resist.", target=True),
    "backstab": dict(cost=2, label="Backstab", desc="Triple damage against something not yet fighting you, or while you're hidden.", target=True),
    "vanish":   dict(cost=2, label="Vanish", desc="Slip out of a fight and stay hidden for a few moments.", combat_only=True),
    "heal":     dict(cost=3, label="Heal", desc="Mend your wounds."),
    "smite":    dict(cost=2, label="Smite", desc="Holy force that ignores armour; doubled against the undead.", target=True),
    "turn":     dict(cost=2, label="Turn undead", desc="Command the dead to flee. Beasts are unmoved.", target=True),
}


from . import arts as ARTS_      # noqa: E402  (the schools; new arts join ABILITIES below)
for _k, _a in ARTS_.ARTS.items():
    ABILITIES[_k] = _a
for _k, (_s, _c) in ARTS_.ORIGINAL.items():
    ABILITIES[_k].update(school=_s, circle=_c)


def known(player):
    """The arts this player has: their class's to begin with, then whatever they learn."""
    ARTS_.ensure(player)
    return player.known


def res_name(player):
    s = spec(player)
    return s["res"] if s else "stamina"


def spec(player):
    return CLASSES.get(getattr(player, "klass", ""), None)


def scale(p, base, per_level):
    return base + per_level * (p.level - 1)


# ------------------------------------------------------------------ dispatch
def use(g, key, rest):
    """Run an ability command. Returns nothing; narrates everything."""
    p, n = g.player, g.narr
    s = spec(p)
    a = ABILITIES[key]
    if key not in known(p):
        who = s["name"].lower() if s else "traveller"
        return g.emit(n.say("{ab_unknown}", dict(klass=who, ability=a["label"].lower())))
    if a.get("combat_only") and not g.combat:
        return g.emit(n.say("{ab_need_fight}", dict(ability=a["label"])))
    if a.get("peace_only") and g.combat:
        return g.emit(n.say("{ab_need_peace}", dict(ability=a["label"])))
    if p.res < a["cost"]:
        return g.emit(n.say("{ab_spent}", dict(res=res_name(p), ability=a["label"])))
    target = None
    if a.get("target"):
        t = g.world.tiles[g.pos]
        if g.combat and not rest:
            target = g.combat
        elif rest:
            target = g.find(rest, [t.creatures])
        elif len(t.creatures) == 1:
            target = t.creatures[0]
        if target is None:
            return g.emit(n.say("{ab_no_target}" if not t.creatures else "{ab_which}", dict(ability=a["label"])))
    p.res -= a["cost"]
    from . import crafts as CR
    CR.practise(p, key)
    if key in ARTS_.ARTS:
        return ARTS_.run(g, key, target)
    globals()["_" + key](g, target)


def finish_exchange(g, c, took, opener=False):
    """After an ability that hit `c`: death, or the creature's reply."""
    if c.hp <= 0:
        return g.finish_off(c)
    g.combat = c
    if opener:
        mind.update(c, g.player, g.world, in_combat=True)
        return
    g.enemy_turn()
    if g.combat is c:
        mind.reinforce(c, going_well=g._enemy_dmg >= took)


def _ctx(g, c=None, **kw):
    d = dict(kw)
    if c is not None:
        d.update(the_c=g.narr.creature_np(c, True), part=c.species["arch"]["parts"])
    return d


# ------------------------------------------------------------------ knight
def _bash(g, c):
    p, n = g.player, g.narr
    hit = g.rng.randint(1, 20) + p.atk - c.df >= 7
    if not hit:
        g.emit(n.say("{ab_bash_miss}", _ctx(g, c)))
        return finish_exchange(g, c, 0)
    dmg = max(1, p.atk + g.rng.randint(0, 2) - c.df)
    c.hp -= dmg
    stun = g.rng.random() < (0.3 if c.boss else 0.6)
    if stun and c.hp > 0:
        mind.ensure(c)["stunned"] = True
    g.emit(n.say("{ab_bash_stun}" if stun else "{ab_bash_hit}", _ctx(g, c)) + f" ({dmg} damage)")
    finish_exchange(g, c, dmg)


def _guard(g, c):
    g.player.guard = 2
    g.emit(g.narr.say("{ab_guard}", {}))
    g.enemy_turn()


# ------------------------------------------------------------------ ranger
def _shoot(g, c):
    p, n = g.player, g.narr
    opener = g.combat is None
    hit = g.rng.randint(1, 20) + p.atk + (3 if opener else 0) - c.df >= 8
    if not hit:
        g.emit(n.say("{ab_shoot_miss}", _ctx(g, c)))
        return finish_exchange(g, c, 0, opener)
    arrows = getattr(p, "arrows", None)
    special = arrows["kind"] if arrows and arrows.get("left", 0) > 0 else None
    if special:
        arrows["left"] -= 1
    dmg = max(1, p.atk + 2 + g.rng.randint(0, 3) - (0 if special == "bodkin" else c.df))
    if opener:
        dmg = int(dmg * 1.5)
    c.hp -= dmg
    extra = ""
    if special == "fire" and c.hp > 0:
        mind.ensure(c)["dot"] = dict(dmg=2, turns=3, verb="burns")
        extra = " The pitch catches, and it burns."
    elif special == "bodkin":
        extra = " The bodkin point goes straight through."
    g.emit(n.say("{ab_shoot_open}" if opener else "{ab_shoot_hit}", _ctx(g, c)) + extra + f" ({dmg} damage)")
    finish_exchange(g, c, dmg, opener)


def _track(g, c):
    w, n = g.world, g.narr
    found = []
    for d, q in w.neighbours(g.pos):
        if q not in w.land:
            continue
        for cr in w.tiles[q].creatures:
            mind.update(cr, g.player, w)
            found.append(n.say("{ab_track_sign}", dict(dir=d, a_c=n.creature_np(cr), intent=n.say("{intent_desc}", {}, [mind.intent(cr)]).lower())))
    g.emit(n.say("{ab_track_start}", {}))
    g.emit(" ".join(found) if found else n.say("{ab_track_none}", {}))


# ------------------------------------------------------------------ wizard
def _firebolt(g, c):
    p, n = g.player, g.narr
    dmg = scale(p, 6, 2) + g.rng.randint(0, 4) + ARTS_.power(p, "arcane")          # ignores armour
    crit = g.rng.random() < 0.12
    if crit:
        dmg = int(dmg * 1.5)
    c.hp -= dmg
    g.emit(n.say("{ab_firebolt_crit}" if crit else "{ab_firebolt}", _ctx(g, c)) + f" ({dmg} damage)")
    finish_exchange(g, c, dmg)


def _ward(g, c):
    p = g.player
    p.ward = scale(p, 9, 3) + ARTS_.power(p, "arcane")
    g.emit(g.narr.say("{ab_ward}", {}) + f" (absorbs {p.ward})")
    if g.combat:
        g.enemy_turn()


def _fear(g, c):
    n = g.narr
    t = mind.ensure(c)["temper"]
    chance = 0.0 if c.boss else max(0.15, 0.85 - 0.5 * t["bold"])
    if g.rng.random() < chance:
        mind.commit(c, "flee", turns=2)
        g.emit(n.say("{ab_fear_ok}", _ctx(g, c)))
        g.combat = c
        g.enemy_turn()          # its turn: it tries to bolt
    else:
        g.emit(n.say("{ab_fear_resist}" if not c.boss else "{ab_fear_boss}", _ctx(g, c)))
        g.combat = c
        g.enemy_turn()


# ------------------------------------------------------------------ rogue
def _backstab(g, c):
    p, n = g.player, g.narr
    unaware = (g.combat is not c and mind.intent(c) in ("wander", "stalk", "hold", "flee")) or getattr(p, "hidden", 0) > 0
    p.hidden = 0
    if unaware:
        dmg = max(3, (p.atk + g.rng.randint(1, 3)) * 3 - c.df)
    else:
        dmg = max(1, p.atk + g.rng.randint(0, 2) - c.df)
    c.hp -= dmg
    g.emit(n.say("{ab_backstab}" if unaware else "{ab_backstab_seen}", _ctx(g, c)) + f" ({dmg} damage)")
    finish_exchange(g, c, dmg)


def _vanish(g, c):
    c = g.combat
    ok = g.rng.random() < (0.6 if c.boss else 1.0)
    if not ok:
        g.emit(g.narr.say("{ab_vanish_fail}", _ctx(g, c)))
        return g.enemy_turn()
    g.combat = None
    g.player.hidden = 3
    m = mind.ensure(c)
    m["support"]["wander"] = max(m["support"].values()) + 0.1   # it has lost you
    m["intent"] = "wander"
    g.emit(g.narr.say("{ab_vanish}", _ctx(g, c)))


# ------------------------------------------------------------------ cleric
def _heal(g, c):
    p = g.player
    before = p.hp
    p.hp = min(p.maxhp, p.hp + scale(p, 9, 2) + g.rng.randint(0, 3) + ARTS_.power(p, "divine"))
    g.emit(g.narr.say("{ab_heal}", {}) + f" (+{p.hp - before} HP)")
    if g.combat:
        g.enemy_turn()


def _smite(g, c):
    p, n = g.player, g.narr
    undead = c.species["arch"].get("undead", False)
    dmg = scale(p, 4, 1) + g.rng.randint(0, 3) + ARTS_.power(p, "divine")
    if undead:
        dmg *= 2
    c.hp -= dmg
    g.emit(n.say("{ab_smite_undead}" if undead else "{ab_smite}", _ctx(g, c)) + f" ({dmg} damage)")
    finish_exchange(g, c, dmg)


def _turn(g, c):
    n = g.narr
    if not c.species["arch"].get("undead", False):
        g.emit(n.say("{ab_turn_beast}", _ctx(g, c)))
        if g.combat:
            g.enemy_turn()
        return
    if c.boss:      # a quest's guardian does not leave its post
        g.emit(n.say("{ab_fear_boss}", _ctx(g, c)))
    else:
        mind.commit(c, "flee", turns=3)
        g.emit(n.say("{ab_turn_ok}", _ctx(g, c)))
    g.combat = c
    g.enemy_turn()
