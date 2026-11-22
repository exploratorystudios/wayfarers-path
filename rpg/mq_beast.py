"""Main quest: the Beast.

Something huge has come down on the land and is killing. The elder names two people who have
seen it close: one knows how to hurt it, the other has seen where it goes. It raids by night,
and the news travels; near its lair the ground carries its tracks, pointing the way. Kill it in
its lair (far easier if you know its weakness) and bring proof home.
"""
from . import mainquest as MQ
from .mainquest import register, home_name
from .textgen import cap, article

ADJ = ["Grey", "Red", "Hollow", "Lame", "Black", "Old", "Pale", "Long", "Hungry", "Scarred"]
NOUN = ["Hunger", "Reaver", "Shadow", "Mother", "Devourer", "Widow-maker", "Thing", "Lord", "Ravener", "Beast"]
PART = {"wolf": "fang", "boar": "tusk", "spider": "foreleg", "serpent": "fang", "toad": "tongue-bone", "crow": "pinion",
        "stag": "antler", "bear": "claw", "goat": "horn", "wraith": "shroud-rag"}

ORIGIN = [
    "It came down out of the high country in the hard frost, and it never went back.",
    "Treasure-diggers opened a barrow out that way. Whatever they let out has been hungry since.",
    "A hunter wounded it, years back, and didn't finish the job. It has hated us ever since.",
    "It was a thing of the old woods, they say, until the woods were cut. Now it takes what it's owed.",
    "Nobody knows where it came from. One spring it was simply there, and the lambing went bad.",
    "The old people say it wakes once a lifetime. My mother saw the last time. Now it's my turn.",
    "It drove the wolves out before it, that first winter. We should have known then what was coming.",
]
TOLL = ["It has taken sheep from every fold for a day's walk.", "It took a drover on the road last month. We found his boots.",
        "Two children went missing at the edge of the wood. We don't let them out now.",
        "It tore the door off a byre and took the cow inside, and the man who went to stop it.",
        "Every night it comes closer to the houses."]
WEAKNESS = [
    dict(when="any", told="\"It guards its throat. Always keeps its head low, always turns that side away. That's where it's soft, mark me.\"",
         fight="You remember what you were told, and go for the throat. The beast screams and twists, and you see it is afraid."),
    dict(when="any", told="\"It's blind on the left. An old wound - an arrow, maybe. Come at it from that side and it'll never see you.\"",
         fight="You keep to its blind side, as you were told. It turns and turns, and never quite finds you."),
    dict(when="day", told="\"It never comes by daylight. I think the sun pains it. Whatever you do, don't go to it after dark.\"",
         fight="In the daylight the beast is slow and squinting, as you were told it would be."),
    dict(when="any", told="\"Fire. It won't come near fire. I kept it off three nights with a burning brand, and it hated me for it.\"",
         fight="You come at it with fire and fury, as you were told, and it shrinks from you."),
    dict(when="day", told="\"It sleeps through the day, gorged. Catch it then, heavy and slow, and you might live.\"",
         fight="You find it sluggish and heavy with sleep, as you were told. It wakes too slowly."),
]
WHERE_TOLD = ["\"I followed its tracks once, further than I should have. It lairs in {site}, {dir}, out in {region}. I came back. Barely.\"",
              "\"I've seen where it goes at dawn: {site}, {dir}, in {region}. Nobody goes there now.\"",
              "\"It drags what it kills back to {site}, {dir}, out in {region}. You can smell the place long before you see it.\""]
ENDINGS = [
    "You walk into {home} with the {part} of {title} held up for all to see. For a moment no one moves. Then a woman laughs out loud, "
    "and someone rings the bell, and before long the whole village is in the lane. That night they let the children play out after dark.",
    "Word runs ahead of you, and by the time you reach {home} they are waiting at the edge of the village. {elder} takes the {part} "
    "in both hands and holds it up, and the shout that goes up is heard, they say, two valleys away.",
    "You lay the {part} of {title} on the step of {elder}'s house. {elder} looks at it a long time. \"It's over, then,\" "
    "{he} says at last, and sits down, quite suddenly, as if {he} had been standing for years.",
]


@register
class BeastQuest(MQ.MainQuest):
    kind = "beast"

    def setup(self, w, r):
        w.tiles[w.quest_pos].site = w.make_ruin(quest=True)
        region = w.region_of(w.quest_pos)["name"]
        self.title = f"the {r.choice(ADJ)} {r.choice(NOUN)} of {region}"
        self.origin, self.toll = r.choice(ORIGIN), r.choice(TOLL)
        self.weak = r.choice(WEAKNESS)
        self.where_told = r.choice(WHERE_TOLD)
        self.ending = r.choice(ENDINGS)
        dist = w.distances(w.start)
        others = [v for v in w.villages if v != w.start]
        lair_d = w.distances(w.quest_pos)
        # the one who knows its weakness lives a fair walk away; the one who has seen its lair, nearer the lair
        near = sorted(others, key=lambda v: abs(dist.get(v, 99) - 8))
        self.va = near[0]
        self.vb = min((v for v in others if v != self.va), key=lambda v: lair_d.get(v, 99))
        self.wa = self.wb = None          # people's names, chosen once villages have people
        self.heard_a = self.heard_b = False
        self.weakened = False
        self.raided = []
        self.tracks = {p for p, d in lair_d.items() if 0 < d <= 5}

    def populate(self, w, r):
        q = w.tiles[w.quest_pos]
        fitting = [s for s in w.species if q.biome in s["arch"]["biomes"] and not s["arch"].get("undead")] or w.species
        c = w.make_creature(r.choice(fitting), q.danger + 1, boss=True)
        c.title = self.title
        self.part = PART.get(c.species["key"], "claw")
        q.creatures = [c]
        for attr, v in (("wa", self.va), ("wb", self.vb)):
            folk = [n for n in w.tiles[v].npcs if n.role != "elder"] or w.tiles[v].npcs
            setattr(self, attr, r.choice(folk).name if folk else None)

    def heading(self, g):
        return cap(self.title)

    # ------------------------------------------------------------ telling
    def where(self, w, here):
        q = w.tiles[w.quest_pos]
        return article(f"ruined {q.site['purpose']}"), w.region_of(w.quest_pos)["name"]

    def who(self, w, name, v):
        n = next((x for x in w.tiles[v].npcs if x.name == name), None)
        return n.pronouns() if n else {"he": "they", "him": "them", "his": "their"}

    def offer(self, g, npc):
        w, n = g.world, g.narr
        va, vb = w.tiles[self.va].site["name"], w.tiles[self.vb].site["name"]
        g.emit(f"{npc.name} doesn't waste words. \"You'll have heard of {self.title}. If you haven't, you will. {self.origin} {self.toll}\"")
        he = self.who(w, self.wa, self.va)["he"]
        g.emit(f"\"Nobody here can kill it. Maybe you can. Talk to {self.wa} in {va}, {n.dir_phrase(g.pos, self.va)} - {he} fought it once and lived. "
               f"And {self.wb} at {vb} has seen where it goes. Find it, kill it, and bring me something of it, so I know it's done.\"")
        g.emit("(Quest: learn how to kill the beast, hunt it to its lair, and bring proof home.)")
        self.active = True

    def goal(self, g):
        w = g.world
        if self.done:
            return f"Bring the {self.part} of {self.title} home to {home_name(w)}."
        va, vb = w.tiles[self.va].site["name"], w.tiles[self.vb].site["name"]
        parts = []
        if not self.heard_a:
            parts.append(f"ask {self.wa} in {va} how to hurt it")
        if not self.heard_b:
            parts.append(f"ask {self.wb} in {vb} where it lairs")
        if parts:
            return f"Hunt {self.title}: " + " and ".join(parts) + "."
        return f"Hunt {self.title} in its lair in {w.region_of(w.quest_pos)['name']}" + (". You know its weakness." if self.heard_a else ".")

    def status(self, g):
        return f"carrying the beast's {self.part}" if self.done else ""

    def mark(self, g):
        if self.done:
            return f"home: bring the {self.part} here"
        return f"the lair of {self.title}" if self.heard_b else "someone here knows the beast"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        out = []
        if not self.heard_a:
            out.append(self.va)
        if not self.heard_b:
            out.append(self.vb)
        return out or [w.quest_pos]

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", f"Bring the {self.part} back.", True
        if not self.heard_a:
            return self.va, f"toward {w.tiles[self.va].site['name']}", f"{self.wa} knows how to hurt the beast.", True
        if not self.heard_b:
            return self.vb, f"toward {w.tiles[self.vb].site['name']}", f"{self.wb} has seen its lair.", True
        return w.quest_pos, "toward the beast's lair", "the lair", p.level >= w.tiles[w.quest_pos].danger + 1

    def act(self, g):
        w = g.world
        if (self.heard_a and not self.done and self.weak["when"] == "day" and w.is_dark and self.boss(w)
                and abs(g.pos[0] - w.quest_pos[0]) + abs(g.pos[1] - w.quest_pos[1]) <= 2 and not g.combat):
            return "rest", "Rest until daylight", "The beast is weakest by day, you were told. Wait for the sun."
        return None

    def vision(self, g):
        site, region = self.where(g.world, g.pos)
        return f"{self.title} asleep in {site} {g.narr.dir_phrase(g.pos, g.world.quest_pos)}, its flanks rising and falling, bones all about it"

    def lore(self, g):
        self.heard_a = True                 # a wise stranger's word is as good as a witness's
        return f"\"{cap(self.title)}? I know a thing about that one.\" {self.weak['told']}"

    def rumour(self, narr, here):
        w = narr.w
        if self.raided:
            v = w.tiles[self.raided[-1]].site["name"]
            return f"{self.title} was at {v} again. Took what it wanted and was gone before anyone could lift a hand"
        return f"{self.title} is out there, {narr.dir_phrase(here, w.quest_pos)}. Folk at {w.tiles[self.vb].site['name']} know more than they say"

    def place_lines(self, narr, pos):
        if self.done or pos not in self.tracks:
            return []
        d = narr.dir_phrase(pos, narr.w.quest_pos).split(" to the ")[-1]
        return [narr.pick([f"Huge tracks are pressed into the ground here, all heading {d}.",
                           f"Something very large has passed this way, more than once. Its trail leads {d}.",
                           f"Broken branches and torn turf mark a trail going {d}. The smell of it hangs in the air."], "beast_tracks")]

    def holds(self, it):
        return it.kind == "token" and it.name.endswith(self.title)

    def carried(self, g):
        it = self.trophy(g)
        return it.name if it else ""

    def trophy(self, g):
        return next((i for i in g.player.inv if self.holds(i)), None)

    # ------------------------------------------------------------ hooks
    def on_talk(self, g, npc):
        w = g.world
        if npc.name == self.wa and not self.heard_a:
            self.heard_a = True
            g.emit(f"{npc.name} goes quiet when you ask about the beast. Then: {self.weak['told']}")
            g.emit("(Journal: you know how to hurt the beast.)")
        elif npc.name == self.wb and not self.heard_b:
            self.heard_b = True
            site, region = self.where(w, g.pos)
            g.emit(f"{npc.name} looks at you a long while before answering. " +
                   self.where_told.format(site=site, dir=g.narr.dir_phrase(g.pos, w.quest_pos), region=region))
            g.emit("(Journal: you know where the beast lairs.)")

    def on_arrive(self, g):
        w = g.world
        if g.pos != w.quest_pos or self.done:
            return
        self.heard_b = True
        c = self.boss(w)
        if c and self.heard_a and not self.weakened and (self.weak["when"] == "any" or not w.is_dark):
            self.weakened = True
            c.hp = max(10, int(c.hp * 0.6))
            c.df = max(0, c.df - 2)
            g.emit(self.weak["fight"] + " (Knowing its weakness, you find it far easier to hurt.)")

    def on_new_day(self, g):
        w = g.world
        if self.done or w.day < 2:
            return
        others = [v for v in w.villages if v != w.start]
        if not others or g.rng.random() > 0.6:
            return
        lair_d = w.distances(w.quest_pos)
        v = min(others, key=lambda v: lair_d.get(v, 99) + g.rng.random() * 8)
        self.raided.append(v)
        name = w.tiles[v].site["name"]
        w.chronicle.append(dict(day=w.day, pos=v, kind="news", text=g.rng.choice([
            f"{self.title} came to {name} in the night and took a cow from the byre",
            f"{self.title} was seen at the edge of {name}; the dogs wouldn't stop howling",
            f"{name} lost sheep to {self.title}, and a shepherd's dog that tried to stop it"])))
        from . import story as S
        near = [q for _, q in w.neighbours(v) if q in w.land and not w.tiles[q].site]
        if near:
            S.add_mark(g, g.rng.choice(near), "The turf is torn up and stained dark here. Something very large fed in this place, not long ago.", days=3)

    def on_kill(self, g, c):
        if not c.boss or self.done:
            return
        from .world import Item
        self.done = True
        it = Item("token", f"{self.part} of {self.title}", value=0, facts=dict(material="bone", glow="the smell of the lair still on it"))
        g.player.inv.append(it)
        g.emit(f"You take the {self.part} of {self.title} as proof. Now take it home to {home_name(g.world)}.")

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and self.trophy(g)):
            return
        if not g.has_quest:
            elder = MQ.elder_of(w)
            if elder:
                g.emit(f"Heads turn at what you carry. {cap(elder.called())} is staring at it. Perhaps you should talk to {elder.pronouns()['him']}.")
            return
        elder = MQ.elder_of(w)
        en = elder.name if elder else "The elder"
        he = elder.pronouns()["he"] if elder else "they"
        MQ.win(g, self.ending.format(home=home_name(w), part=self.part, title=self.title, elder=en, he=he))
