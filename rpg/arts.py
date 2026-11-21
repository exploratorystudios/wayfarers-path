"""Stats, the five schools of learning, books and scrolls, and the arts they teach.

Four stats (might, grace, wits, spirit) are kept as small numbers but only ever
shown in words. Each school has a stat, a home class, and a named trait that
lets you read its books:

    arcane  (wits)    Wizard  - Arcane Letters      spellbooks, grimoires, scrolls
    divine  (spirit)  Cleric  - The Kindled Word    litanies, breviaries, prayer-rolls
    martial (might)   Knight  - Drill-Learned       war-manuals, treatises of arms
    wild    (wits)    Ranger  - Trailwise           field almanacs, hunters' daybooks
    cant    (grace)   Rogue   - Cant-Reader         cant-books, cutpurses' primers

Anyone can earn another school's trait by raising its stat; a class's own
school goes to the fifth circle, another's to the second. Two leanings: a
Cleric can learn first-circle arcane spells from the start, and a Ranger needs
one point less grace than anyone else to read thieves' cant (and can go a
circle further in it).

Every art is data: a list of effects (damage, stun, weaken, ward, flee...)
run by `run()`, so new ones need no new code.
"""
from . import mind
from .textgen import cap, article

STATS = ("might", "grace", "wits", "spirit")
CLASS_STATS = {
    "knight": dict(might=6, grace=3, wits=3, spirit=4),
    "ranger": dict(might=4, grace=5, wits=6, spirit=3),
    "wizard": dict(might=2, grace=4, wits=6, spirit=4),
    "rogue":  dict(might=3, grace=6, wits=4, spirit=3),
    "cleric": dict(might=4, grace=3, wits=4, spirit=6),
}
DEFAULT_STATS = dict(might=4, grace=4, wits=4, spirit=4)
STAT_MAX = 10
GROWTH_STAT = {"knight": "might", "ranger": "wits", "wizard": "wits", "rogue": "grace", "cleric": "spirit"}

# how each stat reads, from 1-2 up to 9-10; several ways to say each, like the rest of the game
STAT_WORDS = {
    "might": [["slight of arm", "not built for heavy work", "light in the arm"],
              ["wiry", "of middling strength", "ordinarily strong"],
              ["strong", "solidly built", "strong in the arm"],
              ["powerful", "broad-shouldered and strong", "hard-muscled"],
              ["mighty", "strong as an ox", "built like a millstone"]],
    "grace": [["clumsy", "heavy-footed", "all elbows"],
              ["steady on your feet", "ordinary in your movements", "sure enough of foot"],
              ["nimble", "light on your feet", "quick-handed"],
              ["deft", "quick as a cat", "fluid in every movement"],
              ["fleet as a hare", "impossibly quick", "quick as a swallow"]],
    "wits":  [["slow to puzzle things out", "plain-minded", "no great thinker"],
              ["sensible", "practical-minded", "level-headed"],
              ["quick-witted", "bright", "sharp enough"],
              ["sharp-witted", "keen of mind", "clever"],
              ["brilliant", "razor-minded", "learned beyond your years"]],
    "spirit": [["easily shaken", "faint of heart", "uncertain of yourself"],
               ["even-tempered", "steady enough of heart", "calm"],
               ["strong-willed", "steady of spirit", "resolute"],
               ["fierce of spirit", "unshakeable", "iron-willed"],
               ["blazing with inner fire", "iron-souled", "unbreakable in will"]],
}
STAT_LABEL = {"might": "Might", "grace": "Grace", "wits": "Wits", "spirit": "Spirit"}
STAT_WHAT = {"might": "strength of arm: heavier blows, and martial techniques",
             "grace": "quickness: dodging, slipping away, and thieves' tricks",
             "wits": "a quick mind: spells, and the lore of the wild",
             "spirit": "will and faith: a deeper well of power, and prayers"}

SCHOOLS = {
    "arcane": dict(name="arcane", stat="wits", home="wizard", menu="Spells", trait="Arcane Letters",
                   trait_desc="You can read spellbooks and magic scrolls.", art="spell",
                   books=["spellbook", "grimoire", "codex"], scroll="scroll",
                   looks=["bound in cracked green vellum", "with a brass clasp gone green with age", "its pages stained with ink and candle-wax",
                          "with a star chart folded inside the cover", "its margins crowded with tiny diagrams"],
                   titles=["The Lesser Key of {name}", "{name}'s Book of Fires", "The Grey Codex", "Of Wards and Their Breaking",
                           "The Seventh Lantern", "{name}'s Commonplace of the Art", "The Book of Small Thunders"],
                   dawn="The crabbed letters of the spellbooks suddenly mean something to you."),
    "divine": dict(name="divine", stat="spirit", home="cleric", menu="Prayers", trait="The Kindled Word",
                   trait_desc="You can read litanies and prayer-rolls.", art="prayer",
                   books=["litany", "breviary", "psalter"], scroll="prayer-roll",
                   looks=["bound in white calfskin worn grey at the edges", "its capitals picked out in faded gold", "smelling of old incense",
                          "with a ribbon marking a well-thumbed page", "its cover stamped with a sun"],
                   titles=["The Litany of {name}", "Hours of the Kindled Lamp", "The Psalter of Mercies", "{name}'s Breviary",
                           "The Book of Vigils", "Prayers for the Road"],
                   dawn="The old prayers no longer feel like someone else's words. They feel like yours."),
    "martial": dict(name="martial", stat="might", home="knight", menu="Feats", trait="Drill-Learned",
                    trait_desc="You can learn from war-manuals and treatises of arms.", art="technique",
                    books=["war-manual", "treatise of arms", "drill-book"], scroll=None,
                    looks=["its pages full of little inked figures mid-blow", "bound in boards scarred by a blade", "with notes in three different hands",
                           "its spine mended with a bootlace", "its diagrams smudged by sweaty thumbs"],
                   titles=["The Art of the Long Sword", "{name}'s Treatise on the Shield", "Drills for the Yard", "The Book of Twelve Guards",
                           "On Holding the Line", "{name}'s Notes on Killing Gracefully"],
                    dawn="The little inked figures in the war-manuals stop looking like dancers and start looking like fights."),
    "wild": dict(name="wild", stat="wits", home="ranger", menu="Skills", trait="Trailwise",
                 trait_desc="You can learn from field almanacs and hunters' daybooks.", art="skill",
                 books=["field almanac", "hunter's daybook", "herbal"], scroll=None,
                 looks=["its pages pressed with dried leaves", "full of sketches of tracks and droppings", "swollen from being rained on",
                        "bound in deerskin", "with a feather tucked in as a bookmark"],
                 titles=["The Almanac of the Grey Hare", "{name}'s Daybook", "Signs and Spoor", "The Hedge Herbal", "Of Snares and Patience",
                         "The Fox's Calendar"],
                 dawn="The hunters' notes and almanacs make sense now: the land, written down."),
    "cant": dict(name="cant", stat="grace", home="rogue", menu="Tricks", trait="Cant-Reader",
                 trait_desc="You can read the thieves' cant in cant-books and primers.", art="trick",
                 books=["cant-book", "cutpurse's primer", "book of tricks"], scroll=None,
                 looks=["written in a cipher of little hooks and crosses", "disguised as a book of sermons", "its pages greasy from many hands",
                        "with a false back where something was once hidden", "tied shut with a cord knotted in a particular way"],
                 titles=["The Primer of the Quiet Hand", "{name}'s Ledger", "Sermons for the Wicked (so the cover says)", "The Book of Doors",
                         "Ways Out", "The Cutpurse's Catechism"],
                 dawn="The hooks and crosses of thieves' cant settle into words you can read."),
}
HOME_SCHOOL = {s["home"]: k for k, s in SCHOOLS.items()}
LITERACY = 7          # the stat it takes to read another school's books
FOREIGN_CAP = 2       # how far you can go in a school that isn't your class's
CIRCLE_WORDS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}

# ------------------------------------------------------------------ the arts
# The original class abilities keep their own code (classes.py) but join the schools here.
ORIGINAL = {"firebolt": ("arcane", 1), "ward": ("arcane", 1), "fear": ("arcane", 2),
            "heal": ("divine", 1), "smite": ("divine", 1), "turn": ("divine", 2),
            "bash": ("martial", 1), "guard": ("martial", 1),
            "shoot": ("wild", 1), "track": ("wild", 1),
            "backstab": ("cant", 1), "vanish": ("cant", 1)}

# fx: dmg(base, per level, pierce, undead x, hits, weapon) / stun / weaken / expose / dot / flee / heal / ward / guard /
#     escape / buff / cleanse / reveal / execute
ARTS = {
    # arcane
    "frost": dict(label="Frost Dart", school="arcane", circle=1, cost=2, target=True,
                  desc="A dart of ice that ignores armour and leaves the creature numb and slow.",
                  fx=[("dmg", dict(base=3, per=1, pierce=True)), ("weaken", 1)],
                  say=["A splinter of ice leaps from your fingers and buries itself in {the_c}'s {part}; frost spreads from the wound.",
                       "You flick your hand and a dart of blue ice takes {the_c} in the {part}. It moves more stiffly at once.",
                       "Cold gathers in your palm and flies: {the_c} flinches as rime creeps over its {part}."]),
    "farsight": dict(label="Farsight", school="arcane", circle=2, cost=3, peace_only=True,
                     desc="Send your sight up and out, like a bird, over the land around you.",
                     fx=[("reveal", 3)],
                     say=["You close your eyes and your sight lifts, up past the treetops, until the land lies spread below you.",
                          "The world tilts and falls away; for a long moment you see as a kite sees."]),
    "thunder": dict(label="Thunderclap", school="arcane", circle=3, cost=4, target=True,
                    desc="A clap of thunder at arm's length: damage, and a good chance to stun.",
                    fx=[("dmg", dict(base=5, per=1, pierce=True)), ("stun", 0.55)],
                    say=["You bring your palms together and the air splits with a crack that knocks {the_c} off its feet.",
                         "Thunder answers your gesture, so close that {the_c} reels from it, half-deafened.",
                         "A boom like a falling tree: the shock hammers {the_c}'s {part}."]),
    "blink": dict(label="Blink", school="arcane", circle=3, cost=3, combat_only=True,
                  desc="Fold the distance between here and a few strides away, and step out of the fight.",
                  fx=[("escape", 2)],
                  say=["You speak a word and simply aren't there any more; {the_c} lunges at empty air.",
                       "The world folds like a cloth. You step out of it a stone's throw away, behind {the_c}, unseen."]),
    "lance": dict(label="Searing Lance", school="arcane", circle=4, cost=5, target=True,
                  desc="A spear of white fire that pierces armour and leaves the creature burning.",
                  fx=[("dmg", dict(base=10, per=2, pierce=True)), ("dot", (3, 3, "burns"))],
                  say=["A lance of white fire leaves your hand and drives straight through {the_c}'s {part}. It keeps burning.",
                       "You pull fire out of the air and throw it like a spear. {the_c.cap} is wreathed in flame."]),
    "unmake": dict(label="Unmaking", school="arcane", circle=5, cost=8, target=True,
                   desc="Speak the word that tells a thing it was never there. Terrible damage that nothing can turn aside.",
                   fx=[("dmg", dict(base=18, per=3, pierce=True))],
                   say=["You speak a word that hurts your mouth. Part of {the_c} simply stops being.",
                        "The Unmaking takes hold: {the_c}'s {part} greys, cracks, and comes apart like ash."]),
    # divine
    "bless": dict(label="Blessing", school="divine", circle=1, cost=2, peace_only=True,
                  desc="Ask for a blessing on your road: steadier blows for half a day.",
                  fx=[("buff", ("blessed", 12, 1))],
                  say=["You bow your head and ask. Warmth settles across your shoulders like a hand.",
                       "You trace the old sign and speak the old words, and feel them answered."]),
    "sanctuary": dict(label="Sanctuary", school="divine", circle=2, cost=3,
                      desc="A circle of quiet light that turns blows aside until it breaks.",
                      fx=[("ward", dict(base=6, per=2))],
                      say=["A ring of pale light rises around you, and the air inside it goes very still.",
                           "You call for sanctuary, and something answers: a soft, unbreakable-looking glow."]),
    "purify": dict(label="Purify", school="divine", circle=3, cost=3,
                   desc="Burn away curses, sickness and ill luck, and mend a little.",
                   fx=[("cleanse", None), ("heal", dict(base=5, per=1))],
                   say=["Clean fire runs through you without burning, and whatever clung to you is gone.",
                        "You pray, and feel something sour lift out of you like smoke."]),
    "radiance": dict(label="Radiance", school="divine", circle=4, cost=5, target=True,
                     desc="Blinding holy light: damage that ignores armour, doubled against the dead, and it may dazzle.",
                     fx=[("dmg", dict(base=7, per=2, pierce=True, undead=2)), ("stun", 0.4)],
                     say=["Light pours out of you, white and merciless, and {the_c} recoils from it.",
                          "You raise your hand and the air blazes like noon; {the_c} cries out, blinded."]),
    "miracle": dict(label="Miracle", school="divine", circle=5, cost=8,
                    desc="Ask for everything at once: wounds closed, and a shield of light about you.",
                    fx=[("heal", dict(base=99, per=0)), ("ward", dict(base=10, per=2))],
                    say=["You ask, and you are answered. Every wound closes; light gathers around you like a cloak.",
                         "For a moment you are not alone at all. When it passes, you are whole, and shining."]),
    # martial
    "cleave": dict(label="Cleave", school="martial", circle=2, cost=3, target=True,
                   desc="Put your whole body behind one great blow.",
                   fx=[("dmg", dict(weapon=True, base=3, per=1))],
                   say=["You put everything into one great swing and it bites deep into {the_c}'s {part}.",
                        "Shoulders, hips, feet: you throw the lot behind a single blow, and {the_c} staggers from it."]),
    "rally": dict(label="Second Wind", school="martial", circle=2, cost=2,
                  desc="Grit your teeth, breathe, and find the strength you didn't know you had.",
                  fx=[("heal", dict(base=6, per=1))],
                  say=["You set your jaw and breathe, long and slow, and the ache recedes.",
                       "You find, somewhere under the tiredness, a little more strength."]),
    "disarm": dict(label="Disarm", school="martial", circle=3, cost=3, target=True,
                   desc="A binding strike that ruins its next attacks for the rest of the fight.",
                   fx=[("dmg", dict(weapon=True, base=0, per=0)), ("weaken", 2)],
                   say=["You bind, twist and strike at its {part}; {the_c} won't hit as hard again.",
                        "A drill you've practised a thousand times: you catch {the_c}'s {part} and wrench. It falters."]),
    "warcry": dict(label="War Cry", school="martial", circle=4, cost=3, target=True,
                   desc="A roar that makes beasts think twice. The bold, and the dead, may stand.",
                   fx=[("flee", dict(turns=2, base=0.75, undead=False))],
                   say=["You roar, and {the_c} hesitates.", "Your war cry rolls out over the ground, and {the_c} shrinks from it."],
                   fail=["You roar. {the_c.cap} doesn't care.", "{the_c.cap} holds its ground against your war cry."]),
    "bulwark": dict(label="Bulwark", school="martial", circle=5, cost=5,
                    desc="Become a wall: your guard holds for three blows, and a shield of will soaks the rest.",
                    fx=[("guard", 3), ("ward", dict(base=8, per=2))],
                    say=["You plant your feet and become the kind of thing that isn't moved.",
                         "Every drill, every bruise, every long day in the yard comes together: you are a wall."]),
    # wild
    "snare": dict(label="Snare", school="wild", circle=2, cost=2, target=True,
                  desc="A cord, a loop, a quick throw: it stumbles and loses its next turn.",
                  fx=[("stun", 0.8)],
                  say=["You whip a looped cord around {the_c}'s {part} and yank. It goes down in a tangle.",
                       "A snare from your belt, a quick throw - {the_c} stumbles, caught."],
                  fail=["Your snare falls short, and {the_c} steps over it.", "{the_c.cap} kicks free of your snare."]),
    "poultice": dict(label="Poultice", school="wild", circle=2, cost=2, peace_only=True,
                     desc="Chew the right leaves into a poultice and bind your wounds.",
                     fx=[("heal", dict(base=8, per=1))],
                     say=["You chew a mouthful of leaves to a bitter paste and bind it over your cuts. The sting fades.",
                          "Yarrow, plantain, a strip of cloth: you dress your hurts the way the old foresters taught."]),
    "volley": dict(label="Twin Shot", school="wild", circle=3, cost=3, target=True,
                   desc="Two arrows, loosed so fast they sound like one.",
                   fx=[("dmg", dict(base=3, per=1, hits=2))],
                   say=["Two arrows leave your bow almost together; both find {the_c}.",
                        "You nock, loose, nock, loose - twice into {the_c}'s {part}."]),
    "calm": dict(label="Beast-Speech", school="wild", circle=4, cost=3, target=True,
                 desc="Speak to a beast in the way beasts understand, and send it on its way. Useless on the dead.",
                 fx=[("flee", dict(turns=3, base=0.9, beasts_only=True))],
                 say=["You make yourself small and quiet and speak low. {the_c.cap} listens, and turns away.",
                      "You meet {the_c}'s eye and say, without words, that this is not its fight. It believes you."],
                 fail=["{the_c.cap} doesn't want to hear it.", "Whatever drives {the_c}, it's past listening."]),
    "mark": dict(label="Hunter's Mark", school="wild", circle=5, cost=4, target=True,
                 desc="Find the weak place and put an arrow in it: every blow after lands harder.",
                 fx=[("expose", 3), ("dmg", dict(base=4, per=1))],
                 say=["You see it: the gap, the soft place. Your arrow goes there, and now you know where to strike.",
                      "You mark {the_c}'s weakness with an arrow in the {part}. It can't guard that place now."]),
    # cant
    "trick": dict(label="Dirty Trick", school="cant", circle=2, cost=2, target=True,
                  desc="Sand in the eyes, a kick, a thrown cloak: it loses its next turn.",
                  fx=[("dmg", dict(base=1, per=0)), ("stun", 0.7)],
                  say=["You fling a handful of grit into {the_c}'s eyes and kick it, hard.",
                       "A feint high, a heel low - {the_c} reels, blinking and confused."],
                  fail=["{the_c.cap} sees your trick coming."]),
    "venom": dict(label="Envenom", school="cant", circle=2, cost=2, target=True,
                  desc="A nick from a blade smeared with something nasty. It keeps hurting.",
                  fx=[("dmg", dict(base=1, per=0)), ("dot", (2, 4, "sickens"))],
                  say=["You nick {the_c}'s {part} with a blade you'd rather not lick. It starts to shake.",
                       "A shallow cut with a darkened edge: {the_c} will feel that for a while."]),
    "feint": dict(label="Feint", school="cant", circle=3, cost=3, target=True,
                  desc="Make it guard the wrong place, then strike where its armour isn't.",
                  fx=[("dmg", dict(weapon=True, base=2, per=1, pierce=True))],
                  say=["You show it one thing and do another; your blade slides in under {the_c}'s guard.",
                       "A twitch of the shoulder, a step, and you're inside its reach, cutting at the {part}."]),
    "shadow": dict(label="Shadowstep", school="cant", circle=4, cost=3, combat_only=True,
                   desc="Step into a shadow and out of the fight, every time - and stay hidden for your next strike.",
                   fx=[("escape", 3)],
                   say=["You step sideways into a shadow that shouldn't be deep enough to hide you. {the_c.cap} loses you completely.",
                        "One moment you're there; the next {the_c} is turning in circles."]),
    "deathblow": dict(label="Deathblow", school="cant", circle=5, cost=4, target=True,
                      desc="Against something already badly hurt: the killing stroke. Otherwise a vicious cut.",
                      fx=[("execute", 0.4), ("dmg", dict(weapon=True, base=3, per=1))],
                      say=["You find the place and strike once. It is enough.", "One clean, cold stroke: {the_c} folds."]),
}

for _k, _a in ARTS.items():
    _a.setdefault("say", [])


def school_of(key):
    if key in ARTS:
        return ARTS[key]["school"], ARTS[key]["circle"]
    return ORIGINAL.get(key, (None, 0))


def arts_in(school, circle=None):
    every = [k for k in list(ORIGINAL) + list(ARTS) if school_of(k)[0] == school]
    return [k for k in every if circle is None or school_of(k)[1] == circle]


# ------------------------------------------------------------------ the player
def ensure(p):
    """Give a player (new or from an older save) stats, points and known arts."""
    from . import classes as K
    if not hasattr(p, "stats") or not p.stats:
        p.stats = dict(CLASS_STATS.get(getattr(p, "klass", None), DEFAULT_STATS))
        for _ in range(max(0, p.level - 1) // 3):          # an older save: the growth it would have had
            g = GROWTH_STAT.get(p.klass)
            if g:
                p.stats[g] = min(STAT_MAX, p.stats[g] + 1)
    if not hasattr(p, "points"):
        p.points = max(0, p.level - 1)                      # older saves get the points their levels earned
    if not hasattr(p, "known") or p.known is None:
        s = K.spec(p)
        p.known = list(s["abilities"]) if s else []
    if not hasattr(p, "scribed"):
        p.scribed = set()                                   # book titles already studied
    if not hasattr(p, "crafted"):
        p.crafted = {}                                      # arts made by spellcraft, composing or honing
    if not hasattr(p, "practice"):
        p.practice = {}                                     # uses of each technique, toward honing


def stat(p, k):
    ensure(p)
    return p.stats.get(k, 4)


def word(p, k, rng=None):
    words = STAT_WORDS[k][min(4, (stat(p, k) - 1) // 2)]
    return rng.choice(words) if rng else words[0]


def band(v):
    return min(4, (v - 1) // 2)


def standing(p, k):
    """The word for a stat, with a hint of progress when it's halfway to the next ('sensible, nearly quick-witted')."""
    v = stat(p, k)
    here = STAT_WORDS[k][band(v)][0]
    if v < STAT_MAX and band(v + 1) > band(v):
        return f"{here}, nearly {STAT_WORDS[k][band(v + 1)][0]}"
    return here


def describe_stats(g):
    p, r = g.player, g.narr.rng
    w = [word(p, k, r) for k in STATS]
    return g.narr.pick([f"You are {w[0]}, {w[1]}, {w[2]} and {w[3]}.",
                        f"In body you are {w[0]} and {w[1]}; in mind {w[2]}, and {w[3]}.",
                        f"{cap(w[0])} and {w[1]}, {w[2]}, {w[3]}: that is you, more or less."])


def bonus(p, k):
    """Above an ordinary 5, a stat starts to tell."""
    return max(0, stat(p, k) - 5)


def power(p, school):
    return bonus(p, SCHOOLS[school]["stat"]) if school in SCHOOLS else 0


def own_school(p):
    return HOME_SCHOOL.get(getattr(p, "klass", None))


def literacy_need(p, school):
    if school == own_school(p):
        return 0
    if p.klass == "ranger" and school == "cant":
        return LITERACY - 1          # a ranger is nearly a rogue already
    return LITERACY


def literate(p, school):
    return school == own_school(p) or stat(p, SCHOOLS[school]["stat"]) >= literacy_need(p, school)


def school_cap(p, school):
    if school == own_school(p):
        return 5
    if p.klass == "ranger" and school == "cant":
        return 3
    return FOREIGN_CAP


def innate(p, school, circle):
    """The Cleric's leaning: the weakest spells, without the letters."""
    return p.klass == "cleric" and school == "arcane" and circle == 1


def can_learn(p, key):
    """(True, "") or (False, why)."""
    school, circle = school_of(key)
    if school is None:
        return False, "That isn't something that can be learned."
    if key in p.known:
        return False, "You already know it."
    if innate(p, school, circle):
        return True, ""
    if not literate(p, school):
        return False, "not literate"
    if circle > school_cap(p, school):
        return False, f"That is deeper in the {school} arts than one of your calling can go."
    need = 4 + circle
    if stat(p, SCHOOLS[school]["stat"]) < need:
        return False, "not yet"
    return True, ""


def circle_ok(p, school, circle):
    """Could you work an art of this circle in this school at all?"""
    return literate(p, school) and circle <= school_cap(p, school) and stat(p, SCHOOLS[school]["stat"]) >= 4 + circle


def traits(p):
    """Named traits: the class passive, plus a reading trait for each school you can read."""
    from . import classes as K
    out = []
    s = K.spec(p)
    if s:
        out.append(s["passive"])
    for k, sc in SCHOOLS.items():
        if literate(p, k):
            out.append((sc["trait"], sc["trait_desc"]))
    if p.klass == "cleric" and not literate(p, "arcane"):
        out.append(("Hedge-Lettered", "You can puzzle out the simplest spells: first-circle arcane books and scrolls."))
    return out


def grow(g, k, n=1, why=""):
    """Raise a stat; announce any trait it brings."""
    p = g.player
    before = {s: literate(p, s) for s in SCHOOLS}
    p.stats[k] = min(STAT_MAX, p.stats[k] + n)
    if k == "spirit" and p.stats[k] > 5 and getattr(p, "res_max", 0):
        p.res_max += n
        p.res += n
    msgs = []
    for s, sc in SCHOOLS.items():
        if literate(p, s) and not before[s]:
            msgs.append(f"{sc['dawn']} (New trait: {sc['trait']} - {sc['trait_desc']})")
    return msgs


def near_hint(p, k):
    """What a point in this stat would bring, in words."""
    v = stat(p, k)
    if v >= STAT_MAX:
        return "as far as anyone can go"
    for s, sc in SCHOOLS.items():
        if sc["stat"] == k and not literate(p, s) and literacy_need(p, s) == v + 1:
            return f"one step from reading {sc['books'][0]}s"
    for s, sc in SCHOOLS.items():
        nxt = v + 1 - 4              # a circle needs the stat at 4 + circle
        if sc["stat"] == k and literate(p, s) and 1 <= nxt <= school_cap(p, s):
            return f"would open {CIRCLE_WORDS[nxt]}-circle {sc['art']}s"
    return ""


def improve(g, rest):
    p = g.player
    ensure(p)
    k = next((s for s in STATS if rest and (rest[0] == s or s.startswith(rest[0]))), None)
    if not p.points:
        return g.emit("You have nothing to spend yet. Each new level brings a point to grow with.")
    if k is None:
        opts = "; ".join(f"{s} - you are {standing(p, s)}" + (f" ({near_hint(p, s)})" if near_hint(p, s) else "") for s in STATS)
        return g.emit(f"You have {p.points} point{'s' if p.points > 1 else ''} to spend. Improve what? {opts}.")
    if p.stats[k] >= STAT_MAX:
        return g.emit(f"You are already {word(p, k)}. There's no further to go.")
    p.points -= 1
    was = band(p.stats[k])
    msgs = grow(g, k)
    if band(p.stats[k]) > was:
        g.emit(g.narr.pick([f"You work at it, and it shows: you are {word(p, k, g.narr.rng)} now.",
                            f"Days on the road have changed you. You are {word(p, k, g.narr.rng)}.",
                            f"You feel the difference. You are {word(p, k, g.narr.rng)}."]))
    else:
        nxt = STAT_WORDS[k][band(p.stats[k] + 1)][0] if p.stats[k] < STAT_MAX else None
        g.emit(g.narr.pick([f"You work at it. You are still {word(p, k)}, but you can feel yourself growing {nxt}." if nxt else
                            f"You push yourself further than you thought anyone could go.",
                            f"A step along the way: not yet {nxt}, but closer." if nxt else "You reach the very limit of what a person can be."]))
    for m in msgs:
        g.emit(m)
    if p.points:
        g.emit(f"({p.points} point{'s' if p.points > 1 else ''} left to spend.)")


def on_level(p, level):
    """Called on each new level: a point to spend, and every third level your calling shapes you."""
    ensure(p)
    p.points += 1
    out = [f"(You have a point to spend on growing: 'improve' might, grace, wits or spirit.)"]
    k = GROWTH_STAT.get(p.klass)
    if k and level % 3 == 0 and p.stats[k] < STAT_MAX:
        p.stats[k] += 1
        if k == "spirit" and p.stats[k] > 5:
            p.res_max += 1
        out.insert(0, f"(Your calling shapes you: you are {word(p, k)} now.)")
    return out


# ------------------------------------------------------------------ running an art
def run(g, key, c):
    """Carry out a data-driven art against creature c (or none)."""
    from . import classes as K
    from . import story as S
    p, n, a = g.player, g.narr, ARTS[key]
    school = a["school"]
    ctx = K._ctx(g, c)
    lines, dealt, failed, fought = [], 0, False, c is not None
    ambush = 1
    for kind, arg in a["fx"]:
        if kind == "ambush" and c is not None:
            if (g.combat is not c and mind.intent(c) in ("wander", "stalk", "hold", "flee")) or getattr(p, "hidden", 0) > 0:
                ambush = arg
            p.hidden = 0
    for kind, arg in a["fx"]:
        if kind == "dmg":
            if c is None:
                continue
            for _ in range(arg.get("hits", 1)):
                base = (p.atk if arg.get("weapon") else 0) + arg.get("base", 0) + arg.get("per", 0) * (p.level - 1) + power(p, school) + g.rng.randint(0, 2)
                if arg.get("undead") and c.species["arch"].get("undead"):
                    base *= arg["undead"]
                base *= ambush
                dmg = max(1, base if arg.get("pierce") else base - c.df)
                c.hp -= dmg
                dealt += dmg
        elif kind == "execute":
            if c is not None and c.hp <= c.maxhp * arg and not c.boss:
                dealt += c.hp
                c.hp = 0
        elif kind == "stun":
            if c is not None and c.hp > 0:
                if g.rng.random() < (arg / 2 if c.boss else arg):
                    mind.ensure(c)["stunned"] = True
                elif not any(k == "dmg" for k, _ in a["fx"]):
                    failed = True
        elif kind == "weaken":
            if c is not None:
                c.atk = max(1, c.atk - arg)
        elif kind == "expose":
            if c is not None:
                c.df = max(0, c.df - arg)
        elif kind == "dot":
            if c is not None and c.hp > 0:
                mind.ensure(c)["dot"] = dict(dmg=arg[0] + power(p, school) // 2, turns=arg[1], verb=arg[2])
        elif kind == "flee":
            undead = c.species["arch"].get("undead", False)
            if arg.get("beasts_only") and undead or c.boss:
                failed = True
                continue
            bold = mind.ensure(c)["temper"]["bold"]
            if g.rng.random() < max(0.15, arg["base"] - 0.4 * bold + 0.05 * power(p, school)):
                mind.commit(c, "flee", turns=arg["turns"])
            else:
                failed = True
        elif kind == "heal":
            before = p.hp
            p.hp = min(p.maxhp, p.hp + arg["base"] + arg["per"] * (p.level - 1) + power(p, school))
            lines.append(f"(+{p.hp - before} HP)")
        elif kind == "ward":
            p.ward = max(getattr(p, "ward", 0), arg["base"] + arg["per"] * (p.level - 1) + power(p, school))
            lines.append(f"(absorbs {p.ward})")
        elif kind == "guard":
            p.guard = arg
        elif kind == "buff":
            S.add_buff(g, *arg)
        elif kind == "cleanse":
            gone = [b for b in ("cursed", "queasy", "soaked") if g.buffs.pop(b, None)]
            if gone:
                lines.append("(" + ", ".join(S.BUFF_NAMES[b] for b in gone) + " lifted)")
        elif kind == "reveal":
            from . import secrets as SEC
            seen = SEC.reveal(g, arg + power(p, school) // 2)
            lines.append(f"You see {seen}." if seen else "You see nothing you didn't know already.")
        elif kind == "escape":
            g.combat = None
            p.hidden = arg
            if c is not None:
                m = mind.ensure(c)
                m["support"]["wander"] = max(m["support"].values()) + 0.1
                m["intent"] = "wander"
    said = n.say(n.pick(a.get("fail") or a["say"]) if failed and a.get("fail") else n.pick(a["say"]), ctx)
    if dealt:
        lines.insert(0, f"({dealt} damage)")
    g.emit(" ".join([said] + lines))
    if any(k == "escape" for k, _ in a["fx"]):
        return
    if fought:
        return K.finish_exchange(g, c, dealt)
    if g.combat:
        g.enemy_turn()


def tick(g, c):
    """Lingering harm (burning, poison) at the start of a creature's turn. True if it died."""
    d = mind.ensure(c).get("dot")
    if not d:
        return False
    c.hp -= d["dmg"]
    d["turns"] -= 1
    if d["turns"] <= 0:
        c.mind.pop("dot", None)
    g.emit(f"{cap(g.narr.creature_np(c, True))} {d['verb']}. ({d['dmg']} damage)")
    if c.hp <= 0:
        g.finish_off(c)
        return True
    return False


# ------------------------------------------------------------------ books and scrolls
def make_book(rng, danger, school=None, names=()):
    school = school or rng.choice(list(SCHOOLS))
    sc = SCHOOLS[school]
    circle = max(1, min(5, int(danger // 1.6) + rng.choice([0, 0, 1])))
    noun = rng.choice(sc["books"])
    title = rng.choice(sc["titles"]).format(name=rng.choice(list(names) or ["Aldo"]))
    return dict(kind="book", name=f"{rng.choice(['worn', 'battered', 'heavy', 'small', 'water-stained', 'well-thumbed', 'slim', 'old'])} {noun}",
                value=20 + 18 * circle, facts=dict(school=school, circle=circle, title=title, look=rng.choice(sc["looks"]), noun=noun))


def make_scroll(rng, danger, school=None):
    school = school or rng.choice(["arcane", "arcane", "divine"])
    sc = SCHOOLS[school]
    circle = max(1, min(5, int(danger // 1.6) + rng.choice([0, 1])))
    seal = rng.choice(["sealed with black wax", "tied with a faded ribbon", "written in ink that shimmers when tilted",
                       "rolled tight around a bone rod", "its edges scorched", "stamped with a seal you don't know"])
    return dict(kind="scroll", name=f"{rng.choice(['brittle', 'yellowed', 'tightly rolled', 'crumpled', 'fine vellum'])} {sc['scroll']}",
                value=12 + 10 * circle, facts=dict(school=school, circle=circle, look=seal, noun=sc["scroll"]))


def readable(it):
    return it.kind in ("book", "scroll")


def _settle(g, it):
    """A book's lesson is settled the first time someone who can read it looks inside."""
    f = it.facts
    if f.get("teaches"):
        return f["teaches"]
    p = g.player
    pool = [k for k in arts_in(f["school"]) if school_of(k)[1] <= f["circle"]]
    fresh = [k for k in pool if k not in p.known]
    exact = [k for k in fresh if school_of(k)[1] == f["circle"]]
    f["teaches"] = g.rng.choice(exact or fresh or pool)
    return f["teaches"]


def can_read(p, it):
    f = it.facts
    return literate(p, f["school"]) or innate(p, f["school"], f["circle"])


def need_word(school, circle):
    """How someone has to be, in words, to master an art of this circle."""
    return STAT_WORDS[SCHOOLS[school]["stat"]][min(4, (4 + circle - 1) // 2)][0]


def describe(g, it):
    p, f = g.player, it.facts
    sc = SCHOOLS[f["school"]]
    head = g.narr.pick([f"{cap(article(it.name))}, {f['look']}.", f"You turn over the {it.name}: {f['look']}.",
                        f"It is {article(it.name)}, {f['look']}."])
    if not can_read(p, it):
        blind = {"arcane": "The writing crawls with symbols you can't follow.",
                 "divine": "It is written in the old church tongue, and you can't make it out.",
                 "martial": "It's full of diagrams of people hitting each other, and notes you can't make head or tail of.",
                 "wild": "The notes are a woodsman's shorthand, and mean nothing to you.",
                 "cant": "It reads like nonsense - or like a code."}[f["school"]]
        return f"{head} {blind}  (worth ~{it.value} coins)"
    key = _settle(g, it)
    from . import classes as K
    a = K.ABILITIES[key]
    if it.kind == "scroll":
        return (f"{head} It holds a single working of {a['label']} ({CIRCLE_WORDS[f['circle']]} circle): {a['desc']} "
                f"Reading it aloud will spend it.  (worth ~{it.value} coins)")
    title = g.narr.pick([f"The title reads \"{f['title']}\". ", f"\"{f['title']}\", says the first page. "]) if f.get("title") else ""
    ok, why = can_learn(p, key)
    if key in p.known:
        state = "You know it already."
    elif ok:
        state = "You could learn it, given a few quiet hours. ('read' it to study.)"
    elif why == "not yet":
        state = f"You can follow the words, but not yet the {sc['art']}: it wants someone {need_word(f['school'], school_of(key)[1])}."
    else:
        state = why
    return (f"{head} {title}It teaches {a['label']}, a {CIRCLE_WORDS[school_of(key)[1]]}-circle {sc['name']} {sc['art']}: {a['desc']} "
            f"{state}  (worth ~{it.value} coins)")


MISFIRES = [
    ("frogs", "The words come out wrong. For a moment it rains frogs - small, cold, and very surprised - and then it stops."),
    ("hair", "Something goes sideways in the working. Your hair stands on end and, judging by your reflection in a puddle, has turned a startling blue."),
    ("snow", "The scroll crumbles mid-word, and a small, personal snowstorm empties itself over your head."),
    ("burn", "The scroll flares up in your hands. You drop it, swearing, as it burns to nothing."),
    ("luck", "The working fizzles - but something about the failed spell leaves you feeling oddly lucky."),
]


def misfire(g):
    from . import story as S
    key, text = g.rng.choice(MISFIRES)
    g.emit(text)
    p = g.player
    if key == "snow":
        S.add_buff(g, "soaked", 4)
    elif key == "burn":
        p.hp = max(1, p.hp - 3)
        g.emit("(3 damage)")
    elif key == "luck":
        S.add_buff(g, "lucky", 12)
    if g.combat:
        g.enemy_turn()


def read(g, it, rest=()):
    """Study a book, or read a scroll aloud."""
    from . import classes as K
    p, f = g.player, it.facts
    ensure(p)
    sc = SCHOOLS[f["school"]]
    if not can_read(p, it):
        return g.emit(g.narr.pick([f"You stare at the {it.name} until your eyes ache. It means nothing to you.",
                                   f"You leaf through the {it.name}, but whatever it says, it isn't saying it to you."]))
    key = _settle(g, it)
    a = K.ABILITIES[key]
    if it.kind == "scroll":
        circle = f["circle"]
        stretch = circle > max(school_cap(p, f["school"]), 1 if innate(p, f["school"], circle) else 0) or \
            stat(p, sc["stat"]) < 4 + circle and not innate(p, f["school"], circle)
        target = None
        if a.get("target"):
            t = g.world.tiles[g.pos]
            target = g.combat or (g.find(list(rest), [t.creatures]) if rest else (t.creatures[0] if len(t.creatures) == 1 else None))
            if target is None:
                return g.emit(f"The {it.name} holds {a['label']}, and it needs something to aim at.")
        if a.get("peace_only") and g.combat:
            return g.emit("Not mid-fight.")
        if a.get("combat_only") and not g.combat:
            return g.emit(f"{a['label']} is for the heat of a fight.")
        p.inv.remove(it)
        g.emit(g.narr.pick([f"You unroll the {it.name} and read it aloud. The words leave the page as you speak them.",
                            f"You break the seal and read. The ink fades line by line as the working takes hold."]))
        if stretch and g.rng.random() < 0.5:
            return misfire(g)
        return cast(g, key, target)
    if key in p.known:
        return g.emit(f"You read the {it.name} again. There's nothing in it you don't already know.")
    ok, why = can_learn(p, key)
    if not ok:
        if why == "not yet":
            return g.emit(g.narr.pick([f"You read the {it.name} through twice. You understand it; you just can't do it. Not yet.",
                                       f"The {it.name} asks more of you than you have. Perhaps when you are {need_word(f['school'], school_of(key)[1])}."]))
        return g.emit(why)
    if g.combat:
        return g.emit("This is no time for study.")
    hours = 1 + school_of(key)[1]
    with g.hush():
        g.pass_time(hours * 60)
    p.known.append(key)
    p.scribed.add(f.get("title", it.name))
    g.emit(g.narr.pick([f"You settle down with the {it.name} and lose {hours} hours to it. When you look up, you know {a['label']}.",
                        f"Page by page, {hours} hours pass. Then something clicks: you have {a['label']}.",
                        f"It takes {hours} hours of reading, muttering and trying. But you have it now: {a['label']}."])
           + f" ({a['desc']} Costs {a['cost']} {(K.spec(p) or {}).get('res', 'effort')}.)")


def cast(g, key, target):
    """Use any art, known or not (scrolls), with no cost or checks."""
    from . import classes as K
    if key in ARTS:
        return run(g, key, target)
    return getattr(K, "_" + key)(g, target)


def favoured_school(g):
    """A school this player can read, most often their own, for books found through deeds."""
    p = g.player
    ensure(p)
    mine = [s for s in SCHOOLS if literate(p, s)] or [own_school(p) or "arcane"]
    own = own_school(p)
    return own if own in mine and g.rng.random() < 0.6 else g.rng.choice(mine)


def stock_for(g, m):
    """When a stall is first looked over: often a book you could read, sometimes a scroll."""
    p, w = g.player, g.world
    ensure(p)
    if m.role != "merchant" or m.job not in ("pedlar", "packman", "trader", "huckster", "chandler", "tinker", "spice-trader"):
        return
    danger = max(1, w.tiles[g.pos].danger + 1)
    if g.rng.random() < 0.55:
        m.stock.append(w.make_item(danger + 1, "book", school=favoured_school(g)))
    if g.rng.random() < 0.4 and (literate(p, "arcane") or literate(p, "divine") or p.klass == "cleric"):
        school = "divine" if literate(p, "divine") and (not literate(p, "arcane") or g.rng.random() < 0.5) else "arcane"
        m.stock.append(w.make_item(danger, "scroll", school=school))
