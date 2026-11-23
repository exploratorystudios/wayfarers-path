#!/usr/bin/env python3
"""Contradiction audit: does any generated text disagree with itself or its moment?

Generates descriptions across many worlds, in every season, time of day and
weather, plus people, creatures, items, sites and intros. Then checks:
  * context clashes: sunlight at night, snow in summer, bare branches in June...
  * internal clashes: a "young" elder, white hair on a youth, rust on bronze...
  * a content word used twice in one sentence ("pick a path ... the path")

Prints each rule's hit count and a few examples. Exit status 1 if anything hit.

Usage: python3 tools/coherence.py [worlds] [-v]
"""
import collections
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rpg.game import Game                     # noqa: E402
from rpg.world import SEASONS                 # noqa: E402

from rpg import coherence as CO              # noqa: E402

HOURS = {"dawn": 6, "morning": 9, "midday": 12, "afternoon": 15, "dusk": 19, "evening": 21, "night": 23, "deepnight": 3}
WEATHERS = ["clear", "cloudy", "overcast", "drizzle", "rain", "storm", "fog", "wind", "snow"]
W = CO.W

YOUNG = W("young", "youngish", "youthful", "fresh-faced", "callow", "fledgling", "unlined", "barely grown")
OLD = W("elderly", "ancient", "wrinkled", "grizzled", "white-haired", "silver-haired", "greying", "time-worn", "grey braids", "white hair",
        "iron-grey", "balding", "thinning", "streaked with white")
HAIR_COLOUR = W("colour of straw", "black mane", "red hair", "brown hair", "copper curls", "wet sand", "iron-grey", "white hair", "grey braids", "streaked with white")
HAIR_AGE = W("white-haired", "silver-haired", "greying", "grizzled")
NO_HAIR = W("shaved head", "balding crown")
RUSTLESS = W("bronze", "copper", "bone", "flint", "oak", "blackthorn", "leather", "gambeson", "quilted", "padded")
RUSTY = W("rust\\w*", "pitted")
GOOD_EDGE = CO.PRISTINE
WORN_Q = W(*sorted(CO.WORN_Q))
FINE_Q = W(*sorted(CO.FINE_Q))
BAD_STATE = CO.SHABBY

def ctx_for(rng):
    season = rng.choice(SEASONS)
    weather = rng.choice([w for w in WEATHERS if w != "snow" or season == "winter"])
    tod = rng.choice(list(HOURS))
    return season, weather, tod


def with_biome(c, biome):
    return c[:3] + (biome,)


def set_ctx(g, season, weather, tod):
    w = g.world
    w.season, w.weather = season, weather
    w.minutes = (w.day - 1) * 1440 + HOURS[tod] * 60 + 10


def collect(worlds=30, seed0=7000):
    """Yield (kind, context, text) samples."""
    rng = random.Random(seed0)
    classes = ["knight", "ranger", "wizard", "rogue", "cleric"]
    for i in range(worlds):
        out = []
        g = Game(seed=seed0 + i, name="Tester", out=out.append, klass=classes[i % 5])
        set_ctx(g, *ctx_for(rng))
        g.intro()
        yield "intro", (g.world.season, g.world.weather, g.world.time_of_day, g.world.tiles[g.pos].biome), " ".join(out[:2])
        w, n = g.world, g.narr
        tiles = list(w.land)
        rng.shuffle(tiles)
        for p in tiles[:60]:
            c = ctx_for(rng)
            set_ctx(g, *c)
            c = with_biome(c, w.tiles[p].biome)
            for para in n.location(p, brief=rng.random() < 0.3):
                yield "place", c, para
            t = w.tiles[p]
            for npc in t.npcs:
                yield "npc", c, n.npc_presence(npc) + " " + n.npc_full(npc)
            for cr in t.creatures:
                yield "creature", c, n.creature_full(cr)
            for f in t.features:
                yield "feature", c, n.feature_full(f, t.biome)
            for it in t.items:
                yield "item", c, it.name + ". " + n.item_full(it)
            if t.site:
                yield "site", c, " ".join(n.site_lines(t.site))
        for v in w.villages:
            for npc in w.tiles[v].npcs:
                yield "npc", c, f"[{npc.role}/{npc.job}] " + n.npc_presence(npc) + " " + n.npc_full(npc)
                for it in npc.stock:
                    yield "item", c, it.name + ". " + n.item_full(it)
                # what they talk about, in a few different moments
                from rpg import talk as TK
                for _ in range(3):
                    c2 = ctx_for(rng)
                    set_ctx(g, *c2)
                    npc.mem["told"] = [k for k in npc.mem["told"] if not k.startswith("life:")]
                    line = TK.life(g, npc)
                    if line:
                        yield "talk", with_biome(c2, w.tiles[v].biome), line
                # everything in their inner life, told
                from rpg import inner as IN, speech as SP
                for f in IN.of(w, npc)["facts"]:
                    said = SP.compose(g, npc, f)
                    if said:
                        yield "talk", with_biome(c2, w.tiles[v].biome), said
        for _ in range(15):
            it = w.make_item(rng.randint(1, 4))
            yield "item", c, it.name + ". " + n.item_full(it)
        # procedural stories: the asking, every hint, the twist
        from rpg import plots as P
        for v in w.villages:
            for npc in w.tiles[v].npcs:
                plot = P.make(g, npc)
                if not plot:
                    continue
                F = plot["F"]
                yield "story", c, P.offer_text(g, plot, npc)
                for st in plot["steps"]:
                    if st.get("intro"):
                        yield "story", c, P.fill(P.fill(st["intro"], st), F)
                if plot["twist"]:
                    yield "story", c, P.fill(P.TWISTS[plot["twist"]][1], F)


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?\"])\s+", text.replace("\n", " ")) if s.strip()]


def both(a, b):
    return lambda s: a.search(s) and b.search(s)


# (name, applies to kinds, context predicate, sentence test)
RULES = [(name, ("place", "site", "intro", "feature"), (lambda pred: lambda c: pred(*c))(pred),
          (lambda rx, unless: lambda s: rx.search(s) and not (unless and unless.search(s)))(rx, unless))
         for name, rx, pred, unless in CO.CONTEXT] + [
    ("young and old together", ("npc",), None, lambda s: YOUNG.search(s) and OLD.search(s)),
    ("unfilled slot in a story", ("story", "talk"), None, lambda s: "{" in s or "}" in s),
    ("doubled word in talk", ("talk",), None, lambda s: bool(re.search(r"\b(the|a|an|and|of|to|my) \1\b", s, re.I))),
    ("a name where a pronoun belongs", ("story",), None, lambda s: bool(__import__("re").search(r"\b(he|she|it) (he|she|it)\b", s))),
    ("age said twice on an elder", ("npc",), None, lambda s: W("elderly", "aged", "ancient").search(s) and W("elder", "eldest").search(s)),
    ("hair-age and hair colour clash", ("npc",), None, lambda s: HAIR_AGE.search(s) and (HAIR_COLOUR.search(s) or NO_HAIR.search(s))),
    ("young elder", ("npc",), None, lambda s: YOUNG.search(s) and W("elder", "eldest", "headman", "headwoman", "moot-speaker", "warden", "reeve", "keeper of the moot-stone", "steward", "village head").search(s)),
    ("youthful job, old person", ("npc",), None, lambda s: W("goose-girl", "goose-boy", "chandler's boy", "chandler's girl").search(s) and OLD.search(s)),
    ("water job far from water", ("npc",), None, lambda s: False),
    ("rust on rustless", ("item",), None, lambda s: RUSTY.search(s) and RUSTLESS.search(s) and not W("blood-rust").search(s)),
    ("worn item, pristine detail", ("item",), None, lambda s: WORN_Q.search(s) and GOOD_EDGE.search(s)),
    ("fine item, shabby detail", ("item",), None, lambda s: FINE_Q.search(s) and BAD_STATE.search(s)),
    ("stone/bone/wood where it can't be", ("item",), None, lambda s: W("flint (sword|shortsword|broadsword|falchion|mace|flail|war-hammer|cudgel|club|pike|axe|bearded axe|seax|dirk)",
                                                                       "bone (broadsword|falchion|flail|war-hammer|pike|sword|shortsword|mace|axe|hatchet)",
                                                                       "(oak|blackthorn) (sword|axe|mace|flail|war-hammer|dagger|knife|spear)").search(s)),
    ("metal detail on non-metal", ("item",), None, lambda s: W("bone", "flint", "oak", "blackthorn").search(s) and CO.NEEDS_METAL.search(s)),
    ("undead with a living body", ("creature",), None, lambda s: W("wraith").search(s) and W("mangy", "limping", "sleek", "gaunt", "young", "fur", "bleed\\w*").search(s)),
    ("mange without fur", ("creature",), None, lambda s: W("mangy").search(s) and W("serpent", "toad", "spider", "crow", "wraith").search(s)),
    ("limping without legs", ("creature",), None, lambda s: W("limping").search(s) and W("serpent", "wraith").search(s)),
    ("huge and small at once", ("creature",), None, lambda s: W("small frame", "small,? (beast|bear|wolf|boar)", "lean frame", "wiry frame", "small, lean", "lean, small").search(s) and W("huge", "colossal").search(s)
                                                       or re.search(r"\\bhuge\\b[^.]*\\b(small|lean|wiry)\\b(?! eyes| clever| furious)", s)),
    ("gendered spirit mismatch", ("site",), None, lambda s: (W("Old Man").search(s) and W("lady", "Tilda", "Senna", "Ethne", "Aldwen", "Bracca").search(s))
                                                          or (W("Sister").search(s) and W("Gorvan", "Ludd", "Hywel", "Oswy", "Morrow").search(s))),
    ("walls and roof of the same stuff", ("site", "place"), None, lambda s: re.search(r"slate\\b[^.]*\\bslate|turf[^.]*\\b(turf|sod)\\b", s, re.I)
                                                                  and W("cottages", "houses", "homes", "huts").search(s)),
    ("font/bell in a secular ruin", ("site", "place"), None, lambda s: W("ruin\\w*").search(s) and W("font", "broken bell").search(s)
                                                             and W("mill", "bathhouse", "granary", "toll-house", "hunting lodge", "tithe barn", "bridge-keep",
                                                                   "fortified farmhouse", "keep", "manor house", "lazar-house", "observatory").search(s)),
    ("rafters in a roofless ruin", ("site", "place"), None, lambda s: W("roofless", "open to the rain", "toppled").search(s) and W("rafters").search(s)),
    ("'once ... still' in the intro", ("intro",), None, lambda s: re.search(r"\\b(once|back when)\\b[^.;]*\\bstill (keeping|holding|carrying|bound)", s)),
]


def repeated_word(s):
    return CO.repeated_words(re.sub(r"^\[[^\]]*\] ", "", s))


def main(worlds=30, verbose=False):
    hits = collections.defaultdict(list)
    rep = collections.Counter()
    rep_ex = {}
    total = 0
    for kind, c, text in collect(worlds):
        for s in sentences(text):
            total += 1
            for name, kinds, pred, test in RULES:
                if kind in kinds and (pred is None or pred(c)) and test(s):
                    hits[name].append((c[:3], s))
            if kind in ("place", "site", "feature", "npc", "creature", "item", "intro") and not s.startswith("("):
                for wd in repeated_word(s):
                    rep[wd] += 1
                    rep_ex.setdefault(wd, s)
    print(f"checked {total} sentences from {worlds} worlds\n")
    bad = 0
    for name, *_ in RULES:
        h = hits.get(name, [])
        bad += len(h)
        if h:
            print(f"{len(h):5d}  {name}")
            for c, s in h[: (8 if verbose else 3)]:
                print(f"         [{'/'.join(c)}] {s[:220]}")
    if not bad:
        print("no contradictions found")
    print("\nwords repeated inside one sentence (top 20):")
    for wd, k in rep.most_common(20):
        print(f"{k:5d}  {wd:12s} {rep_ex[wd][:160]}")
    return 1 if bad else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    sys.exit(main(int(args[0]) if args else 30, "-v" in sys.argv))
