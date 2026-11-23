"""Main quest: the Missing Heir.

The elder's grandchild (or ward, or apprentice) has gone. The trail runs through a chain of
places across the map; at each, someone remembers them, or they left something behind, and that
tells you where to go next. At the end of the trail you find them: held by something that must
be killed, or living a life of their own that they may not want to leave. Bring them home, or
bring home word of them.

It has a clock: after some days the trail goes cold, and at its end you find only what they left
behind. The quest can still be finished, for a sadder ending.
"""
from . import mainquest as MQ
from . import story as S
from .mainquest import register, home_name
from .textgen import cap

RELATION = {"female": ["granddaughter", "niece", "ward", "apprentice"], "male": ["grandson", "nephew", "ward", "apprentice"]}
# why they went; "held" ones end in a fight, "free" ones in a choice
REASONS = [
    dict(key="light", held=True, told="{they} followed a light out over the fields one night, singing. We heard the singing stop.",
         end="You find {name} at the heart of the place, sitting very still, eyes open, held by whatever kept them. As it dies, {they} blinks, and sees you, and begins to weep."),
    dict(key="hill", held=True, told="{they} went up to the old places to leave an offering, and didn't come down. Folk say the hollow hill keeps what it takes.",
         end="Behind where the thing stood, {name} is curled in the dark, thin and cold but breathing. {they.cap} grips your hand as if it were a rope."),
    dict(key="troupe", held=False, told="{they} ran off with a troupe of players that came through at midsummer. Said {they} was meant for more than goose-minding.",
         end="{name} is there, painted and laughing, among the troupe's wagons. When {they} sees you the laughter stops."),
    dict(key="company", held=False, told="{they} went to take the free company's coin. Wanted to see the world, and fight in it.",
         end="{name} is there among the company's fires, older-looking than {they} has any right to be. {they.cap} knows at once who sent you."),
    dict(key="love", held=False, told="{they} went off with someone we didn't approve of. I said things I shouldn't have. {they.cap} left that night.",
         end="{name} is there, with the one {they} left for, in a hut they've made between them. {they.cap} stands in the doorway and doesn't come out."),
    dict(key="grave", held=False, told="{they} went to find where {their} father fell, out in the wild country. Said {they} wouldn't come back until {they} had.",
         end="{name} is there, kneeling by a cairn {they} has built with {their} own hands. {they.cap} has found what {they} came for, and doesn't know what to do next."),
]
CLUE_VILLAGE = ["At {place}, people remember {name}: {they} stopped here, asked the way {dir}, and went on toward {next}.",
                "Someone in {place} sold {name} a loaf and a blanket, and saw {them} take the road {dir}, toward {next}.",
                "{place} remembers {name} well enough: {they} slept in a byre here, and left at dawn, heading {dir} for {next}."]
CLUE_SITE = ["At {place} you find the ashes of a small fire, and a scrap of cloth from {name}'s coat caught on a thorn. Tracks lead {dir}, toward {next}.",
             "Scratched on a stone at {place}: {name}'s mark, the one {they} used as a child. An arrow beside it points {dir}, toward {next}.",
             "At {place} someone has left a ribbon tied to a branch, the colour {name} always wore. Beyond it, a trail goes {dir}, toward {next}."]
COLD = ["{name} is gone. There are signs {they} stayed here a long while, waiting, perhaps, for someone to come; then {they} went on, over the edge "
        "of the known country. On a stone, weighted down, {they} has left a letter for home.",
        "You are too late. {name} left here days ago, beyond where anyone can follow. Pinned under a stone is a letter, in {their} careful hand, addressed to home."]
ENDINGS = {
    "home": ["You walk into {home} with {name} beside you. {elder} sees {them} from the doorway and drops what {he} is holding, and then "
             "{he} is running, which nobody has seen {elder} do in years. That night the whole village eats at one table.",
             "{name} hangs back at the edge of {home}, suddenly shy. Then {elder} is there, and there's no more hanging back. You leave them "
             "to it. Later, someone brings you ale, and someone else brings more, and nobody lets you pay for anything."],
    "letter": ["You give {elder} the letter. {he.cap} reads it twice, standing in the lane, and then folds it small and puts it inside "
               "{his} shirt, over {his} heart. \"{name} is well,\" {he} says, to no one in particular. \"Well, and happy. That will do.\"",
               "{elder} reads {name}'s letter by the fire, and laughs once, and then is quiet a long time. \"{they.cap} always did know {their} own "
               "mind,\" {he} says at last. \"Thank you for finding {them}. Thank you for letting {them} be.\""],
    "cold": ["You give {elder} the letter you found. {he.cap} reads it, and sits down slowly. \"Gone on,\" {he} says. \"But not gone. "
             "{they.cap} says {they} will write.\" {he.cap} holds the letter as if it were {name}'s hand.",
             "{elder} takes the letter without a word. Whatever {name} wrote, it is enough: when {he} looks up, {he} is almost smiling. "
             "\"Somewhere out there,\" {he} says, \"{they} is all right. I can live with that.\""],
}


def pron(gender):
    return dict(they="she", them="her", their="her") if gender == "female" else dict(they="he", them="him", their="his")


@register
class HeirQuest(MQ.MainQuest):
    kind = "heir"
    clocked = True

    def setup(self, w, r):
        self.gender = r.choice(["female", "male"])
        self.name = w.new_name(w.culture_of(w.start), self.gender)
        self.relation = r.choice(RELATION[self.gender])
        self.reason = r.choice(REASONS)
        self.ending_pick = r.random()
        # the place they are: a camp at the far end of the trail
        w.tiles[w.quest_pos].site = dict(kind="camp")
        dist, qd = w.distances(w.start), w.distances(w.quest_pos)
        total = dist.get(w.quest_pos, 20)
        # the trail: four places, each further from home, wandering rather than heading straight for the end
        villages = [v for v in w.villages if v != w.start]
        sites = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] in ("camp", "shrine", "ruin") and p != w.quest_pos
                 and not w.tiles[p].site.get("quest")]
        md = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
        trail, prev = [], w.start
        for cands, lo, hi in ((villages, 4, total * 0.45), (sites, total * 0.3, total * 0.7),
                              (villages, total * 0.45, total * 0.85), (sites + villages, total * 0.6, total)):
            pool = [p for p in cands if p not in trail and lo <= dist.get(p, -1) <= hi and md(p, prev) >= 5 and md(p, w.quest_pos) >= 3]
            if pool:
                prev = r.choice(pool)
                trail.append(prev)
        self.trail = trail + [w.quest_pos]
        self.stage = 0                    # index into trail of where to go next
        self.deadline = 12
        self.found = False                # they are coming home with you
        self.letter = False               # you carry their letter instead
        self.ended = ""                   # "home", "letter" or "cold"

    def populate(self, w, r):
        if self.reason["held"]:
            q = w.tiles[w.quest_pos]
            undead = [s for s in w.species if s["arch"].get("undead")]
            c = w.make_creature(r.choice(undead or w.species), q.danger + 1, boss=True)
            c.title = f"the {r.choice(['Hollow', 'Pale', 'Singing', 'Grey', 'Silent'])} {r.choice(['Lady', 'King', 'Keeper', 'Warden', 'Piper'])} of {w.region_of(w.quest_pos)['name']}"
            q.creatures = [c]

    # ------------------------------------------------------------ words
    def fmt(self, text, g=None, **extra):
        p = pron(self.gender)
        ctx = dict(name=self.name, they=p["they"], them=p["them"], their=p["their"], **extra)
        ctx.update({"they.cap": cap(p["they"])})
        for k, v in ctx.items():
            text = text.replace("{" + k + "}", str(v))
        return text

    def place_name(self, w, p):
        from . import travel as TR
        return TR.label(w, p)

    def days_left(self, w):
        return max(0, self.deadline - w.day + 1)

    def cold(self, w):
        return w.day > self.deadline

    def heading(self, g):
        return f"The lost heir, {self.name}"

    # ------------------------------------------------------------ telling
    def offer(self, g, npc):
        w, n = g.world, g.narr
        first = self.trail[0]
        from . import lex_elders as EL
        they = self.fmt("{they}")
        g.emit(EL.speak(g, npc, "heir", dict(relation=self.relation, hname=self.name, reason=cap(self.fmt(self.reason["told"])),
                                             they_s={"text": they, "num": "pl" if they == "they" else "sg"}, they_cap=cap(they), them=self.fmt("{them}"),
                                             first=self.place_name(w, first), dir=n.dir_phrase(g.pos, first), days=self.days_left(w))))
        g.emit(f"(Quest: follow {self.name}'s trail and find {self.fmt('{them}')}. The trail goes cold after day {self.deadline}.)")

    def goal(self, g):
        w = g.world
        if self.found:
            return f"Bring {self.name} home to {home_name(w)}."
        if self.letter:
            return f"Take {self.name}'s letter home to {home_name(w)}."
        nxt = self.trail[self.stage]
        clock = " The trail has gone cold." if self.cold(w) else f" The trail goes cold in {self.days_left(w)} day{'s' if self.days_left(w) != 1 else ''}."
        if self.stage == len(self.trail) - 1:
            return f"Find {self.name} at {self.place_name(w, nxt)}." + clock
        return f"Follow {self.name}'s trail to {self.place_name(w, nxt)}." + clock

    def status(self, g):
        return f"bringing {self.name} home" if self.found else f"carrying {self.name}'s letter" if self.letter else ""

    def mark(self, g):
        if self.found or self.letter:
            return "home"
        return f"{self.name} was here" if self.stage < len(self.trail) - 1 else f"{self.name} is somewhere here"

    def targets(self, g):
        w = g.world
        return [w.start] if (self.found or self.letter) else [self.trail[self.stage]]

    def step(self, g):
        w, p = g.world, g.player
        if self.found or self.letter:
            return w.start, "toward home", f"Bring {'them' if self.found else 'the letter'} home.", True
        nxt = self.trail[self.stage]
        last = self.stage == len(self.trail) - 1
        ready = not (last and self.boss(w)) or p.level >= w.tiles[nxt].danger + 1
        return nxt, f"toward {self.place_name(w, nxt)}", f"{self.name}'s trail leads there.", ready

    def vision(self, g):
        w = g.world
        end = w.quest_pos
        if self.reason["held"]:
            return self.fmt(f"{self.name}, sitting very still in the dark {g.narr.dir_phrase(g.pos, end)}, and something tall standing over {{them}}")
        return self.fmt(f"{self.name} by a fire {g.narr.dir_phrase(g.pos, end)}, laughing at something someone has said")

    def lore(self, g):
        w = g.world
        return self.fmt(f"\"{self.name}? I've seen {{them}}. Went by {g.narr.dir_phrase(g.pos, w.quest_pos)}, a while back. "
                        + ("Didn't look like {they} was walking of {their} own will." if self.reason["held"] else "Looked like {they} knew where {they} was going.") + "\"")

    def rumour(self, narr, here):
        w = narr.w
        return self.fmt(f"the {self.relation} of the old one at {home_name(w)} went missing. {self.name}, {{they}} was called. Somebody saw {{them}} heading {narr.dir_phrase(here, w.quest_pos).split(' to the ')[-1]}")

    def carried(self, g):
        return ""

    def holds(self, it):
        return it.kind == "token" and it.name == f"{self.name}'s letter"

    # ------------------------------------------------------------ hooks
    def on_arrive(self, g):
        w = g.world
        if not g.has_quest or self.found or self.letter:
            return
        if g.pos not in self.trail[self.stage:]:
            return
        self.stage = self.trail.index(g.pos, self.stage)      # skipping ahead on the trail is fine
        last = self.stage == len(self.trail) - 1
        if not last:
            nxt = self.trail[self.stage + 1]
            d = g.narr.dir_phrase(g.pos, nxt).split(" to the ")[-1]
            pool = CLUE_VILLAGE if (w.tiles[g.pos].site or {}).get("kind") == "village" else CLUE_SITE
            g.emit(self.fmt(g.narr.pick(pool, "heir_clue"), place=self.place_name(w, g.pos), dir=d, next=self.place_name(w, nxt)))
            self.stage += 1
            g.emit(f"(Journal: {self.name}'s trail leads on to {self.place_name(w, nxt)}.)")
            return
        if self.cold(w):
            self.give_letter(g, cold=True)
            return
        if self.boss(w):
            return                        # the fight first; on_kill frees them
        self.meet(g)

    def on_kill(self, g, c):
        w = g.world
        if c.boss and g.pos == w.quest_pos and g.has_quest and not self.found:
            if self.cold(w):
                return self.give_letter(g, cold=True)
            g.emit(self.fmt(self.reason["end"]))
            self.found = True
            g.emit(f"({self.name} will come home with you. Take {self.fmt('{them}')} to {home_name(w)}.)")

    def meet(self, g):
        g.emit(self.fmt(self.reason["end"]))
        elder = MQ.elder_of(g.world)
        S.ask(g, self.fmt(f"\"Did {elder.name if elder else 'they'} send you?\" {self.name} asks."),
              [(self.fmt("Tell {them} how much {they} is missed at home"), "heir_plead", {}),
               (self.fmt("Give {them} the elder's love, and leave {them} to {their} own life"), "heir_leave", {}),
               (self.fmt("Tell {them} {they} is coming home, like it or not"), "heir_force", {})], leave=1)

    def give_letter(self, g, cold=False):
        from .world import Item
        if cold:
            g.emit(self.fmt(g.rng.choice(COLD)))
        g.player.inv.append(Item("token", f"{self.name}'s letter", value=0, facts=dict(material="folded paper", glow="a careful hand")))
        self.letter = True
        self.ended = "cold" if cold else "letter"
        g.emit(f"(Take {self.name}'s letter home to {home_name(g.world)}.)")

    def check(self, g):
        w = g.world
        if g.pos != w.start or not g.has_quest or not (self.found or (self.letter and any(self.holds(i) for i in g.player.inv))):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their", "him": "them"}
        kind = "home" if self.found else self.ended or "letter"
        pool = ENDINGS[kind]
        text = pool[int(self.ending_pick * len(pool))]
        text = self.fmt(text, home=home_name(w), elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"])
        text = text.replace("{he.cap}", cap(pr["he"]))
        MQ.win(g, text)


@S.choice_handler("heir_plead")
def _plead(g, d):
    q = g.world.quest
    if q.reason["key"] in ("troupe", "company") and g.rng.random() < 0.35:
        g.emit(q.fmt(f"{q.name} listens, and {{their}} face works, but in the end {{they}} shakes {{their}} head. \"I can't. Not yet. Give them this.\""))
        return q.give_letter(g)
    g.emit(q.fmt(f"You tell {{them}} about the empty place at the table, and the lamp left burning. {q.name} is quiet a long while. "
                 f"Then {{they}} nods, and goes to fetch {{their}} things."))
    q.found = True
    g.emit(f"({q.name} will come home with you.)")


@S.choice_handler("heir_leave")
def _leave(g, d):
    q = g.world.quest
    g.emit(q.fmt(f"You tell {q.name} {{they}} is loved, and missed, and free. {{they.cap}} hugs you, fierce and sudden, and writes a letter for home by the light of the fire."))
    q.give_letter(g)


@S.choice_handler("heir_force")
def _force(g, d):
    q = g.world.quest
    g.emit(q.fmt(f"{q.name} hears you out with {{their}} jaw set. In the night {{they}} slips away, and in the morning there is only a letter, "
                 f"weighted with a stone, addressed to home."))
    q.give_letter(g)
