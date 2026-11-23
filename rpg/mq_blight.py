"""Main quest: the Blight.

A rot is spreading over the land from one place, a little further every day: grass greys,
water sours, trees weep black. You can see it in the descriptions, and it is always thickest
toward its heart. The elder knows roughly where it began. At the heart something feeds it; kill
that, and bless the ground (a shrine's favour, or holy water) to end it. Then go home.

It has a clock: if the blight reaches home before you end it, the people flee, and the ending,
when it comes, is a sadder one. The quest can still be finished.
"""
from . import mainquest as MQ
from .mainquest import register, home_name
from .textgen import cap, article

CAUSE = [
    "Treasure-diggers broke into {site} out in {region}, and whatever they woke has been leaking out since.",
    "There was a killing at {site} in {region}, a bad one, and the ground never forgave it.",
    "Somebody laid a curse at {site} in {region}. I don't know who, and I don't know why. I know it's working.",
    "Something died at {site} in {region}, something old that should not have been able to die, and it is rotting into the land.",
    "The spring at {site} in {region} went sour at midsummer. Everything it waters has gone sour after it.",
]
SIGN = ["The bees are dying in their skeps.", "The milk turns in the pail before it's cool.", "The well water tastes of pennies and graves.",
        "Lambs are coming wrong, the ones that come at all.", "The crows have left. Even the crows."]
LINES = {
    "plains": ["The grass here is grey and brittle, as if a frost had come and never lifted.", "Patches of turf have gone black and soft, and give under your boots.",
               "Nothing sings out here. The grass has a dull, sick sheen to it."],
    "forest": ["The bark here is spotted black, and some of the trees weep a dark sap.", "Fungus the colour of old bruises crowds the roots of every tree.",
               "The undergrowth has gone limp and grey, and smells faintly sweet, like meat left out."],
    "hills": ["The heather is dead in great grey swathes, and the bracken has blackened where it stands.", "The sheep-tracks are empty, and the turf has a grey crust on it."],
    "marsh": ["The pools have an oily skin on them, and the reeds are dying from the tips down.", "The water smells wrong here, sweet and rotten at once."],
    "peaks": ["Even the lichen on the rocks has gone grey and flaky.", "A grey film coats the stones, and comes away on your fingers like ash."],
}
EDGE = ["The rot is thinner here. It grows worse toward the {d}.", "It's worst toward the {d}; you can see the grey deepen that way.",
        "The blight is thickest to the {d}."]
ENDINGS = [
    "You come home to {home} with the land healing behind you. Green is already pushing up through the grey. {elder} meets you in the lane "
    "and doesn't say anything at all, only holds your hands a long while. That night they draw water from the well, and drink it, and it is sweet.",
    "By the time you reach {home} the news has gone ahead of you on the wind: the blight is lifting. People are out in the fields, "
    "kneeling, putting their hands on the turf as if to make sure. {elder} has set a place for you at the head of the table.",
]
LATE = [
    "You come home to {home}. The blight is lifting, and the grass will come back, but the houses stand empty. Its people went to {refuge} "
    "when the rot reached their doors; some of them will come home, in time. {elder} stayed, as the old will. \"You ended it,\" {he} says. "
    "\"That's what matters. The rest we'll mend.\"",
    "The blight is gone, and {home} is quiet. Most of its people fled to {refuge} when the grey came over the fields. {elder} sits on "
    "{his} doorstep in the empty lane and watches the first green come back. \"They'll return,\" {he} says. \"I'll be here when they do.\"",
]


@register
class BlightQuest(MQ.MainQuest):
    kind = "blight"
    clocked = True

    def setup(self, w, r):
        site = w.make_ruin(quest=True)
        w.tiles[w.quest_pos].site = site
        self.cause = r.choice(CAUSE)
        self.sign = r.choice(SIGN)
        self.ending, self.late_ending = r.choice(ENDINGS), r.choice(LATE)
        self.dist = w.distances(w.quest_pos)
        self.home_d = self.dist.get(w.start, 20)
        self.r0 = 2.0
        self.rate = max(0.8, (self.home_d - self.r0) / 11.0)     # reaches home around day twelve
        self.cleansed = False
        self.blessed_by = None
        others = [v for v in w.villages if v != w.start]
        self.refuge = max(others, key=lambda v: self.dist.get(v, 0)) if others else w.start
        self.warned = 0

    def populate(self, w, r):
        q = w.tiles[w.quest_pos]
        undead = [s for s in w.species if s["arch"].get("undead")]
        fitting = undead or [s for s in w.species if q.biome in s["arch"]["biomes"]] or w.species
        c = w.make_creature(r.choice(fitting), q.danger + 1, boss=True)
        c.title = f"the {r.choice(['Rot', 'Grey', 'Sour', 'Weeping', 'Hollow'])} {r.choice(['Mother', 'King', 'Heart', 'Root', 'Keeper'])} of {w.region_of(w.quest_pos)['name']}"
        q.creatures = [c]
        self.boss_title = c.title

    # ------------------------------------------------------------ the spread
    def radius(self, w):
        return self.r0 + self.rate * (w.day - 1)

    def blighted(self, w, p):
        return not self.cleansed and self.dist.get(p, 999) <= self.radius(w)

    def steps_from_home(self, w):
        return max(0, int(self.home_d - self.radius(w)))

    def days_left(self, w):
        return max(0, int((self.home_d - self.radius(w)) / self.rate + 0.999))

    # ------------------------------------------------------------ telling
    def site_words(self, w):
        q = w.tiles[w.quest_pos]
        return article(f"ruined {q.site['purpose']}"), w.region_of(w.quest_pos)["name"]

    def offer(self, g, npc):
        w, n = g.world, g.narr
        site, region = self.site_words(w)
        from . import lex_elders as EL
        when = "It's already in our gardens." if self.late else f"At this rate it'll be on our doorsteps in {self.days_left(w)} days."
        g.emit(EL.speak(g, npc, "blight", dict(dir=n.dir_phrase(g.pos, w.quest_pos), cause=self.cause.format(site=site, region=region), sign=self.sign, when=when)))
        g.emit("(Quest: find the heart of the blight, kill what feeds it, bless the ground, and return. It spreads every day.)")

    def goal(self, g):
        w = g.world
        if self.done:
            return f"The blight is ending. Go home to {home_name(w)}."
        site, region = self.site_words(w)
        clock = (f" The rot has reached {home_name(w)}; its people have fled." if self.late else
                 f" It is {self.steps_from_home(w)} squares from {home_name(w)}: about {self.days_left(w)} days.")
        if self.boss(w):
            return f"Find the heart of the blight in {region} and kill what feeds it." + clock
        if not self.blessing(g):
            return "Get a blessing against the blight: pray at a shrine, or carry holy water, and bring it to the heart." + clock
        return f"Bring the blessing to the heart of the blight in {region}." + clock

    def status(self, g):
        if self.done:
            return "the blight is lifting"
        return f"the blight {self.steps_from_home(g.world)} squares from home" if not self.late else "home lost to the blight"

    def mark(self, g):
        return f"home: the blight is ending" if self.done else "the heart of the blight"

    def targets(self, g):
        w = g.world
        if self.done:
            return [w.start]
        if not self.boss(w) and not self.blessing(g):
            sh = self.nearest_shrine(g)
            return [sh] if sh else [w.quest_pos]
        return [w.quest_pos]

    def act(self, g):
        t = g.world.tiles[g.pos]
        if not self.done and not self.blessing(g) and t.site and t.site["kind"] == "shrine" and g.has_quest:
            return "pray", "Pray for a blessing against the blight", "The spirit of a shrine can bless the ground at the blight's heart."
        return None

    def nearest_shrine(self, g):
        w = g.world
        d = w.distances(g.pos)
        shrines = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "shrine"]
        return min(shrines, key=lambda p: d.get(p, 999)) if shrines else None

    def step(self, g):
        w, p = g.world, g.player
        if self.done:
            return w.start, "toward home", "The blight is lifting; tell them.", True
        if self.boss(w):
            return w.quest_pos, "toward the heart of the blight", "the heart", p.level >= w.tiles[w.quest_pos].danger + 1
        if not self.blessing(g):
            sh = self.nearest_shrine(g)
            if sh:
                return sh, "toward a shrine", "A shrine's blessing will end the blight.", True
        return w.quest_pos, "toward the heart of the blight", "Bless the ground there.", True

    def vision(self, g):
        site, region = self.site_words(g.world)
        return f"{site} {g.narr.dir_phrase(g.pos, g.world.quest_pos)}, black at the heart of a grey stain that spreads across the land like ink in water"

    def lore(self, g):
        return ("\"The blight? It's fed, like a fire. Something sits at the heart of it, drinking. Kill that, and bless the ground "
                "where it sat - a shrine's favour, or holy water - and the land will heal itself. It wants to.\"")

    def rumour(self, narr, here):
        w = narr.w
        if self.cleansed:
            return "the grey's [going out of|lifting from] the [grass|fields]. [Whatever you did, it's working|Somebody did something right|You can see green again]"
        return f"the blight's [spreading|creeping out|coming] from {w.region_of(w.quest_pos)['name']}, {narr.dir_phrase(here, w.quest_pos)}. [A little more every morning|Another field every day|You can watch it move, nearly]"

    def place_lines(self, narr, pos):
        w = narr.w
        if pos == w.start and self.late and not self.done:
            return [f"Doors stand open on empty houses. The blight lies grey on the gardens; most of the people have gone to {w.tiles[self.refuge].site['name']}."]
        if not self.blighted(w, pos) or pos == w.quest_pos:
            return []
        t = w.tiles[pos]
        out = [narr.pick(LINES.get(t.biome, LINES["plains"]), f"blight:{t.biome}")]
        d = narr.dir_phrase(pos, w.quest_pos).split(" to the ")[-1]
        out.append(narr.pick(EDGE, "blight_edge").format(d=d))
        return out

    def blessing(self, g):
        return next((i for i in g.player.inv if (i.kind == "token" and i.name.startswith("blessing of")) or i.name == "flask of holy water"), None)

    def holds(self, it):
        return it.kind == "token" and it.name.startswith("blessing of")

    # ------------------------------------------------------------ hooks
    def on_pray(self, g, site):
        from .world import Item
        if self.done or any(self.holds(i) for i in g.player.inv):
            return ""
        g.player.inv.append(Item("token", f"blessing of {site['spirit']}", value=0, facts=dict(material="a sprig of green", glow="a smell of rain on clean earth")))
        return (f"When you speak of the blight, the {site['form']} seems to stir. Something green lies at its foot that wasn't there before: "
                f"a sprig, fresh as spring. (You carry the blessing of {site['spirit']}. Take it to the heart of the blight.)")

    def on_arrive(self, g):
        self.try_cleanse(g)

    def on_kill(self, g, c):
        if c.boss and g.pos == g.world.quest_pos:
            g.emit("The thing at the heart of the blight is dead, but the grey does not lift. The ground itself is sick. It needs blessing.")
            self.try_cleanse(g)

    def try_cleanse(self, g):
        w = g.world
        if self.done or g.pos != w.quest_pos or self.boss(w):
            return
        b = self.blessing(g)
        if not b:
            return
        g.player.inv.remove(b)
        self.done = self.cleansed = True
        how = "pour out the holy water" if b.name == "flask of holy water" else f"set the {b.name.replace('blessing of ', 'sprig of ')}'s green into the grey earth"
        g.emit(f"You {how} at the heart of the blight. For a long moment nothing happens. Then the wind changes, and the air smells of rain, "
               f"and at your feet the grey begins, very slowly, to go green. (The blight is ending. Go home to {home_name(w)}.)")

    def on_new_day(self, g):
        w = g.world
        if self.done:
            return
        if not self.late and self.radius(w) >= self.home_d:
            self.late = True
            if g.has_quest:
                g.emit(f"(Bad news travels fast: the blight has reached {home_name(w)}. Its people have fled to {w.tiles[self.refuge].site['name']}. "
                       f"It isn't too late to end the blight, but home will be emptier for it.)")
        elif g.has_quest and not self.late and self.days_left(w) <= 3 and self.warned != w.day:
            self.warned = w.day
            g.emit(f"(The blight is {self.steps_from_home(w)} squares from {home_name(w)}. About {self.days_left(w)} days left.)")

    def check(self, g):
        w = g.world
        if not (self.done and g.pos == w.start and g.has_quest):
            return
        elder = MQ.elder_of(w)
        pr = elder.pronouns() if elder else {"he": "they", "his": "their"}
        text = (self.late_ending if self.late else self.ending).format(
            home=home_name(w), elder=elder.name if elder else "The elder", he=pr["he"], his=pr["his"], refuge=w.tiles[self.refuge].site["name"])
        MQ.win(g, text)
