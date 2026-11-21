"""Keeping generated text consistent with itself and with the moment.

Two kinds of guard live here:

* CONTEXT rules: a sentence must not contradict the current time, weather,
  season or place (sunlight at night, stars at noon, far views in fog, snow in
  high summer...). The narrator re-rolls any sentence that breaks one.
* compatibility tables used at world generation, so that fixed facts agree with
  each other: a person's age, hair, build, job and role; a weapon's material,
  form and condition; a creature's trait and body; a village's walls and roof;
  a ruin's purpose and what is left inside it; a shrine's spirit and setting.

tools/coherence.py audits generated text against the same rules.
"""
import re


def W(*words):
    return re.compile(r"\b(" + "|".join(words) + r")\b", re.I)


# ----------------------------------------------------------------- context rules
SUN = W("sunlight", "sunlit", "sunshine", "sunbeams?", r"sun (glints|glares|beats|blazes|warms|is fierce|comes and goes)",
        r"shafts of sun", "patch of sun", "dappl\\w+", "your shadow", "shadows (lie|stand|stretch) crisp", "heat (shimmers|haze)",
        "cloud-shadows?", "bright air", "blue sky", "hard blue", "into blue", "patches of blue", "larks hang", "rainbow\\w*", "lizards bask", "bakes in the heat")
NIGHT_SKY = W("stars? (appear|wheel|prick|glitter|shine|burn|crowd)", "starlight", "starlit", "moonlight", "moonlit", "the moon (rises|hangs|sails|is up)",
              "(waxing|waning|full|new|crescent|gibbous) moon")
STARS_SEEN = W("full moon floods", "moon (hangs|rises|throws|lights|sits|clings|looks back|lies on)", "moonlight (silvers|makes|picks|fills|lights)", "in the moonlight", "under the full moon", "starlight", "starlit", "stars? (appear|wheel|prick|glitter|shine|burn|crowd)", "moonlit", "moonlight")
FALLING_RAIN = W("rain (falls|drums|patters|lashes|hisses|beats|comes down|rattles)", "drizzle", "downpour", "raindrops", "it is pouring", "mizzle")
FAR = W("for miles", "the horizon", "far-off things", "distant things look close", "every crack in the distant", "into the distance",
        "far distance", "see for", "the land rolls away")
CALM = W("still air", "windless", "not a breath of wind", "air (hangs|is) still", "no wind", "feel no wind", "clear and still", "not a ripple",
         "unbroken by any ripple", "not a single ripple", "unmoving surface")
SNOWY = W("snow\\w*", "icicles?", "skin of ice", "frozen", "hoarfrost", "rime\\w*", "frost-rimed", "glazed with frost", "white with frost", "snowdrops?")
WINTER_ONLY = W("bare branches", "leafless", "snowdrops?", "holly berries", "hoarfrost")
LEAFY = W("full leaf", "leaves move", "canopy roars", "heavy with leaves", "green canopy", "foxgloves", "bluebells", "meadowsweet", "lily pads", "water-lilies",
          "dragonflies", "butterflies", "lizards?", "warm stone", "basks?", "basking")
SPRING_ONLY = W("blossom\\w*", "catkins?", "lambs?", "new leaves", "first green", "frogspawn")
AUTUMN_ONLY = W("fallen leaves", "leaf-fall", "turning leaves", "russet leaves", "stubble fields?", "rutting")
HARVEST = W("harvest(ers|ing)?", "haymaking", "hay-making", "reapers?", "sheaves")
VILLAGE_BUSTLE = W("lanes are busy", "children (play|run|chase|shriek)", "market day", "folk going about their day", "busy with folk", "bustl\\w+")

DARK_TIMES = ("evening", "night", "deepnight")
DAY_TIMES = ("morning", "midday", "afternoon")
DULL = ("overcast", "drizzle", "rain", "storm", "fog", "snow")
CLOUDED = ("overcast", "drizzle", "rain", "storm", "fog", "snow")


DISTANT_PEAKS = W("mountains?", "crags?", "summits?", "peaks?", "snowfields?", "glaciers?")
# (name, sentence regex, predicate on (season, weather, time, biome), exception regex)
CONTEXT = [
    ("sunlight while dark", SUN, lambda s, w, t, b: t in DARK_TIMES),
    ("sunlight in dull weather", SUN, lambda s, w, t, b: w in DULL),
    ("stars or moon by day", NIGHT_SKY, lambda s, w, t, b: t in DAY_TIMES),
    ("stars through cloud", STARS_SEEN, lambda s, w, t, b: w in CLOUDED),
    ("falling rain in dry weather", FALLING_RAIN, lambda s, w, t, b: w in ("clear", "cloudy", "wind", "fog", "snow")),
    ("far views in fog", FAR, lambda s, w, t, b: w == "fog"),
    ("far views in the dark", FAR, lambda s, w, t, b: t in ("night", "deepnight")),
    ("calm in wind or rain", CALM, lambda s, w, t, b: w in ("wind", "storm", "rain", "drizzle")),
    ("snow out of season", SNOWY, lambda s, w, t, b: (s == "summer" or (s in ("spring", "autumn") and w != "snow")) and b != "peaks", DISTANT_PEAKS),
    ("icicles out of season", W("icicles?"), lambda s, w, t, b: s != "winter"),
    ("winter sights out of winter", WINTER_ONLY, lambda s, w, t, b: s in ("spring", "summer")),
    ("summer leaves in winter", LEAFY, lambda s, w, t, b: s == "winter"),
    ("spring sights in autumn or winter", SPRING_ONLY, lambda s, w, t, b: s in ("autumn", "winter")),
    ("autumn sights in spring or summer", AUTUMN_ONLY, lambda s, w, t, b: s in ("spring", "summer")),
    ("harvest out of season", HARVEST, lambda s, w, t, b: s in ("winter", "spring")),
    ("village bustle at night", VILLAGE_BUSTLE, lambda s, w, t, b: t in ("night", "deepnight")),
]


CONTEXT = [r if len(r) == 4 else r + (None,) for r in CONTEXT]


def context_clashes(sentence, season, weather, time, biome=None):
    return [name for name, rx, pred, unless in CONTEXT
            if pred(season, weather, time, biome) and rx.search(sentence) and not (unless and unless.search(sentence))]


# a content word used twice in one sentence ("pick a path ... the path")
_STOP = set("""the and with that this from into onto over under their there here they them then than your you its
have has had were was are is been be being some what which while where when who whom whose would could should
about above after again against all also among around because before behind below beneath beside between beyond
both down during each even every few further more most much near nothing once only other others out own same
such through toward towards until upon very well like just still away back seem seems little long one ones side
sides more less half""".split())
_IDIOM = re.compile(r"\b(\w+) (to|after|by|upon|on) \1\b|\bnever quite\b|\bagain\b|\bmore and more\b|\bon and on\b", re.I)


def repeated_words(sentence):
    s = _IDIOM.sub(" ", sentence.lower())
    s = re.sub(r"\"[^\"]*\"", " ", s)          # quoted speech may repeat itself
    words = [w.rstrip("s") for w in re.findall(r"[a-z][a-z'-]+", s) if len(w) > 3 and w not in _STOP]
    seen, dup = set(), []
    for w in words:
        if w in seen and w not in dup:
            dup.append(w)
        seen.add(w)
    return dup


# ----------------------------------------------------------------- people
AGE_BAND = {
    "young": "young", "youngish": "young", "youthful": "young", "fresh-faced": "young",
    "middle-aged": "mid", "careworn": "mid", "weathered": "mid", "ageless-seeming": "any",
    "grizzled": "old", "elderly": "old", "ancient": "old", "aged": "old", "greying": "old", "white-haired": "old",
    "silver-haired": "old", "time-worn": "old",
}
AGE_NAMES_HAIR = {"greying", "white-haired", "silver-haired", "grizzled"}     # these already say what the hair looks like
# hair: which ages it suits, and whether it states a colour or baldness
HAIR_RULES = {
    "hair the colour of straw": ("young", "mid"), "a shaved head": ("young", "mid", "old"),
    "grey braids": ("old",), "a wild black mane": ("young", "mid"), "thinning red hair": ("mid", "old"),
    "a cloud of white hair": ("old",), "close-cropped brown hair": ("young", "mid"),
    "a long plait wound around the head": ("young", "mid", "old"), "hair hidden under a linen coif": ("young", "mid", "old"),
    "copper curls tied back with string": ("young", "mid"), "hair cropped close for lice": ("young", "mid", "old"),
    "a single thick braid": ("young", "mid", "old"), "a tangle of iron-grey hair": ("old", "mid"),
    "hair the colour of wet sand": ("young", "mid"), "a fringe cut straight across": ("young", "mid"),
    "a balding crown and a fierce beard": ("mid", "old"), "dark hair streaked with white": ("mid", "old"),
    "hair hidden under a felt cap": ("young", "mid", "old"),
}
HAIR_NEUTRAL = {"a long plait wound around the head", "hair hidden under a linen coif", "a single thick braid",
                "hair hidden under a felt cap", "hair cropped close for lice"}   # fine beside "white-haired"
BUILD_NOT_YOUNG = {"stooped", "hunched", "round-bellied"}
YOUNG_JOBS = {"goose-girl", "goose-boy", "chandler's boy", "chandler's girl"}
ROLE_AGES = {"elder": ("old",)}
# jobs that only make sense in some country; anything unlisted works anywhere
JOB_LAND = {
    "eel-catcher": {"marsh", "water"}, "ferryman": {"water", "marsh"}, "net-mender": {"water", "marsh"},
    "charcoal-burner": {"forest"}, "woodcutter": {"forest"}, "hurdle-maker": {"forest", "plains"},
    "shepherd": {"hills", "plains", "peaks"}, "drover": {"hills", "plains"}, "ploughman": {"plains", "hills"},
    "goose-girl": {"plains", "marsh", "water"}, "goose-boy": {"plains", "marsh", "water"}, "swineherd": {"forest", "plains", "marsh"},
}


# an elder's title already says they are old; these would only say it again ("an elderly village elder")
ELDER_AVOID = {"elderly", "aged", "ancient"}


def age_ok(age, role, job):
    band = AGE_BAND.get(age, "any")
    if role in ROLE_AGES and band not in ROLE_AGES[role]:
        return False
    if role == "elder" and age in ELDER_AVOID:
        return False
    if job in YOUNG_JOBS and band != "young":
        return False
    return True


MALE_ONLY_HAIR = {"a balding crown and a fierce beard"}


def hair_ok(hair, age, gender=None):
    if gender == "female" and hair in MALE_ONLY_HAIR:
        return False
    band = AGE_BAND.get(age, "any")
    if age in AGE_NAMES_HAIR and hair not in HAIR_NEUTRAL:
        return False
    allowed = HAIR_RULES.get(hair)
    return allowed is None or band == "any" or band in allowed


def build_ok(build, age):
    return not (AGE_BAND.get(age) == "young" and build in BUILD_NOT_YOUNG)


def job_ok(job, lands):
    need = JOB_LAND.get(job)
    return need is None or bool(need & lands)


# ----------------------------------------------------------------- weapons & armour
METALS = {"bronze", "iron", "steel", "black iron", "star-metal", "copper"}
WEAPON_MATERIALS = {
    # noun -> materials it can be made of
    "sword": METALS - {"copper"}, "shortsword": METALS, "broadsword": METALS - {"copper", "bronze"}, "falchion": METALS - {"copper"},
    "axe": METALS, "hand-axe": METALS | {"flint"}, "bearded axe": METALS - {"copper"}, "hatchet": METALS | {"flint"},
    "spear": METALS | {"flint", "bone"}, "boar-spear": METALS, "javelin": METALS | {"flint", "bone"}, "pike": METALS - {"copper"},
    "mace": METALS, "cudgel": {"oak", "blackthorn", "bone"}, "flail": METALS - {"copper"}, "war-hammer": METALS, "club": {"oak", "blackthorn", "bone"},
    "dagger": METALS | {"flint", "bone"}, "knife": METALS | {"flint", "bone"}, "dirk": METALS, "seax": METALS - {"copper"},
    "quarterstaff": {"oak", "blackthorn"}, "staff": {"oak", "blackthorn"}, "shod staff": {"oak", "blackthorn"},
}
# what wear and tear looks like on each material (replaces "rusted"/"pitted")
WORN_WORDS = {
    "bronze": {"rusted": "verdigrised", "pitted": "tarnished"}, "copper": {"rusted": "verdigrised", "pitted": "tarnished"},
    "bone": {"rusted": "cracked", "pitted": "yellowed"}, "flint": {"rusted": "chipped", "pitted": "rough-knapped"},
    "oak": {"rusted": "split", "pitted": "worm-eaten"}, "blackthorn": {"rusted": "split", "pitted": "warped"},
}
SOFT_ARMOUR = {"leather jerkin", "padded gambeson", "quilted coat"}
SOFT_WORN = {"pitted": "scuffed", "notched": "patched", "rusted": "mildewed"}
# details that need a metal edge or point, and details whose condition must match the item's quality
NEEDS_METAL = W("honed", "blue sheen", "blood-rust", "fuller", "keen enough to shave", "polished bright", "hammered bands", "iron knobs", "crossguard")
PRISTINE = W("keen enough to shave", "polished bright", "took good care", "very little use", "holds a faint blue sheen", "well oiled")
SHABBY = W("dull and needs a whetstone", "split and bound", "nicked in several places", "blood-rust", "dented from heavy use", "patched in several places")
WORN_Q = {"rusted", "pitted", "notched", "verdigrised", "tarnished", "cracked", "yellowed", "chipped", "rough-knapped", "split",
          "worm-eaten", "warped", "scuffed", "patched", "mildewed"}
FINE_Q = {"well-made", "fine", "masterwork"}


def detail_ok(text, quality, material):
    if quality and re.search(r"\b" + re.escape(quality) + r"\b", text, re.I):
        return False                   # "a patched jerkin. It is patched in several places."
    if material not in METALS and NEEDS_METAL.search(text):
        return False
    if quality in WORN_Q and PRISTINE.search(text):
        return False
    if quality in FINE_Q and SHABBY.search(text):
        return False
    return True


# ----------------------------------------------------------------- creatures
UNDEAD_TRAITS = ["restless", "ancient", "flickering", "hollow-eyed", "huge", "hungering", "old"]
TRAITS_BY_COVER = {     # which individual traits suit which bodies (others come from lex_entities.INDIVIDUAL)
    "no_mange": {"serpent", "toad", "spider", "crow", "wraith"},
    "no_limp": {"serpent", "wraith"},
}
SMALL_SIZES = {"small", "lean", "wiry"}


def trait_ok(trait, key, size, undead):
    if undead:
        return trait in UNDEAD_TRAITS and not (trait == "huge" and size in SMALL_SIZES)
    if trait == "mangy" and key in TRAITS_BY_COVER["no_mange"]:
        return False
    if trait == "limping" and key in TRAITS_BY_COVER["no_limp"]:
        return False
    if trait == "huge" and size in SMALL_SIZES:
        return False
    return True


# ----------------------------------------------------------------- places
def _stuff(word):
    w = word.lower()
    for k in ("slate", "turf", "sod", "thatch", "tile", "shingle", "stone", "timber"):
        if k in w:
            return {"sod": "turf", "tile": "tile"}.get(k, k)
    return None


def walls_roof_ok(material, roof):
    a, b = _stuff(material), _stuff(roof)
    if a and a == b:
        return False                    # "green-slate cottages under grey slate"
    if material in ("pole-and-daub", "wattle-and-daub", "clay-walled", "turf-walled", "cob") and roof in ("stone slabs", "grey slate", "slate"):
        return False                    # flimsy walls can't carry a stone roof
    return True


RELIGIOUS = {"chapel", "temple", "monastery", "abbey", "chantry", "manor chapel", "mausoleum"}
BELLS = RELIGIOUS | {"beacon tower", "gatehouse", "watchtower", "court-house"}
ROOFLESS = {"roofless", "roofless and open to the rain", "toppled", "half-collapsed", "fire-blackened", "gutted", "picked clean by stone-robbers"}


def ruin_ok(purpose, state, interior):
    if "font" in interior and purpose not in RELIGIOUS:
        return False
    if "bell" in interior and purpose not in BELLS:
        return False
    if "rafters" in interior and state in ROOFLESS - {"half-collapsed", "fire-blackened"}:
        return False
    if "open to the sky" in interior and state in ("sunk to its windows in earth", "shored up with rotting timbers"):
        return False
    return True


SPIRIT_MASC = {"Gorvan", "Ludd", "Hywel", "Oswy", "Morrow"}
SPIRIT_FEM = {"Ethne", "Tilda", "Senna", "Aldwen", "Bracca"}
TREE_SHRINES = {"rag-tree", "hollow oak"}


def spirit_ok(pre, name, domain):
    if pre == "Old Man" and name in SPIRIT_FEM:
        return False
    if pre == "Sister" and name in SPIRIT_MASC:
        return False
    if domain.startswith("lady") and (pre == "Old Man" or name in SPIRIT_MASC):
        return False
    return True


def shrine_form_ok(form, biome):
    return not (form in TREE_SHRINES and biome in ("peaks", "marsh"))
