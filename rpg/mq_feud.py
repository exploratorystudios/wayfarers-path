"""Main quest: the Feud.

Two villages are about to go to war over a grievance, and the elder fears it will drag everyone
in. Hear each side (someone in each village tells it), then go to the place where it happened
and find out what really did. There's something there that knows the truth, or is the truth;
sometimes it has to be killed. Then you choose what to tell them, and go home.
"""
from . import mainquest as MQ
from . import story as S
from .mainquest import register, home_name
from .textgen import cap

GRIEVANCES = [
    dict(key="cattle", a="\"{b} stole our cattle. Twelve head, gone in a night, and their tracks led toward {b}. What else are we to think?\"",
         b="\"{a} says we took their cattle. We never. We lost beasts ourselves that month, and nobody asks about those.\"",
         truth="beast", found="Here, at {place}, the truth is plain: bones, dozens of them, cattle from both villages, gnawed and split. Something has been feeding here, and it is still here."),
    dict(key="stone", a="\"They moved the boundary stone at {place}. Moved it in the night, a furlong onto our grazing. Our grandfathers set that stone.\"",
         b="\"The stone moved itself, for all we know. We never touched it. {a} wants our grazing, and that's the size of it.\"",
         truth="flood", found="At {place} you see what happened: the stream changed its course in the spring floods and undercut the bank. The stone slid; nobody moved it. You can see the old hole, full of water."),
    dict(key="drowned", a="\"A child of ours drowned near {place}, and one of theirs was seen there that day. They know something, and they won't say.\"",
         b="\"Our boy was there, yes. He tried to pull the little one out. He's not spoken since. And they call him a murderer.\"",
         truth="witness", found="At {place} there's a fisherman's hut, and an old man in it who saw everything. \"The lad went in after her,\" he says. \"Went in twice. Nobody asked me. Nobody ever asks me.\""),
    dict(key="well", a="\"They poisoned the well at {place}. Half our sheep died drinking from it.\"",
         b="\"Poison! We drink from the same water. If it's foul, it's foul for everyone.\"",
         truth="beast", found="At {place} you find the reason the water went bad: a carcass rotting in the spring-head, and the thing that dragged it there coming back for more."),
    dict(key="betrothal", a="\"Their son broke a betrothal with our daughter at the altar at {place}, in front of everyone. There's no forgiving that.\"",
         b="\"He never broke it. She did. She sent word by her own cousin that she wouldn't have him, and he walked away rather than shame her.\"",
         truth="witness", found="At {place} the old priest who was to marry them remembers it well. \"The girl sent a message,\" he says. \"I carried it. She'd give her heart elsewhere. Nobody wanted to hear it.\""),
]
ENDINGS = {
    "truth": ["You come home to {home}. News has gone ahead of you: {a} and {b} have sat down at one table, and argued, and then got drunk together, "
              "which in these parts is the same as a treaty. {elder} shakes your hand a long time. \"Truth's a hard thing to carry,\" {he} says. \"You carried it.\"",
              "Word comes to {home} before you do: the men of {a} and {b} have gone home, and the cudgels are back in the thatch. {elder} meets you "
              "in the lane. \"No war,\" {he} says. \"I didn't think I'd live to say it.\""],
    "kind": ["You come home to {home}. {a} and {b} have made their peace, on your word; it isn't quite the true word, but it's a kind one. "
             "{elder} looks at you a long while, and seems to understand more than you told. \"Peace is peace,\" {he} says. \"Let it lie.\""],
}


@register
class FeudQuest(MQ.MainQuest):
    kind = "feud"

    def setup(self, w, r):
        dist = w.distances(w.start)
        others = sorted((v for v in w.villages if v != w.start), key=lambda v: dist.get(v, 99))
        md = lambda p, q: abs(p[0] - q[0]) + abs(p[1] - q[1])
        pairs = [(a, b) for i, a in enumerate(others) for b in others[i + 1:] if 5 <= md(a, b) <= 14]
        self.va, self.vb = r.choice(pairs) if pairs else (others[0], others[-1])
        self.griev = r.choice(GRIEVANCES)
        # where it happened: the quest's far square, a landmark between them or beyond
        self.place_pos = w.quest_pos
        t = w.tiles[w.quest_pos]
        t.site = None
        if not t.features:
            from . import lexicon as L
            t.features = [w.make_feature(L.FEATURES[t.biome][0])]
        self.heard_a = self.heard_b = False
        self.found = False
        self.told = ""
        self.ending_pick = r.random()

    def populate(self, w, r):
        if self.griev["truth"] == "beast":
            MQ.guardian(w, self.place_pos, r, title=MQ.region_title(w, self.place_pos, r, ["Red", "Gorged", "Old", "Night"], ["Taker", "Reaver", "Prowler", "Thief"]))

    # ------------------------------------------------------------ telling
    def place(self, w):
        t = w.tiles[self.place_pos]
        noun = t.features[0].noun if t.features else "place"
        return f"the {noun} in {w.region_of(self.place_pos)['name']}"

    def names(self, w):
        return w.tiles[self.va].site["name"], w.tiles[self.vb].site["name"]

    def offer(self, g, npc):
        w, n = g.world, g.narr
        a, b = self.names(w)
        g.emit(f"{npc.name} is grim. \"{a} and {b} are sharpening scythes for each other. It started over something at {self.place(w)}, and "
               f"it's grown in the telling until nobody remembers what's true. If it comes to blood, every village from here to the hills will be in it by winter.\"")
        g.emit(f"\"Somebody has to hear both sides with no stake in it, and go and see for themselves. Start at {a}, {n.dir_phrase(g.pos, self.va)}, "
               f"and {b}, {n.dir_phrase(g.pos, self.vb)}. Find out what happened at {self.place(w)}. Then do what you think is right, and come and tell me.\"")
        g.emit("(Quest: hear both sides of the feud, find out what really happened, and settle it.)")

    def goal(self, g):
        w = g.world
        a, b = self.names(w)
        if self.done:
            return f"The feud is settled. Go home to {home_name(w)}."
        if not (self.heard_a and self.heard_b):
            left = [x for x, h in ((a, self.heard_a), (b, self.heard_b)) if not h]
            return f"Hear the feud from both sides: go to {' and '.join(left)}."
        return f"Find out what really happened at {self.place(w)}."

    def status(self, g):
        return "the feud settled" if self.done else ""

    def mark(self, g):
        if self.done:
            return "home"
        if not (self.heard_a and self.heard_b):
            return "one side of the feud"
        return "where the feud began"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        left = [v for v, h in ((self.va, self.heard_a), (self.vb, self.heard_b)) if not h]
        return left or [self.place_pos]

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", "The feud is settled; tell them.", True
        left = [v for v, h in ((self.va, self.heard_a), (self.vb, self.heard_b)) if not h]
        if left:
            d = w.distances(g.pos)
            v = min(left, key=lambda v: d.get(v, 999))
            return v, f"toward {w.tiles[v].site['name']}", "One side of the feud lives there.", True
        return self.place_pos, "toward where it began", "Find out what really happened.", p.level >= w.tiles[self.place_pos].danger + (1 if self.boss_here(w) else 0)

    def boss_here(self, w):
        return any(c.boss for c in w.tiles[self.place_pos].creatures)

    def vision(self, g):
        return f"{self.place(g.world)}, {g.narr.dir_phrase(g.pos, self.place_pos)}, and on the ground there the answer to an old quarrel"

    def lore(self, g):
        a, b = self.names(g.world)
        return f"\"{a} and {b}? Fools, the pair of them. Neither's lying, and neither's right. Go and look at {self.place(g.world)} with your own eyes.\""

    def rumour(self, narr, here):
        a, b = self.names(narr.w)
        if self.done:
            return f"{a} and {b} have made it up. Who'd have thought"
        return f"there'll be blood between {a} and {b} before the year's out, mark me"

    # ------------------------------------------------------------ hooks
    def on_arrive(self, g):
        w = g.world
        if not g.has_quest or self.done or g.pending:
            return
        a, b = self.names(w)
        if g.pos == self.va and not self.heard_a:
            self.heard_a = True
            g.emit(f"In {a} they talk of nothing else. " + self.griev["a"].format(a=a, b=b, place=self.place(w)) + " (Journal: you've heard {a}'s side.)".format(a=a))
        elif g.pos == self.vb and not self.heard_b:
            self.heard_b = True
            g.emit(f"In {b} the mood is sour. " + self.griev["b"].format(a=a, b=b, place=self.place(w)) + " (Journal: you've heard {b}'s side.)".format(b=b))
        elif g.pos == self.place_pos and not self.found:
            g.emit(self.griev["found"].format(place=self.place(w)))
            if not self.boss_here(w):
                self.reveal(g)

    def on_kill(self, g, c):
        if c.boss and g.pos == self.place_pos and not self.found:
            g.emit("With the beast dead, there is nothing left to steal from either village. Now they only need to be told.")
            self.reveal(g)

    def reveal(self, g):
        self.found = True
        a, b = self.names(g.world)
        S.ask(g, f"You know what happened now. What will you tell {a} and {b}?",
              [("The whole truth, hard as it is", "feud_truth", {}), ("A kinder story that lets both sides save face", "feud_kind", {})], leave=None)

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and g.has_quest):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their"}
        a, b = self.names(w)
        pool = ENDINGS[self.told or "truth"]
        text = pool[int(self.ending_pick * len(pool))]
        MQ.win(g, text.format(home=home_name(w), a=a, b=b, elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"]))


@S.choice_handler("feud_truth")
def _truth(g, d):
    q = g.world.quest
    a, b = q.names(g.world)
    q.done, q.told = True, "truth"
    g.emit(f"You send word to {a} and {b} by the first carter going that way: what you saw, all of it. It will sting. It will also be true. "
           f"(The feud is settled. Go home to {home_name(g.world)}.)")


@S.choice_handler("feud_kind")
def _kind(g, d):
    q = g.world.quest
    a, b = q.names(g.world)
    q.done, q.told = True, "kind"
    g.emit(f"You send word to {a} and {b}: a story in which nobody is to blame, and everyone was a little wrong. It isn't what happened. "
           f"It will do. (The feud is settled. Go home to {home_name(g.world)}.)")
