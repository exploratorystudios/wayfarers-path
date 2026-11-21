"""Place names: villages, towns and regions, built the way real place names grow.

Most old place names are a founder's name or a feature, worn down, plus an
element meaning farm, stream, clearing or hill. So:

  - founder + element: a fresh name from the name model, clipped to its first
    syllable or two, plus an ending ("Asa" + "by" -> Asby)
  - feature + element: a word for a tree, beast, stone or colour, plus an ending
    (Oak + ley -> Oakley, Stan + beck -> Stanbeck)
  - affixed forms: Long Wendham, Nether Asby, Chipping Holt (a market town),
    Asby-under-Edge, Wendham Cross

Endings follow the region's tradition, so a place sounds like its people:
Northish (north) -by, -thwaite, -garth, -beck; Westron (middle) -ton, -ham, -ley,
-bury; Southron (south) -combe, -leigh, -port, -hayes.

Regions pair a biome word (Weald, Moss, Fells...) with a root, an adjective, or
a possessive. Within one world no root, ending or adjective is used twice, so
names stay distinct. A separate random stream keeps the rest of the world the
same for a given seed.
"""
import random

ENDINGS = {
    "Northish": ["by", "thorpe", "thwaite", "garth", "beck", "toft", "wick", "kirk", "dale", "scar", "holm", "ness", "keld", "sett", "gill", "rigg", "with", "ay"],
    "Westron":  ["ton", "ham", "ley", "bury", "field", "worth", "stead", "ford", "well", "hurst", "den", "cote", "stow", "wich", "ing", "borough", "hall", "bourne"],
    "Southron": ["combe", "leigh", "minster", "hayes", "port", "tor", "mouth", "sey", "lade", "bridge", "cott", "hithe", "ock", "pool", "ridge", "lynch", "stoke", "wyn"],
}
# first elements: features of the land, beasts, trees, people
FEATURES = ["Oak", "Ash", "Alder", "Birch", "Elm", "Hazel", "Thorn", "Holly", "Rowan", "Yew", "Willow", "Lind", "Aspen", "Sloe", "Box",
            "Brock", "Hart", "Wolf", "Fox", "Crow", "Raven", "Hawk", "Swan", "Crane", "Otter", "Hare", "Boar", "Ox", "Ram", "Stot", "Gos", "Duck",
            "Stan", "Flint", "Chalk", "Clay", "Sand", "Mere", "Brook", "Wel", "Fen", "Moss", "Heath", "Bram", "Bracken", "Rush", "Reed", "Hay",
            "Cold", "Black", "White", "Red", "Green", "Grey", "Brad", "Long", "Mickle", "Lit", "High", "Nether", "Hol", "Dun", "Har",
            "Kirk", "Church", "Mill", "Bridge", "Cross", "Barrow", "Burg", "Wall", "Ship", "Shep", "Swin", "Cow", "Gate", "Mark", "Thing", "Hob",
            "Elf", "Thurs", "Wodens", "Fair", "Fowl", "Honey", "Salt", "Wheat", "Bar", "Rye", "Hemp", "Flax", "Apple", "Pear", "Cherry", "Nut"]
# a Northish, Westron or Southron flavour for some feature words
FEATURE_CULTURE = {"Northish": ["Skel", "Kel", "Thwait", "Ulf", "Bek", "Hrafn", "Grim", "Tof", "Orm", "Sca", "Ketil", "Ulver", "Haw"],
                   "Southron": ["Pen", "Tre", "Lan", "Pol", "Ros", "Tor", "Car", "Bos", "Coom", "Mor", "Hel", "Ven", "Zen"],
                   "Westron": ["Ald", "Ead", "Wulf", "Wen", "Sel", "Ced", "Os", "Here", "Gods", "Cyn", "Leof", "Ælf", "Sige"]}
PREFIXES = ["Long", "Great", "Little", "Nether", "Upper", "Old", "East", "West", "North", "South", "High", "Low", "Much", "Steeple", "King's", "Bishop's", "Abbot's"]
TOWN_PREFIXES = ["Chipping", "Market", "Great", "King's", "Cheap"]
SUFFIX_PHRASES = ["-under-Edge", "-on-the-Water", "-in-the-Marsh", "-on-the-Hill", " Cross", " Bridge", " Green", " End", " Parva", " Magna",
                  "-by-the-Wood", " Heath", " Moor", "-le-Dale", " Wells", " St Agnes"]
# region adjectives: weather, colour, mood, story
ADJECTIVES = ["Weeping", "Drowned", "Whispering", "Gloaming", "Bitter", "Sleeping", "Hollow", "Grey", "Wending", "Forgotten", "Moaning", "Restless",
              "Broken", "Burning", "Hushed", "Fallow", "Thorny", "Witching", "Gallows", "Sunken", "Hollowed", "Lantern", "Silver", "Lost", "Barrow",
              "Long", "Black", "White", "Red", "Golden", "Starved", "Weary", "Singing", "Crooked", "Blind", "Cold", "Windy", "Wild", "Hidden",
              "Lonely", "Nameless", "Shivering", "Smoking", "Shining", "Dun", "Pale", "Rust", "Ember", "Heron", "Wolfish", "Kestrel", "Owl's",
              "Hag's", "Devil's", "Giant's", "Maiden's", "Shepherd's", "Hermit's", "Pilgrim's", "Drover's", "Miller's", "Widow's", "Fiddler's",
              "Thieves'", "Kings'", "Dead Man's", "Ninefold", "Seven", "Twelve", "Endless", "Quiet", "Restful", "Ragged", "Bleak", "Bramble",
              "Briar", "Raven's", "Sorrow", "Merry", "Mournful", "Marrow", "Ashen", "Iron", "Copper", "Murmuring"]
BIOME_WORDS = {
    "forest": ["Wood", "Weald", "Holt", "Forest", "Wildwood", "Greenwood", "Chase", "Hanger", "Shaw", "Frith", "Spinney", "Copse", "Thicket", "Hurst"],
    "marsh": ["Fen", "Mire", "Marsh", "Carr", "Moss", "Bog", "Levels", "Flats", "Slough", "Sedge", "Wash", "Quag", "Moors", "Fleet"],
    "plains": ["Downs", "Heath", "Lea", "Moor", "Wold", "Fields", "Plain", "Common", "Waste", "Meads", "Vale", "Wolds", "Sweep", "Barrens"],
    "hills": ["Hills", "Fells", "Knolls", "Rise", "Edge", "Tops", "Brae", "Howes", "Pikes", "Lows", "Scarp", "Ridges", "Banks", "Barrows"],
    "peaks": ["Crags", "Teeth", "Peaks", "Spires", "Heights", "Horns", "Fangs", "Scars", "Pikes", "Bens", "Stacks", "Pinnacles", "Thrones", "Mountains"],
    "lake": ["Mere", "Water", "Lake", "Tarn", "Pool", "Broad", "Loch", "Reach", "Sound", "Deeps"],
}
VOWELS = set("aeiouyæ")


def _clip(name):
    """A founder's name worn down to a place-name root: Asaecy -> Asa, Gayllie -> Gayl."""
    n = name.replace("'", "")
    i = 0
    while i < len(n) and n[i].lower() not in VOWELS:
        i += 1
    while i < len(n) and n[i].lower() in VOWELS:
        i += 1
    if i < len(n) and n[i].lower() not in VOWELS:
        i += 1                               # keep one consonant after the first vowel: As-, Gayl-
    root = n[:max(i, 2)]
    if len(root) < 3 and len(n) > 3:
        root = n[:min(len(n), 4)]
    return root


def _join(root, end):
    """Glue a root and an ending without awkward seams: no tripled letters, no vowel pile-ups."""
    r, e = root, end
    if r[-1].lower() == e[0].lower():
        r = r[:-1] if len(r) > 2 else r
    if r[-1].lower() in VOWELS and e[0].lower() in VOWELS:
        r = r[:-1] if len(r) > 3 else r + {"a": "n", "e": "d", "i": "s", "o": "n", "u": "l", "y": "s"}.get(r[-1].lower(), "n")
    if r.lower().endswith(("ck", "gh", "th", "sh")) and e[0].lower() in "bcdfgkpst" and len(e) > 2:
        pass
    out = r + e
    return out[0].upper() + out[1:]


def _overlap(a, b):
    """'Barrow Barrows', 'Fenmoss Moss': the two halves say the same thing."""
    a, b = a.lower(), b.lower().rstrip("s")
    return b in a or a.rstrip("s") in b


class Namer:
    def __init__(self, seed, people=None):
        self.rng = random.Random(f"{seed}-places")
        self.people = people                  # the name model, for founders' names
        self.used_roots, self.used_ends, self.used_adj, self.used_words, self.names = set(), set(), set(), set(), set()

    def _pick(self, pool, used):
        fresh = [x for x in pool if x not in used]
        x = self.rng.choice(fresh or pool)
        used.add(x)
        return x

    def root(self, culture, clipped=None):
        """A first element. clipped=True forces a founder's name, False a feature word, None either."""
        r = self.rng.random() if clipped is None else (0.0 if clipped else 1.0)
        self.last_clipped = False
        if r < 0.45 and self.people is not None:
            for _ in range(10):
                try:
                    g = self.people.generate(self.rng, culture, self.rng.choice(["female", "male"]))
                except Exception:
                    break
                root = _clip(g)
                if root not in self.used_roots and len(root) >= 3:
                    self.used_roots.add(root)
                    self.last_clipped = True
                    return root
        pool = FEATURES + FEATURE_CULTURE.get(culture, []) * 2
        return self._pick(pool, self.used_roots)

    def settlement(self, culture, scale="village"):
        """A village, hamlet or town name."""
        for _ in range(30):
            base = _join(self.root(culture), self._pick(ENDINGS.get(culture, ENDINGS["Westron"]), self.used_ends))
            roll = self.rng.random()
            if scale == "town" and roll < 0.45:
                name = f"{self.rng.choice(TOWN_PREFIXES)} {base}" if self.rng.random() < 0.6 else f"{base} Market"
            elif roll < 0.16:
                name = f"{self.rng.choice(PREFIXES)} {base}"
            elif roll < 0.27:
                name = base + self.rng.choice(SUFFIX_PHRASES)
            else:
                name = base
            if name not in self.names:
                self.names.add(name)
                return name
        return name

    def region(self, biome, culture):
        """A region name: Asby Weald, the Weeping Moss, the Fells of Kelgarth, Haldra's Chase."""
        for _ in range(30):
            word = self._pick(BIOME_WORDS.get(biome, ["Lands"]), self.used_words)
            style = self.rng.random()
            if style < 0.36:
                root = self.root(culture)
                if self.last_clipped or self.rng.random() < 0.4:      # a founder's clipped name always takes an ending
                    root = _join(root, self._pick(ENDINGS.get(culture, ENDINGS["Westron"]), self.used_ends))
                if _overlap(root, word):
                    continue
                name = f"{root} {word}"
            elif style < 0.68:
                adj = self._pick(ADJECTIVES, self.used_adj)
                if adj.lower().rstrip("'s") == word.lower():
                    continue
                name = f"the {adj} {word}"
            elif style < 0.9:
                place = _join(self.root(culture), self._pick(ENDINGS.get(culture, ENDINGS["Westron"]), self.used_ends))
                if _overlap(place, word):
                    continue
                name = f"the {word} of {place}"
            else:
                founder = self.people.generate(self.rng, culture, self.rng.choice(["female", "male"])) if self.people else self.root(culture, False)
                name = f"{founder}' {word}" if founder.endswith("s") else f"{founder}'s {word}"
            if name not in self.names:
                self.names.add(name)
                return name
        return name


# ---------------------------------------------------------------- the world's own name
# Every world has a name as a whole, above its regions and villages: worked out from the seed alone
# (with its own dice), so it never changes and worlds saved before it existed get one too.
REALM_ENDS = ["ia", "oria", "aria", "or", "ond", "eth", "mere", "orn", "avel", "oth", "ara", "dor", "wyn", "ys",
              "enmark", "garde", "holm", "ador", "ellion", "anthe", "ost", "andar", "esse", "umbra"]
REALM_ADJ = ["Sundered", "Ageless", "Ashen", "Hallowed", "Twilit", "Unbroken", "Fallen", "Gilded", "Shrouded",
             "Forsaken", "Evergreen", "Ninefold", "Hollow", "Silent", "Undying", "Wandering", "Weeping", "Iron",
             "Elder", "Thousand-Year", "Unconquered", "Drowned", "Hidden", "Forgotten", "Old", "Last", "Bright", "Grey"]
REALM_NOUNS = ["Realm", "Kingdom", "Marches", "Dominion", "Reaches", "Holds", "Crownlands", "Commonwealth", "Wilds",
               "Shires", "Principality", "Expanse", "Lands", "Vales", "Protectorate", "Empire", "Domain", "March"]
REALM_EPITHETS = ["the Ninefold Realm", "Land of Long Winters", "the Hollow Crown", "Last of the Old Kingdoms",
                  "the World Under Ash", "the Kingdom of Bells", "Cradle of Kings", "the Country of Lost Roads",
                  "Where the Old Gods Sleep", "the Land Between the Ages", "Realm of the Twice-Crowned",
                  "the Unwritten Kingdom", "Last Light of the West", "Land of a Thousand Barrows", "the Weeping Crown",
                  "the Long Twilight", "the Kingless Country", "the Land That Remembers", "Hearth of the World",
                  "the Realm Beyond the Wall", "Seat of the Seven Thrones", "the Broken Crown", "the Quiet Kingdom",
                  "the Land of Kept Oaths", "the Ember Throne", "the Green Dominion", "Home of the Hundred Banners",
                  "the Realm of Ash and Bells", "the Country of Saints", "the Dreaming Lands"]


def world_title(seed, people=None):
    """A grandiose name for a whole world, e.g. 'Valdoria, Land of Long Winters' or 'The Sundered Marches of Ostmere'."""
    rng = random.Random(f"{seed}-world-title")
    culture = rng.choice(["Archaic", "Westron", "Northish", "Southron"])
    root = None
    if people is not None:
        try:
            root = _clip(people.generate(rng, culture, rng.choice(["female", "male"])))
        except Exception:
            root = None
    if not root or len(root) < 3:
        root = rng.choice(FEATURES)
    name = _join(root, rng.choice(REALM_ENDS))
    roll = rng.random()
    if roll < 0.35:
        return f"{name}, {rng.choice(REALM_EPITHETS)}"
    if roll < 0.7:
        return f"The {rng.choice(REALM_ADJ)} {rng.choice(REALM_NOUNS)} of {name}"
    if roll < 0.88:
        return f"The {rng.choice(REALM_NOUNS)} of {name}"
    return name
