"""World generation. Everything here is *fact*: decided once from the seed and
then stable. Prose is produced separately (describe.py) every time it's needed."""
import random
from collections import deque
from dataclasses import dataclass, field

from . import lexicon as L
from . import lex_entities as E
from .textgen import Grammar
from . import lex_variety as V
from . import coherence as C
from . import names as NAMES
from . import arts as ARTS
from . import goods as GOODS
from . import places as PLACES

V.apply_fact_pools(L, E)

DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
TIMES = [(5, "dawn"), (8, "morning"), (11, "midday"), (14, "afternoon"), (18, "dusk"),
         (20, "evening"), (23, "night")]
# job titles that carry a gender take the form that matches the person
GENDERED_JOBS = {
    "goose-girl": {"male": "goose-boy"}, "goose-boy": {"female": "goose-girl"},
    "chandler's boy": {"female": "chandler's girl"}, "chandler's girl": {"male": "chandler's boy"},
    "wise-woman": {"male": "wise-man"}, "wise-man": {"female": "wise-woman"},
}
GENDERED_BASE = {"goose-boy": "goose-girl", "chandler's girl": "chandler's boy", "wise-man": "wise-woman", "headwoman": "headman"}
PRONOUNS = {"female": dict(he="she", him="her", his="her", hers="hers", himself="herself"),
            "male": dict(he="he", him="him", his="his", hers="his", himself="himself")}


def guess_gender(name):
    """Which name list a name sounds most like, by the name model's scores."""
    try:
        g = NAMES.gen()
        best = max(((g.score(name.lower(), c, gd), gd) for c in NAMES_CULTURES for gd in ("female", "male")))
        return best[1]
    except Exception:
        return "female" if name.lower().endswith(("a", "e", "y", "is", "ia")) else "male"


NAMES_CULTURES = ["Archaic", "Westron", "Northish", "Southron"]
SEASONS = ["spring", "summer", "autumn", "winter"]
WEATHER_NEXT = {
    "clear": [("clear", 5), ("cloudy", 3), ("wind", 1), ("fog", 1)],
    "cloudy": [("cloudy", 3), ("clear", 2), ("overcast", 3), ("wind", 1)],
    "overcast": [("overcast", 3), ("drizzle", 2), ("cloudy", 2), ("rain", 1), ("fog", 1)],
    "drizzle": [("drizzle", 2), ("rain", 2), ("overcast", 2)],
    "rain": [("rain", 2), ("storm", 1), ("drizzle", 2), ("overcast", 1)],
    "storm": [("rain", 3), ("storm", 1), ("wind", 1)],
    "fog": [("fog", 2), ("overcast", 2), ("clear", 1)],
    "wind": [("wind", 2), ("cloudy", 2), ("clear", 1), ("rain", 1)],
    "snow": [("snow", 3), ("overcast", 2), ("clear", 1)],
}
FLAVOUR = {
    "forest": {"forest:tree": 2, "forest:undergrowth": 2},
    "marsh": {"marsh:plant": 3, "marsh_tree": 1},
    "plains": {"plains:grass": 3, "lone_tree": 1},
    "hills": {"lichen_colour": 2},
    "peaks": {"alpine_plant": 2},
}
MOON = ["The new moon is invisible, and the dark is deep.",
        "A thin crescent moon hangs low, sharp as a paring.",
        "A half moon lights the land in silver and ink.",
        "A swollen gibbous moon throws strong shadows.",
        "The full moon floods everything with cold, colourless light.",
        "A waning moon rises late, lopsided and yellow.",
        "A last-quarter moon sits pale above the horizon.",
        "A faint sliver of old moon clings to the sky."]


COLOUR_KIN = {"red": ("red", "rust", "russet", "copper", "fox", "tawny"), "white": ("white", "pale", "silver", "snow", "cream"),
              "black": ("black", "dark", "jet", "soot", "sable"), "grey": ("grey", "ash", "silver", "slate", "dun"),
              "pale": ("pale", "white", "silver", "grey", "ash", "cream", "fawn"), "ash": ("ash", "grey", "pale", "silver"),
              "blood": ("red", "blood", "rust", "crimson")}


@dataclass
class Feature:
    noun: str
    adjs: list
    verb: str
    where: str
    details: list
    kind: str = ""          # the archetype ("oak", "holy well"...); older saves work it out from the noun
    state: dict = None      # what has happened here: searched, climbed, secret found...

    @property
    def archetype(self):
        return self.kind or L.FEATURE_KIND.get(self.noun, self.noun)

    @property
    def keywords(self):
        return set(self.noun.split()) | set(w for a in self.adjs for w in a.split())


@dataclass
class Item:
    kind: str                 # weapon armour herb potion food trinket relic
    name: str                 # noun phrase without article
    value: int = 1
    dmg: int = 0
    df: int = 0
    heal: int = 0
    cls: str = ""
    facts: dict = field(default_factory=dict)

    @property
    def keywords(self):
        return set(self.name.lower().replace("-", " ").split()) | {self.kind}


@dataclass
class Creature:
    species: dict
    trait: str
    hp: int
    maxhp: int
    atk: int
    df: int
    xp: int
    aggressive: bool
    boss: bool = False
    title: str = ""
    mind: dict = None          # intents with decaying support (see mind.py), created on first contact

    @property
    def name(self):
        return self.title or self.species["name"]

    @property
    def keywords(self):
        return set(self.name.lower().replace("-", " ").split()) | {self.species["arch"]["noun"], "creature", "beast"}


@dataclass
class NPC:
    name: str
    role: str
    job: str
    look: dict
    demeanour: str
    stock: list = field(default_factory=list)
    talked: int = 0
    home: tuple = (0, 0)
    # memory: what this person knows about the player
    mem: dict = field(default_factory=lambda: dict(met=0, last_day=0, knows_name=False, disp=0,
                                                   told=[], events=[], deeds_heard=0, gave_gift=False))

    @property
    def known(self):
        """Has this person told the player their name? (Everyone you've talked to has.)"""
        return bool(self.mem.get("introduced") or self.mem["met"] > 0)

    @property
    def gender(self):
        """female/male, from the name list they were named from (older saves: guessed from the name's sound)."""
        g = self.look.get("name_gender")
        if g not in ("female", "male"):
            g = guess_gender(self.name)
            self.look["name_gender"] = g
        return g

    @property
    def age_band(self):
        """young, mid or old: fixed when the person was made."""
        b = self.look.get("age_band")
        if b is None:       # older saves: work it out once from the word, then keep it
            b = self.look["age_band"] = C.AGE_BAND.get(self.look.get("age"), "mid")
            if b == "any":
                b = self.look["age_band"] = "mid"
        return b

    def pronouns(self):
        return PRONOUNS[self.gender]

    def called(self):
        """How the player can refer to them: by name once introduced, by trade before."""
        return self.name if self.known else f"the {self.job}"

    def ref(self):
        """A word the parser will match, without leaking a name the player hasn't heard."""
        return self.name.lower() if self.known else self.job.split()[-1]

    @property
    def keywords(self):
        words = set(self.job.lower().replace("-", " ").split()) | {self.job.split()[-1].lower(), self.role}
        if self.role == "merchant":
            words |= {"merchant", "trader", "shopkeeper", "seller"}
        if self.known:
            words.add(self.name.lower())
        return words

    @property
    def tier(self):
        d = self.mem["disp"]
        return "cold" if d < 0 else "neutral" if d < 4 else "friendly" if d < 9 else "devoted"

    def remember(self, kind, **info):
        e = dict(kind=kind, said=False)
        e.update(info)
        self.mem["events"].append(e)

    def like(self, n):
        self.mem["disp"] += n


@dataclass
class Tile:
    x: int
    y: int
    biome: str
    region: int = -1
    mood: str = "serene"
    features: list = field(default_factory=list)
    flavour: dict = field(default_factory=dict)   # fixed vocabulary (which trees grow here, etc.)
    site: dict = None
    creatures: list = field(default_factory=list)
    npcs: list = field(default_factory=list)
    items: list = field(default_factory=list)
    visited: bool = False
    danger: int = 1


def _value_noise(rng, w, h, cell):
    gw, gh = w // cell + 2, h // cell + 2
    grid = [[rng.random() for _ in range(gw)] for _ in range(gh)]
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            gx, gy = x / cell, y / cell
            x0, y0 = int(gx), int(gy)
            tx, ty = gx - x0, gy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = grid[y0][x0] * (1 - tx) + grid[y0][x0 + 1] * tx
            b = grid[y0 + 1][x0] * (1 - tx) + grid[y0 + 1][x0 + 1] * tx
            row.append(a * (1 - ty) + b * ty)
        out.append(row)
    return out


def _fbm(rng, w, h):
    layers = [(_value_noise(rng, w, h, c), wt) for c, wt in ((6, 0.6), (3, 0.3), (2, 0.1))]
    return [[sum(l[y][x] * wt for l, wt in layers) for x in range(w)] for y in range(h)]


class World:
    W = H = 16

    @property
    def title(self):
        """The world's own name, from the seed alone (so saves from before it existed have one too)."""
        t = self.__dict__.get("_title")
        if t is None:
            try:
                people = NAMES.gen()
            except Exception:
                people = None
            t = self._title = PLACES.world_title(self.seed, people)
        return t

    def __init__(self, seed, player_name=""):
        self.seed = seed
        self.player_name = player_name
        self.rng = random.Random(seed)
        r = self.rng
        self.name_rng = random.Random(f"{seed}-names")      # names have their own dice, so they don't shift the rest of the world
        # a pool of local names, for the dead whose names are carved on old things
        self.name_pool = [self.new_name(c, g) for c in NAMES_CULTURES for g in ("female", "male") for _ in range(4)]
        self.fg = Grammar(r, E.ITEM_RULES)   # fact grammar: details fixed at creation
        self.minutes = (r.randint(6, 10)) * 60
        self.day = 1
        self.season = r.choice(SEASONS)
        self.weather = r.choice(["clear", "cloudy", "overcast", "fog"])
        self.moon0 = r.randrange(8)
        try:
            people = NAMES.gen()
        except (OSError, ValueError):
            people = None
        self.namer = PLACES.Namer(seed, people)      # place names: their own dice, never saved
        self._terrain()
        self._regions()
        self._species()
        self._sites()
        self._populate()
        del self.namer

    # ------------------------------------------------------------- terrain
    def _terrain(self):
        r, W, H = self.rng, self.W, self.H
        elev, moist = _fbm(r, W, H), _fbm(r, W, H)
        flat = sorted(v for row in elev for v in row)
        q = lambda p: flat[int(p * (len(flat) - 1))]
        lake, hills, peaks = q(0.12), q(0.70), q(0.90)
        mflat = sorted(v for row in moist for v in row)
        wet, mid = mflat[int(0.72 * len(mflat))], mflat[int(0.40 * len(mflat))]
        self.tiles = {}
        for y in range(H):
            for x in range(W):
                e, m = elev[y][x], moist[y][x]
                if e < lake:
                    b = "lake"
                elif e > peaks:
                    b = "peaks"
                elif e > hills:
                    b = "hills"
                elif m > wet and e < q(0.5):
                    b = "marsh"
                elif m > mid:
                    b = "forest"
                else:
                    b = "plains"
                self.tiles[(x, y)] = Tile(x, y, b)
        # keep the largest connected landmass; other land becomes water
        seen, best = set(), set()
        for p, t in self.tiles.items():
            if t.biome == "lake" or p in seen:
                continue
            comp = self._flood(p, lambda a, b: self.tiles[b].biome != "lake")
            seen |= comp
            if len(comp) > len(best):
                best = comp
        for p, t in self.tiles.items():
            if t.biome != "lake" and p not in best:
                t.biome = "lake"
        self.land = best

    def _flood(self, start, ok):
        out, dq = {start}, deque([start])
        while dq:
            p = dq.popleft()
            for d in DIRS.values():
                n = (p[0] + d[0], p[1] + d[1])
                if n in self.tiles and n not in out and ok(p, n):
                    out.add(n)
                    dq.append(n)
        return out

    def neighbours(self, p):
        for name, d in DIRS.items():
            n = (p[0] + d[0], p[1] + d[1])
            if n in self.tiles:
                yield name, n

    def distances(self, start):
        dist, dq = {start: 0}, deque([start])
        while dq:
            p = dq.popleft()
            for _, n in self.neighbours(p):
                if n not in dist and n in self.land:
                    dist[n] = dist[p] + 1
                    dq.append(n)
        return dist

    # ------------------------------------------------------------- regions
    def make_place_name(self, biome):
        r = self.rng
        noun = r.choice(L.BIOME_NAMES[biome])
        root = r.choice(L.NAME_PRE) + r.choice(L.NAME_SUF)
        while root.lower().endswith(noun.lower()) or noun.lower().startswith(root[-4:].lower()):
            root = r.choice(L.NAME_PRE) + r.choice(L.NAME_SUF)
        style = r.random()
        if style < 0.45:
            return f"{root} {noun}"
        if style < 0.8:
            return f"the {r.choice(L.NAME_ADJ)} {noun}"
        return f"the {noun} of {root}"

    def _regions(self):
        self.regions = []
        used = set()
        for p, t in self.tiles.items():
            if t.region >= 0:
                continue
            comp = self._flood(p, lambda a, b: self.tiles[b].biome == self.tiles[a].biome)
            name = self.namer.region(t.biome, self.culture_of(p))
            used.add(name)
            for q in comp:
                self.tiles[q].region = len(self.regions)
            self.regions.append(dict(name=name, biome=t.biome, size=len(comp)))
        r = self.rng
        for p in self.land:
            t = self.tiles[p]
            t.mood = r.choice(L.MOODS[t.biome])
            archs = r.sample(L.FEATURES[t.biome], min(len(L.FEATURES[t.biome]), r.choice([1, 1, 2, 2, 3])))
            t.features = []
            for a in archs:          # no two landmarks on one tile share a name, or you couldn't tell them apart
                t.features.append(self.make_feature(a, {f.noun for f in t.features}))
            for sym, n in FLAVOUR.get(t.biome, {}).items():
                pool = L.RULES[sym]
                t.flavour[sym.split(":")[-1]] = r.sample(pool, min(n, len(pool)))

    def make_feature(self, a, taken=()):
        r = self.rng
        noun = self.pick(a["noun"], lambda n: n not in taken)
        adjs = [r.choice(a["adj"])]
        adjs.append(self.pick(a["adj2"], lambda x: not C.repeated_words(" ".join(adjs + [x, noun]))))
        first = r.choice(a["detail"])
        second = self.pick([d for d in a["detail"] if d != first],
                           lambda d: not C.repeated_words(" ".join([first, d, noun] + adjs)))
        return Feature(noun=noun, adjs=adjs, verb=r.choice(a["verb"]), where=r.choice(a["where"]),
                       details=[first, second], kind=a["kind"], state={})

    def region_of(self, p):
        return self.regions[self.tiles[p].region]

    # ------------------------------------------------------------- species
    def _species(self):
        r = self.rng
        self.species = []
        archs = list(E.ARCHETYPES.items())
        r.shuffle(archs)
        for key, arch in archs:
            for _ in range(r.choice([1, 1, 2])):
                biome = r.choice(arch["biomes"])
                style = r.random()
                if style < 0.4:
                    name = f"{r.choice(E.SPECIES_PREFIX[biome])} {arch['noun']}"
                elif style < 0.75:
                    name = f"{r.choice(E.SPECIES_TRAIT)}-{r.choice(E.SPECIES_PART_WORD[key])}ed {arch['noun']}"
                    name = name.replace("eed ", "ed ").replace("eded", "ed")
                else:
                    name = f"{r.choice(arch['colours']).split()[0]} {arch['noun']}"
                if any(s["name"] == name for s in self.species):
                    continue
                # a species named for a colour ("pale-pelted", "black bear") must look it
                said = name.split("-")[0].split()[0]
                fits = [c for c in arch["colours"] if any(w in c for w in COLOUR_KIN.get(said, ()))]
                if said in COLOUR_KIN and not fits:
                    name = name.replace(said, r.choice(["scar", "long", "hook", "iron"]), 1)
                self.species.append(dict(name=name, key=key, arch=arch, home=biome,
                                         colour=r.choice(fits or arch["colours"]), mark=r.choice(arch["marks"]),
                                         size=r.choice(E.SIZES), habits=r.sample(arch["idle"], 2),
                                         aggression=r.choice([0.2, 0.4, 0.6, 0.8])))

    def make_creature(self, sp, danger, boss=False):
        r = self.rng
        a = sp["arch"]
        hp = r.randint(*a["hp"]) + (danger - 1) * 4
        undead = bool(a.get("undead"))
        trait = self.pick(C.UNDEAD_TRAITS if undead else E.INDIVIDUAL, lambda x: C.trait_ok(x, sp["key"], sp["size"], undead))
        c = Creature(species=sp, trait=trait, hp=hp, maxhp=hp,
                     atk=a["atk"] + danger - 1, df=a["df"] + (danger - 1) // 2,
                     xp=4 + hp // 2 + a["atk"] * 2, aggressive=r.random() < sp["aggression"])
        if boss:
            c.boss, c.aggressive = True, True
            c.hp = c.maxhp = hp * 2 + 10
            c.atk += 3
            c.df += 2
            c.xp *= 4
            c.trait = "colossal"
            c.title = f"the {r.choice(['Old', 'Grey', 'Hollow', 'Elder', 'Pale'])} {r.choice(['Mother', 'King', 'Warden', 'Hunger', 'One'])} of {self.region_of(self.quest_pos)['name'].replace('the ', '')}"
        return c

    # ------------------------------------------------------------- sites & npcs
    def _pick_sites(self, n, biomes, min_gap, exclude):
        r = self.rng
        cands = [p for p in self.land if self.tiles[p].biome in biomes and self.tiles[p].site is None]
        r.shuffle(cands)
        out = []
        for p in cands:
            if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= min_gap for q in out + exclude):
                out.append(p)
            if len(out) == n:
                break
        return out

    def _sites(self):
        r = self.rng
        cx = cy = self.W // 2
        start_cands = sorted((p for p in self.land if self.tiles[p].biome in ("plains", "forest", "hills")),
                             key=lambda p: abs(p[0] - cx) + abs(p[1] - cy) + r.random() * 3)
        self.start = start_cands[0]
        dist = self.distances(self.start)
        for p, d in dist.items():
            self.tiles[p].danger = 1 + d // 4
        # quest site: a ruin far away
        far = sorted(dist, key=lambda p: -dist[p])
        self.quest_pos = far[r.randrange(min(4, len(far)))]
        others = self._pick_sites(5, ("plains", "forest", "hills", "marsh"), 4, [self.start, self.quest_pos])
        if len(others) < 3:
            others += self._pick_sites(3 - len(others), ("plains", "forest", "hills", "marsh", "peaks"), 3, [self.start, self.quest_pos] + others)
        villages = [self.start] + others
        # one market town, a fair walk from home; the rest villages and hamlets
        town = min(others, key=lambda p: abs(dist.get(p, 99) - 7)) if others else None
        small = [p for p in others if p != town]
        scales = {self.start: "village", town: "town"}
        for i, p in enumerate(small):
            scales[p] = "hamlet" if i % 2 == 0 else "village"
        for p in villages:
            self.tiles[p].site = self.make_village(self.tiles[p].biome, scales[p], p)
            self.tiles[p].danger = 0
        self.relic = Item("relic", f"{r.choice(E.RELIC_ADJ)} {r.choice(E.RELIC_NOUN)}", value=500,
                          facts=dict(material=r.choice(["gold", "silver", "black iron", "bone", "crystal", "bronze"]),
                                     glow=r.choice(["a faint inner warmth", "a hum you feel in your teeth", "a cold light", "a smell of rain"])))
        self.tiles[self.quest_pos].site = self.make_ruin(quest=True)
        for p in self._pick_sites(4, ("plains", "forest", "hills", "marsh", "peaks"), 3, villages + [self.quest_pos]):
            self.tiles[p].site = self.make_ruin()
        for p in self._pick_sites(3, ("plains", "forest", "hills", "peaks"), 3, villages):
            self.tiles[p].site = self.make_shrine(self.tiles[p].biome)
        for p in self._pick_sites(3, ("plains", "forest", "hills", "marsh"), 2, villages):
            self.tiles[p].site = dict(kind="camp")
        self.villages = villages

    def culture_of(self, pos):
        """Which naming tradition a place follows: Northish in the north, Southron in the south, Westron between."""
        y = pos[1]
        return "Northish" if y < self.H // 3 else "Southron" if y >= 2 * self.H // 3 else "Westron"

    def new_name(self, culture, gender, taken=()):
        try:
            g = NAMES.gen()
        except (OSError, ValueError):      # no trained model: fall back to the old list
            return self.name_rng.choice([n for n in E.GIVEN if n not in taken] or E.GIVEN)
        for _ in range(20):
            n = g.generate(self.name_rng, culture, gender)
            if n not in taken:
                return n
        return n

    def pick(self, pool, ok, weight=None):
        """Choose from the options that agree with facts already decided (optionally weighted)."""
        good = [x for x in pool if ok(x)] or list(pool)
        if weight:
            return self.rng.choices(good, [weight.get(x, 1) for x in good])[0]
        return self.rng.choice(good)

    SIZE_WORDS = {"hamlet": ["hamlet", "huddle", "steading"], "village": ["village"], "town": ["market town", "town"]}

    def make_village(self, biome="plains", scale="village", pos=None):
        r = self.rng
        namer = getattr(self, "namer", None) or PLACES.Namer(f"{self.seed}-late")
        name = namer.settlement(self.culture_of(pos) if pos else "Westron", scale)
        facts = {k: r.choice(v) for k, v in E.VILLAGE.items()}
        facts["scale"] = scale
        facts["size"] = r.choice(self.SIZE_WORDS[scale])
        facts["roof"] = self.pick(E.VILLAGE["roof"], lambda x: C.walls_roof_ok(facts["material"], x))
        trades = r.sample(V.ECONOMY.get(biome, V.ECONOMY["plains"]), 2)     # a main trade and a side trade
        facts["economy"], facts["economy2"] = trades
        signs = r.sample(V.ECONOMY_SIGNS[trades[0]], min(2, len(V.ECONOMY_SIGNS[trades[0]])))
        signs.append(r.choice(V.ECONOMY_SIGNS[trades[1]]))
        facts["signs"] = signs
        return dict(kind="village", name=name, **facts)

    def make_ruin(self, quest=False):
        r = self.rng
        facts = {k: r.choice(v) for k, v in E.RUIN.items()}
        facts["interior"] = self.pick(E.RUIN["interior"], lambda x: C.ruin_ok(facts["purpose"], facts["state"], x))
        return dict(kind="ruin", quest=quest, **facts)

    def make_shrine(self, biome="plains"):
        r = self.rng
        form = self.pick(E.SHRINE["form"], lambda f: C.shrine_form_ok(f, biome))
        domain = r.choice(E.SHRINE["domain"])
        pre = self.pick(E.SHRINE["spirit_pre"], lambda x: any(C.spirit_ok(x, n, domain) for n in E.SHRINE["spirit_name"]))
        name = self.pick(E.SHRINE["spirit_name"], lambda n: C.spirit_ok(pre, n, domain))
        return dict(kind="shrine", form=form, spirit=f"{pre} {name}",
                    domain=domain, offerings=r.choice(E.SHRINE["offerings"]), used=False)

    def make_npc(self, role, home=(0, 0), stall=False):
        r = self.rng
        taken = {n.name for t in self.tiles.values() for n in t.npcs} | {getattr(self, "player_name", "")}
        gender = r.choice(["female", "male"])
        culture = "Archaic" if role == "elder" and self.name_rng.random() < 0.6 else self.culture_of(home)
        name = self.new_name(culture, gender, taken)
        # the land around their home decides which trades make sense
        lands = {self.tiles[home].biome} if home in self.tiles else {"plains"}
        lands |= {"water" if self.tiles[q].biome == "lake" else self.tiles[q].biome for _, q in self.neighbours(home)} if home in self.tiles else set()
        here = {GENDERED_BASE.get(n.job, n.job) for n in self.tiles[home].npcs} if home in self.tiles else set()
        job = self.pick(E.OCCUPATIONS[role], lambda j: C.job_ok(j, lands) and j not in here and (not stall or j in GOODS.STALL_FOLK
                                                                                                 or GENDERED_JOBS.get(j, {}).get("female") in GOODS.STALL_FOLK))
        # age is a fact about the person (young / mid / old); the word is just how it's put
        band = self.pick(C.AGE_BANDS, lambda b: C.band_ok(b, role, job), C.BAND_WEIGHT)
        age = self.pick(C.age_words(band, E.AGE), lambda a: C.age_ok(a, role, job))
        look = dict(age=age, age_band=band, build=self.pick(E.BUILD, lambda b: C.build_ok(b, age)),
                    hair=self.pick(E.HAIR, lambda h: C.hair_ok(h, age, gender) and
                                   all(n.look["hair"] != h for n in self.tiles[home].npcs) if home in self.tiles else C.hair_ok(h, age, gender),
                                   C.HAIR_WEIGHT),
                    clothes=self.pick(E.CLOTHES, lambda c: all(n.look["clothes"] != c for n in self.tiles[home].npcs) if home in self.tiles else True),
                    mark=self.pick(E.MARK, lambda m: all(n.look["mark"] != m for n in self.tiles[home].npcs) if home in self.tiles else True),
                    surname=r.choice(E.SURNAME_PRE) + r.choice(E.SURNAME_SUF), name_gender=gender, culture=culture)
        job = GENDERED_JOBS.get(job, {}).get(gender, job)      # the title matches the person
        if job in ("headman", "headwoman"):
            job = "headwoman" if gender == "female" else "headman"
        npc = NPC(name=name, role=role, job=job, look=look,
                  demeanour=r.choice(E.DEMEANOUR) if role != "elder" else r.choice(["warm", "melancholy", "shrewd", "gruff"]),
                  home=home)
        if npc.demeanour in ("suspicious", "gruff"):
            npc.mem["disp"] = -1
        if GOODS.sells(npc):
            lo, hi = GOODS.stall_size(npc)
            npc.stock = GOODS.stock(self, npc.job, r.randint(lo, hi), 2 if home == getattr(self, "start", None) else 3, getattr(self, "season", None))
        return npc

    # ------------------------------------------------------------- items
    def make_item(self, danger=1, kind=None, wtype=None, akind=None, school=None):
        r = self.rng
        kind = kind or r.choices(["weapon", "armour", "herb", "potion", "food", "trinket", "book", "scroll"], [3, 2, 3, 2, 3, 3, 1.2, 1.5])[0]
        if kind in ("book", "scroll"):
            d = ARTS.make_book(r, danger, school, self.name_pool) if kind == "book" else ARTS.make_scroll(r, danger, school)
            return Item(d["kind"], d["name"], value=d["value"], facts=d["facts"])
        if kind == "weapon":
            wk = wtype or r.choice(list(E.WEAPONS))
            w = E.WEAPONS[wk]
            noun = r.choice(w["names"])
            mats = [m for m in E.MATERIALS if m in C.WEAPON_MATERIALS.get(noun, E.MATERIALS)]
            weights = [3 if E.MATERIALS[m][0] <= 0 else (2 if E.MATERIALS[m][0] == 1 else max(0.2, danger - 1.5)) for m in mats]
            mat = r.choices(mats, weights)[0]
            q = r.choices(E.QUALITY, [3, 3, 3, 4, 3, 2, 1, 0.3 * danger])[0]
            qword = C.WORN_WORDS.get(mat, {}).get(q[0], q[0])
            dmg = max(1, w["dmg"] + E.MATERIALS[mat][0] + q[1])
            facts = dict(details=self._details(E.ITEM_DETAIL[wk if wk in E.ITEM_DETAIL else w["cls"]], qword, mat),
                         noun=noun, material=mat)
            facts["hist"] = self._history(qword, mat)
            return Item("weapon", f"{qword} {mat} {noun}", value=int((8 + dmg * 6) * E.MATERIALS[mat][1] * q[2]),
                        dmg=dmg, cls=w["cls"], facts=facts)
        if kind == "armour":
            ak = akind or r.choices(list(E.ARMOUR), [4, 2, max(0.3, danger - 1)])[0]
            a = E.ARMOUR[ak]
            q = r.choices(E.QUALITY[1:7], [3, 3, 4, 3, 2, 1])[0]
            df = max(1, a["df"] + (q[1] if q[1] > 0 else 0))
            noun = r.choice(a["names"])
            qword = C.SOFT_WORN.get(q[0], q[0]) if noun in C.SOFT_ARMOUR else q[0]
            mat = "leather" if noun in C.SOFT_ARMOUR else "iron"
            return Item("armour", f"{qword} {noun}", value=int((14 + df * 15) * q[2]), df=df,
                        facts=dict(detail=self._details(["{armour_detail}"], qword, mat, 1)[0], hist=self._history(qword, mat)))
        if kind == "herb":
            name = (r.choice(E.HERB_PRE) + r.choice(E.HERB_SUF))
            name = "sprig of " + name.replace("ll", "l") if r.random() < 0.5 else "bundle of " + name
            return Item("herb", name, value=4, heal=r.randint(4, 7), facts=dict(look=r.choice(E.HERB_LOOK)))
        if kind == "potion":
            col = r.choice(E.POTION_COLOUR)
            return Item("potion", f"vial of {col} draught", value=15, heal=r.randint(10, 16),
                        facts=dict(colour=col, smell=r.choice(E.POTION_SMELL),
                                   vessel=r.choice(["a stoppered clay vial", "a tiny green-glass bottle", "a corked horn flask", "a wax-sealed phial"])))
        if kind == "food":
            name, heal = r.choice(E.FOOD)
            return Item("food", name, value=heal, heal=heal)
        mat = r.choice(E.TRINKET_MAT)
        noun = self.pick(E.TRINKETS, lambda t: not set(t.split()) & set(mat.split()))
        return Item("trinket", f"{mat} {noun}", value=r.randint(8, 30),
                    facts=dict(detail=r.choice(E.TRINKET_DETAIL)))

    def _details(self, templates, quality, material, n=2):
        """Expand item details, re-rolling any that contradict the item's condition or material."""
        out = []
        for d in self.rng.sample(templates, min(n, len(templates))):
            for _ in range(12):
                text = self.fg.expand(d)
                if C.detail_ok(text, quality, material) and text not in out:
                    break
            out.append(text)
        return out

    def _history(self, quality="plain", material="iron"):
        if self.rng.random() < 0.35:
            return ""
        for _ in range(12):
            text = self.fg.expand("{history}", dict(given=getattr(self, "name_pool", None) or E.GIVEN))
            if C.detail_ok(text, quality, material):
                return text
        return ""

    # ------------------------------------------------------------- populate
    def _populate(self):
        r = self.rng
        for i, p in enumerate(self.villages):
            t = self.tiles[p]
            scale = t.site.get("scale", "village")
            if i == 0:
                t.npcs.append(self.make_npc("elder", p))
            merchants = {"town": 3, "village": 1, "hamlet": 0}[scale]
            folk = {"town": r.randint(2, 3), "village": r.randint(1, 2), "hamlet": r.randint(1, 2)}[scale]
            for _ in range(merchants):
                t.npcs.append(self.make_npc("merchant", p))
            for j in range(folk):      # towns and hamlets always have at least one craftsperson with a stall
                t.npcs.append(self.make_npc("folk", p, stall=(j == 0 and scale in ("town", "hamlet"))))
        for p in self.land:
            t = self.tiles[p]
            if t.site and t.site["kind"] == "village":
                continue
            fitting = [s for s in self.species if s["home"] == t.biome] or \
                      [s for s in self.species if t.biome in s["arch"]["biomes"]]
            if fitting and r.random() < (0.25 + 0.05 * t.danger) and t.danger > 0:
                t.creatures.append(self.make_creature(r.choice(fitting), t.danger))
            if r.random() < 0.12:
                t.items.append(self.make_item(t.danger))
            if t.site and t.site["kind"] in ("ruin", "camp"):
                for _ in range(r.randint(1, 2)):
                    t.items.append(self.make_item(t.danger + 1))
        q = self.tiles[self.quest_pos]
        fitting = [s for s in self.species if q.biome in s["arch"]["biomes"]] or self.species
        q.creatures = [self.make_creature(r.choice(fitting), q.danger + 1, boss=True)]
        q.items.append(self.relic)

    # ------------------------------------------------------------- time & weather
    @property
    def hour(self):
        return (self.minutes // 60) % 24

    @property
    def time_of_day(self):
        h = self.hour
        if h >= 23 or h < 1:
            return "night"
        if h < 5:
            return "deepnight"
        name = "night"
        for start, n in TIMES:
            if h >= start:
                name = n
        return name

    @property
    def is_dark(self):
        return self.time_of_day in ("evening", "night", "deepnight")

    @property
    def moon_line(self):
        return MOON[(self.moon0 + self.day) % 8]

    @property
    def weather_class(self):
        return "bright" if self.weather in ("clear", "cloudy", "wind") else "dull"

    def advance(self, minutes, rng):
        before = self.minutes
        self.minutes += minutes
        self.day = 1 + self.minutes // (24 * 60)
        changes = (self.minutes // 90) - (before // 90)
        for _ in range(changes):
            opts = WEATHER_NEXT[self.weather]
            if self.season == "winter" and self.weather in ("overcast", "cloudy"):
                opts = opts + [("snow", 2)]
            if self.season != "winter" and self.weather == "snow":
                opts = [("overcast", 1)]
            self.weather = rng.choices([o for o, _ in opts], [w for _, w in opts])[0]
        old_day = 1 + before // (24 * 60)
        if (self.day - 1) // 12 > (old_day - 1) // 12:
            self.season = SEASONS[(SEASONS.index(self.season) + 1) % 4]
