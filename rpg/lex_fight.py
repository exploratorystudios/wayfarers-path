"""The words of a fight: blows by weapon and calling, what each kind of beast does with its body,
how a fight opens, how it turns, what the ground and the weather do to it, and how it ends.

rpg/fight.py chooses among these; it keeps a running record of the fight so a line can know
whether this is the first blow or the tenth, whether a wound is fresh or opened again."""

# --------------------------------------------------------------------- words, scoped by weapon class
RULES = {
    "blade:f_swing": ["swing", "slash", "cut", "sweep"], "axe:f_swing": ["swing", "hew", "chop", "hack"],
    "pierce:f_swing": ["thrust", "stab", "jab", "lunge"], "blunt:f_swing": ["swing", "club", "bring your weapon down", "lash out"],
    "fist:f_swing": ["swing", "punch", "throw a fist"], "f_swing": ["swing", "strike"],
    # you + verb + "the wolf's flank"
    "blade:f_hit": ["slash", "cut", "carve into", "slice across", "open a gash in"],
    "axe:f_hit": ["hew into", "chop into", "split", "hack into", "bite deep into"],
    "pierce:f_hit": ["stab", "drive your point into", "skewer", "stab deep into", "run your point into"],
    "blunt:f_hit": ["smash", "crack", "club", "batter", "pound"],
    "fist:f_hit": ["punch", "hammer a fist into", "strike", "drive a fist into"], "f_hit": ["strike", "hit"],
    # your weapon + verb + "the wolf's flank"
    "blade:f_whit": ["bites into", "opens", "slices across", "lays open"],
    "axe:f_whit": ["bites deep into", "chops into", "hacks into", "splits"],
    "pierce:f_whit": ["punches into", "sinks into", "drives into", "goes deep into"],
    "blunt:f_whit": ["smashes into", "cracks against", "thuds into", "batters"],
    "fist:f_whit": ["thuds into", "cracks against", "slams into"], "f_whit": ["strikes", "lands on"],
    # you + verb + "the wolf's flank", lightly
    "blade:f_graze": ["nick", "score", "scratch", "skim"], "axe:f_graze": ["clip", "nick", "glance off"],
    "pierce:f_graze": ["prick", "graze", "nick"], "blunt:f_graze": ["clip", "glance off", "catch"],
    "fist:f_graze": ["clip", "catch", "glance off"], "f_graze": ["graze", "clip"],
    "blade:f_stroke": ["stroke", "cut", "slash"], "axe:f_stroke": ["chop", "swing", "blow"], "pierce:f_stroke": ["thrust", "lunge", "jab"],
    "blunt:f_stroke": ["blow", "swing", "smash"], "fist:f_stroke": ["punch", "blow", "swing"], "f_stroke": ["blow", "strike"],
    "blade:f_wound": ["cut", "gash", "slash"], "axe:f_wound": ["gash", "wound", "cleft"], "pierce:f_wound": ["wound", "hole", "puncture"],
    "blunt:f_wound": ["bruise", "swelling", "dent"], "fist:f_wound": ["bruise", "swelling"], "f_wound": ["wound"],
    "f_miss_why": ["it twists aside", "you misjudge the distance", "your footing slips", "it's quicker than you", "it shifts at the last moment",
                   "you swing a heartbeat early"],
    "f_evade": ["sidesteps", "ducks under", "leaps clear of", "twists away from", "slips"],
    "f_evade_short": ["dodges", "jerks back", "slips aside", "recoils", "gives ground"],
    "f_dodge": ["twist aside", "jump back", "duck", "get your guard up in time", "throw yourself clear", "sway out of reach"],
    "f_pain": ["flares in", "lances through", "blooms across", "bites into"],
    "f_hurt_reel": ["reel backward", "nearly fall", "see stars", "stagger", "lose your footing for a heartbeat"],
    "f_hurt_adj": ["already bloodied", "wounded", "battered", "aching"],
}

# --------------------------------------------------------------------- your blows
# context: the_c, weapon ("your sword"), part, r_small / r_mid / r_big (the beast's reactions)
BLOW = {
    "miss": ["You {f_swing} at {the_c}, but {f_miss_why}.", "{the_c.cap} {f_evade} your {f_stroke}.",
             "Your {f_stroke} goes wide as {the_c} {f_evade_short}.", "You {f_swing} at its {part} and meet only air.",
             "{weapon.cap} whistles past {the_c}'s {part}.", "You commit to the {f_stroke}, and {the_c} simply isn't there."],
    "graze": ["You {f_graze} {the_c}'s {part}; it {r_small}.", "{weapon.cap} catches {the_c}'s {part}, no more than a scratch.",
              "A glancing {f_stroke} scores {the_c}'s {part}.", "You get a piece of its {part}, though not much of one.",
              "You {f_graze} its {part}, and it {r_small}."],
    "hit": ["You {f_hit} {the_c}'s {part}, and it {r_mid}.", "{weapon.cap} {f_whit} {the_c}'s {part}. It {r_mid}.",
            "You step in and {f_hit} {the_c}'s {part}.", "A clean {f_stroke}: you {f_hit} its {part}, and it {r_mid}.",
            "You find a gap and {f_hit} its {part}. It {r_mid}."],
    "crit": ["You see the opening and take it: {weapon} {f_whit} {the_c}'s {part}, and it {r_big}.",
             "Everything comes together. You {f_hit} {the_c}'s {part} with your whole weight behind it, and it {r_big}.",
             "A perfect {f_stroke}! You {f_hit} its {part}, and it {r_big}.",
             "For one moment it leaves itself open, and {weapon} {f_whit} its {part}. It {r_big}."],
}

# striking a wound you already opened
REOPEN = {
    "hit": ["You find the {f_wound} on its {part} again, and it {r_mid}.", "{weapon.cap} goes into its {part}, right where you hurt it before. It {r_mid}.",
            "You go for the {f_wound} on its {part}, and get it. It {r_mid}."],
    "crit": ["The {f_wound} on its {part} was waiting for you: {weapon} {f_whit} it, and {the_c} {r_big}.",
             "You put everything into its {part}, already hurt, and it {r_big}."],
}
REOPEN_CLS = {
    "blade": ["The cut on its {part} opens wider under your {f_stroke}; it {r_mid}."],
    "axe": ["You chop into the same {part} again, and the gash deepens. It {r_mid}."],
    "pierce": ["You put your point into the wound on its {part} again; it {r_mid}."],
    "blunt": ["You hit the same {part} again, and this time something gives. It {r_mid}."],
    "fist": ["You hammer the same sore {part} again, and it {r_mid}."],
}

# a blow that ends it (the death itself follows)
FINISH = {
    "blade": ["Your last stroke opens its {part}, and that's the end of it.", "{weapon.cap} finds its {part} one final time.",
              "You cut once more, low and hard, across its {part}."],
    "axe": ["You bring {weapon} down on its {part} with everything you have left.", "One last chop to the {part} ends it.",
            "{weapon.cap} bites into its {part}, and this time it doesn't come out clean."],
    "pierce": ["You drive {weapon} deep into its {part} and lean on it until it stops.", "Your point goes into its {part} and stays there.",
               "One last thrust, into the {part}, and you feel it give."],
    "blunt": ["A last crushing blow to its {part}, and something breaks that won't mend.", "{weapon.cap} comes down on its {part} with a sound you'll remember.",
              "You put all your weight behind one more blow to its {part}."],
    "fist": ["You hit it once more, on the {part}, with everything left in you.", "One last punch to the {part}, and it's done."],
}
FINISH_KIND = {
    "undead": ["{weapon.cap} goes through its {part}, and this time the cold comes apart around it.",
               "You strike at the heart of the chill, and feel it break like ice on a pond."],
    "boss": ["You find the opening you've been waiting for all fight, and {weapon} goes into its {part}.",
             "With the last of your strength, you drive {weapon} into its {part}."],
}

# how each calling fights, mixed in with the plain blows
STYLE = {
    "knight": {
        "miss": ["You hold your guard and cut once, carefully, and it isn't there.", "You keep your shield up and {f_swing}, but {the_c} gives ground."],
        "hit": ["You take its rush on your shield and answer with {weapon}, which {f_whit} its {part}.",
                "You drive forward behind your shield and {f_hit} {the_c}'s {part}.", "Shield, step, strike: you {f_hit} its {part} as you were taught."],
        "crit": ["Years of drill take over: a feint high, then {weapon} {f_whit} its {part}, and it {r_big}.",
                 "You batter it off balance with your shield and {f_hit} its {part}. It {r_big}."],
    },
    "ranger": {
        "miss": ["You misjudge it; this one is faster than most of its kind.", "You wait for the shift of its weight, and it doesn't come."],
        "hit": ["You've watched enough of its kind to know where it'll be: {weapon} meets its {part} there.",
                "You read the shift of its weight and {f_hit} its {part}.", "You keep low, as you would stalking, and {f_hit} its {part}."],
        "crit": ["It moves the way its kind always moves, and you're waiting: {weapon} {f_whit} its {part}, and it {r_big}.",
                 "You know exactly where to put {weapon}, and you put it there: its {part}. It {r_big}."],
    },
    "wizard": {
        "miss": ["You swing {weapon} with more hope than skill, and miss.", "Your {f_stroke} is a scholar's, and {the_c} has no trouble avoiding it."],
        "graze": ["You flail and catch its {part}, more by accident than design."],
        "hit": ["It isn't pretty, but {weapon} {f_whit} {the_c}'s {part}.", "You swing more like a scholar than a soldier, and still {f_hit} its {part}."],
        "crit": ["By luck or some half-remembered geometry, {weapon} lands perfectly on its {part}. It {r_big}."],
    },
    "rogue": {
        "miss": ["You feint, and it doesn't fall for it.", "You dart in, but it's already turning to meet you, and you dart out again."],
        "graze": ["You dart in, nick its {part}, and dance out again."],
        "hit": ["You slip inside its reach and {f_hit} its {part} before it knows you're there.", "Low and quick, you {f_hit} the back of its {part}.",
                "You feint left and {f_hit} its {part} from the right."],
        "crit": ["You find the soft place under its {part} and put {weapon} there. It {r_big}.",
                 "You let it overreach, step behind it, and {f_hit} its {part}. It {r_big}."],
    },
    "cleric": {
        "miss": ["Your blow falls wide; you mutter something that isn't quite a prayer."],
        "hit": ["With a muttered word, you {f_hit} {the_c}'s {part}.", "You bring {weapon} down like a verdict on its {part}.",
                "Grim and steady, you {f_hit} its {part}. It {r_mid}."],
        "crit": ["\"Begone,\" you say, and {weapon} {f_whit} its {part}. It {r_big}.",
                 "You strike as if the blow were a blessing, and {weapon} {f_whit} its {part}. It {r_big}."],
    },
}

# what kind of thing it is
KIND = {
    "undead": {
        "miss": ["{weapon.cap} goes through it as if it were smoke, because just then, it is.", "It flickers, and your {f_stroke} cuts only cold air."],
        "hit": ["{weapon.cap} passes through cold, clinging mist, and something in it tears.",
                "You strike its {part}; it's like hitting a winter fog, and still it {r_mid}."],
        "crit": ["{weapon.cap} rips through its {part}, and for a moment it comes apart entirely. It {r_big}."],
    },
    "boss": {
        "miss": ["{the_c.cap} turns your blow aside with contemptuous ease.", "You {f_swing}, and {the_c} is simply not where you aimed."],
        "graze": ["You {f_graze} its {part}. It doesn't seem to notice."],
        "hit": ["You {f_hit} {the_c}'s {part}. It's like striking an old oak.", "{weapon.cap} {f_whit} its {part}, and it {r_mid}, but only a little."],
    },
    "small": {
        "miss": ["It's too small and too quick; your {f_stroke} finds only air.", "You {f_swing} where it was a moment ago."],
    },
    "big": {
        "hit": ["You {f_hit} its {part}; it hardly seems to notice, until it does. It {r_mid}.", "You {f_hit} the great bulk of its {part}, and it {r_mid}."],
    },
}
SMALL = {"crow", "spider", "serpent"}
BIG = {"bear", "stag", "boar"}

# --------------------------------------------------------------------- each beast: how it reacts, how it weakens, how it attacks
# r: small / mid / big reactions to your blows; hurt / fail: how it looks as it weakens
# acts: what it does with each of its weapons (subject: the beast); tools: (its weapon, verbs that agree with it, misses that finish the sentence)
BEASTS = {
    "wolf": dict(
        r_small=["snarls", "yelps", "flinches back"], r_mid=["yelps and gives ground", "staggers, snapping", "lets out a sharp howl"],
        r_big=["howls and nearly goes down", "yelps, its hind legs buckling", "stumbles, badly hurt"],
        hurt=["Blood mats its fur.", "It's favouring one leg now.", "Its breath comes in ragged pants."],
        fail=["It's still snarling, but its legs are shaking.", "It can barely keep its feet now.", "Its head is low and its tail is down."],
        acts={"its teeth": ["lunges and snaps at you", "darts in, going for your legs"], "its jaws": ["leaps for you", "circles and rushes you"]},
        tools=[("its teeth", ["sink into", "tear at", "close on"], ["snap shut on air", "clack together an inch short"]),
               ("its jaws", ["close on", "rip at", "fasten on"], ["snap on nothing", "close a hand's breadth from your {bp}"])]),
    "boar": dict(
        r_small=["grunts", "squeals", "shakes it off"], r_mid=["squeals and wheels away", "staggers, snorting", "grunts and stumbles"],
        r_big=["shrieks and drops to one knee", "squeals and nearly goes over", "reels, bleeding hard"],
        hurt=["Blood runs down its bristles.", "It's snorting blood now.", "It's breathing in heavy grunts."],
        fail=["It's swaying on its short legs.", "Its charges have no weight left in them.", "Its tusks hang low; it can hardly lift its head."],
        acts={"its tusks": ["hooks upward at you", "wheels and rushes you", "charges you head down"], "its shoulder": ["barrels into you", "charges you head down"]},
        tools=[("its tusks", ["rip into", "gouge", "hook into"], ["rip past your {bp}", "gouge the earth beside you"]),
               ("its shoulder", ["slams into", "batters"], ["thuds past you"])]),
    "spider": dict(
        r_small=["hisses", "twitches", "skitters back"], r_mid=["recoils, legs flailing", "shrieks, a thin dry sound", "lurches sideways"],
        r_big=["shrieks and folds half its legs", "spasms, legs jerking", "staggers, dragging a leg"],
        hurt=["Pale ichor oozes from its wounds.", "One of its legs drags now.", "Its eyes have lost some of their glitter."],
        fail=["It's dragging itself on half its legs.", "Its legs keep folding under it.", "It can barely hold itself up."],
        acts={"its fangs": ["rears and stabs down at you", "skitters in and bites"], "a foreleg": ["lashes its forelegs at you", "scuttles at you"]},
        tools=[("its fangs", ["sink into", "stab into", "pierce"], ["stab into the ground where you stood", "click shut on nothing"]),
               ("a foreleg", ["rakes", "hooks into"], ["whips past your face"])]),
    "serpent": dict(
        r_small=["hisses", "recoils", "flicks back"], r_mid=["writhes and recoils", "thrashes, hissing", "rears back, its coils knotting"],
        r_big=["thrashes wildly", "convulses in loops", "rears and nearly falls"],
        hurt=["Its scales are slick with blood.", "Its strikes come a fraction slower.", "It moves in uneven loops now."],
        fail=["It can barely lift its head.", "Its coils are slack.", "It sways, struggling to stay raised."],
        acts={"its fangs": ["strikes at you", "rears and strikes", "coils and lunges"], "its coils": ["lashes out at you", "coils and lunges"]},
        tools=[("its fangs", ["sink into", "punch into", "find"], ["snap shut an inch from your {bp}"]),
               ("its coils", ["whip across", "crush against"], ["slither past your legs"])]),
    "toad": dict(
        r_small=["croaks", "puffs itself up", "barely notices"], r_mid=["deflates with a wet grunt", "lurches back, croaking", "shudders all over"],
        r_big=["bellows and sags", "flops sideways, gasping", "lets out a long, wet groan"],
        hurt=["Milky poison weeps from its wounds.", "Its throat pulses faster now.", "It's breathing in wet gasps."],
        fail=["It squats, gasping, and hardly moves.", "Its great mouth hangs open.", "It can barely lift its own weight."],
        acts={"its tongue": ["flings its tongue at you"], "its weight": ["throws its bulk at you"], "its wide mouth": ["lunges, mouth gaping"]},
        tools=[("its tongue", ["slaps wetly across", "lashes"], ["slaps the mud beside you"]),
               ("its weight", ["slams into", "crushes down on"], ["thumps down where you were"]),
               ("its wide mouth", ["clamps on"], ["gapes on nothing"])]),
    "crow": dict(
        r_small=["squawks", "flaps back", "shrieks"], r_mid=["tumbles in the air", "crashes down, wings beating", "screams and lurches"],
        r_big=["drops like a stone and scrambles up", "spins out of the air", "shrieks and drags a wing"],
        hurt=["Feathers drift down around you.", "One wing drags now.", "Its flight is ragged."],
        fail=["It can barely get off the ground.", "It hops more than it flies now.", "It's down to scrabbling and pecking."],
        acts={"its beak": ["stabs down at you", "dives at you"], "its claws": ["drops on you out of the air", "flaps in your face"]},
        tools=[("its beak", ["stabs", "pecks at", "rips"], ["jabs at nothing"]),
               ("its claws", ["rake", "tear at"], ["rake the air beside your head"])]),
    "stag": dict(
        r_small=["snorts", "shakes its head", "stamps"], r_mid=["bellows and backs off", "staggers, antlers swinging", "rears, bellowing"],
        r_big=["crashes to its knees and heaves up again", "bellows in agony", "stumbles badly"],
        hurt=["Blood darkens its hide.", "It's limping now.", "Its breath comes in great gusts."],
        fail=["Its antlers droop; it can barely hold them up.", "Its legs tremble under it.", "It stands splay-legged, swaying."],
        acts={"its antlers": ["lowers its antlers and drives at you", "sweeps its antlers at you"], "a hoof": ["rears and kicks at you"]},
        tools=[("its antlers", ["rake", "slam into", "gore"], ["sweep past your {bp}"]),
               ("a hoof", ["cracks against", "lands on"], ["thuds into the ground"])]),
    "bear": dict(
        r_small=["grunts", "huffs", "hardly notices"], r_mid=["roars and rears back", "staggers, swinging its head", "lets out a bellow"],
        r_big=["roars and drops to all fours", "lurches, roaring", "bellows, badly hurt"],
        hurt=["Blood darkens its fur.", "It's moving slower now.", "Its breathing is a deep, ragged huffing."],
        fail=["It sways on its feet, head low.", "It can barely lift a paw.", "Its roars have turned to groans."],
        acts={"its claws": ["swipes at you", "rears and comes down on you"], "its jaws": ["lunges, jaws wide"], "a huge paw": ["swipes at you", "bowls into you"]},
        tools=[("its claws", ["rake", "tear across", "open"], ["whistle past your face"]),
               ("its jaws", ["clamp on", "close on"], ["snap shut on air"]),
               ("a huge paw", ["clubs", "slams into"], ["sweeps over your head"])]),
    "goat": dict(
        r_small=["bleats", "skips back", "shakes its head"], r_mid=["bleats and stumbles", "staggers on the stony ground", "rears, bleating"],
        r_big=["crashes over and scrambles up", "screams, a horribly human sound", "nearly loses its footing"],
        hurt=["Blood streaks its hair.", "It's limping.", "It's breathing hard."],
        fail=["Its legs are shaking.", "It can barely stand.", "It sways, horns low."],
        acts={"its horns": ["butts at you", "charges you"], "its hooves": ["rears and slams down at you"]},
        tools=[("its horns", ["crack into", "slam into"], ["crack against rock instead"]),
               ("its hooves", ["batter", "strike"], ["clatter on the stones"])]),
    "wraith": dict(
        r_small=["flickers", "hisses like a cold kettle", "doesn't so much as flinch"],
        r_mid=["shrieks and comes apart for a moment", "wavers like a guttering flame", "lets out a moan that sets your teeth on edge"],
        r_big=["tears half apart and pulls itself back together", "screams, thinning to almost nothing", "unravels at the edges"],
        hurt=["Its edges are fraying.", "It's thinner than it was; you can see the land through it.", "The cold coming off it is weaker now."],
        fail=["It's barely there now, a smear of grey.", "It flickers in and out.", "It hangs together by a thread."],
        acts={"its cold fingers": ["reaches for you", "rakes at you, shrieking", "swoops down at you"], "its chill": ["drifts through you"]},
        tools=[("its cold fingers", ["sink into", "pass through", "close on"], ["pass a hair's breadth from your face"]),
               ("its chill", ["seeps into", "bites into"], ["washes past you, barely touching"])]),
}
BEAST_DEFAULT = "wolf"

# --------------------------------------------------------------------- its blows
# context: the_c, act, tool, toolhit, toolmiss (a whole clause), bp (where it hits you), armour
FOE = {
    "miss": ["{the_c.cap} {act}, but you {f_dodge}.", "{the_c.cap} {act}, and {toolmiss}.", "You {f_dodge} as {the_c} {act}.",
             "You see it coming. {toolmiss.cap}.", "{the_c.cap} {act}; you {f_dodge}, and {toolmiss}."],
    "block": ["{the_c.cap} {act}, but your {armour} takes it.", "{tool.cap} {toolhit} your {armour}, and it holds.",
              "Your {armour} turns it as {the_c} {act}."],
    "block_bare": ["{the_c.cap} {act}, but it's a poor blow, and you shrug it off.", "{the_c.cap} {act}, and you take it on the meat of your arm without much harm."],
    "hit": ["{the_c.cap} {act}, and {tool} {toolhit} your {bp}.", "{the_c.cap} {act}; you're a moment slow, and {tool} {toolhit} your {bp}.",
            "You don't get clear in time: {tool} {toolhit} your {bp}.", "Pain {f_pain} your {bp} as {tool} {toolhit} {bp_it}.",
            "Your guard slips, and {tool} {toolhit} your {bp}."],
    "hard": ["{the_c.cap} {act} with everything it has, and {tool} {toolhit} your {bp}. You {f_hurt_reel}.",
             "A savage blow: {tool} {toolhit} your {bp}, and you {f_hurt_reel}.",
             "{tool.cap} {toolhit} your {bp} so hard your sight goes white for a moment."],
}
FOE_BOSS = {
    "hit": ["{the_c.cap} {act}, and the ground shakes with it; {tool} {toolhit} your {bp}."],
    "hard": ["{the_c.cap} {act}, unhurried and enormous, and {tool} {toolhit} your {bp}. You {f_hurt_reel}."],
}
BODY = ["arm", "shoulder", "ribs", "thigh", "side", "hand", "shin", "forearm", "hip"]

# --------------------------------------------------------------------- the opening beat
OPEN = {
    "brazen": ["{the_c.cap} doesn't back away. It comes to meet you.", "{the_c.cap} sees you coming and seems glad of it.",
               "You close in, and {the_c} holds its ground as if it's been waiting for you."],
    "furtive": ["{the_c.cap} startles, half-turns to slip away, then thinks better of it.", "You come at {the_c}, and for a heartbeat it looks for a way out.",
                "{the_c.cap} shrinks low as you close, watching you sidelong."],
    "eerie": ["{the_c.cap} goes utterly still as you come on, and the air seems to cool.",
              "Something about the way {the_c} watches you is wrong. You raise {weapon} anyway.", "{the_c.cap} makes no sound at all as you close in."],
    "sullen": ["{the_c.cap} turns, slowly and grudgingly, to face you.", "{the_c.cap} gives you a long, resentful look, and braces.",
               "You close in. {the_c.cap} doesn't want this, and it lets you know."],
    "skittish": ["{the_c.cap} flinches as you come, every muscle bunched to bolt.", "{the_c.cap} shies, then wheels to face you, wild-eyed.",
                 "You come on fast, and {the_c} jerks back, startled into a fight."],
    "cunning": ["{the_c.cap} shifts as you close, watching your feet.", "{the_c.cap} lets you come, and you have the uneasy sense it's choosing the ground.",
                "As you close, {the_c} sidesteps, testing you."],
    "undead": ["The air goes cold as you close on {the_c}; your breath smokes.", "{the_c.cap} turns its hollow face toward you, and your skin crawls.",
               "A cold that has nothing to do with the weather comes off {the_c} as you near it."],
    "boss": ["{the_c.cap} turns its full attention on you, and the world narrows to the space between you.",
             "This is what you came for. {the_c.cap} rises to meet you.", "{the_c.cap} regards you for a long moment, unhurried, then comes."],
}
OPEN_STYLE = {
    "knight": ["You set your feet and bring your shield up.", "You settle into the guard you were drilled in."],
    "ranger": ["You watch its weight, not its eyes, and wait for it to tell you where it's going.", "You keep low and light, the way you'd stalk it."],
    "wizard": ["You grip {weapon} and wish, not for the first time, you'd spent less time with books.", "You keep your distance and gather your will."],
    "rogue": ["You loosen your shoulders and stay light on your feet.", "You drift sideways, looking for its blind side."],
    "cleric": ["You murmur a line of prayer and step forward.", "You touch your holy symbol, then raise {weapon}."],
    None: ["You set your feet and raise {weapon}.", "You take a breath and close the distance."],
}

# --------------------------------------------------------------------- the ground and the sky
GROUND = {
    "forest": ["A root catches your heel, and you nearly go down.", "You put a tree between you for a heartbeat, then step out again.",
               "Leaf litter skids under your boots.", "A low branch whips your face as you circle."],
    "marsh": ["The mud sucks at your boots, slowing every step.", "You splash through a pool, and black water fountains up.",
              "The reeds hiss and bend around you both.", "Your foot sinks to the ankle in the bog."],
    "plains": ["The grass whips at your legs as you circle.", "There's nowhere to hide out here; you circle in the open.",
               "Your boot skids on the turf.", "You give ground across the open turf, then take it back."],
    "hills": ["Loose stones skitter away under your feet.", "You fight for the higher ground, one step at a time.",
              "Bracken tangles your boots.", "The slope tilts under you; you keep your balance, just."],
    "peaks": ["Scree slides under your boots, and you nearly lose your footing.", "The thin air burns in your chest.",
              "There's a drop at your back, and you know it.", "Your boot finds ice, and you catch yourself on the rock."],
}
SKY = {
    "rain": ["Rain runs into your eyes; you blink and blink.", "The rain makes {weapon} slick in your grip.", "Rain hammers down on you both."],
    "drizzle": ["Drizzle beads on your face and in your eyes.", "The fine rain makes your grip uncertain."],
    "storm": ["Thunder cracks overhead, and you both flinch.", "Lightning throws your shadows huge across the ground.",
              "The wind tears at you, and the rain comes sideways."],
    "fog": ["{the_c.cap} slides half out of sight in the fog, then back.", "The fog swallows every sound but your breathing.",
            "You lose it in the fog for a heartbeat, and then it's there, too close."],
    "wind": ["The wind snatches at your cloak.", "A gust throws grit in your eyes."],
    "snow": ["Snow flies up around your feet.", "Your breath and its breath smoke in the cold air.", "The snow is churned to grey slush beneath you."],
    "dark": ["In the dark you fight half by sound.", "You can barely see it; you track it by the noise it makes.",
             "The dark makes every shadow look like it."],
    "sun": ["The sun flashes on {weapon}.", "The light is in your eyes; you shift to put it behind you."],
}

# --------------------------------------------------------------------- how you're holding up
WINDED = ["Your arms are starting to burn.", "You're breathing hard now.", "Sweat stings your eyes.", "Your grip on {weapon} is tiring."]
HURT = ["You're hurt, and you can feel yourself slowing.", "Blood is running down your {bp}.", "Every move hurts now."]
DIRE = ["Your vision swims at the edges.", "You can't take much more of this.", "Your legs are shaking under you."]
LOW_POWER = {
    "arcane": ["The power comes thin now; your fingertips ache with it.", "The words are getting harder to hold in your head."],
    "divine": ["Your prayers feel thinner, as if heard from further off.", "You feel your faith stretched thin."],
    "martial": ["Your muscles burn; you haven't much more of that left in you.", "You're running short of wind."],
    "wild": ["The wild in you is quieter now, harder to call.", "You're tiring; the old knacks come slower."],
    "cant": ["You're running short of tricks.", "Your nerve is fraying; you've used up most of your sleights."],
}

# --------------------------------------------------------------------- afterwards
AFTER = {
    "quick": ["It was over almost before it began.", "You've barely broken a sweat.", "Short, sharp work."],
    "clean": ["It never laid a mark on you.", "You come out of it without a scratch.", "Not a mark on you; it can't say the same.",
              "You check yourself over and find nothing worse than mud."],
    "long": ["It's done, at last. You stand there a while, chest heaving.", "You lower {weapon}; your arms are shaking from the long fight.",
             "That went on far longer than you liked."],
    "close": ["You sway on your feet. That was too close.", "You're bleeding, and shaking, and alive.",
              "You let out a breath you didn't know you were holding. Too close."],
    "boss": ["The silence afterwards is enormous.", "For a long moment nothing in the land seems to move.",
             "You stand over it, and slowly understand that it's over."],
    "plain": ["You catch your breath.", "The quiet comes back slowly.", "You wipe {weapon} clean.", "Your heart takes a while to slow."],
}
