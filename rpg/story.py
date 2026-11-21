"""The things that make a world remember: choices, quests, the chronicle and traces.

* Choices: an event can stop and ask ("1. Help them  2. Walk on"). The player answers
  with a number (or `choose 2`). Moving away takes the choice's "leave" option.
* Quests: small jobs with a goal and a reward, kept in the journal:
    bring    - carry an item to a person
    deliver  - carry an item to a place
    slay     - kill a particular creature
    escort   - lead someone to a place (they follow you)
    find     - reach a place (then something happens there)
* Chronicle: everything notable that happens, with the day it happened.
* Traces: marks left on a tile ("A cairn of fresh stones marks the shepherd's grave").
* Deeds: stories about the player that spread to people nearby, then further.

Everything here is plain data on the Game/World/Tile, so it pickles with saves.
"""
from .textgen import article, cap

INFO_VERBS = {"look", "l", "examine", "x", "inspect", "check", "status", "stats", "inventory", "i", "inv", "journal", "quests",
              "chronicle", "history", "help", "h", "?", "map", "m", "saves", "save", "load", "hints", "read", "listen"}

HANDLERS = {}    # choice key -> function(game, data)


def choice_handler(key):
    def deco(fn):
        HANDLERS[key] = fn
        return fn
    return deco


def ensure(g):
    """Give older saves the newer bookkeeping."""
    w = g.world
    for attr, default in (("quests", list), ("companions", list), ("pending", lambda: None), ("quest_seq", lambda: 0),
                          ("buffs", dict), ("encounters_seen", set), ("last_encounter_turn", lambda: -99)):
        if not hasattr(g, attr):
            setattr(g, attr, default())
    for attr, default in (("chronicle", list), ("troubles_seen", set), ("last_tick_day", lambda: w.day)):
        if not hasattr(w, attr):
            setattr(w, attr, default())
    # older worlds: gentler words for old people, and no more "eldest" as a title
    for v in getattr(w, "villages", []):
        for n in w.tiles[v].npcs:
            if n.role == "elder" and n.job not in ("village elder", "elder", "village head", "headman", "headwoman"):
                g_ = n.look.get("name_gender")
                n.job = "headwoman" if g_ == "female" else "headman" if g_ == "male" else "village elder"
            if n.gender == "female" and n.look.get("hair") in ("a balding crown and a fierce beard",):
                n.look["hair"] = "dark hair streaked with white" if n.age_band != "young" else "a single thick braid"
            n.age_band          # older saves: fix the age group in place
            if n.look.get("age") == "ancient":
                n.look["age"] = "aged"
            if n.role == "elder" and n.look.get("age") in ("elderly", "aged"):
                from .coherence import HAIR_NEUTRAL
                n.look["age"] = "white-haired" if n.look.get("hair") in HAIR_NEUTRAL else "time-worn"   # never white hair beside copper curls
    # older worlds: a fallen oak/ash/elm/beech was filed as a standing oak (climb to the top of it, light on its crown)
    from . import secrets as SEC
    for t in w.tiles.values():
        for f in t.features:
            if f.kind == "oak" and f.noun in ("oak", "beech", "elm", "ash") and set(f.adjs) & {"fallen", "uprooted", "storm-felled"}:
                f.kind = "fallen tree"
                sec = (f.state or {}).get("secret")
                if sec and not sec.get("found"):
                    where = SEC.DECK.get(sec["key"], (None, set()))[1]
                    if "fallen tree" in where or "log" in where:
                        sec["verbs"] = sorted(v for v in sec["verbs"] if SEC.can(v, f)) or ["search"]
                    else:
                        f.state["secret"] = None      # a nest high in its branches can't be there any more
    if not hasattr(w, "secrets_placed"):
        from . import secrets
        secrets.place_all(w)
        w.secrets_placed = True


# ------------------------------------------------------------------ chronicle, traces, deeds
def record(g, text, kind="event", pos=None, mark=None, mark_days=None, story=None, like=1, reach=6):
    """Remember something. `mark` leaves a visible trace on the tile; `story` spreads as gossip."""
    w = g.world
    pos = pos or g.pos
    w.chronicle.append(dict(day=w.day, pos=pos, kind=kind, text=text))
    if mark:
        add_mark(g, pos, mark, mark_days)
    if story:
        g.deeds.append(dict(kind="story", pos=pos, day=w.day, story=story, like=like, reach=reach,
                            where=w.region_of(pos)["name"], thing=""))


def add_mark(g, pos, text, days=None):
    t = g.world.tiles[pos]
    if not hasattr(t, "marks") or t.marks is None:
        t.marks = []
    t.marks.append(dict(text=text, day=g.world.day, until=(g.world.day + days) if days else None))


def marks(world, pos):
    t = world.tiles[pos]
    out = []
    for m in getattr(t, "marks", None) or []:
        if m["until"] is None or m["until"] >= world.day:
            out.append(m["text"])
    return out


# ------------------------------------------------------------------ choices
def ask(g, text, options, leave=None, source=""):
    """Offer a choice. options: [(label, handler_key, data)]. leave: index taken if the player walks away."""
    g.pending = dict(text=text, options=[dict(label=l, key=k, data=d or {}) for l, k, d in options],
                     leave=leave, source=source)
    g.emit(text)
    for i, o in enumerate(g.pending["options"], 1):
        g.out(f"  {i}. {o['label']}")
    g.out("(Type a number to choose.)")


def resolve(g, index):
    p = g.pending
    if not p or not (0 <= index < len(p["options"])):
        return False
    o = p["options"][index]
    g.pending = None
    with g.hush():
        HANDLERS[o["key"]](g, o["data"])
    return True


def intercept(g, verb, words):
    """Called before a command runs. Returns True if the command was used up by a pending choice."""
    p = g.pending
    if not p:
        return False
    pick = None
    if words and words[0].isdigit():
        pick = int(words[0]) - 1
    elif verb == "choose" and len(words) > 1 and words[1].isdigit():
        pick = int(words[1]) - 1
    if pick is not None:
        if not resolve(g, pick):
            g.emit(f"Choose a number from 1 to {len(p['options'])}.")
        return True
    if verb in INFO_VERBS:
        return False
    from .world import DIRS
    if (verb in DIRS or verb in ("go", "flee", "run")) and p.get("leave") is not None:
        resolve(g, p["leave"])
        return False             # then the move goes ahead
    g.emit("First you need to decide: " + "; ".join(f"{i}. {o['label']}" for i, o in enumerate(p["options"], 1)) + ".")
    return True


# ------------------------------------------------------------------ quests
def new_quest(g, kind, title, desc, reward, giver=None, target=None, item=None, creature=None, companion=None,
              deadline=None, source="", on_done=None, data=None):
    g.quest_seq += 1
    q = dict(id=g.quest_seq, kind=kind, title=title, desc=desc, reward=reward, giver=giver.name if giver else None,
             giver_home=giver.home if giver else None, target=target, item=item, creature=creature, companion=companion,
             status="active", day=g.world.day, deadline=deadline, source=source, on_done=on_done, data=data or {}, stage="")
    g.quests.append(q)
    if companion:
        g.companions.append(companion)
    g.emit(f"(New in your journal: {title}.)")
    return q


def active(g):
    return [q for q in g.quests if q["status"] == "active"]


def finish(g, q, text=None, success=True):
    """Pay out a quest's reward (or record its failure)."""
    from . import living
    q["status"] = "done" if success else "failed"
    if q.get("companion") in g.companions:
        g.companions.remove(q["companion"])
    if text:
        g.emit(text)
    if not success:
        record(g, f"You failed: {q['title']}.", "quest", pos=g.pos)
        g.emit(f"(Journal: {q['title']} - failed.)")
        return
    r = q["reward"] or {}
    p, w = g.player, g.world
    bits = []
    if r.get("gold"):
        p.gold += r["gold"]
        bits.append(f"{r['gold']} coins")
    if r.get("item"):
        it = w.make_item(r.get("danger", 2), r["item"])
        p.inv.append(it)
        bits.append(article(it.name))
    if r.get("xp"):
        for m in p.gain_xp(r["xp"]):
            g.emit(m)
        bits.append(f"{r['xp']} experience")
    if r.get("heal"):
        p.hp = p.maxhp
        bits.append("your strength restored")
    if r.get("maxhp"):
        p.maxhp += r["maxhp"]
        p.hp += r["maxhp"]
        bits.append(f"+{r['maxhp']} max health")
    if r.get("buff"):
        add_buff(g, *r["buff"])
        bits.append(BUFF_NAMES.get(r["buff"][0], r["buff"][0]))
    giver = find_npc(w, q.get("giver"))
    if giver and r.get("like", 1):
        giver.like(r.get("like", 3))
    if r.get("village_like") and q.get("giver_home"):
        for n in w.tiles[q["giver_home"]].npcs:
            n.like(r["village_like"])
    if q["data"].get("lift"):
        g.buffs.pop(q["data"]["lift"], None)
    if bits:
        g.emit("(Reward: " + ", ".join(bits) + ".)")
    g.emit(f"(Journal: {q['title']} - done.)")
    record(g, r.get("chronicle") or f"You completed: {q['title']}.", "quest", pos=g.pos,
           story=r.get("story"), like=r.get("story_like", 2))
    if q.get("on_done"):
        living.quest_done(g, q)


def quest_items(g):
    """Names of items promised to someone or somewhere."""
    return {q["item"] for q in active(g) if q.get("item")}


def find_npc(world, name):
    if not name:
        return None
    for v in world.villages:
        for n in world.tiles[v].npcs:
            if n.name == name:
                return n
    for t in world.tiles.values():
        for n in t.npcs:
            if n.name == name:
                return n
    return None


def on_arrive(g):
    """Quest goals that are met by getting somewhere."""
    for q in list(active(g)):
        if q["target"] != g.pos:
            continue
        if q["kind"] == "deliver" and q["item"]:
            it = next((i for i in g.player.inv if i.name == q["item"]), None)
            if it:
                g.player.inv.remove(it)
                finish(g, q, q["data"].get("done_text") or f"You set down the {it.name}. It is done.")
        elif q["kind"] == "escort":
            finish(g, q, q["data"].get("done_text") or f"{cap(q['companion']['name'])} is home safe.")
        elif q["kind"] == "find":
            from . import living
            living.found(g, q)


def on_kill(g, creature):
    for q in active(g):
        if q["kind"] == "slay" and q["creature"] is creature:
            if q["giver"]:
                q["stage"] = "slain"
                g.emit(f"(Journal: {q['title']} - the deed is done. Return to {q['giver']}.)")
            else:
                finish(g, q)


def on_talk(g, npc):
    """Hand in quests to the person who gave them. Returns True if something was handed in."""
    done = False
    for q in list(active(g)):
        if q["giver"] != npc.name:
            continue
        if q["kind"] == "bring" and q["data"].get("message"):
            finish(g, q, q["data"].get("done_text"))
            done = True
        elif q["kind"] == "bring":
            it = next((i for i in g.player.inv if i.name == q["item"] or (q["data"].get("any_kind") and i.kind == q["data"]["any_kind"])), None)
            if it:
                g.player.inv.remove(it)
                if it is g.player.weapon:
                    g.player.weapon = None
                finish(g, q, q["data"].get("done_text", f"You hand over the {it.name}. {npc.name} takes it with both hands.").replace("{thing}", it.name))
                done = True
        elif q["kind"] == "slay" and q["stage"] == "slain":
            finish(g, q, q["data"].get("done_text", f"{npc.name} listens to your tale and grips your arm. \"Thank you.\""))
            done = True
    return done


def expire(g):
    """Quests with deadlines fail when the day passes."""
    for q in list(active(g)):
        if q.get("deadline") and g.world.day > q["deadline"]:
            finish(g, q, q["data"].get("fail_text"), success=False)


def journal_lines(g):
    w, n = g.world, g.narr
    lines = []
    for q in active(g):
        where = ""
        if q["target"]:
            where = f" ({n.dir_phrase(g.pos, q['target'])}, in {w.region_of(q['target'])['name']})" if q["target"] != g.pos else " (here)"
        elif q["kind"] == "bring" and q.get("giver_home"):
            home = w.tiles[q["giver_home"]].site
            where = f" (in {home['name']})" if home and home["name"] not in q["desc"] else ""
        if q["kind"] == "slay" and q["stage"] == "slain":
            where = f" (return to {q['giver']})"
        due = f" Before day {q['deadline'] + 1}." if q.get("deadline") else ""
        lines.append(f"- {q['title']}: {q['desc']}{where}.{due}")
    return lines


# ------------------------------------------------------------------ buffs (blessings, curses, luck)
BUFF_NAMES = {"lucky": "luck", "blessed": "a blessing", "cursed": "a curse", "fae": "fae favour", "soaked": "a soaking",
              "strong": "strength", "warded": "a ward", "queasy": "a bad stomach"}


def add_buff(g, name, hours, power=1):
    g.buffs[name] = dict(until=g.world.minutes + hours * 60, power=power)


def buff(g, name):
    b = getattr(g, "buffs", {}).get(name)
    if b and b["until"] >= g.world.minutes:
        return b["power"]
    return 0


def tick_buffs(g):
    for name in list(getattr(g, "buffs", {})):
        if g.buffs[name]["until"] < g.world.minutes:
            del g.buffs[name]
            g.emit({"lucky": "(Your luck has run its course.)", "blessed": "(The blessing fades.)", "cursed": "(The curse lifts at last.)",
                    "fae": "(The fae favour slips away like a dream.)", "soaked": "(You are dry again.)", "strong": "(The strength drains away.)",
                    "warded": "(The protection fades.)", "queasy": "(Your stomach settles.)"}.get(name, f"({name} fades.)"))


def effects_line(g):
    on = [BUFF_NAMES.get(k, k) for k in getattr(g, "buffs", {}) if buff(g, k)]
    return ", ".join(on)
