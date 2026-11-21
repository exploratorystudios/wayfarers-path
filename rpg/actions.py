"""The complete action catalogue for the current moment.

Every command the game understands is listed, whether or not it is useful right
now. Each action carries:
  group, id, label, desc   - where it lives in the menu and what it does
  cmd                      - a template; {name} placeholders are filled from params
  params                   - [{name, prompt, options:[{label, value, note}]}] or
                             [{name, prompt, text: default, choices: [...]}] for free text
  enabled, reason          - whether it applies now, and why not
"""
from . import mind
from . import classes as K
from .advisor import fight_risk
from .world import DIRS

GROUPS = ["Look", "Explore", "Items", "People", "Fight", "Rest & Time", "Info", "Game"]


def groups(g):
    """Menu groups for this character: the class's own menu sits after Fight."""
    s = K.spec(g.player)
    out = list(GROUPS)
    if s:
        out.insert(out.index("Fight") + 1, s["menu"])
    if getattr(g, "pending", None):
        out.insert(0, "Respond")
    return out


def _opt(label, value, note=""):
    return dict(label=label, value=value, note=note)


def catalog(g):
    w, p = g.world, g.player
    t = w.tiles[g.pos]
    m = g.merchant()
    dead = g.died
    fighting = g.combat is not None
    out = []

    def act(group, id_, label, desc, cmd=None, params=None, enabled=True, reason="", ui=None):
        if dead and id_ not in ("load", "saves", "help", "manage"):
            enabled, reason = False, "You are dead. Load a save, or start a new game."
        out.append(dict(group=group, id=id_, label=label, desc=desc, cmd=cmd or id_,
                        params=params or [], enabled=bool(enabled), reason="" if enabled else reason,
                        **({"ui": ui} if ui else {})))

    # ------------------------------------------------------------ a choice is waiting
    pend = getattr(g, "pending", None)
    if pend:
        for i, o in enumerate(pend["options"], 1):
            act("Respond", f"choose{i}", o["label"], "Choose this.", str(i))

    # ------------------------------------------------------------ movement (compass)
    for d, (dx, dy) in DIRS.items():
        q = (g.pos[0] + dx, g.pos[1] + dy)
        if q not in w.tiles:
            ok, why = False, "The land beyond is trackless."
        elif q not in w.land:
            ok, why = False, "Open water blocks the way."
        else:
            ok, why = True, ""
        desc = "Try to break away and run " + d if fighting else f"Walk {d}"
        act("Move", d, d.capitalize(), desc, enabled=ok, reason=why)

    # ------------------------------------------------------------ look
    targets = []
    targets += [_opt(c.name, c.species["arch"]["noun"], "creature") for c in t.creatures]
    targets += [_opt(f"{n.name} the {n.job}" if n.known else f"the {n.job}", n.ref(), "person") for n in t.npcs]
    targets += [_opt(f.noun, f.noun, "landmark") for f in t.features]
    targets += [_opt(i.name, i.name, "on the ground") for i in t.items]
    targets += [_opt(i.name, i.name, "carried") for i in p.inv]
    seen = bool(m and m.mem.get("wares_seen"))
    if seen:
        targets += [_opt(i.name, i.name, f"for sale, {g.buy_price(m, i)} coins") for i in m.stock]
    if t.site:
        word = {"village": "village", "ruin": "ruin", "shrine": "shrine", "camp": "camp"}[t.site["kind"]]
        targets.append(_opt(f"the {word}", word, "place"))
    targets += [_opt("the sky and weather", "sky", ""), _opt("yourself", "me", "")]
    act("Look", "look", "Look around", "Describe this place afresh.")
    act("Look", "examine", "Examine…", "Look closely at something or someone.", "examine {what}",
        [dict(name="what", prompt="Examine what?", options=targets)])

    # ------------------------------------------------------------ explore (landmarks)
    from . import secrets as SEC
    verbs = [("search", "Search…", "Hunt around a landmark for anything hidden."), ("climb", "Climb…", "Get up high and see the land around."),
             ("drink", "Drink from…", "Drink, or bathe, at water."), ("touch", "Touch…", "Lay a hand on it. Some places answer."),
             ("read", "Read…", "Make out carvings or writing."), ("listen", "Listen at…", "Stand quiet and listen."),
             ("forage", "Forage…", "Gather food or herbs, depending on the season.")]
    for verb, label, desc in verbs:
        fit = [f for f in t.features if SEC.can(verb, f)]
        opts = [_opt(f.noun, f.noun, "done" if verb in (f.state or {}).get("done", []) and verb in ("search", "climb") else "") for f in fit]
        why = "Not while fighting." if fighting else "There's no landmark here for that."
        act("Explore", verb, label, desc, f"{verb} {{what}}", [dict(name="what", prompt=f"{label.rstrip('…')} what?", options=opts)],
            enabled=fit and not fighting, reason=why)
    offer_items = [_opt(i.name, i.name, i.kind) for i in p.inv if i.kind not in ("relic", "token")]
    act("Explore", "offer", "Leave an offering…", "Leave something at a landmark. Some places notice.", "give {item} to {what}",
        [dict(name="item", prompt="Offer what?", options=offer_items),
         dict(name="what", prompt="Where?", options=[_opt(f.noun, f.noun) for f in t.features])],
        enabled=t.features and offer_items and not fighting, reason="Not while fighting." if fighting else "Nothing to offer, or nowhere to offer it.")

    # ------------------------------------------------------------ items
    ground = [_opt(i.name, i.name, i.kind) for i in t.items]
    if len(t.items) > 1:
        ground.insert(0, _opt("everything here", "all", f"{len(t.items)} items"))
    act("Items", "take", "Take…", "Pick something up.", "take {item}",
        [dict(name="item", prompt="Take what?", options=ground)],
        enabled=t.items and not fighting, reason="Not while fighting." if fighting else "There's nothing here to take.")
    inv = [_opt(i.name, i.name, "wielded" if i is p.weapon else "worn" if i is p.armour else i.kind) for i in p.inv]
    act("Items", "drop", "Drop…", "Leave something here.", "drop {item}",
        [dict(name="item", prompt="Drop what?", options=inv)], enabled=p.inv, reason="You carry nothing.")
    gear = [_opt(i.name, i.name, f"damage {i.dmg}" if i.kind == "weapon" else f"protection {i.df}")
            for i in p.inv if i.kind in ("weapon", "armour") and i is not p.weapon and i is not p.armour]
    act("Items", "equip", "Equip…", "Wield a weapon or wear armour.", "equip {item}",
        [dict(name="item", prompt="Equip what?", options=gear)], enabled=gear, reason="Nothing new to wield or wear.")
    heals = [_opt(i.name, i.name, f"heals ~{i.heal}") for i in p.inv if i.heal]
    act("Items", "use", "Use / eat / drink…", "Use a healing item.", "use {item}",
        [dict(name="item", prompt="Use what?", options=heals)], enabled=heals, reason="You have nothing that heals.")
    act("Items", "inventory", "Inventory", "List what you carry.")

    # ------------------------------------------------------------ people
    people = [_opt(n.name, n.ref(), n.job + f" - {n.tier}") if n.known else _opt(f"The {n.job}", n.ref(), "not met yet")
              for n in t.npcs]
    no_one = "There's no one here."
    act("People", "talk", "Talk to…", "Greet someone and hear what they know.", "talk {who}",
        [dict(name="who", prompt="Talk to whom?", options=people)], enabled=people, reason=no_one)
    giftable = [_opt(i.name, i.name, i.kind) for i in p.inv if i.kind not in ("relic", "token")]
    act("People", "give", "Give…", "Give an item to someone. People remember gifts.", "give {item} to {who}",
        [dict(name="item", prompt="Give what?", options=giftable),
         dict(name="who", prompt="To whom?", options=people)],
        enabled=people and giftable, reason=no_one if not people else "You have nothing to give.")
    no_m = "There's no merchant here."
    act("People", "trade", "See wares", f"Step over to {m.called()}'s stall and see what's for sale." if m else "List what the merchant sells.",
        enabled=m, reason=no_m)
    first = f"See {m.called()}'s wares first." if m else no_m
    stock = [_opt(i.name, i.name, f"{g.buy_price(m, i)} coins" + ("" if g.buy_price(m, i) <= p.gold else " - can't afford"))
             for i in m.stock] if seen else []
    act("People", "buy", "Buy…", "Buy something from the merchant.", "buy {item}",
        [dict(name="item", prompt="Buy what?", options=stock)], enabled=seen and stock,
        reason=no_m if not m else first if not seen else "Sold out.")
    from . import story as S
    promised = S.quest_items(g) if hasattr(g, "quests") else set()
    sellable = [_opt(i.name, i.name, f"{g.sell_price(m, i)} coins") for i in p.inv if i.kind not in ("relic", "token") and i.name not in promised] if seen else []
    act("People", "sell", "Sell…", "Sell something you carry.", "sell {item}",
        [dict(name="item", prompt="Sell what?", options=sellable)], enabled=seen and sellable,
        reason=no_m if not m else first if not seen else "You have nothing to sell.")

    # ------------------------------------------------------------ fight
    foes = []
    for c in t.creatures:
        r = fight_risk(p, c)
        odds = "looks beatable" if r < 0.4 else "risky" if r < 0.8 else "dangerous"
        foes.append(_opt(c.name, c.species["arch"]["noun"], f"{odds}; {mind.intent(c)}ing" if mind.intent(c) != "hold" else f"{odds}; guarding"))
    if fighting:
        act("Fight", "attack", f"Attack the {g.combat.name}", "Strike at what you're fighting.", "attack")
    else:
        act("Fight", "attack", "Attack…", "Start a fight.", "attack {who}",
            [dict(name="who", prompt="Attack what?", options=foes)], enabled=foes, reason="There's nothing here to fight.")
    act("Fight", "flee", "Flee", "Break away and run in a random direction.", enabled=fighting, reason="You're not fighting anything.")

    # ------------------------------------------------------------ class abilities
    s = K.spec(p)
    if s:
        for key in s["abilities"]:
            a = K.ABILITIES[key]
            label = f"{a['label']}" + ("…" if a.get("target") and not fighting else "")
            desc = f"{a['desc']} ({a['cost']} {s['res']})"
            ok, why = True, ""
            if p.res < a["cost"]:
                ok, why = False, f"Needs {a['cost']} {s['res']}; you have {p.res}."
            elif a.get("combat_only") and not fighting:
                ok, why = False, "Only in a fight."
            elif a.get("peace_only") and fighting:
                ok, why = False, "Not mid-fight."
            elif a.get("target") and not fighting and not t.creatures:
                ok, why = False, "There's nothing here to use it on."
            if a.get("target") and not fighting:
                act(s["menu"], key, label, desc, f"{key} {{who}}",
                    [dict(name="who", prompt=f"{a['label']}: which?", options=foes)], enabled=ok, reason=why)
            else:
                act(s["menu"], key, label, desc, key, enabled=ok, reason=why)

    # ------------------------------------------------------------ rest & time
    village = bool(t.site and t.site["kind"] == "village")
    act("Rest & Time", "rest", "Rest", "Sleep in safety: fully healed." if village else "Rest in the wild: heals a third, but you may be found.",
        enabled=not fighting, reason="Not with an enemy at your throat.")
    act("Rest & Time", "wait", "Wait an hour", "Let time pass.", enabled=not fighting, reason="Not mid-fight.")
    shrine = bool(t.site and t.site["kind"] == "shrine")
    act("Rest & Time", "pray", "Pray", "Ask the shrine's spirit for healing (once per shrine).",
        enabled=shrine and not t.site.get("used"), reason="Only at a shrine." if not shrine else "This shrine has already answered you.")

    # ------------------------------------------------------------ info
    act("Info", "journal", "Journal", "Your quests, and what you're under (luck, curses...).")
    act("Info", "chronicle", "Chronicle", "Everything notable that has happened.")
    act("Info", "status", "Status", "Your health, level and gear.")
    act("Info", "map", "Text map", "Print the map into the story log.")
    act("Info", "help", "All commands", "Every typed command, at a glance.")

    # ------------------------------------------------------------ game
    saves = [s.stem for s in g.list_saves()]
    act("Game", "manage", "Manage saves…", "See every save with its details; load, rename or delete them.",
        "saves", ui="saves")
    act("Game", "save", "Save…", "Save your progress to a named slot.", "save {slot}",
        [dict(name="slot", prompt="Save to which slot?", text="quicksave", choices=saves)],
        enabled=not fighting, reason="You can't save mid-fight.")
    act("Game", "load", "Load…", "Return to a saved game.", "load {slot}",
        [dict(name="slot", prompt="Load which save?", options=[_opt(s, s) for s in saves])],
        enabled=saves, reason="No saves yet.")
    return out
