"""Rations and fast travel.

Travel rations come from those who have food to spare: travelling merchants, and the miller or
eel-catcher who keeps a stall (each has only so many, and restocks every few days with the rest of
their goods). They also turn up as loot: in caches, camps and strongboxes. With
rations in your pack, `travel <place>` takes you to anywhere you have already been: a village, a
ruin, a shrine, a camp, or any landmark. The way follows roads where it can and known country
where it must. It costs a ration for each half-day of walking, the days really pass, and the road
can still surprise you: a stop on the way may bring an encounter, and something hunting the
country you cross may cut the journey short. You won't walk blind into danger: if something is
waiting at the place you name, you stop a square short.
"""
import heapq
import math

from . import mind
from .textgen import cap

RATION_PRICE = 5
RATION_MAX = 10
START_RATIONS = 2
WALK_DAY = 600          # minutes of walking in a travelling day; the rest is camp and sleep
PER_RATION = 300        # minutes of walking one ration covers (half a day)
NIGHT = 14 * 60


# who keeps food for the road: merchants who carry food, and the stall-folk who make it
RATION_TRADES = {"pedlar", "packman", "trader", "huckster", "horse-coper", "miller", "eel-catcher"}
PACKS = ["oilcloth packet", "bundle", "cloth-wrapped parcel", "knotted bag"]


def rations(g):
    return getattr(g.player, "rations", 0)


def sells_rations(npc):
    return npc.job in RATION_TRADES


def supply(npc, rng=None):
    """How many rations this seller has left (set on first asking, and at each restock). The first
    count comes from the seller's own name, so merely looking (the advisor, the menus) never
    disturbs the game's dice."""
    if "rations" not in npc.mem:
        import random
        restock(npc, random.Random(f"rations-{npc.name}"))
    return npc.mem["rations"]


def restock(npc, rng):
    npc.mem["rations"] = rng.randint(4, 8) if npc.role == "merchant" else rng.randint(2, 5)


def ration_item(rng, n=None):
    """Rations found as loot: an Item that folds into your ration count once it's in your pack."""
    from .world import Item
    n = n or rng.choice([1, 2, 2, 3])
    pack = rng.choice(PACKS)
    return Item("ration", pack_name(pack, n), value=n * RATION_PRICE, facts=dict(n=n, pack=pack))


def pack_name(pack, n):
    if n == 1:
        return "travel ration wrapped in a cloth"
    return f"{pack} of {n} travel rations"


def describe(it):
    n = it.facts.get("n", 1)
    return (f"{cap(it.name)}: oatcakes, hard cheese and dried meat, still good. Enough for {n} half-day{'s' if n != 1 else ''} on the road "
            f"when you travel ('travel'). In your pack it goes in with your other rations.  (worth ~{it.value} coins)")


def fold(g):
    """Any ration packets in your pack become part of your ration count, as far as there's room."""
    p = g.player
    before = rations(g)
    for it in [i for i in p.inv if i.kind == "ration"]:
        room = RATION_MAX - rations(g)
        n = it.facts.get("n", 1)
        take = min(room, n)
        if take <= 0:
            break
        add_rations(g, take)
        if take == n:
            p.inv.remove(it)
        else:
            it.facts["n"] = n - take
            it.name = pack_name(it.facts.get("pack", "bundle"), n - take)
            it.value = (n - take) * RATION_PRICE
    if rations(g) > before:
        full = any(i.kind == "ration" for i in p.inv)
        g.emit(f"(The food goes in with your rations: you carry {rations(g)}" + (", as many as you can, and keep the rest aside.)" if full else ".)"))


def add_rations(g, n):
    g.player.rations = min(RATION_MAX, rations(g) + n)


def known(w, p):
    t = w.tiles[p]
    return t.visited or getattr(t, "glimpsed", False)


def step_minutes(g, a, b):
    w = g.world
    if w.road_between(a, b):
        return 20
    rough = w.tiles[b].biome in ("marsh", "peaks") and g.klass() != "ranger"
    return 35 + (20 if rough else 0)


def route(g, dest):
    """The quickest way to dest over country you know: (path, walking minutes), or ([], 0)."""
    w = g.world
    start = g.pos
    best, prev, pq = {start: 0}, {}, [(0, start)]
    while pq:
        c, p = heapq.heappop(pq)
        if p == dest:
            break
        if c > best.get(p, 1e9):
            continue
        for _, n in w.neighbours(p):
            if n not in w.land or not known(w, n):
                continue
            nc = c + step_minutes(g, p, n)
            if nc < best.get(n, 1e9):
                best[n], prev[n] = nc, p
                heapq.heappush(pq, (nc, n))
    if dest not in best:
        return [], 0
    path = [dest]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return path[::-1], best[dest]


def need(minutes):
    return max(1, math.ceil(minutes / PER_RATION))


def how_long(minutes):
    if minutes < WALK_DAY / 2 - 30:
        h = max(1, round(minutes / 60))
        return "an hour" if h == 1 else f"{h} hours"
    halves = max(1, round(minutes / (WALK_DAY / 2)))
    if halves == 1:
        return "half a day"
    if halves == 2:
        return "a day"
    if halves % 2:
        return "a day and a half" if halves == 3 else f"{halves // 2} and a half days"
    return f"{halves // 2} days"


# ------------------------------------------------------------------ where you can go
def label(w, p):
    t = w.tiles[p]
    region = w.region_of(p)["name"]
    s = t.site
    if s:
        if s["kind"] == "village":
            return s["name"]
        if s["kind"] == "ruin":
            return f"the ruined {s['purpose']} in {region}"
        if s["kind"] == "shrine":
            return f"the shrine of {s['spirit']} in {region}"
        if s["kind"] == "camp":
            return f"the old camp in {region}"
    if t.features:
        return f"the {t.features[0].noun} in {region}"
    return region


def places(g):
    """Every square you have walked, with its name, sites and villages first."""
    w = g.world
    out = []
    for p, t in w.tiles.items():
        if not t.visited or p == g.pos:
            continue
        kind = t.site["kind"] if t.site else "place"
        out.append(dict(pos=p, label=label(w, p), kind=kind,
                        words={x.noun for x in t.features} | {w.region_of(p)["name"].lower()} |
                              ({t.site["name"].lower()} if t.site and t.site.get("name") else set())))
    order = {"village": 0, "shrine": 1, "ruin": 2, "camp": 3, "place": 4}
    out.sort(key=lambda d: (order.get(d["kind"], 5), d["label"]))
    return out


def resolve(g, text):
    """The place you mean by text: best match, nearest to you among equals."""
    text = text.lower().strip()
    for prefix in ("to ", "the "):
        if text.startswith(prefix):
            text = text[len(prefix):]
    if not text:
        return None
    w = g.world
    def score(d):
        lab = d["label"].lower()
        if text == lab or text in {x.lower() for x in d["words"]}:
            return 4 if d["kind"] != "place" else 3
        if lab.startswith(text) or text in lab:
            return 2 if d["kind"] != "place" else 1.5
        words = set(text.split())
        if words and words <= set(lab.replace(",", "").split()):
            return 1
        return 0
    scored = [(score(d), d) for d in places(g)]
    top = max((s for s, _ in scored), default=0)
    if not top:
        return None
    best = [d for s, d in scored if s == top]
    d = dict(min(best, key=lambda d: abs(d["pos"][0] - g.pos[0]) + abs(d["pos"][1] - g.pos[1])))
    noun = next((n for n in w.tiles[d["pos"]].features if n.noun == text), None)
    if noun and d["kind"] != "village":            # you named the landmark: call the place by it
        d["label"] = f"the {noun.noun} in {w.region_of(d['pos'])['name']}"
    return d


def options(g):
    """Destinations for the menu: villages and sites you know, with cost; a few landmarks too."""
    out = []
    for d in places(g):
        if d["kind"] == "place":
            continue
        path, mins = route(g, d["pos"])
        if path:
            out.append(dict(label=d["label"], value=d["label"], note=f"{how_long(mins)}, {need(mins)} ration{'s' if need(mins) > 1 else ''}",
                            mins=mins))
    return out


# ------------------------------------------------------------------ going
def blocked(g):
    if g.combat:
        return "Not with an enemy at your throat."
    if getattr(g, "pending", None):
        return "Answer what's in front of you first."
    t = g.world.tiles[g.pos]
    watcher = next((c for c in t.creatures if mind.intent(c) in ("stalk", "hunt", "hold")), None)
    if watcher:
        return f"Not with {g.narr.creature_np(watcher, True)} watching you. You'd never get far with that at your back."
    return ""


def danger_at(g, p):
    t = g.world.tiles[p]
    return any(c.aggressive or c.boss for c in t.creatures)


def list_places(g):
    opts = options(g)
    have = rations(g)
    lines = [f"You carry {have} ration{'s' if have != 1 else ''} (at most {RATION_MAX}). Merchants, millers and eel-catchers sell them for {RATION_PRICE} coins each ('buy rations'), and you may find some on the road."]
    if not opts:
        lines.append("You haven't been anywhere worth travelling back to yet. Places you walk become places you can return to.")
    else:
        lines.append("Places you can travel back to:")
        lines += [f"  {cap(o['label'])} - {o['note']}" for o in sorted(opts, key=lambda o: o["mins"])]
        lines.append("Or name any landmark you've seen, such as 'travel standing stone'.")
    g.out("\n".join(lines))


def travel(g, text):
    if not text.strip():
        return list_places(g)
    why = blocked(g)
    if why:
        return g.emit(why)
    d = resolve(g, text)
    if not d:
        return g.emit(f"You don't know of anywhere called '{text.strip()}' that you've been. (Type 'travel' to see where you can go.)")
    path, mins = route(g, d["pos"])
    if not path:
        return g.emit(f"You can't see how to get to {d['label']} from here by any way you know.")
    if len(path) <= 3:
        return g.emit(f"{cap(d['label'])} is close enough to walk; it's only {len(path) - 1} step{'s' if len(path) > 2 else ''} away.")
    stop_short = danger_at(g, d["pos"])
    if stop_short:
        path = path[:-1]
        mins -= step_minutes(g, path[-1], d["pos"])
    cost = need(mins)
    if rations(g) < cost:
        return g.emit(f"It's {how_long(mins)} to {d['label']}, and you'd need {cost} ration{'s' if cost > 1 else ''}. "
                      f"You have {rations(g)}. (Merchants, millers and eel-catchers sell them: 'buy rations'.)")
    w = g.world
    roads = sum(1 for a, b in zip(path, path[1:]) if w.road_between(a, b))
    by = "by road" if roads >= 0.7 * (len(path) - 1) else "partly by road" if roads else "across country"
    g.emit(g.narr.pick([f"You shoulder your pack and set off for {d['label']}, {by}.",
                        f"You set out for {d['label']}, {by}, with {how_long(mins)} of walking ahead.",
                        f"You turn your face toward {d['label']} and start walking, {by}."], "travel_start"))
    walked, day_walked, stopped, why_stop = 0, 0, len(path) - 1, None
    with g.hush():
        for i, (a, b) in enumerate(zip(path, path[1:]), 1):
            m = step_minutes(g, a, b)
            g.pass_time(m)
            walked += m
            day_walked += m
            t = w.tiles[b]
            if i < len(path) - 1 and any(c.aggressive for c in t.creatures) and not w.road_between(a, b) \
                    and g.rng.random() < (0.12 if g.klass() == "ranger" else 0.25):
                stopped, why_stop = i, "beast"
                break
            if day_walked >= WALK_DAY and i < len(path) - 1:
                day_walked = 0
                g.pass_time(NIGHT)
                p = g.player
                p.hp = min(p.maxhp, p.hp + p.maxhp // 3)
                if not t.site and not t.creatures and g.rng.random() < 0.35:
                    stopped, why_stop = i, "encounter"
                    break
    used = min(rations(g), need(walked))
    g.player.rations = rations(g) - used
    came_from = path[stopped - 1]
    g.pos = path[stopped]
    if not hasattr(g, "trail"):
        g.trail = []
    g.trail.extend(path[1:stopped + 1])
    days = how_long(walked)
    ate = f"You eat {used} of your rations on the way" + (f"; {rations(g)} left." if rations(g) else ", and have none left.")
    if why_stop == "beast":
        g.emit(f"After {days} on the road your way is barred. {ate}")
    elif why_stop == "encounter":
        g.emit(f"You are {days} into the journey when the road brings you something unexpected. {ate}")
    elif stop_short:
        g.emit(f"{days.capitalize()} later you come within sight of {d['label']}, and stop. Something is waiting there. {ate}")
    else:
        g.emit(g.narr.pick([f"{days.capitalize()} later you reach {d['label']}. {ate}",
                            f"After {days} of walking you arrive at {d['label']}. {ate}",
                            f"The journey takes {days}, and brings you to {d['label']}. {ate}"], "travel_end"))
    t = w.tiles[g.pos]
    for c in t.creatures:
        mind.update(c, g.player, w)
    step = (g.pos[0] - came_from[0], g.pos[1] - came_from[1])
    facing = {(0, -1): "north", (0, 1): "south", (1, 0): "east", (-1, 0): "west"}.get(step)
    g.show_location(brief=t.visited, came_from=came_from, direction=facing)
    t.visited = True
    if why_stop == "encounter":
        from . import encounters as ENC
        opts = ENC.possible(g)
        if opts:
            key = g.rng.choices([k for k, _ in opts], [wt for _, wt in opts])[0]
            g.encounters_seen.add(key)
            g.last_encounter_turn = getattr(g, "turns", 0)
            g.emit("")
            ENC.START[key](g)
    else:
        g.creatures_react(arrived=True, updated=True)
    g.check_win()
    if not g.over:
        from . import story as S
        S.on_arrive(g)


def seller(g):
    """Someone here who'll sell you rations and still has some, or None."""
    sellers = [n for n in g.sellers() if sells_rations(n)]
    return next((n for n in sellers if supply(n) > 0), None)


def buy(g, text):
    """'buy rations', 'buy 4 rations': from a merchant or a miller or eel-catcher with a stall."""
    t = g.world.tiles[g.pos]
    if not (t.site and t.site["kind"] == "village"):
        return g.emit("There's no one out here to sell you food for the road. Try a village with a merchant, a miller or an eel-catcher.")
    m = seller(g)
    if not m:
        unmet = [n for n in t.npcs if sells_rations(n) and n not in g.sellers()]
        if unmet:
            return g.emit(f"Nobody's offered you food for the road yet. ({unmet[0].name}, the {unmet[0].job}, might, once you've talked.)")
        if any(sells_rations(n) for n in g.sellers()):
            return g.emit("Nobody here has any rations left to sell. They'll have more in a few days.")
        return g.emit(f"No one in {t.site['name']} has food to spare for the road. A merchant, a miller or an eel-catcher would.")
    words = text.split()
    n = next((int(x) for x in words if x.isdigit()), 0)
    room = RATION_MAX - rations(g)
    if room <= 0:
        return g.emit(f"Your pack holds no more food than this ({RATION_MAX} rations).")
    n = min(n or min(4, room), room)
    afford = g.player.gold // RATION_PRICE
    if afford <= 0:
        return g.emit(f"Rations are {RATION_PRICE} coins each, and you haven't the coin.")
    n = min(n, afford, supply(m))
    g.player.gold -= n * RATION_PRICE
    add_rations(g, n)
    m.mem["rations"] -= n
    who = m.name
    g.emit(g.narr.pick([f"{who} wraps up {n} rations of bread, hard cheese and dried meat for you. ({n * RATION_PRICE} coins; you carry {rations(g)} rations.)",
                        f"For {n * RATION_PRICE} coins you get {n} travel ration{'s' if n > 1 else ''}, tied in a cloth. (You carry {rations(g)}.)",
                        f"{who} sells you {n} ration{'s' if n > 1 else ''} for the road: oatcakes, cheese and a twist of salt meat. ({n * RATION_PRICE} coins; {rations(g)} in your pack.)"],
                       "ration_buy"))


def eat(g):
    if rations(g) <= 0:
        return g.emit("You have no rations left.")
    p = g.player
    g.player.rations -= 1
    heal = min(4, p.maxhp - p.hp)
    p.hp += heal
    g.emit(f"You eat one of your travel rations. It is filling, and that is all that can be said for it. (" + (f"+{heal} HP; " if heal else "") + f"{rations(g)} left.)")
