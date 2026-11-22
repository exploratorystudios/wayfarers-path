"""The main quest: what the village elder asks of you, and how the game ends.

Each world rolls one kind of main quest (the relic, the beast, the blight, the missing heir...).
A quest kind is a class here or in an mq_* module, registered with @register. The rest of the
game never asks "is it a relic?"; it asks the quest:

    offer(g, npc)            the elder's telling, when the quest is given
    elder(g, npc)            the elder's reaction later (True if they said something)
    goal(g)                  one line for the journal and the status panel
    status(g)                a few words for a save card ("carrying the relic"), or ""
    targets(g)               map squares to mark while the quest is active
    step(g)                  where to go next and why, for the advisor: (pos, label, why, ready) or None
    vision(g) / lore(g)      what a vision shows, and what a wise stranger says
    rumour(narr, here)       a rumour for village gossip, or None
    place_lines(narr, pos)   extra sentences in a place's description (blight, tracks...)
    holds(it)                True for things the quest won't let you sell or give away
    carried(g)               the name of what you carry that people notice, or ""
    on_take / on_kill / on_arrive / on_talk / on_new_day / on_pray   hooks
    check(g)                 the ending, if it has come

Quests with a clock (`clocked = True`) can be finished late, for a bittersweet ending, but are
never lost outright.
"""
import os
import random

from .textgen import cap, article

REGISTRY = {}


def register(cls):
    REGISTRY[cls.kind] = cls
    return cls


def kinds():
    _load()
    return sorted(REGISTRY)


def _load():
    from . import mq_beast, mq_blight, mq_heir     # noqa: F401  (registering)


def choose(world):
    """Pick this world's quest kind from its own dice (RPG_QUEST forces one, for testing)."""
    _load()
    want = os.environ.get("RPG_QUEST")
    if want in REGISTRY:
        return REGISTRY[want]
    r = random.Random(f"{world.seed}-mainquest")
    return REGISTRY[r.choice(sorted(REGISTRY))]


def of(world):
    """The world's quest. Worlds saved before quests had kinds get a relic quest built from what they hold."""
    q = world.__dict__.get("main")
    if q is None:
        q = world.main = RelicQuest.adopt(world)
    return q


def home_name(w):
    return w.tiles[w.start].site["name"]


def elder_of(w):
    return next((n for n in w.tiles[w.start].npcs if n.role == "elder"), None)


def win(g, text):
    g.emit("")
    g.emit(text)
    g.emit(f"*** You have won, on day {g.world.day}, at level {g.player.level}. ***")
    for v in g.world.villages:
        for npc in g.world.tiles[v].npcs:
            npc.like(10)
    g.over = g.won = True


class MainQuest:
    kind = ""
    clocked = False
    verb = "go"

    def __init__(self, world, r):
        self.done = False             # the deed is done (the ending comes on reaching home)
        self.late = False             # a clocked quest whose clock ran out
        self.setup(world, r)

    # world generation
    def setup(self, world, r):
        pass

    def populate(self, world, r):
        pass

    # telling
    def offer(self, g, npc):
        raise NotImplementedError

    def elder(self, g, npc):
        """Before the quest is given: if you've already done the deed, the elder sees it."""
        if not g.has_quest and (self.done or getattr(self, "found", False) or getattr(self, "letter", False)):
            g.has_quest = True
            g.emit(f"{npc.name} sees how things stand before you say a word, and has to sit down.")
            self.check(g)
            return True
        return False

    def goal(self, g):
        return ""

    def status(self, g):
        return ""

    def mark(self, g):
        """What the map says at the quest's marked place."""
        return "your quest leads here"

    def targets(self, g):
        return []

    def step(self, g):
        return None

    def act(self, g):
        """Something to do right here for the quest: (command, label, why), or None."""
        return None

    def vision(self, g):
        return ""

    def lore(self, g):
        return ""

    def rumour(self, narr, here):
        return None

    def place_lines(self, narr, pos):
        return []

    def holds(self, it):
        return False

    def carried(self, g):
        """The name of what you carry that people will notice and remark on, or ""."""
        return ""

    # hooks
    def on_take(self, g, it):
        pass

    def on_kill(self, g, c):
        pass

    def on_arrive(self, g):
        pass

    def on_talk(self, g, npc):
        pass

    def on_new_day(self, g):
        pass

    def on_pray(self, g, site):
        return ""

    def check(self, g):
        pass

    # helpers
    def boss(self, world):
        return next((c for c in world.tiles[world.quest_pos].creatures if c.boss), None)


# ====================================================================== the relic
@register
class RelicQuest(MainQuest):
    """Recover the village's lost relic from a guarded ruin far away, and bring it home."""
    kind = "relic"

    @classmethod
    def adopt(cls, world):
        q = cls.__new__(cls)
        q.done = q.late = False
        return q

    def setup(self, world, r):
        from .world import Item
        from . import lex_entities as E
        world.relic = Item("relic", f"{r.choice(E.RELIC_ADJ)} {r.choice(E.RELIC_NOUN)}", value=500,
                           facts=dict(material=r.choice(["gold", "silver", "black iron", "bone", "crystal", "bronze"]),
                                      glow=r.choice(["a faint inner warmth", "a hum you feel in your teeth", "a cold light", "a smell of rain"])))
        world.tiles[world.quest_pos].site = world.make_ruin(quest=True)

    def populate(self, world, r):
        q = world.tiles[world.quest_pos]
        fitting = [s for s in world.species if q.biome in s["arch"]["biomes"]] or world.species
        q.creatures = [world.make_creature(r.choice(fitting), q.danger + 1, boss=True)]
        q.items.append(world.relic)

    def offer(self, g, npc):
        from . import relic_tale
        g.emit(relic_tale.speech(g, npc))
        g.emit("(Quest: recover the relic and return here.)")

    def elder(self, g, npc):
        w = g.world
        if not g.has_quest and w.relic in g.player.inv:
            g.has_quest = True
            g.emit(f"{npc.name} stares at the {w.relic.name} in your hands, and for a moment cannot speak. "
                   f"\"You found it. You didn't even know what it was, and you found it.\"")
            self.check(g)
            return True
        return False

    def goal(self, g):
        w = g.world
        if not g.has_quest:
            return "Speak with the village elder."
        if w.relic in g.player.inv:
            return f"Bring the {w.relic.name} home to {home_name(w)}."
        return f"Recover the {w.relic.name} from {w.region_of(w.quest_pos)['name']}."

    def status(self, g):
        return "carrying the relic" if g.world.relic in g.player.inv else ""

    def mark(self, g):
        w = g.world
        return f"home: bring the {w.relic.name} here" if w.relic in g.player.inv else f"the {w.relic.name} lies hereabouts"

    def carried(self, g):
        return g.world.relic.name if g.world.relic in g.player.inv else ""

    def holds(self, it):
        return it.kind == "relic"

    def targets(self, g):
        w = g.world
        return [w.start] if w.relic in g.player.inv else [w.quest_pos]

    def step(self, g):
        w, p = g.world, g.player
        if w.relic in p.inv:
            return w.start, "toward home", f"Bring the {w.relic.name} back.", True
        return w.quest_pos, "toward the relic", "the ruin", p.level >= w.tiles[w.quest_pos].danger + 1

    def vision(self, g):
        w = g.world
        return f"the {w.relic.name}, lying in the dark in a broken place {g.narr.dir_phrase(g.pos, w.quest_pos)}. Something breathes beside it"

    def lore(self, g):
        w = g.world
        return (f"\"The {w.relic.name}? Aye. It lies {g.narr.dir_phrase(g.pos, w.quest_pos)}. The thing that guards it is old and slow "
                f"and does not forgive. Go strong, or don't go.\"")

    def rumour(self, narr, here):
        w = narr.w
        q = w.tiles[w.quest_pos]
        return (f"the {w.relic.name} lies in {article(q.site['state'] + ' ' + q.site['purpose'])} {narr.dir_phrase(here, w.quest_pos)}, "
                f"in {w.region_of(w.quest_pos)['name']}. Something old guards it.")

    def on_take(self, g, it):
        if it.kind == "relic":
            g.emit(f"The {it.name} is yours. Now take it back to {home_name(g.world)}.")

    def check(self, g):
        w = g.world
        if g.pos != w.start or w.relic not in g.player.inv:
            return
        if not g.has_quest:
            elder = elder_of(w)
            if elder:
                g.emit(f"Heads turn as you walk in. {cap(elder.called())} is staring at what you carry. Perhaps you should talk to {elder.pronouns()['him']}.")
            return
        v = home_name(w)
        win(g, f"You walk into {v} with the {w.relic.name} held high. People come out of their houses, one by one, "
               f"and then all at once. Someone is weeping; someone else begins to sing. That night the sky over {v} clears, "
               f"and for the first time in generations, the {w.season} tastes as it should.")
