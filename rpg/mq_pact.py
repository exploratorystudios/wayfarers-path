"""Main quest: the Broken Pact.

Long ago the village swore an oath with the spirit of a high place, and renewed it every
generation with three gifts. This year no one went, and things are going wrong. Gather the three
gifts from three places (water from a spring or well, a stone from an old circle or cairn,
something from a great tree), the last of them kept by a guardian, and bring them to the
spirit's place by night. What you say to the spirit there decides the ending.
"""
from . import mainquest as MQ
from . import story as S
from .mainquest import register, home_name
from .textgen import cap, and_list

SPIRIT_PRE = ["the Lady of", "Old Man", "the Grey Watcher of", "the Mother of", "the Horned One of", "the Sleeper under"]
GIFTS = [
    dict(key="water", tags={"water"}, item="flask of {noun} water", take="You kneel and fill a flask from the {noun}. The water is so cold it aches.",
         ask="This is the {noun} the old songs name. Its water is one of the three gifts."),
    dict(key="stone", kinds={"standing stone", "stone circle", "cairn", "outcrop"}, item="stone from the {noun}",
         take="You work a small stone loose from the {noun}, and ask its pardon as you do. It is heavier than it looks.",
         ask="This is the {noun} the old songs name. A stone from it is one of the three gifts."),
    dict(key="tree", tags={"tree"}, item="sprig of the {noun}", take="You cut a sprig from the {noun}. The cut weeps a little, then stops.",
         ask="This is the {noun} the old songs name. A sprig of it is one of the three gifts."),
]
WRONG = ["The springs are drying up, one by one.", "The cattle won't go near the high pastures any more.",
         "Children wake screaming, all of them, the same nights.", "The harvest rots in the barn before it can be threshed.",
         "The river has started running backwards at dusk. I've seen it."]
WHY = ["The one who should have gone died in the spring, and nobody else knew the way.",
       "We forgot. That's the truth of it. A hundred years is a long time, and we forgot.",
       "The young ones said it was a story for children, and the old ones let them say it."]
ENDINGS = {
    "renew": ["You come home to {home} with the night's work still on you like dew. Before you can say a word, {elder} has seen it in your face. "
              "By morning the springs are running, and in the high pastures the cattle are grazing as if nothing had ever been wrong.",
              "News of what you did on the hill reaches {home} before you do; such news always does. {elder} meets you with a cup of the "
              "first water from the spring, and it is sweet. \"Another hundred years,\" {he} says. \"You've bought us another hundred years.\""],
    "bargain": ["You come home to {home} and tell {elder} what you agreed. {he.cap} is quiet a long while. \"It's done, then,\" {he} says. "
                "\"And it will be easier for us than the old pact, and harder for whoever comes after. Well. We'll teach them the way, this time.\""],
}


@register
class PactQuest(MQ.MainQuest):
    kind = "pact"

    def setup(self, w, r):
        w.tiles[w.quest_pos].site = w.make_shrine(w.tiles[w.quest_pos].biome)
        self.spirit = w.tiles[w.quest_pos].site["spirit"]
        self.wrong, self.why = r.choice(WRONG), r.choice(WHY)
        dist = w.distances(w.start)
        total = dist.get(w.quest_pos, 20)
        spots, used = [], [w.start, w.quest_pos]
        for i, gift in enumerate(GIFTS):
            lo, hi = [(4, total * 0.5), (total * 0.3, total * 0.75), (total * 0.5, total)][i]
            cands = MQ.landmark_spots(w, kinds=gift.get("kinds"), tags=gift.get("tags"), lo=lo, hi=hi, avoid=used)
            if not cands:
                cands = MQ.landmark_spots(w, kinds=gift.get("kinds"), tags=gift.get("tags"), avoid=used, gap=3)
            pos, f = r.choice(cands) if cands else (r.choice([p for p in w.land if p not in used]), None)
            noun = f.noun if f else {"water": "spring", "stone": "stone", "tree": "tree"}[gift["key"]]
            spots.append(dict(key=gift["key"], pos=pos, noun=noun, item=gift["item"].format(noun=noun), got=False))
            used.append(pos)
        r.shuffle(spots)
        self.spots = spots
        self.renewed = ""
        self.ending_pick = r.random()

    def populate(self, w, r):
        last = max(self.spots, key=lambda s: w.distances(w.start).get(s["pos"], 0))
        MQ.guardian(w, last["pos"], r, title=MQ.region_title(w, last["pos"], r, ["Old", "Grey", "Thorn", "Hollow"], ["Warden", "Keeper", "Watcher"]))
        self.kept = last["key"]

    def heading(self, g):
        return f"The pact with {self.spirit}"

    # ------------------------------------------------------------ telling
    def missing(self):
        return [s for s in self.spots if not s["got"]]

    def offer(self, g, npc):
        w, n = g.world, g.narr
        from . import lex_elders as EL
        parts = "; ".join(f"the {s['noun']} {n.dir_phrase(g.pos, s['pos'])}" for s in self.spots)
        g.emit(EL.speak(g, npc, "pact", dict(spirit=self.spirit, why=self.why, wrong=self.wrong, spots=parts, dir=n.dir_phrase(g.pos, w.quest_pos))))
        g.emit("(Quest: gather the three gifts and bring them to the spirit's shrine by night.)")

    def goal(self, g):
        w = g.world
        if self.done:
            return f"The pact is made. Go home to {home_name(w)}."
        left = self.missing()
        if left:
            return "Gather the gifts for the pact: " + and_list(f"the {s['item']}" for s in left) + "."
        return f"Bring the three gifts to {self.spirit}'s shrine in {w.region_of(w.quest_pos)['name']}, by night."

    def status(self, g):
        return "the pact renewed" if self.done else f"{3 - len(self.missing())} of 3 gifts gathered"

    def mark(self, g):
        if self.done:
            return "home"
        return f"{self.spirit}'s shrine" if not self.missing() else "a place the old songs name"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        left = self.missing()
        return [s["pos"] for s in left] if left else [w.quest_pos]

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", "The pact is made; tell them.", True
        left = self.missing()
        if left:
            d = w.distances(g.pos)
            s = min(left, key=lambda s: d.get(s["pos"], 999))
            ready = not any(c.boss for c in w.tiles[s["pos"]].creatures) or p.level >= w.tiles[s["pos"]].danger + 1
            return s["pos"], f"toward the {s['noun']}", f"One of the three gifts is there.", ready
        return w.quest_pos, f"toward {self.spirit}'s shrine", "Bring the gifts there by night.", True

    def act(self, g):
        w = g.world
        if self.done or self.missing() or g.pos != w.quest_pos or g.pending or g.combat:
            return None
        if w.is_dark:
            return "pray", f"Present the gifts to {self.spirit}", "It is night; the spirit is listening."
        return "wait", "Wait for nightfall", f"{self.spirit} only listens by night."

    def on_pray(self, g, site):
        w = g.world
        if self.done or g.pos != w.quest_pos or self.missing():
            return ""
        if not w.is_dark:
            return f"You lay out the gifts, but the shrine is only stone in daylight. {self.spirit} listens by night."
        self.present(g)
        return "(Choose what to say.)"

    def present(self, g):
        g.emit(f"The night is very still at {self.spirit}'s shrine. Then the stillness changes, and you know you are not alone.")
        S.ask(g, f"\"You have brought the gifts,\" says {self.spirit}, in a voice like wind in a chimney. \"Say the words, and the pact is made again.\"",
              [("Say the old words, and renew the pact as it was", "pact_renew", {}),
               ("Ask for a better bargain for the village", "pact_bargain", {})], leave=None)

    def vision(self, g):
        return f"three gifts laid on a stone at {self.spirit}'s shrine {g.narr.dir_phrase(g.pos, g.world.quest_pos)}, and something vast and patient leaning down to look at them"

    def lore(self, g):
        return (f"\"{cap(self.spirit)}? An old pact, that. Water, stone and green wood, and the words said by moonlight. Miss the night and "
                f"you'll be talking to an empty hill.\"")

    def rumour(self, narr, here):
        return f"the old pact with {self.spirit} has [run out|lapsed|come due], [they say|so the old folk say], and [nobody's been up the hill to make it again|nobody remembers the words|the hill's gone quiet]"

    def holds(self, it):
        return it.kind == "token" and any(it.name == s["item"] for s in self.spots)

    # ------------------------------------------------------------ hooks
    def spot_here(self, g):
        return next((s for s in self.spots if s["pos"] == g.pos and not s["got"]), None)

    def on_arrive(self, g):
        w = g.world
        if not g.has_quest or self.done or g.pending:
            return
        s = self.spot_here(g)
        if s and not any(c.boss for c in w.tiles[g.pos].creatures):
            gift = next(x for x in GIFTS if x["key"] == s["key"])
            S.ask(g, gift["ask"].format(noun=s["noun"]), [(f"Take the {s['item']}", "pact_take", dict(key=s["key"])), ("Leave it for now", "pact_wait", {})], leave=1)
        elif g.pos == w.quest_pos and not self.missing() and w.is_dark:
            self.present(g)

    def on_kill(self, g, c):
        if c.boss and self.spot_here(g):
            g.emit("With its keeper dead, the place is quiet. You can take what you came for.")
            self.on_arrive(g)

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and g.has_quest):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their"}
        pool = ENDINGS[self.renewed or "renew"]
        text = pool[int(self.ending_pick * len(pool))]
        MQ.win(g, text.format(home=home_name(w), elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"]).replace("{he.cap}", cap(pr["he"])))


@S.choice_handler("pact_take")
def _take(g, d):
    from .world import Item
    q = g.world.quest
    s = next(x for x in q.spots if x["key"] == d["key"])
    gift = next(x for x in GIFTS if x["key"] == s["key"])
    s["got"] = True
    g.player.inv.append(Item("token", s["item"], value=0, facts=dict(material="a gift for the pact", glow="something older than you")))
    left = len(q.missing())
    g.emit(gift["take"].format(noun=s["noun"]) + (f" ({left} gift{'s' if left != 1 else ''} still to find.)" if left else
                                                  f" (That's all three gifts. Take them to {q.spirit}'s shrine, by night.)"))


@S.choice_handler("pact_wait")
def _wait(g, d):
    g.emit("You leave it be, for now.")


def _finish(g, how, text):
    q = g.world.quest
    for s in q.spots:
        it = next((i for i in g.player.inv if i.name == s["item"]), None)
        if it:
            g.player.inv.remove(it)
    q.done, q.renewed = True, how
    g.emit(text + f" (The pact is made. Go home to {home_name(g.world)}.)")


@S.choice_handler("pact_renew")
def _renew(g, d):
    q = g.world.quest
    _finish(g, "renew", f"You lay the three gifts on the stone and say the words as the elder taught them. {q.spirit} takes the gifts, "
                        f"one by one, and when you look again the stone is bare and the night smells of rain.")


@S.choice_handler("pact_bargain")
def _bargain(g, d):
    q = g.world.quest
    _finish(g, "bargain", f"You ask for more: a gentler pact, an easier price. {q.spirit} laughs, and the hill shakes with it. \"Bold. Very well: "
                          f"less from them now, and more from those who come after.\" The gifts are gone from your hands.")
