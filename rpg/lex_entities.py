"""Vocabulary for creatures, people, items, sites and combat."""

# --------------------------------------------------------------------- creatures
# Each archetype is a body plan; species are generated from it per world.
ARCHETYPES = {
    "wolf": dict(noun="wolf", biomes=["forest", "plains", "hills", "peaks"], covering="fur",
                 colours=["grey", "ash-pale", "black", "rust-brown", "silver-tipped", "dun"],
                 marks=["a torn ear", "a white blaze on its chest", "yellow, unblinking eyes", "ribs showing through its coat", "a muzzle grizzled with age"],
                 parts=["throat", "flank", "shoulder", "foreleg", "muzzle", "haunch"],
                 attacks=["lunges and snaps at", "darts in to bite at", "leaps for", "slashes its fangs across"],
                 idle=["paces at the edge of sight", "watches you, head low", "sniffs the air, hackles rising", "circles slowly, never quite closing"],
                 death=["collapses with a whine and lies still", "staggers, legs folding, and goes down", "gives a last snarl that dies in its throat"],
                 hp=(10, 14), atk=4, df=1),
    "boar": dict(noun="boar", biomes=["forest", "marsh", "plains"], covering="bristles",
                 colours=["black", "mud-brown", "grizzled grey", "red-brown"],
                 marks=["tusks yellow and curved like sickles", "a crest of raised hackles down its spine", "an old spear scar across its shoulder", "small, furious eyes"],
                 parts=["flank", "snout", "shoulder", "back", "foreleg"],
                 attacks=["charges and hooks its tusks at", "barrels into", "rips upward with its tusks at", "gores at"],
                 idle=["roots noisily in the earth", "stands its ground, snorting", "paws the ground, tusks lowered", "grunts and stamps"],
                 death=["crashes onto its side, legs kicking, then still", "squeals once and topples", "sinks to its knees and does not rise"],
                 hp=(14, 18), atk=5, df=2),
    "spider": dict(noun="spider", biomes=["forest", "marsh", "peaks"], covering="chitin",
                   colours=["glossy black", "mottled brown", "bone-pale", "banded yellow", "bruise-purple"],
                   marks=["a cluster of eight glittering eyes", "fangs beaded with venom", "a bloated, pulsing abdomen", "legs bristling with hairs"],
                   parts=["leg", "abdomen", "eye-cluster", "mandibles", "thorax"],
                   attacks=["rears and stabs its fangs at", "skitters forward and bites at", "lashes its forelegs at", "spits a gobbet of venom at"],
                   idle=["hangs motionless in a web strung between trunks", "crouches, legs drawn in", "picks its way over the ground, testing", "waits, eyes glinting"],
                   death=["curls its legs inward and stops moving", "twitches, then folds up like a dead flower", "collapses in a jerking heap"],
                   hp=(8, 12), atk=5, df=1),
    "serpent": dict(noun="serpent", biomes=["marsh", "plains", "hills"], covering="scales",
                    colours=["olive", "copper-banded", "black and yellow", "moss-green", "dusty brown"],
                    marks=["a diamond pattern down its back", "a flickering, forked tongue", "a hood that flares when it is angry", "eyes like chips of amber"],
                    parts=["coils", "head", "neck", "tail", "body"],
                    attacks=["strikes like a whip at", "lashes out at", "coils and lunges at", "snaps its fangs toward"],
                    idle=["lies coiled in a patch of light", "tastes the air with its tongue", "slides slowly through the undergrowth", "rears, swaying"],
                    death=["thrashes in loops and then goes limp", "writhes, slower and slower, then lies still", "uncoils and lies like dropped rope"],
                    hp=(8, 12), atk=4, df=1),
    "toad": dict(noun="toad", biomes=["marsh"], covering="warty hide",
                 colours=["mud-yellow", "bilious green", "liver-spotted", "slick black"],
                 marks=["a throat that swells like a bladder", "glands oozing milky poison", "eyes like gold coins", "a mouth wide enough to swallow a dog"],
                 parts=["throat", "back", "leg", "belly", "head"],
                 attacks=["whips its sticky tongue at", "flings its bulk onto", "snaps its wide mouth at"],
                 idle=["squats in the mud, throat pulsing", "blinks slowly at you", "croaks, a sound like a cracked drum", "sits half-submerged in a pool"],
                 death=["deflates with a long wet sigh", "rolls onto its pale belly", "sags into the mud and does not move"],
                 hp=(12, 16), atk=4, df=1),
    "crow": dict(noun="crow", biomes=["plains", "hills", "marsh", "forest"], covering="feathers",
                 colours=["oil-black", "grey-hooded", "blue-black", "ragged black"],
                 marks=["a beak like a pick", "one milky eye", "a sheen like spilled ink", "a tuft of white at its throat"],
                 parts=["wing", "breast", "head", "tail"],
                 attacks=["dives and rakes its claws at", "stabs its beak at", "beats its wings in the face of"],
                 idle=["perches nearby, cocking its head", "hops along the ground, watching", "croaks a harsh complaint", "circles overhead"],
                 death=["drops in a burst of feathers", "flaps once and falls", "tumbles to the ground in a black heap"],
                 hp=(6, 9), atk=3, df=0),
    "stag": dict(noun="stag", biomes=["forest", "hills", "plains"], covering="hide",
                 colours=["red", "fallow-spotted", "pale grey", "dark brown"],
                 marks=["a crown of many-pointed antlers", "a heavy, maned neck", "a white rump", "an antler broken short"],
                 parts=["neck", "flank", "chest", "shoulder", "leg"],
                 attacks=["lowers its antlers and drives at", "rears and kicks at", "sweeps its antlers at"],
                 idle=["stands proud, watching you", "bellows a challenge", "scrapes its antlers against a tree", "grazes, wary"],
                 death=["crashes down, antlers ploughing the earth", "staggers, then falls heavily", "sinks down with a last long breath"],
                 hp=(14, 18), atk=5, df=1),
    "bear": dict(noun="bear", biomes=["forest", "hills", "peaks"], covering="shaggy fur",
                 colours=["brown", "black", "grizzled", "honey-coloured"],
                 marks=["claws as long as fingers", "a massive hump of shoulder", "a scar pulling one lip into a sneer", "small, clever eyes"],
                 parts=["shoulder", "chest", "head", "forearm", "flank"],
                 attacks=["swipes a huge paw at", "rears and mauls", "lunges, jaws wide, at", "bowls into"],
                 idle=["sits back on its haunches, sniffing", "tears at a rotten log for grubs", "swings its head, huffing", "rises onto its hind legs"],
                 death=["topples like a felled tree", "groans and slumps forward", "rolls onto its side with a final huff"],
                 hp=(22, 28), atk=7, df=2),
    "goat": dict(noun="goat", biomes=["peaks", "hills"], covering="shaggy hair",
                 colours=["white", "piebald", "dirty cream", "black"],
                 marks=["horns curled back in thick ridges", "a long, matted beard", "slotted yellow eyes", "a broken horn"],
                 parts=["horn", "flank", "neck", "leg"],
                 attacks=["butts its horns into", "charges at", "rears and slams down at"],
                 idle=["balances on an impossible ledge", "chews and stares", "bleats, an oddly human sound", "scrapes at the rock"],
                 death=["tumbles onto its side", "bleats once and is still", "slides down the rocks, limp"],
                 hp=(10, 13), atk=4, df=1),
    "wraith": dict(noun="wraith", biomes=["marsh", "plains", "peaks"], covering="tattered shroud",
                   colours=["grey", "pallid", "translucent", "smoke-dark"],
                   marks=["a face that is mostly hollows", "fingers long as knitting needles", "a cold that spreads from it like spilled water", "a voice like wind in a chimney"],
                   parts=["shroud", "hollow chest", "face", "trailing form"],
                   attacks=["reaches cold fingers into", "drifts through", "shrieks and rakes at"],
                   idle=["drifts a hand's breadth above the ground", "turns its hollow face toward you", "flickers, there and then not there", "murmurs words you almost understand"],
                   death=["tears apart like mist in the wind", "lets out a fading sigh and dissolves", "unravels into nothing"],
                   hp=(10, 14), atk=5, df=2, undead=True),
}

SPECIES_PREFIX = {
    "forest": ["thicket", "briar", "wood", "moss", "thorn"],
    "marsh": ["bog", "mire", "fen", "reed", "silt"],
    "plains": ["heath", "barrow", "grass", "dust"],
    "hills": ["tor", "stone", "scree", "ridge"],
    "peaks": ["crag", "frost", "cliff", "storm"],
}
SPECIES_TRAIT = ["red", "white", "black", "grey", "pale", "scar", "iron", "long", "hook", "knife", "ash", "blood"]
SPECIES_PART_WORD = {"wolf": ["fang", "back", "mane"], "boar": ["tusk", "back", "snout"], "spider": ["leg", "eye", "back"],
                     "serpent": ["back", "fang", "throat"], "toad": ["back", "throat", "eye"], "crow": ["wing", "beak", "eye"],
                     "stag": ["horn", "back", "flank"], "bear": ["claw", "back", "pelt"], "goat": ["horn", "beard", "hoof"],
                     "wraith": ["eye", "hand", "shroud"]}
SIZES = ["small", "lean", "rangy", "hulking", "large", "massive", "wiry", "heavy-set"]
INDIVIDUAL = ["scarred", "limping", "young", "old", "gaunt", "huge", "battle-torn", "sleek", "mangy", "restless"]

CREATURE_RULES = {
    "presence": ["{a_creature.cap} {idle} {where_c}.", "{where_c.cap}, {a_creature} {idle}.",
                 "You are not alone: {a_creature} {idle}.", "{a_creature.cap} is here. It {idle}."],
    "where_c": ["nearby", "a short way off", "close at hand", "not far from you", "just ahead"],
    "aggro_line": ["{the_creature.cap} catches your scent and comes for you!", "{the_creature.cap} attacks without warning!",
                   "With a sudden rush, {the_creature} is upon you!", "{the_creature.cap} decides you are prey."],
}

# --------------------------------------------------------------------- people
GIVEN = ["Aldric", "Bryn", "Cathal", "Dunstan", "Edda", "Fen", "Gwyn", "Hilde", "Isolde", "Jory", "Kester", "Linnet",
         "Maud", "Nell", "Osric", "Pell", "Rowan", "Sabine", "Tobin", "Una", "Wat", "Yselde", "Ebba", "Corwen",
         "Agnes", "Hob", "Merrick", "Tamsin", "Godric", "Ilse", "Ansel", "Briony", "Ceri", "Dagny", "Emrys", "Ottilie"]
SURNAME_PRE = ["Ash", "Black", "Mill", "Thatch", "Wood", "Brook", "Hay", "Stone", "Fletch", "Cope", "Weld", "Tan", "Hart", "Marsh"]
SURNAME_SUF = ["er", "well", "wright", "ward", "ley", "ford", "by", "man", "smith", "ing", "croft", "dale"]

OCCUPATIONS = {
    "elder": ["village elder", "elder", "village head", "headman", "headwoman"],
    "merchant": ["pedlar", "trader", "chandler", "tinker", "huckster"],
    "folk": ["shepherd", "eel-catcher", "charcoal-burner", "thatcher", "midwife", "smith", "brewer", "weaver", "miller", "swineherd", "hedge-witch", "ferryman", "woodcutter", "beekeeper"],
}
AGE = ["young", "youngish", "middle-aged", "grizzled", "elderly", "aged", "weathered"]
BUILD = ["stooped", "broad-shouldered", "wiry", "stout", "gaunt", "tall", "short", "round-bellied", "bony", "sturdy"]
HAIR = ["hair the colour of straw", "a shaved head", "grey braids", "a wild black mane", "thinning red hair", "a cloud of white hair",
        "close-cropped brown hair", "a long plait coiled at the crown", "hair hidden under a linen coif"]
CLOTHES = ["a patched woollen tunic", "a leather apron scorched in places", "a faded blue kirtle", "a sheepskin jerkin",
           "a mud-stained smock", "a fine but threadbare coat", "layers of undyed wool", "a cloak pinned with a bone brooch"]
MARK = ["a missing front tooth", "ink-stained fingers", "a burn scar on one forearm", "startlingly pale eyes", "a nose broken more than once",
        "a constant, nervous smile", "a hacking cough", "a voice much deeper than expected", "hands cracked from work", "a squint"]
DEMEANOUR = ["warm", "suspicious", "nervous", "gruff", "cheerful", "melancholy", "shrewd", "dreamy"]

NPC_RULES = {
    "npc_presence": ["{name}, {a_desc}, is here, {doing}.", "{name} the {job} is here, {doing}.",
                     "{a_desc.cap} - {name}, the {job} - is here, {doing}.", "Here is {name}, {doing}.",
                     "You see {name}, {a_desc}, {doing}."],
    "npc_presence_anon": ["{a_desc.cap} is here, {doing}.", "There's {a_desc} here, {doing}.",
                          "You see {a_desc}, {doing}.", "Nearby, {a_desc} is {doing}."],
    "npc_intro": ["\"I'm {name}, {job} hereabouts.\"", "\"Name's {name}.\"", "\"{name},\" {he} offers, tapping {his} chest.",
                  "\"Folk call me {name}.\"", "\"{name}. The {job} here, for my sins.\"", "\"I'm {name}. Pleased, I'm sure.\""],
    "doing": {
        "elder": ["leaning on a carved staff", "watching the road with tired eyes", "sitting on a bench outside the largest house"],
        "merchant": ["sitting beside a pack heaped with goods", "arranging wares on a blanket", "counting coins with quick fingers"],
        "elder_dark": ["sitting up late beside a banked fire", "standing in a lit doorway", "walking the lanes with a lantern"],
        "merchant_dark": ["packing wares away by lamplight", "dozing beside a pack of goods", "counting the day's coins by a candle"],
        "folk_dark": ["sitting in a doorway with a pipe", "heading home with a lantern", "warming {his} hands at a brazier", "awake late, and curious about you"],
        "folk": ["going about {his} work", "mending something in {his} lap", "resting from {his} labours", "chatting idly with no one in particular", "eyeing you with curiosity"],
    },
    "warm:greet": ["\"Well met, stranger! Sit, rest your feet.\"", "\"A new face! The road's been kind to bring you.\"", "\"Welcome, welcome. You look like you've walked a long way.\""],
    "suspicious:greet": ["\"What do you want?\"", "\"I don't know you. Say your business.\"", "\"Strangers bring trouble, in my experience.\""],
    "nervous:greet": ["\"Oh! You startled me. Sorry - you startled me.\"", "\"Is - is something wrong?\"", "\"Keep your voice down, if you would.\""],
    "gruff:greet": ["\"Hm.\"", "\"If you're going to talk, talk.\"", "\"Busy. Make it quick.\""],
    "cheerful:greet": ["\"Hello there! Grand day for it, whatever it is.\"", "\"Ha! Another traveller. Come, have news for me?\"", "\"There's a smile I haven't seen before!\""],
    "melancholy:greet": ["\"Ah. Another day, another face.\"", "\"Welcome, I suppose. Not that there's much here.\"", "\"You should have come in better times.\""],
    "shrewd:greet": ["\"A traveller. And what might you be worth to me, I wonder?\"", "\"Information has a price, friend. Usually.\"", "\"You've a look about you. Adventurer?\""],
    "dreamy:greet": ["\"Did you see the clouds this morning? Like whales.\"", "\"Oh - hello. I was somewhere else.\"", "\"The wind told me someone would come.\""],
    "rumour_frame": ["\"{rumour}\"", "\"I'll tell you this much: {rumour}\"", "\"They say {rumour}\"", "\"Mark me - {rumour}\"", "\"Word is, {rumour}\""],
}

# --------------------------------------------------------------------- items
WEAPONS = {
    "sword": dict(cls="blade", dmg=4, names=["sword", "shortsword", "broadsword", "falchion"]),
    "axe": dict(cls="axe", dmg=5, names=["axe", "hand-axe", "bearded axe", "hatchet"]),
    "spear": dict(cls="pierce", dmg=4, names=["spear", "boar-spear", "javelin", "pike"]),
    "mace": dict(cls="blunt", dmg=4, names=["mace", "cudgel", "flail", "war-hammer", "club"]),
    "dagger": dict(cls="pierce", dmg=2, names=["dagger", "knife", "dirk", "seax"]),
    "staff": dict(cls="blunt", dmg=3, names=["quarterstaff", "staff", "shod staff"]),
}
MATERIALS = {
    # name: (damage bonus, value multiplier, nouns it suits)
    "bronze": (0, 1.0), "iron": (1, 1.2), "steel": (2, 2.0), "bone": (0, 0.6), "flint": (-1, 0.4),
    "black iron": (2, 2.2), "star-metal": (3, 4.0), "oak": (0, 0.5), "blackthorn": (1, 0.9), "copper": (-1, 0.7),
}
WOOD_ONLY = {"staff", "mace"}
QUALITY = [("rusted", -1, 0.5), ("pitted", -1, 0.6), ("notched", 0, 0.8), ("plain", 0, 1.0), ("serviceable", 0, 1.0),
           ("well-made", 1, 1.5), ("fine", 1, 1.8), ("masterwork", 2, 3.0)]
ARMOUR = {
    "jerkin": dict(df=1, names=["leather jerkin", "padded gambeson", "quilted coat"]),
    "mail": dict(df=2, names=["mail shirt", "byrnie", "coat of rings"]),
    "scale": dict(df=3, names=["scale hauberk", "lamellar coat", "brigandine"]),
}
ITEM_DETAIL = {
    "blade": ["The edge {edge_state}.", "A fuller runs down the blade, {fuller_detail}.", "The crossguard is {guard_detail}."],
    "axe": ["The head {edge_state}.", "The haft is {haft_detail}.", "The beard of the blade is {guard_detail}."],
    "pierce": ["The point {edge_state}.", "The shaft is {haft_detail}.", "Just below the point is {guard_detail}."],
    "blunt": ["The striking end {blunt_state}.", "The haft is {haft_detail}.", "Near the grip it is {guard_detail}."],
    "dagger": ["The blade {edge_state}.", "The grip is {haft_detail}.", "The guard is {guard_detail}."],
    "staff": ["The ends are {staff_end}.", "The wood is {haft_detail}.", "At its midpoint the staff is {guard_detail}."],
}
ITEM_RULES = {
    "staff_end": ["shod with iron caps", "worn round and smooth", "blackened as if fire-hardened", "bound with copper rings"],
    "edge_state": ["is keen enough to shave with", "has been honed so often it has narrowed", "is nicked in several places", "is dull and needs a whetstone", "holds a faint blue sheen"],
    "blunt_state": ["is studded with iron knobs", "is dark with old stains", "is dented from heavy use", "is shaped like a clenched fist", "is bound with hammered bands"],
    "fuller_detail": ["etched with a running pattern of hounds", "filled with old blood-rust", "inscribed with letters you cannot read", "polished bright"],
    "guard_detail": ["plain and functional", "bound with a strip of red cloth", "shaped like a pair of spread wings", "wound with copper wire", "carved with a tiny grinning face", "decorated with a ring of punched dots"],
    "haft_detail": ["wrapped in sweat-darkened leather", "smooth with long handling", "carved with notches - a tally of something", "split and bound with twine", "stained almost black"],
    "history": ["A maker's mark near the {grip} shows {maker_mark}.", "Someone has scratched a name - {given} - into the {grip}.",
                "It looks like it has seen {wars}.", "It smells faintly of {item_smell}.", "There is a story in it, if only it could tell it.",
                "Whoever owned it before took good care of it.", "It has clearly passed through many hands."],
    "grip": ["grip", "hilt", "handle", "base"],
    "maker_mark": ["a stylised hammer", "a three-legged bird", "an anvil inside a ring", "a crescent moon", "a running fox"],
    "wars": ["more than one war", "hard use in a border feud", "a great deal of honest work", "very little use at all"],
    "item_smell": ["woodsmoke", "old blood", "oil and leather", "the sea, somehow", "lavender"],
    "armour_detail": ["It is {armour_state}.", "The lining is {lining}.", "Someone has {armour_mark}."],
    "armour_state": ["patched in several places", "stiff with age but sound", "well oiled and supple", "stained at the collar", "lighter than it looks"],
    "lining": ["faded red wool", "rough linen", "sheepskin, worn smooth", "stained with old sweat"],
    "armour_mark": ["painted a faded sun on the breast", "stitched a charm into the hem", "carved initials in the collar", "repaired a gash over the ribs with care"],
}

HERB_PRE = ["bitter", "maiden", "blood", "wolf", "moon", "crow", "self", "heart", "fever", "elf", "all", "sorrow", "marsh"]
HERB_SUF = ["wort", "root", "bane", "leaf", "heal", "foot", "bloom", "thistle", "moss", "weed"]
HERB_LOOK = ["spiky grey-green leaves", "tiny star-shaped white flowers", "a fat, knobbled root", "leaves furred like a mouse's ear",
             "a sticky purple stem", "frilled leaves that smell of aniseed", "berries like drops of wax"]
POTION_COLOUR = ["amber", "cloudy green", "blood-red", "milky blue", "near-black", "honey-gold", "violet", "water-clear"]
POTION_SMELL = ["pine resin", "burnt sugar", "pond water", "cloves", "something rotten", "mint", "copper", "elderflower"]
FOOD = [("heel of rye bread", 3), ("strip of smoked eel", 4), ("wedge of hard cheese", 4), ("handful of dried apples", 3),
        ("cold mutton pie", 6), ("pot of honey", 5), ("twist of salted pork", 5), ("oatcake", 3)]
TRINKETS = ["locket", "ring", "brooch", "comb", "figurine", "amulet", "dice set", "hand mirror", "bead necklace", "carved whistle"]
TRINKET_MAT = ["silver", "tarnished silver", "jet", "amber", "bone", "gilt bronze", "carved antler", "blue glass", "pewter"]
TRINKET_DETAIL = ["containing a lock of red hair", "engraved with a pair of clasped hands", "set with a tiny garnet", "worn smooth by nervous fingers",
                  "shaped like a curled-up hare", "with a name half-rubbed away", "inscribed: 'come home'", "with a crack mended in gold"]

# --------------------------------------------------------------------- sites
SITE_RULES = {
    # village
    "village_line": ["The {size} of {name} {sits} here: {material} houses roofed with {roof}{around}.",
                     "{name} is here, a {size} of {material} cottages under {roof}{around}.",
                     "You have come to {name}, where {material} houses huddle beneath {roof}.",
                     "Smoke rises from {name}, a {size} of {material} houses under {roof}."],
    "sits": ["huddles", "sits", "sprawls", "clusters"],
    "village_centre": ["At its heart stands {centre}.", "The houses gather around {centre}.", "In the middle of it all is {centre}."],
    "village_economy": ["The place lives by {economy}, by the look of it.", "Signs of {economy} are everywhere.", "{economy.cap} is clearly the trade here.", "Everything you see speaks of {economy}."],
    "village_mood_busy": ["People bustle between the houses.", "There is noise and life everywhere: children, dogs, hammering.", "The lanes are busy with folk going about their day."],
    "village_mood_wary": ["Doors close as you pass, and faces watch from shutters.", "People eye you with frank suspicion.", "Conversations stop when you come near."],
    "village_mood_sleepy": ["Nothing much seems to happen here, and no one minds.", "A dog sleeps in the lane; no one moves it.", "It is quiet, almost drowsy."],
    "village_mood_mournful": ["A black ribbon hangs on several doors.", "The few people about walk with their heads down.", "There is grief here, thick as smoke."],
    "night_village": ["Lamplight glows behind a few shutters.", "Most of the windows are dark.", "A dog barks somewhere, then thinks better of it."],
    # ruin
    "ruin_line": ["The {state} shell of {a_purpose} rises here, built of {stone}.",
                  "Here stand the remains of {a_purpose} - {stone}, {state}, {overgrown}.",
                  "{a_purpose.cap} once stood here. Now it is {state}, its {stone} {overgrown}.",
                  "You come upon a ruin: {a_purpose}, {state} and {overgrown}."],
    "ruin_detail": ["Above a fallen doorway, {carving} has been carved.", "Inside, {interior}.", "Its walls still bear traces of {carving}.", "The stones are marked with {carving}, weathered almost smooth."],
    # shrine
    "shrine_line": ["{a_form.cap} stands here, a shrine to {spirit}, {domain}.", "Here is a shrine: {a_form}, raised to {spirit}, {domain}.",
                    "{a_form.cap} marks a holy place. Locals honour {spirit} here, {domain}."],
    "shrine_offer": ["{offerings} have been left at its foot.", "Around it lie {offerings}.", "The faithful have left {offerings}."],
    # camp
    "camp_line": ["Someone camped here not long ago: {camp_detail}.", "This was a camp once - {camp_detail}.", "You find the remains of a camp: {camp_detail}."],
    "camp_detail": ["a ring of blackened stones holding cold ash", "a torn lean-to and scattered bones", "a firepit, still faintly warm", "a trampled hollow and a broken pot"],
}
VILLAGE = dict(size=["hamlet", "village", "huddle", "steading"],
               material=["cob", "timber-framed", "fieldstone", "wattle-and-daub", "flint"],
               roof=["thatch", "slate", "turf", "split shingles", "reed thatch"],
               around=["", ", ringed by a ditch and a thorn hedge", ", with fields stretching away from it", ", fenced by a ragged palisade", ", strung along a muddy lane"],
               centre=["a deep stone well", "a moot-stone worn smooth by generations of hands", "a great spreading oak", "a timber hall with carved doorposts", "a little shrine with a guttering lamp"],
               economy=["sheep-farming", "eel-fishing", "charcoal-burning", "peat-cutting", "brewing", "pig-keeping", "bee-keeping", "weaving"],
               mood=["busy", "wary", "sleepy", "mournful"])
RUIN = dict(purpose=["watchtower", "chapel", "manor house", "keep", "granary", "temple", "toll-house", "monastery", "hall"],
            stone=["grey stone", "red sandstone", "knapped flint", "dressed granite", "pale limestone", "old brick"],
            state=["roofless", "half-collapsed", "sunk to its windows in earth", "fire-blackened", "toppled"],
            overgrown=["choked with ivy", "furred with moss", "thick with nettles", "sprouting elder saplings", "half-buried in brambles"],
            carving=["a crowned serpent", "a weeping face", "a row of figures holding hands", "a sun with a hollow centre", "runes no one reads any more"],
            interior=["a fallen staircase climbs to nowhere", "rubble covers the floor knee-deep", "a hearth stands open to the sky", "rainwater pools on cracked flagstones"])
SHRINE = dict(form=["cairn", "standing stone", "carved post", "well-head", "stone niche", "weathered statue"],
              spirit_pre=["Old", "Mother", "Grey", "Lady", "Father", "Green", "Hollow"],
              spirit_name=["Hesk", "Annet", "Brigga", "Thurl", "Wenna", "Corm", "Ysil", "Maddoc"],
              domain=["keeper of crossings", "who watches over lost things", "lord of the winter dark", "who brings the rain", "mother of the hunt", "who guards the dead"],
              offerings=["Faded ribbons", "Coins and buttons", "Small bones", "Withered flowers", "Bundles of herbs", "Tiny clay figures"])

RELIC_NOUN = ["crown", "chalice", "horn", "mirror", "lantern", "sceptre", "seal", "torc", "reliquary", "harp"]
RELIC_ADJ = ["Ember", "Drowned", "Weeping", "Moonsilver", "Thornbound", "Sunken", "Hollow", "Ashen", "Wending", "Gloaming"]

# --------------------------------------------------------------------- combat
COMBAT_RULES = {
    # player attacks: ctx weapon (noun phrase incl. 'your'), target ('the boar'), part, cls-scoped verbs
    "blade:swing": ["swing", "slash", "cut", "sweep"], "blade:hitverb": ["slash", "carve", "open a gash in", "cut deep into", "slice across"],
    "axe:swing": ["swing", "hew", "chop", "bring down"], "axe:hitverb": ["bury your blade in", "hew into", "chop into", "split"],
    "pierce:swing": ["thrust", "stab", "jab", "lunge"], "pierce:hitverb": ["drive your point into", "stab deep into", "skewer", "punch through"],
    "blunt:swing": ["swing", "smash", "club", "bring down"], "blunt:hitverb": ["smash into", "crack against", "pound", "slam into"],
    "fist:swing": ["swing", "punch", "throw a fist"], "fist:hitverb": ["punch", "hammer your fist into", "strike"],
    "miss": ["You {swing} {weapon} at {target}, but {miss_why}.", "{target.cap} {evade} your {attack_noun}.",
             "Your {attack_noun} goes wide as {target} {evade_short}.", "You {swing} - and meet only air."],
    "miss_why": ["it twists aside", "you misjudge the distance", "your footing slips", "it is quicker than you", "the blow glances off harmlessly"],
    "evade": ["sidesteps", "ducks under", "leaps clear of", "twists away from", "weathers"],
    "evade_short": ["dodges", "jerks back", "slips aside", "recoils"],
    "attack_noun": ["blow", "strike", "attack", "swing", "stroke"],
    "graze": ["You {swing} and catch {target} on the {part}, a shallow wound.", "{weapon.cap} grazes {target}'s {part}.",
              "You nick {target}'s {part}; it {react_small}.", "A glancing blow scores {target}'s {part}."],
    "hit": ["You {hitverb} {target}'s {part}. It {react}.", "{weapon.cap} finds {target}'s {part}, and it {react}.",
            "A solid strike! You {hitverb} {target}'s {part}.", "You step in and {hitverb} {target}'s {part}; it {react}."],
    "crit": ["A perfect strike! You {hitverb} {target}'s {part} with all your weight behind it.",
             "You see the opening and take it, and {weapon} lands squarely on {target}'s {part}. It {react_big}.",
             "Everything comes together: you {hitverb} {target}'s {part}, and it {react_big}."],
    "react_small": ["flinches", "snarls", "barely notices", "hisses"],
    "react": ["reels", "staggers back", "howls", "lurches sideways", "shudders"],
    "react_big": ["is nearly knocked down", "shrieks in agony", "stumbles, badly hurt", "lets out a terrible cry"],
    # enemy attacks: ctx attacker, attackverb
    "enemy_miss": ["{attacker.cap} {attackverb} you, but you {dodge}.", "{attacker.cap} {attackverb} you - and misses by a hair.",
                   "You {dodge} as {attacker} {attackverb} you."],
    "dodge": ["twist aside", "jump back", "duck", "get your guard up in time", "throw yourself clear"],
    "enemy_block": ["{attacker.cap} {attackverb} you, but your {armour} turns the blow.", "Your {armour} takes the force as {attacker} {attackverb} you."],
    "enemy_hit": ["{attacker.cap} {attackverb} you, and pain {pain} your {bodypart}.", "{attacker.cap} {attackverb} you and connects with your {bodypart}.",
                  "You are too slow - {attacker} {attackverb} you, striking your {bodypart}."],
    "enemy_hard": ["{attacker.cap} {attackverb} you with terrible force, and your {bodypart} {hurt_bad}!", "A savage blow: {attacker} {attackverb} you, and you {hurt_reel}."],
    "pain": ["flares in", "lances through", "blooms across", "bites into"],
    "bodypart": ["arm", "shoulder", "ribs", "thigh", "side", "hand", "shin"],
    "hurt_bad": ["explodes with pain", "goes numb", "runs with blood"],
    "hurt_reel": ["reel backward", "nearly fall", "see stars"],
    "flee_ok": ["You break away and run, not looking back.", "You turn and flee, heart pounding.", "You scramble away and put distance between you."],
    "flee_fail": ["You try to break away, but {attacker} cuts you off!", "There is no escape - {attacker} is too close."],
}
