"""Next-action advisor: looks at the game state and proposes a handful of
sensible commands, each with a short reason. Purely advisory - the player can
always type anything."""
from collections import deque
from dataclasses import dataclass, field

from .world import DIRS
from . import mind
from . import classes as K
from . import goods as GOODS


@dataclass
class Suggestion:
    cmd: str            # exactly what gets typed
    label: str          # short human label
    why: str            # one-line reason
    score: float
    path: list = field(default_factory=list)   # map positions, for travel suggestions
    travel: bool = False


def path_to(world, start, goal, avoid=frozenset()):
    """Shortest walkable path (excluding start), or [] if unreachable. Tiles in
    `avoid` are only entered if they are the goal."""
    if start == goal:
        return []
    prev, dq = {start: None}, deque([start])
    while dq:
        p = dq.popleft()
        if p == goal:
            break
        for _, n in world.neighbours(p):
            if n in world.land and n not in prev and (n not in avoid or n == goal):
                prev[n] = p
                dq.append(n)
    if goal not in prev:
        return []
    out, p = [], goal
    while p != start:
        out.append(p)
        p = prev[p]
    return out[::-1]


def step_dir(a, b):
    for name, (dx, dy) in DIRS.items():
        if (a[0] + dx, a[1] + dy) == b:
            return name
    return None


def spell_power(player):
    """Per-turn damage the class's best attack ability deals while its resource lasts."""
    k, lvl = getattr(player, "klass", None), player.level
    if k == "wizard" and player.res >= 3:
        return 8 + 2 * (lvl - 1), player.res // 3
    if k == "cleric" and player.res >= 2:
        return 5.5 + (lvl - 1), player.res // 2
    return 0, 0


def fight_risk(player, c):
    """Rough expected fraction of current HP lost killing this creature."""
    hit = min(0.95, max(0.2, (16 + player.atk - c.df) / 20))
    per_turn = max(1, player.atk + 1.5 - c.df) * hit
    power, casts = spell_power(player)
    if power > per_turn and casts:
        # spells first, then the weapon: average over the likely fight
        melee = per_turn
        spell_turns = min(casts, c.hp / power)
        left = max(0.0, c.hp - spell_turns * power)
        per_turn = c.hp / max(0.5, spell_turns + left / melee)
    turns = c.hp / per_turn
    enemy_hit = min(0.95, max(0.05, (10 + c.atk - player.df) / 20))
    taken = turns * enemy_hit * max(0.5, c.atk - 0.5 - player.df)
    return 1.4 * taken / max(1, player.hp)      # pessimistic: bad luck kills


def heal_choice(player, heals):
    """Smallest healing item that covers the missing HP, else the biggest."""
    missing = player.maxhp - player.hp
    enough = [i for i in heals if i.heal >= missing * 0.7]
    return min(enough, key=lambda i: i.heal) if enough else max(heals, key=lambda i: i.heal)


def suggest(g, n=6):
    w, p = g.world, g.player
    t = w.tiles[g.pos]
    out = []

    def add(score, cmd, label, why, path=None, travel=False):
        out.append(Suggestion(cmd, label, why, score, path or [], travel))

    hp = p.hp / p.maxhp
    heals = [i for i in p.inv if i.heal]
    # tiles you've seen holding something you shouldn't walk into
    avoid = frozenset(q for q in w.land if q != g.pos and w.tiles[q].visited and any(
        fight_risk(p, c) >= 0.5 or (mind.intent(c) == "hold" and fight_risk(p, c) >= 0.3)
        for c in w.tiles[q].creatures))
    route_to = lambda q: path_to(w, g.pos, q, avoid)
    turns = getattr(g, "turns", 0)
    novice = turns < 40

    # ---------------------------------------------------------------- a choice is waiting
    pend = getattr(g, "pending", None)
    if pend and not g.over:
        for i, o in enumerate(pend["options"], 1):
            out.append(Suggestion(str(i), o["label"], "Your choice." if i > 1 else "Your choice - every option leads somewhere.", 200 - i, [], False))
        return out[:n]

    # ---------------------------------------------------------------- game over
    if g.over:
        if g.died or not g.won:
            mine = g.list_saves(getattr(g, "run_id", None)) if getattr(g, "run_id", None) else []
            for i, s in enumerate(mine[:4] or g.list_saves()[:4]):
                ref = s.stem if mine else f"{s.parent.name}/{s.stem}"
                add(100 - i, f"load {ref}", f"Load '{s.stem}'", "Pick up from that save.")
        return _finish(out, n, getattr(g, 'recent_cmds', []))

    # ---------------------------------------------------------------- combat
    if g.combat:
        c = g.combat
        cname = c.name
        risk = fight_risk(p, c)
        enemy_hit = max(1, c.atk - 0.5 - p.df)
        useful = [i for i in heals if i.heal >= 1.5 * enemy_hit]
        if hp < 0.45 and useful:
            it = heal_choice(p, useful)
            add(93 if risk < 1.0 else 75, f"use {it.name}", f"Use the {it.name}",
                f"Heals about {it.heal}; it hits for roughly {enemy_hit:.0f}.")
        foe = c.hp / c.maxhp
        foe_intent = mind.intent(c)
        if foe_intent == "flee" and risk < 1.0:
            add(88, "attack", f"Attack the {cname}", "It's trying to escape - finish it before it bolts.")
        elif foe_intent == "stalk" and risk < 1.0:
            add(87, "attack", f"Attack the {cname}", "It's circling, waiting for an opening - strike while it hesitates. Its next blow will be a hard one.")
        if risk >= 1.0:
            add(90, "flee", "Flee!", "At this rate it will kill you before you kill it.")
            add(40, "attack", f"Attack the {cname}", "A long shot. Only if you feel lucky.")
        elif risk >= 0.6:
            add(72, "attack", f"Attack the {cname}", "You can probably win, but it will cost you." if foe > 0.35 else "It's nearly finished - press the attack.")
            add(58, "flee", "Flee", "Live to fight another day; it may get a parting blow.")
        else:
            add(86, "attack", f"Attack the {cname}", "It's nearly finished - press the attack." if foe < 0.35 else "Trade blows; you look the stronger.")
            add(30, "flee", "Flee", "Running usually works, but it may get a free hit.")
        add(20, f"examine {c.species['arch']['noun']}", f"Size up the {cname}", "Looking costs no time, even mid-fight.")
        _class_combat(g, add, c, risk, hp)
        return _finish(out, n, getattr(g, 'recent_cmds', []))

    # ---------------------------------------------------------------- survival
    village = bool(t.site and t.site["kind"] == "village")
    shrine_here = bool(t.site and t.site["kind"] == "shrine" and not t.site["used"])
    if shrine_here and hp < 0.95:
        add(88, "pray", "Pray at the shrine", "Shrines heal you fully, once, and toughen you a little.")
    if hp < 0.5:
        if heals:
            it = heal_choice(p, heals)
            add(86, f"use {it.name}", f"Use the {it.name}", f"You're hurt; it heals about {it.heal}.")
        if village:
            add(84, "rest", "Rest the night", "Sleeping in a village is safe and heals you fully.")
        elif hp < 0.35:
            add(66, "rest", "Rest a while", "Heals a third of your health, but something might find you.")
        shrines = [q for q in w.land if w.tiles[q].visited and w.tiles[q].site
                   and w.tiles[q].site["kind"] == "shrine" and not w.tiles[q].site["used"] and q != g.pos]
        if shrines:
            target = min(shrines, key=lambda q: len(route_to(q)) or 99)
            route = route_to(target)
            if route:
                d = step_dir(g.pos, route[0])
                add(64, d, f"Go {d}, toward the shrine", f"An unused shrine you found is {len(route)} steps away.", route, True)
    if hp < 0.6 and not village:
        homes = [q for q in w.villages if w.tiles[q].visited]
        routes = [r for r in (route_to(q) for q in homes) if r]
        if routes:
            route = min(routes, key=len)
            d = step_dir(g.pos, route[0])
            vname = w.tiles[route[-1]].site["name"]
            add(68 if not heals else 50, d, f"Go {d}, back to {vname}", f"Rest safely there. {len(route)} steps.", route, True)
    if village and w.is_dark:
        add(58, "rest", "Sleep until morning", "The wilds are more dangerous after dark.")

    # ---------------------------------------------------------------- people
    elder = next((x for x in t.npcs if x.role == "elder"), None)
    if elder and not g.has_quest:
        if w.quest.carried(g):
            add(98, f"talk {elder.ref()}", f"Talk to {elder.called()}", f"{elder.pronouns()['he'].capitalize()}'s staring at what you carry.")
        else:
            add(93, f"talk {elder.ref()}", f"Talk to {elder.called()}", f"{elder.pronouns()['he'].capitalize()} seems to be waiting for someone. This starts the main quest.")
    for x in t.npcs:
        if x is elder and not g.has_quest:
            continue
        if x.mem["met"] == 0:
            add(74, f"talk {x.ref()}", f"Talk to {x.called()}",
                "You haven't met. People share rumours, and they remember you.")
        elif x.mem["last_day"] < w.day:
            add(38, f"talk {x.ref()}", f"Catch up with {x.name}", f"{x.pronouns()['he'].capitalize()} may have fresh news since you last spoke.")
    for s_ in g.sellers():
        if s_.role != "merchant" and not s_.mem.get("wares_seen"):
            add(46, f"trade {s_.ref()}", f"See {s_.name}'s wares", f"{s_.pronouns()['he'].capitalize()} sells {GOODS.WARES_WORDS.get(s_.job, 'a few things')}.")
            break
    if village:
        from . import travel as TR
        if TR.rations(g) < 3 and p.gold >= 3 * TR.RATION_PRICE + 10:
            add(52, "buy rations", "Buy travel rations", f"Food for the road, {TR.RATION_PRICE} coins each. With rations you can travel back to anywhere you've been ('travel').")
    m = g.merchant()
    if m and not m.mem.get("wares_seen"):
        add(50, "trade", f"See what {m.called()} sells", f"Merchants buy as well as sell. You have {p.gold} coins.")
    elif m:
        if any(g.buy_price(m, it) <= p.gold for it in m.stock):
            add(48, "trade", f"See what {m.name} sells", f"You have {p.gold} coins to spend.")
        from . import story as S
        junk = [it for it in p.inv if it.kind == "trinket" and it.name not in S.quest_items(g)]
        if junk:
            add(54, f"sell {junk[0].name}", f"Sell the {junk[0].name}", f"Trinkets are only good for coin (~{g.sell_price(m, junk[0])}).")

    # ---------------------------------------------------------------- items & gear
    for it in t.items:
        why = {"relic": "This is what you came for!" if g.has_quest else "It looks old, and important to someone.", "weapon": "A weapon - possibly better than yours.",
               "armour": "Armour reduces the damage you take.", "potion": "Potions heal a lot, fast.",
               "herb": "Herbs heal a little.", "food": "Food heals a little.", "trinket": "Worth coin to a merchant.",
               "book": "A book - perhaps something you could learn from.", "scroll": "A scroll: one spell or prayer, if you can read it."}.get(it.kind, "Might be useful.")
        add(99 if it.kind == "relic" else 70, f"take {it.name}", f"Pick up the {it.name}", why)
    cur_dmg = p.weapon.dmg if p.weapon else 0
    best_w = max((i for i in p.inv if i.kind == "weapon"), key=lambda i: i.dmg, default=None)
    if best_w and best_w.dmg > cur_dmg:
        add(80, f"equip {best_w.name}", f"Wield the {best_w.name}", f"Damage {best_w.dmg}, versus {cur_dmg} now.")
    cur_df = p.armour.df if p.armour else 0
    best_a = max((i for i in p.inv if i.kind == "armour"), key=lambda i: i.df, default=None)
    if best_a and best_a.df > cur_df:
        add(80, f"equip {best_a.name}", f"Put on the {best_a.name}", f"Protection {best_a.df}, versus {cur_df} now.")

    # ---------------------------------------------------------------- creatures
    lurking = False
    guard = None
    for c in t.creatures:
        noun = c.species["arch"]["noun"]
        risk = fight_risk(p, c)
        it = mind.intent(c)
        if it in ("stalk", "hunt", "hold"):
            lurking = True
        if it == "hold" and risk >= 0.4:
            guard = c.name
        if it == "stalk":
            add(52 if risk < 0.6 else 24, f"attack {noun}", f"Confront the {c.name}",
                "It's stalking you, and will strike when you're weak or asleep. Better to face it now." if risk < 0.6 else
                "It's stalking you, but it's dangerous. Moving on may be wiser; it may follow.")
        if it == "flee":
            add(30, f"attack {noun}", f"Chase down the {c.name}", "It's skittish and will likely bolt.")
        if c.boss and risk >= 0.6:
            add(5, f"attack {noun}", f"Fight {c.name}", "Suicide, at your strength. Leave while you can.")
            continue
        if risk < 0.4:
            add(62, f"attack {noun}", f"Fight the {c.name}", f"Looks beatable. Worth {c.xp} experience.")
        elif risk < 0.8:
            add(32, f"attack {noun}", f"Fight the {c.name}", "A real risk - heal up first if you can.")
        else:
            add(15, f"attack {noun}", f"Fight the {c.name}", "Dangerous: it is likely stronger than you.")
            add(56, f"examine {noun}", f"Size up the {c.name}", "It looks dangerous. Consider leaving.")
        if novice and risk < 1.0:
            add(30, f"examine {noun}", f"Look closely at the {c.name}", "See how hurt and how hostile it is.")

    if lurking:
        for s_ in out:
            if s_.cmd == "rest":
                s_.score -= 70
                s_.why += " But something here is watching you."

    _class_peace(g, add, t, hp)
    _living(g, add, t, route_to, novice)

    # ---------------------------------------------------------------- flavour for newcomers
    examined = getattr(g, "examined", set())
    if novice:
        for f in t.features:
            if (g.pos, f.noun) not in examined:
                add(28, f"examine {f.noun}", f"Examine the {f.noun}", "Every close look is written afresh.")
                break
        if turns < 3:
            add(25, "help", "List every command", "Everything you can type, at a glance.")

    # ---------------------------------------------------------------- travel
    qa = w.quest.act(g) if g.has_quest else None
    if qa:
        add(95, *qa)
    st = w.quest.step(g) if g.has_quest else None
    if st:
        goal, what, why, ready = st
        route = route_to(goal) if goal != g.pos else []
        guarded = any(c.boss for c in w.tiles[goal].creatures)
        boss = next((c for c in w.tiles[goal].creatures if c.boss), None)
        if boss and ready and fight_risk(p, boss) >= 0.8:
            ready = False                         # level alone isn't enough: the odds have to be there
        if guarded and ready and route and len(route) <= 3 and hp < 0.85 and not g.combat:
            ready = False                         # never walk up to a boss hurt: rest first
            add(62, "rest", "Rest before going on", "What waits ahead is the worst thing in this land. Go to it whole.")
        if route:
            d = step_dir(g.pos, route[0])
            homeward = goal == w.start
            if homeward or ready:
                add(90 if homeward else 57, d, f"Go {d}, {what}", f"{why} {len(route)} steps to go.", route, True)
            else:
                near = len(route) <= 2
                add(4 if near else 14, d, f"Go {d}, {what}",
                    f"{len(route)} steps - but what waits there would likely kill you at level {p.level}." if near else
                    f"{len(route)} steps. Grow stronger first: what waits there is deadly.", route, True)
            from . import travel as TR
            if (homeward or ready) and len(route) > 5 and not TR.blocked(g) and w.tiles[goal].visited:
                tpath, mins = TR.route(g, goal)
                if tpath and TR.rations(g) >= TR.need(mins):
                    name = TR.label(w, goal)
                    add(92 if homeward else 59, f"travel {name}", f"Travel to {name}", f"{TR.how_long(mins)} on the road, {TR.need(mins)} rations. Quicker than walking it step by step.")
    unexplored = []
    for d, q in w.neighbours(g.pos):
        if q in w.land and not w.tiles[q].visited:
            new_region = not any(w.tiles[r].visited and w.tiles[r].region == w.tiles[q].region for r in w.land)
            unexplored.append((new_region, d, q))
    unexplored.sort(key=lambda x: (not x[0], x[1]))
    unexplored.sort(key=lambda x: (w.tiles[x[2]].danger > p.level, not x[0], x[1]))
    for new_region, d, q in unexplored[:2]:
        kind = {"forest": "woodland", "marsh": "marsh", "plains": "open country", "hills": "hills", "peaks": "mountains"}[w.tiles[q].biome]
        if w.tiles[q].danger > p.level:
            add(18, d, f"Explore {d}", f"Unexplored {kind}, but the land grows dangerous for your level.", [q], True)
        else:
            add(44 if new_region else 36, d, f"Explore {d}", f"Unexplored {kind}" + (", somewhere new." if new_region else "."), [q], True)
    if hp < 0.6:
        for s_ in out:
            if s_.travel and "back to" not in s_.label and "shrine" not in s_.label:
                s_.score -= 25
    # nothing good nearby? head for the nearest unexplored land that suits your strength
    if not any(x.travel and x.score >= 30 for x in out):
        safe = [q for q in w.land if not w.tiles[q].visited and w.tiles[q].danger <= p.level and q != w.quest_pos]
        routes = [r for r in (route_to(q) for q in safe) if r and w.quest_pos not in r]
        if routes:
            route = min(routes, key=len)
            d = step_dir(g.pos, route[0])
            add(34, d, f"Head {d}", f"Toward unexplored land that suits your strength ({len(route)} steps).", route, True)
    if False:
        frontier = []
        if frontier:
            target = min(frontier, key=lambda q: abs(q[0] - g.pos[0]) + abs(q[1] - g.pos[1]))
            route = route_to(target)
            if route:
                d = step_dir(g.pos, route[0])
                add(34, d, f"Head {d}", "Toward the nearest land you haven't seen.", route, True)

    # a guardian that would beat you: leave, along the best route already found
    if guard:
        exits = [d for d, q in w.neighbours(g.pos) if q in w.land and q not in avoid]
        best_travel = max((x for x in out if x.travel and x.cmd in exits), key=lambda x: x.score, default=None)
        d = best_travel.cmd if best_travel else (exits[0] if exits else None)
        if d:
            add(60, d, f"Leave {d}", f"The {guard} is guarding this ground. It warned you; it won't follow.", travel=True)

    # ---------------------------------------------------------------- housekeeping
    if turns - getattr(g, "last_save_turn", 0) > 60:
        add(22, "save", "Save your game", "It's been a while. (Quitting also autosaves.)")
    return _finish(out, n, getattr(g, 'recent_cmds', []))


def _living(g, add, t, route_to, novice):
    """Quests, troubles and landmarks."""
    from . import story as S, secrets as SEC, living as LV
    w, p = g.world, g.player
    if g.combat:
        return
    # hand-ins to people here
    for q in S.active(g):
        giver = next((n for n in t.npcs if n.name == q["giver"]), None)
        if giver:
            has = q["kind"] == "bring" and (q["data"].get("message") or S.bring_match(g, q) is not None)
            if has or (q["kind"] == "slay" and q["stage"] == "slain"):
                add(96, f"talk {giver.ref()}", f"Talk to {giver.name}", f"Finish: {q['title']}.")
    # standing where an errand points
    for q in S.active(g):
        if q["kind"] == "find" and q["data"].get("search") and q["target"] == g.pos:
            noun = q["data"].get("noun")
            f = next((x for x in t.features if x.noun == noun), None)
            sec = (f.state or {}).get("secret") if f else None
            if f and sec and not sec["found"]:
                add(92, f"{sec['verbs'][0]} {f.noun}", f"{sec['verbs'][0].capitalize()} the {f.noun}", f"This is where it pointed: {q['title']}.")
    # quest destinations: keep to one errand at a time, so two in opposite directions don't pull you back and forth
    best = None
    focus = getattr(g, "advisor_focus", None)
    for q in sorted(S.active(g), key=lambda q: (q["id"] != focus, q["id"])):
        target = q["target"]
        if q["kind"] == "bring" and not q["data"].get("message"):
            ready = S.bring_match(g, q) is not None
            target = q["giver_home"] if ready else None
            if not ready:          # something a stall sells: buy it if it's here
                for s_ in g.sellers():
                    if not s_.mem.get("wares_seen"):
                        continue
                    want = next((it for it in s_.stock if it.name == q["item"] or it.kind == q["data"].get("any_kind") or it.name in q["data"].get("any_name", ())), None)
                    if want and g.buy_price(s_, want) <= p.gold:
                        add(80, f"buy {want.name}", f"Buy the {want.name}", f"For: {q['title']}.")
                        break
        elif q["kind"] == "bring":
            target = q["giver_home"]
        elif q["kind"] == "slay" and q["stage"] == "slain":
            target = q["giver_home"]
        elif q["kind"] == "slay":     # follow the creature, wherever it has wandered
            target = next((pp for pp, tt in w.tiles.items() if q["creature"] in tt.creatures), None)
        if not target or target == g.pos:
            continue
        route = route_to(tuple(target))
        if q["kind"] == "slay" and q["stage"] != "slain" and fight_risk(p, q["creature"]) >= 0.5:
            continue
        if route and (best is None or (q["id"] == focus and best[0]["id"] != focus) or
                      (best[0]["id"] != focus and len(route) < len(best[1]))):
            best = (q, route)
    if best:
        q, route = best
        g.advisor_focus = q["id"]
        d = step_dir(g.pos, route[0])
        score = 56 if q["kind"] in ("escort", "deliver") else 50
        add(score, d, f"Go {d}: {q['title']}", f"{len(route)} steps.", route, True)
    # a village asking for help
    site = t.site
    trouble = site.get("trouble") if site and site["kind"] == "village" else None
    if trouble and not trouble.get("accepted"):
        giver = next((n for n in t.npcs if n.name == trouble["giver"]), None)
        if giver:
            add(72, f"talk {giver.ref()}", f"Talk to {giver.called()}", f"Something is wrong in this village; {giver.pronouns()['he']} looks like {giver.pronouns()['he']} needs help.")
    # landmarks: answer what the land is hinting at, otherwise poke around now and then
    done_here = False
    for f in t.features:
        sec = (f.state or {}).get("secret")
        if sec and SEC.ready(w, sec) and sec["key"] in SEC.HINTS:
            add(66, f"{sec['verbs'][0]} {f.noun}", f"{sec['verbs'][0].capitalize()} the {f.noun}", "Something about it caught your eye.")
            done_here = True
    if not done_here:
        for f in t.features:
            done = (f.state or {}).get("done", [])
            if "search" not in done:
                add(38 if novice else 26, f"search {f.noun}", f"Search the {f.noun}", "Landmarks keep secrets; some only show themselves at night, or in fog.")
                break
        for f in t.features:
            if SEC.can("climb", f) and "climb" not in (f.state or {}).get("done", []) and any(
                    not w.tiles[q].visited for q in w.land if abs(q[0] - g.pos[0]) + abs(q[1] - g.pos[1]) <= 2):
                add(30, f"climb {f.noun}", f"Climb the {f.noun}", "See the land around from up high.")
                break


def _can(g, key):
    p = g.player
    return key in K.known(p) and p.res >= K.ABILITIES[key]["cost"]


def _learned_combat(g, add, c, risk, hp):
    """The arts learned from books: suggest them by what they do."""
    from . import arts as ARTS
    p, res = g.player, K.res_name(g.player)
    for key in K.known(p):
        if key not in ARTS.ARTS or not _can(g, key) or ARTS.ARTS[key].get("peace_only"):
            continue
        a = ARTS.ARTS[key]
        kinds = {k for k, _ in a["fx"]}
        tip = f"{a['desc']} ({a['cost']} {res})"
        if "heal" in kinds and hp < 0.45:
            add(95, key, a["label"], tip)
        elif ("ward" in kinds or "guard" in kinds) and hp < 0.5 and not p.ward:
            add(90, key, a["label"], tip)
        elif "escape" in kinds and (risk >= 1.0 or hp < 0.3):
            add(93, key, a["label"], tip)
        elif "flee" in kinds and risk >= 0.8 and not c.boss:
            add(91, key, a["label"], tip)
        elif "execute" in kinds and c.hp <= c.maxhp * 0.4 and not c.boss:
            add(94, key, a["label"], tip)
        elif "stun" in kinds and not c.mind.get("stunned"):
            add(84, key, a["label"], tip)
        elif "dmg" in kinds:
            add(82 + min(8, ARTS.school_of(key)[1] * 2), key, a["label"], tip)


def _study(g, add):
    """Books you could learn from now, and growth points waiting."""
    from . import arts as ARTS
    p = g.player
    if g.combat:
        return
    for it in p.inv:
        if it.kind == "book" and ARTS.can_read(p, it):
            key = ARTS._settle(g, it)
            if ARTS.can_learn(p, key)[0]:
                add(58, f"read {it.name}", f"Study the {it.name}", f"It teaches {K.ABILITIES[key]['label']}; a few quiet hours would do it.")
                break
    from . import crafts as CR
    for k, opts in CR.honeable(p):
        add(43, f"hone {k} {opts[0][1].split()[0].lower()}", f"Hone your {K.ABILITIES[k]['label']}",
            f"You've practised it enough: it could become {opts[0][1]} or {opts[1][1]}. ('hone' to compare.)")
        break
    for school in ("arcane", "divine"):
        wv = CR.WEAVES[school]
        if ARTS.literate(p, school) and any(i.name == wv["material"] for i in p.inv):
            made = {s["label"] for s in p.crafted.values()}
            fresh = [r for r in CR.recipes(p, school) if r[4]["label"] not in made and r[4]["label"] not in {K.ABILITIES[x]["label"] for x in p.known}]
            if fresh and len(p.crafted) < 2:
                pr, sh, tw, sec, spec = max(fresh, key=lambda r: r[4]["circle"])
                add(36, f"{wv['verb']} {' '.join(x for x in (pr, sh, tw, sec) if x)}", f"{wv['craft']}: {spec['label']}",
                    f"Your {wv['material']} could make something new: {spec['desc']}")
    room = [k for k in ARTS.STATS if ARTS.stat(p, k) < ARTS.STAT_MAX]
    if getattr(p, "points", 0) and room:
        mine = ARTS.SCHOOLS.get(ARTS.own_school(p) or "", {}).get("stat")
        best = max(room, key=lambda k: (bool(ARTS.near_hint(p, k)), k == mine, -ARTS.stat(p, k)))
        add(44, f"improve {best}", "Spend your growth point", f"You've a point to spend on might, grace, wits or spirit ({best} looks promising).")


def _class_combat(g, add, c, risk, hp):
    p, res = g.player, K.spec(g.player)["res"] if K.spec(g.player) else ""
    undead = c.species["arch"].get("undead", False)
    cost = lambda k: f"({K.ABILITIES[k]['cost']} {res})"
    if _can(g, "heal") and hp < 0.45:
        add(96, "heal", "Heal", f"Mend your wounds mid-fight {cost('heal')}.")
    if _can(g, "ward") and hp < 0.5 and not p.ward:
        add(91, "ward", "Cast ward", f"Soak up the next blows {cost('ward')}.")
    if _can(g, "fear") and risk >= 0.8 and not c.boss and mind.intent(c) != "flee":
        add(93, "fear", "Cast fear", f"Terrify it into fleeing; bold creatures may resist {cost('fear')}.")
    if _can(g, "turn") and undead and not c.boss and risk >= 0.6:
        add(92, "turn", "Turn undead", f"Command the dead thing to flee {cost('turn')}.")
    if _can(g, "firebolt"):
        add(89, "firebolt", "Cast firebolt", f"Fire ignores armour - about {8 + 2 * (p.level - 1)} damage {cost('firebolt')}.")
    if _can(g, "smite"):
        add(90 if undead else 84, "smite", "Smite", ("Doubled against the undead! " if undead else "Ignores armour. ") + cost("smite"))
    if _can(g, "bash") and not c.mind.get("stunned"):
        add(87 if risk >= 0.4 else 80, "bash", "Shield bash", f"Damage, and a good chance it loses its next turn {cost('bash')}.")
    if _can(g, "guard") and hp < 0.5 and not p.guard:
        add(88, "guard", "Raise your guard", f"Halve the next two blows while you recover {cost('guard')}.")
    if _can(g, "vanish") and (risk >= 1.0 or hp < 0.3):
        add(94, "vanish", "Vanish", f"Slip away and hide - then strike again from hiding {cost('vanish')}.")
    if _can(g, "backstab") and getattr(p, "hidden", 0):
        add(95, "backstab", "Backstab", f"You're hidden: triple damage {cost('backstab')}.")
    if _can(g, "shoot"):
        add(81, "shoot", "Shoot", f"A solid arrow at close range {cost('shoot')}.")
    _learned_combat(g, add, c, risk, hp)
    for it in p.inv:
        use = it.facts.get("use") if it.kind in ("tool", "potion", "charm") else None
        if use == "holy" and undead:
            add(92, f"use {it.name}", f"Throw the {it.name}", "Holy water scalds the dead.")
        elif use == "smoke" and (risk >= 1.0 or hp < 0.25):
            add(95, f"use {it.name}", f"Smash the {it.name}", "Vanish in a cloud of smoke.")
        elif use == "clarity" and p.res < p.res_max // 3:
            add(80, f"use {it.name}", f"Drink the {it.name}", "Refill your well of power.")


def _class_peace(g, add, t, hp):
    p, s = g.player, K.spec(g.player)
    if not s:
        return
    res = s["res"]
    if _can(g, "heal") and hp < 0.6:
        add(87, "heal", "Heal", f"Mend your wounds ({K.ABILITIES['heal']['cost']} {res}) - cheaper than resting.")
    _study(g, add)
    for it in p.inv:
        use = it.facts.get("use") if it.kind in ("tool", "potion", "charm") else None
        if use == "picks" and t.site and t.site["kind"] in ("ruin", "camp") and t.site.get("box") != "open" and not t.creatures:
            add(57, f"use {it.name}", "Look for a strongbox to pick", "Ruins and abandoned camps sometimes hide a locked box.")
        elif use == "arrows" and _can(g, "shoot") and not (getattr(p, "arrows", None) or {}).get("left"):
            add(40, f"use {it.name}", f"Fill your quiver: {it.name}", "Your next three shots hit harder.")
    for key in ("poultice", "rally", "purify"):
        if _can(g, key) and hp < 0.6:
            add(86, key, K.ABILITIES[key]["label"], f"{K.ABILITIES[key]['desc']} ({K.ABILITIES[key]['cost']} {res})")
            break
    for c in t.creatures:
        noun = c.species["arch"]["noun"]
        risk = fight_risk(p, c)
        if c.boss and risk >= 0.6:
            continue
        if _can(g, "backstab") and mind.intent(c) in ("wander", "stalk", "hold", "flee") and risk < 1.3:
            add(76, f"backstab {noun}", f"Backstab the {c.name}", "It isn't fighting you yet: triple damage from the shadows.")
        if _can(g, "shoot") and risk < 1.1:
            add(70, f"shoot {noun}", f"Shoot the {c.name}", "Open from range: it can't strike back this turn.")
        if _can(g, "firebolt") and risk < 1.0:
            add(66, f"firebolt {noun}", f"Firebolt the {c.name}", "Open with fire before it reaches you.")
        if _can(g, "smite") and c.species["arch"].get("undead") and risk < 1.0:
            add(68, f"smite {noun}", f"Smite the {c.name}", "Holy force, doubled against the undead.")
    if _can(g, "track") and not t.creatures and getattr(g, "turns", 0) % 7 == 0:
        add(27, "track", "Track", "Read what lurks on the neighbouring tiles, and what it intends.")
    if s and p.res < p.res_max // 3 and not g.combat and not t.creatures:
        add(26, "wait", "Catch your breath", f"Low on {res}: it returns as you travel, wait, or rest.")


INFO_VERBS = {"trade", "examine", "look", "help", "status", "inventory", "saves", "sell", "talk"}


def _finish(out, n, recent=()):
    # don't keep recommending something that only shows information and was just done
    recent = list(recent)
    for s in out:
        verb = s.cmd.split()[0]
        if verb in INFO_VERBS and s.cmd in recent[-6:]:
            s.score -= 70
    best = {}
    for s in out:
        if s.cmd not in best or s.score > best[s.cmd].score:
            best[s.cmd] = s
    ranked = sorted(best.values(), key=lambda s: -s.score)
    top = ranked[:n]
    # always keep one way to move on, if there is one
    if top and not any(s.travel for s in top):
        mover = next((s for s in ranked[n:] if s.travel), None)
        if mover:
            top[-1] = mover
    return top
