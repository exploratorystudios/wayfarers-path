"""Main quest: the Beacons.

The year has stuck. Something that turns the seasons has fallen asleep, and the old way to wake
it is fire on the high places: three beacons on three far hills, lit in turn. Each beacon is a
pile of old timber that wants coaxing (burn some of your rations' fat, or spend hours gathering
fuel and risk what comes), and something has made its lair by at least one of them. With all
three alight, the sleeper wakes on its own high place; go to it, and then home.

The world starts in winter and stays there (the season never turns) until the sleeper wakes,
and then it is spring at once.
"""
from . import mainquest as MQ
from . import story as S
from . import travel as TR
from .mainquest import register, home_name
from .textgen import cap

SLEEPER = ["the Old Man of the Hill", "the Turner of the Year", "the Grey Sleeper", "the Lantern-bearer", "the Woman Under the Snow"]
WRONG = ["The {season} has gone on for three seasons' length. The stores are nearly gone.", "The birds left and haven't come back. The days don't lengthen.",
         "The sun rises in the same place every morning, and has done since the solstice. It shouldn't.",
         "Nothing grows and nothing dies. The whole land is holding its breath."]
WOKE = ["Far off, on its high place, something stirs: you feel it in the ground, like a cart passing on a road you can't see.",
        "As the last beacon catches, the wind changes, and somewhere a long way off a great voice yawns."]
ENDINGS = ["You come down out of the high country with the year turning behind you. By the time you reach {home} the ice is going off the ponds "
           "and the children are out looking for the first green. {elder} has kept the beacon-horn the old ones used, and sounds it once, for you.",
           "The weather breaks the day you come home to {home}: a warm wind, a smell of rain and turned earth. {elder} stands in the lane with "
           "{his} face turned up to it. \"There,\" {he} says, as if to someone you can't see. \"There. Told you they'd do it.\""]


@register
class BeaconsQuest(MQ.MainQuest):
    kind = "beacons"

    def setup(self, w, r):
        w.season = "winter"            # the year stuck in its dead season; waking the sleeper brings the spring
        self.sleeper = r.choice(SLEEPER)
        self.wrong = r.choice(WRONG)
        self.ending = r.choice(ENDINGS)
        w.tiles[w.quest_pos].site = dict(kind="camp")          # the sleeper's high place, an old fire-ring
        dist = w.distances(w.start)
        total = dist.get(w.quest_pos, 20)
        high = [p for p in w.land if w.tiles[p].biome in ("hills", "peaks") and not w.tiles[p].site]
        beacons = []
        for lo, hi in ((5, total * 0.6), (total * 0.35, total * 0.85), (total * 0.5, total * 1.1)):
            cands = [p for p in high if lo <= dist.get(p, -1) <= hi and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 6 for q in beacons + [w.quest_pos])]
            if not cands:
                cands = [p for p in w.land if p not in beacons and lo <= dist.get(p, -1) <= hi and not w.tiles[p].site] or \
                        [p for p in w.land if p not in beacons and p != w.quest_pos and not w.tiles[p].site]
            beacons.append(r.choice(cands))
        self.beacons = beacons
        self.lit = []
        self.woken = False

    def populate(self, w, r):
        far = max(self.beacons, key=lambda p: w.distances(w.start).get(p, 0))
        MQ.guardian(w, far, r, title=MQ.region_title(w, far, r, ["Cinder", "Ash", "Grey", "Old"], ["Watcher", "Keeper", "Hag", "King"]))

    # ------------------------------------------------------------ telling
    def unlit(self):
        return [p for p in self.beacons if p not in self.lit]

    def offer(self, g, npc):
        w, n = g.world, g.narr
        g.emit(f"{npc.name} looks older than {npc.pronouns()['he']} did a month ago. \"{self.wrong.format(season=w.season)} "
               f"The old ones would have known what to do: {self.sleeper} has gone to sleep, and must be woken, and the way to wake a sleeper like that is fire.\"")
        g.emit("\"Three beacons stand on the high places: " + "; ".join(f"{w.region_of(p)['name']}, {n.dir_phrase(g.pos, p)}" for p in self.beacons) +
               ". Light all three, and go up to where the sleeper lies when it stirs. Then come home and tell me the year has turned.\"")
        g.emit("(Quest: light the three beacons, then go to the sleeper's high place.)")

    def goal(self, g):
        w = g.world
        if self.done:
            return f"The year is turning. Go home to {home_name(w)}."
        if self.unlit():
            return f"Light the beacons ({len(self.lit)} of 3 lit): " + ", ".join(w.region_of(p)["name"] for p in self.unlit()) + "."
        return f"Go to {self.sleeper}'s high place in {w.region_of(w.quest_pos)['name']}."

    def status(self, g):
        return "the year turning" if self.done else f"{len(self.lit)} of 3 beacons lit"

    def mark(self, g):
        if self.done:
            return "home"
        return "an unlit beacon" if self.unlit() else f"{self.sleeper}'s high place"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        return self.unlit() or [w.quest_pos]

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", "The year is turning; tell them.", True
        left = self.unlit()
        if left:
            d = w.distances(g.pos)
            b = min(left, key=lambda q: d.get(q, 999))
            ready = not any(c.boss for c in w.tiles[b].creatures) or p.level >= w.tiles[b].danger + 1
            return b, "toward a beacon", "An unlit beacon stands there.", ready
        return w.quest_pos, "toward the sleeper", "The beacons are lit; the sleeper is stirring.", True

    def vision(self, g):
        return f"a great shape asleep on a high place {g.narr.dir_phrase(g.pos, g.world.quest_pos)}, frost in its beard, and three dark hilltops waiting for fire"

    def lore(self, g):
        return f"\"{cap(self.sleeper)}? Fire wakes it. Three fires, on the three high places. Bring fat to feed them; that old timber's half rotten.\""

    def rumour(self, narr, here):
        if self.lit:
            return f"someone's lit the old beacon on {narr.w.region_of(self.lit[-1])['name']}. You can see it from the ridge at night"
        return "the year's stuck. Old folk say the beacons want lighting, like in their grandmothers' day"

    def holds_season(self):
        return not self.done            # the year is stuck until the sleeper wakes

    def place_lines(self, narr, pos):
        if pos not in self.beacons:
            return []
        if pos in self.lit:
            return ["The beacon you lit still burns here, a red heart in a ring of blackened stones."]
        return ["On the highest point stands an old beacon: a pile of weathered timber in a ring of fire-blackened stones."]

    # ------------------------------------------------------------ hooks
    def on_arrive(self, g):
        w = g.world
        if not g.has_quest or self.done or g.pending:
            return
        if g.pos in self.unlit() and not any(c.boss for c in w.tiles[g.pos].creatures):
            opts = []
            if TR.rations(g) >= 2:
                opts.append(("Burn two rations' fat to get it going", "beacon_fat", {}))
            opts.append(("Spend a few hours gathering fuel", "beacon_gather", {}))
            opts.append(("Leave it for now", "beacon_wait", {}))
            S.ask(g, "The beacon's timber is old and damp. It will take some coaxing to light.", opts, leave=len(opts) - 1)
        elif g.pos == w.quest_pos and not self.unlit():
            self.done = True
            w.season = "spring"
            g.emit(f"{cap(self.sleeper)} is awake. You feel it more than see it: a great presence turning over, the way a sleeper turns toward morning. "
                   f"The wind comes round to the south, warm, and the snow starts to drip from every branch. Spring has come, all at once. (The year has turned. Go home to {home_name(w)}.)")
            from . import living as LV
            LV.season_check(g, quiet=True)

    def on_kill(self, g, c):
        if c.boss and g.pos in self.unlit():
            g.emit("With its keeper dead, the beacon is yours to light.")
            self.on_arrive(g)

    def light(self, g):
        w = g.world
        self.lit.append(g.pos)
        left = len(self.unlit())
        g.emit("The fire catches, crawls up the old timber, and then roars. From here it will be seen for miles." +
               (f" ({left} beacon{'s' if left != 1 else ''} still to light.)" if left else ""))
        if not left:
            g.emit(g.rng.choice(WOKE) + f" (Go to {self.sleeper}'s high place in {w.region_of(w.quest_pos)['name']}.)")
            self.woken = True

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and g.has_quest):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their"}
        MQ.win(g, self.ending.format(home=home_name(w), elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"]))


@S.choice_handler("beacon_fat")
def _fat(g, d):
    g.player.rations -= 2
    g.emit("You smear the fat from two of your rations over the kindling and strike a light.")
    g.world.quest.light(g)


@S.choice_handler("beacon_gather")
def _gather(g, d):
    w, t = g.world, g.world.tiles[g.pos]
    g.pass_time(180)
    g.emit("It takes hours to find enough dry wood, and the light is going by the time you have it.")
    g.world.quest.light(g)
    if g.rng.random() < 0.4:
        fitting = [s for s in w.species if t.biome in s["arch"]["biomes"]]
        if fitting:
            c = w.make_creature(g.rng.choice(fitting), max(1, t.danger))
            c.aggressive = True
            t.creatures.append(c)
            g.emit("The fire draws something out of the dark.")
            g.emit(g.narr.creature_presence(c))


@S.choice_handler("beacon_wait")
def _wait(g, d):
    g.emit("You leave the beacon unlit, for now.")
