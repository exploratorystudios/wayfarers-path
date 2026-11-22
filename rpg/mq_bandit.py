"""Main quest: the Bandit Lord.

A robber captain holds an old fort on the roads, and takes a toll of everything that moves.
No one village can stand against them. Go to three villages and win them over: each asks
something (coin for arms, or proof that you're worth following). Then go to the fort. With
the villages behind you the captain's champion, a great beast they keep on a chain, is
weaker; with all three, the captain may yield without a fight. Then home.
"""
from . import mainquest as MQ
from . import story as S
from .mainquest import register, home_name
from .textgen import cap, and_list

TITLES = ["the Red Captain", "the Toll-lord", "Captain Ashes", "the Widow's Son", "the Grey Captain", "Black Hollin"]
DEEDS = ["They took the miller's whole harvest at the ford, and the miller's son for a hostage.",
         "They hanged a carter on the crossroads gibbet for paying short.", "Nobody takes goods to market now. What's the point, when half goes to the fort?",
         "They burned the toll-house at the bridge to show us what refusing looks like."]
ASKS = [
    dict(key="coin", ask="\"We'll stand with you, if we've arms to stand with. {n} coins buys spears for the young ones.\"", cost=20),
    dict(key="proof", ask="\"Show us you can fight first. We'll not follow someone the captain's dogs would eat.\"", level=3),
    dict(key="word", ask="\"We'll come. We've waited years for someone to ask.\""),
]
ENDINGS = {
    "yield": ["You come home to {home} with the roads open behind you. The captain gave up the fort without a blow struck, when they saw three villages at "
              "the gate. {elder} has the toll-chain from the bridge hung over {his} door. \"Never again,\" {he} says, and means it."],
    "fight": ["You come home to {home} with the fort burning behind you, and the roads open for the first time in years. Carts are already moving. "
              "{elder} counts them going by from {his} doorstep, and every one is a small, quiet victory.",
              "The captain's gone, run off over the hills with what they could carry, and the fort is ash. When you reach {home}, {elder} has the "
              "whole village out to meet you, and the first full market in years is being set up in the lane."],
}


@register
class BanditQuest(MQ.MainQuest):
    kind = "bandit"

    def setup(self, w, r):
        self.captain = r.choice(TITLES)
        self.deed = r.choice(DEEDS)
        w.tiles[w.quest_pos].site = w.make_ruin(quest=True)
        dist = w.distances(w.start)
        others = sorted((v for v in w.villages if v != w.start), key=lambda v: dist.get(v, 99))
        pick = [others[i] for i in sorted({0, len(others) // 2, len(others) - 1}) if i < len(others)]
        asks = list(ASKS)
        r.shuffle(asks)
        self.allies = [dict(pos=v, ask=a["key"], won=False) for v, a in zip(pick, asks)]
        self.yielded = False
        self.ending_pick = r.random()

    def populate(self, w, r):
        hounds = [s for s in w.species if s["key"] in ("wolf", "bear", "boar")] or w.species
        q = w.tiles[w.quest_pos]
        c = w.make_creature(r.choice(hounds), q.danger + 1, boss=True)
        c.title = f"{self.captain}'s war-{c.species['arch']['noun']}"
        q.creatures = [c]

    def heading(self, g):
        return cap(self.captain)

    # ------------------------------------------------------------ telling
    def won(self):
        return [a for a in self.allies if a["won"]]

    def name(self, w, a):
        return w.tiles[a["pos"]].site["name"]

    def fort(self, w):
        q = w.tiles[w.quest_pos]
        return f"the old {q.site['purpose']} in {w.region_of(w.quest_pos)['name']}"

    def offer(self, g, npc):
        w, n = g.world, g.narr
        g.emit(f"{npc.name} spits. \"{cap(self.captain)}. Holds {self.fort(w)}, {n.dir_phrase(g.pos, w.quest_pos)}, and has made a fort of it, with a crew of cut-throats and a beast on a chain. "
               f"{self.deed}\"")
        g.emit("\"No village can stand alone. Together, maybe. Go to " + and_list(self.name(w, a) for a in self.allies) +
               " and ask them to stand with us. Then go to the fort. If they see enough of us at the gate, they might not even fight.\"")
        g.emit("(Quest: win over three villages, then break the captain's hold on the roads.)")

    def goal(self, g):
        w = g.world
        if self.done:
            return f"The roads are free. Go home to {home_name(w)}."
        left = [a for a in self.allies if not a["won"]]
        tail = f"Go to the captain's fort, {self.fort(w)}" + (f" ({len(self.won())} of 3 villages with you)." if self.won() else ".")
        if left:
            return "Win over " + and_list(self.name(w, a) for a in left) + f", or go straight to {self.fort(w)}."
        return tail

    def status(self, g):
        return "the roads free" if self.done else f"{len(self.won())} of 3 villages rallied"

    def mark(self, g):
        if self.done:
            return "home"
        return f"{self.captain}'s fort"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        left = [a["pos"] for a in self.allies if not a["won"]]
        return left or [w.quest_pos]

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", "The roads are free; tell them.", True
        left = [a for a in self.allies if not a["won"] and self.can_win(g, a)]
        if left:
            d = w.distances(g.pos)
            a = min(left, key=lambda a: d.get(a["pos"], 999))
            return a["pos"], f"toward {self.name(w, a)}", "Ask them to stand with you.", True
        if len(self.won()) == 3:
            return w.quest_pos, "toward the fort", "Three villages stand with you.", True
        return w.quest_pos, "toward the fort", "Break the captain's hold.", p.level >= w.tiles[w.quest_pos].danger + 1 - len(self.won()) // 2

    def can_win(self, g, a):
        need = next(x for x in ASKS if x["key"] == a["ask"])
        if need.get("cost"):
            return g.player.gold >= need["cost"]
        if need.get("level"):
            return g.player.level >= need["level"]
        return True

    def vision(self, g):
        return f"a fort {g.narr.dir_phrase(g.pos, g.world.quest_pos)} with a red rag for a flag, and a great beast pacing on a chain inside the gate"

    def lore(self, g):
        return f"\"{cap(self.captain)}? All bluster and a big dog. Bring enough people to the gate and you'll see how brave they are.\""

    def rumour(self, narr, here):
        if self.won():
            return f"{self.name(narr.w, self.won()[-1])} has said it'll stand against {self.captain}. Brave, or mad"
        return f"{self.captain} took another cart on the old road. Folk are saying enough is enough"

    # ------------------------------------------------------------ hooks
    def ally_here(self, g):
        return next((a for a in self.allies if a["pos"] == g.pos and not a["won"]), None)

    def on_arrive(self, g):
        w = g.world
        if not g.has_quest or self.done or g.pending:
            return
        a = self.ally_here(g)
        if a:
            need = next(x for x in ASKS if x["key"] == a["ask"])
            text = f"In {self.name(w, a)} they've heard why you've come. " + need["ask"].replace("{n}", str(need.get("cost", 0)))
            opts = []
            if need.get("cost"):
                opts.append((f"Pay {need['cost']} coins for spears", "bandit_pay", {}) if g.player.gold >= need["cost"] else
                            ("You haven't the coin yet", "bandit_later", {}))
            elif need.get("level"):
                opts.append(("Show them what you can do", "bandit_prove", {}) if g.player.level >= need["level"] else
                            ("You aren't ready to prove yourself yet", "bandit_later", {}))
            else:
                opts.append(("Thank them", "bandit_word", {}))
            if opts[0][1] != "bandit_later":
                opts.append(("Not now", "bandit_later", {}))
            S.ask(g, text, opts, leave=len(opts) - 1)
        elif g.pos == w.quest_pos and len(self.won()) == 3 and not self.yielded:
            self.yielded = True
            c = self.boss(w)
            if c:
                w.tiles[g.pos].creatures.remove(c)
            g.combat = None
            self.done = True
            g.emit(f"Three villages' worth of people come up the road behind you, with spears and flails and their grandfathers' swords. {cap(self.captain)} "
                   f"looks down at them from the wall a long while. Then the gate opens, and the chain on the great beast is handed out to you, "
                   f"and the captain and their crew walk away over the hills. (The roads are free. Go home to {home_name(w)}.)")
        elif g.pos == w.quest_pos and self.won():
            c = self.boss(w)
            if c and not getattr(self, "softened", False):
                self.softened = True
                cut = 0.2 * len(self.won())
                c.hp = max(10, int(c.hp * (1 - cut)))
                g.emit(f"The people of {', '.join(self.name(w, a) for a in self.won())} came with you; they hold the captain's crew at the gate while you face the beast.")

    def on_kill(self, g, c):
        if c.boss and g.pos == g.world.quest_pos and not self.done:
            self.done = True
            g.emit(f"With its champion dead, {self.captain}'s crew breaks and runs. By nightfall the fort is burning. (The roads are free. Go home to {home_name(g.world)}.)")

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and g.has_quest):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their"}
        pool = ENDINGS["yield" if self.yielded else "fight"]
        text = pool[int(self.ending_pick * len(pool))]
        MQ.win(g, text.format(home=home_name(w), elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"]))


def _join(g):
    q = g.world.quest
    a = q.ally_here(g)
    if a:
        a["won"] = True
        g.emit(f"{q.name(g.world, a)} will stand with you. ({len(q.won())} of 3 villages.)")


@S.choice_handler("bandit_pay")
def _pay(g, d):
    q = g.world.quest
    a = q.ally_here(g)
    cost = next(x for x in ASKS if x["key"] == a["ask"])["cost"] if a else 0
    if g.player.gold < cost:
        return g.emit("You haven't the coin.")
    g.player.gold -= cost
    g.emit(f"You count out {cost} coins. By evening there's a smith working by lamplight, beating out spearheads.")
    _join(g)


@S.choice_handler("bandit_prove")
def _prove(g, d):
    g.emit("You knock the village's best wrestler flat on the green, twice, and the second time he laughs from the ground and offers his hand.")
    _join(g)


@S.choice_handler("bandit_word")
def _word(g, d):
    g.emit("They need no persuading. Somebody has already taken a scythe down from the rafters.")
    _join(g)


@S.choice_handler("bandit_later")
def _later(g, d):
    g.emit("\"Come back when you're ready, then.\"")
