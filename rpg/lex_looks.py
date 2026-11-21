"""Looking at, climbing and searching landmarks: wording that belongs to each kind of place.

The old examine text gave every landmark the same three beats in one of four frames, so after a few
looks you stopped reading and started recognising slots. Here each kind of landmark has its own things
to notice (SIG), each family of landmark its own textures (FOCUS), and the frames vary in length, order
and what leads: a detail, a texture, the weather, your own movement. A second look moves on to
something new instead of restating the first.

Lines here make no claims about weather, season or time of day (those come from the landmark's
"moment" lines), so they can't contradict the scene.
"""

# what a family of landmark feels like close to: textures, small life, the marks of use
FOCUS = {
    "stone": [
        "Lichen has mapped the {noun} in grey-green and rust.",
        "Put a palm to the {noun} and it is colder than the air.",
        "Rain has worn shallow channels down the {noun}, smooth as the inside of a shell.",
        "There are cup-shaped hollows in the {noun}, too regular to be weather's work.",
        "The rock of the {noun} sparkles faintly where it has broken fresh.",
        "Moss has the shady side of the {noun}; the other side is bare and pale.",
        "Someone has wedged a coin into a crack in the {noun}, green with age.",
        "Up close the {noun} is not one grey but a dozen.",
        "A snail has left a silver trail across the {noun}, wandering and doubling back.",
        "The base of the {noun} is polished where sheep have rubbed against it.",
    ],
    "tree": [
        "The bark of the {noun} is ridged deep enough to lose a fingertip in.",
        "Ants run a busy road up the {noun} and vanish into a split in the bark.",
        "Somewhere in the {noun} a bird scolds you and will not stop.",
        "One low branch of the {noun} has been worn smooth, as if by many hands.",
        "Initials are cut into the {noun}, old enough that the bark has half healed over them.",
        "The roots of the {noun} grip the ground like knuckles.",
        "A woodpecker has drilled a neat row of holes around the {noun}.",
        "Something has stripped a strip of bark from the {noun}, low down; deer, perhaps.",
        "The {noun} creaks once, softly, though you can't feel any wind.",
        "Ivy has climbed a third of the way up the {noun} and is thinking about the rest.",
    ],
    "water": [
        "Small things move in the shallows of the {noun}, then hold still as your shadow falls.",
        "The water of the {noun} tastes of stone when you cup a little.",
        "Weed streams in the {noun}, all leaning one way.",
        "There are pale pebbles at the bottom of the {noun}, sorted by size as if by a patient hand.",
        "A water-boatman rows across the {noun} in short, important strokes.",
        "The edge of the {noun} is trodden into mud by hooves and paws.",
        "Your reflection in the {noun} wavers, steadies, and wavers again.",
        "Foam gathers in a quiet corner of the {noun}, yellowish and slow.",
    ],
    "earth": [
        "The turf over the {noun} is thin and springy, with flints breaking through.",
        "Rabbits have been at the {noun}; the spoil of their burrows is pale and fresh.",
        "The ground around the {noun} rings faintly hollow under your heel.",
        "Molehills dot the {noun}, and in one of them is a sherd of old pot.",
        "Thistles grow thick on the {noun}, as they do where the ground was once disturbed.",
        "There is a smell of cold earth about the {noun}, like an opened cellar.",
        "Old spade-marks show in the side of the {noun}, softened by years of grass.",
        "A path has been worn across the {noun} by feet that had somewhere to be.",
    ],
    "built": [
        "Whoever made the {noun} knew their work; whoever mended it did not.",
        "The timbers of the {noun} are grey and split, and soft as cork where you press them.",
        "Nails in the {noun} have rusted to orange stains.",
        "Nettles have moved in around the {noun}, as nettles do wherever people once were.",
        "There are tool marks on the {noun}, each one a moment of somebody's day.",
        "The {noun} leans, slightly, as if listening for something.",
        "A spider has strung the corners of the {noun} with old, dusty webs.",
        "Someone has patched the {noun} with whatever came to hand: a cart-board, a hurdle, a door.",
    ],
    "log": [
        "Bracket fungus steps up the side of the {noun} like a staircase for something small.",
        "The bark is coming away from the {noun} in sheets; underneath, beetles have written in tunnels.",
        "The {noun} is soft at one end and hard as iron at the other.",
        "Moss has covered the {noun} so thickly that it looks upholstered.",
        "The root-plate of the {noun} stands up taller than you, still clutching stones.",
        "Something lives under the {noun}; there's a worn hollow and a smell of fox.",
    ],
    "plant": [
        "Bees work steadily through the {noun}, unbothered by you.",
        "The {noun} is full of small sounds: rustles, ticks, a cricket somewhere.",
        "The growth here is thick enough that you can't see the ground.",
        "A deer has lain here recently; the stems are pressed flat in an oval.",
    ],
    "fungus": [
        "The caps of the {noun} are cold and faintly damp, like a frog's back.",
        "The {noun} smells sweet and earthy, with something sharper underneath.",
        "Nothing grows inside the {noun}; even the grass there looks thinner.",
    ],
    "ice": [
        "The ice of the {noun} is blue as a bruise deep down, white at the surface.",
        "Somewhere inside the {noun} water runs, a hollow, hidden sound.",
        "Grit and stones are locked in the {noun}, carried from somewhere far uphill.",
    ],
}

# what each particular kind of landmark draws the eye to
SIG = {
    "standing stone": ["The stone is taller than it looked from a distance, and leans a hand's breadth to the east.",
                       "Faint grooves run down one face of the stone - weathering, or the ghost of a pattern.",
                       "A ring of trampled ground circles the stone, as if people walk round it still."],
    "stone circle": ["Count the stones and you get one number; count again and you get another.",
                     "The stones are all different heights, but their tops are level with each other.",
                     "One stone in the circle has fallen inward and lies with its face to the sky."],
    "cairn": ["Each stone of the cairn was carried here by someone; a few are white quartz, chosen.",
              "There is a gap near the top of the cairn where a stone has been taken. Bad luck, folk would say.",
              "The cairn is built tighter at the base than at the top, the work of more than one generation."],
    "outcrop": ["The outcrop is split by a deep crack you could fit your arm into.",
                "Layers show in the outcrop like the pages of a closed book."],
    "chasm": ["A stone dropped into the chasm takes too long to answer.",
              "Air rises out of the chasm, cool and smelling of wet rock."],
    "cave mouth": ["The floor of the cave mouth is dry and scuffed by more than weather.",
                   "Just inside the cave mouth, soot has blackened the roof - old fires."],
    "eyrie": ["White streaks stain the rock below the eyrie, and small bones lie scattered at its foot.",
              "Sticks the size of your arm are woven into the eyrie; it has been added to for years."],
    "oak": ["Acorn cups crunch underfoot beneath the oak.", "The oak's lowest limb is as thick as most trees."],
    "yew": ["The yew's trunk is fluted and hollow, more like several trees grown together.",
            "Nothing grows under the yew; its needles carpet the ground dark and soft."],
    "willow": ["The willow's trunk is split and leaning, and new shoots grow straight up from the break.",
               "Ribbons hang from a few of the willow's switches, faded nearly white."],
    "hawthorn": ["The hawthorn is all elbows and thorns, bent into the shape of the prevailing wind.",
                 "Rags and threads are tied to the hawthorn's twigs: wishes, or thanks."],
    "rowan": ["Someone has cut a rowan twig and tied it in a cross; the knot is still neat.",
              "The rowan grows straight out of a crack in a rock, stubborn as a goat."],
    "fallen tree": ["The fallen tree has taken a smaller one down with it, and the two lie crossed.",
                    "Where the fallen tree stood there is now a gap of sky."],
    "fallen beech": ["The fallen beech's bark is still smooth and grey as an elephant's hide.",
                     "Beech mast lies scattered in the hollow the fallen tree tore up."],
    "bog oak": ["The bog oak is black right through and heavy as stone.",
                "The grain of the bog oak shows silver where the peat has worn it."],
    "stream": ["The stream is clear enough to count the stones, and cold enough to ache.",
               "In one place the stream undercuts the bank, and roots hang down like hair."],
    "pool": ["The pool is deeper than its size suggests; the bottom drops away into brown.",
             "Something rises in the pool, leaves a ring, and does not show itself."],
    "dew pond": ["The dew pond is lined with clay; you can see where it has been puddled smooth.",
                 "Hoofprints ring the dew pond, and a single heron's footprint."],
    "waterfall": ["Behind the curtain of the waterfall there's a dark slot of rock.",
                  "The waterfall has hollowed a basin below it, smooth and round as a bowl."],
    "tarn": ["The tarn is so still that the far shore seems to hang upside down in it.",
             "Stones have been set along one edge of the tarn, a rough jetty going nowhere."],
    "holy well": ["Coins glint at the bottom of the holy well, some of them very old.",
                  "A cup on a chain hangs at the holy well, worn thin by lips."],
    "hot spring": ["The hot spring smells of eggs and iron, and the stones around it are stained orange.",
                   "The water of the hot spring is too hot to keep a hand in for long."],
    "ring of toadstools": ["The ring of toadstools is almost perfect, broken only where a hoof came down.",
                           "Inside the ring of toadstools the grass is a darker green."],
    "glacier": ["The glacier creaks, a slow sound like a door in an empty house.",
                "A boulder sits on the glacier's back, carried there from who knows where."],
    "glade": ["The glade is quieter than the woods around it, as if the trees have stepped back.",
              "A fallen log in the glade has been worn smooth on top; people sit here."],
    "reed island": ["The reed island shifts a little when you step on its edge.",
                    "A coot's nest is wedged into the reed island, built up out of the water."],
    "causeway": ["The causeway's stones are rounded by feet and water; a few have sunk out of line.",
                 "Wooden piles show along the causeway's edge, black and soft, older than the stones."],
    "eel trap": ["The eel trap is woven of willow and still smells of the river.",
                 "One end of the eel trap has been mended with newer, paler withies."],
    "track": ["The track is sunk between its banks, worn down by more feet than you can imagine.",
              "Ruts in the track hold water, and every rut has its own small sky."],
    "sheepfold": ["The sheepfold's walls are laid dry, no mortar, each stone choosing its neighbour.",
                  "Fleece is snagged on the sheepfold's stones, and the ground inside is trodden bare."],
    "hunter's hide": ["The hunter's hide has a slit at eye height, facing the open ground.",
                      "Inside the hunter's hide the earth is flattened where someone lay and waited."],
    "sunken punt": ["Only the gunwales of the sunken punt show above the water.",
                    "A pole lies alongside the sunken punt, as if the punter simply stepped away."],
    "gibbet": ["The gibbet's chains are rusted but whole, and they move a little on their own.",
               "Nobody has cut back the grass under the gibbet; nobody wants to stand there."],
    "dovecote": ["The dovecote's walls are pocked with nesting holes, rows and rows of them.",
                 "Feathers and old droppings crust the dovecote's ledges."],
    "hermit's cell": ["The hermit's cell is barely big enough to lie down in.",
                      "A cross is scratched into the lintel of the hermit's cell, small and careful."],
    "charcoal-burner's mound": ["The charcoal-burner's mound is black at the heart and grassed over at the edges.",
                                "Black crumbs still turn up in the charcoal-burner's mound when you scuff it."],
    "badger sett": ["The badger sett has half a dozen entrances, each with its own heap of spoil.",
                    "A well-worn path leads away from the badger sett, low and narrow."],
    "peat cutting": ["The peat cutting's walls show layers like a cake, darkest at the bottom.",
                     "A peat spade's marks are still clear in the cutting, regular as stitching."],
    "barrow": ["The barrow is longer than it is wide, and lies east to west.",
               "There is a dip at the top of the barrow, where someone once dug and gave up - or didn't."],
    "hill fort": ["The hill fort's banks still stand chest-high, ring within ring.",
                  "Where the hill fort's gate once was, the banks turn in on themselves to make a passage."],
    "chalk figure": ["Up close the chalk figure is just trenches of white in the turf; its shape is lost.",
                     "The chalk figure has been scoured recently; its lines are clean and bright."],
    "old mine": ["Spoil from the old mine lies in heaps, grassed over and sparkling with quartz.",
                 "The old mine's entrance is propped with timbers that would not hold a sneeze."],
}

# how the examination is framed: lengths, orders and leads all vary. Pieces:
#   {noun} {a1} {a2} {verb} {where}  - the landmark's own words
#   {D1}/{d1} {D2}/{d2}               - its fixed details, true right now (capitalised / not)
#   {focus} {sig}                     - a texture of its family / something about its kind
#   {now}                             - how it looks right now (weather, light), when there's a line for it
EXAMINE = [
    ("At the {noun} you see {d1}. {focus}", 1.0),
    ("The {noun} is {a1}. {focus}", 1.0),
    ("{sig} {D1}.", 1.0),
    ("What you notice first is {d1}. Then {d2}.", 0.8),
    ("It's {d1} that holds your eye. {sig}", 1.0),
    ("{now} You see {d1}.", 1.0),
    ("{focus} {sig}", 1.0),
    ("{A1} and {a2}, the {noun} {verb} {where}. {focus}", 0.8),
    ("You see {d1} - and, when you look again, {d2}.", 0.8),
    ("For a while you just look. {sig}", 0.9),
    ("You make out {d2}; that, and {d1}, is most of what the {noun} has to show.", 0.7),
    ("{focus} You notice {d1}.", 1.0),
    ("You walk once around the {noun}. {sig}", 0.9),
    ("Close to, the {noun} is {a2}, with {d1}.", 1.0),
    ("{sig}", 0.8),
    ("{now} {focus}", 0.9),
    ("The {noun}: {a1}, {a2}, {d1}.", 0.6),
    ("{sig} You notice {d1}, too.", 0.9),
    ("You crouch for a better look. {focus}", 0.7),
    ("Nearer, you see {d2}. {sig}", 0.9),
]

# a second look moves on: something not yet mentioned, or what has changed
AGAIN = [
    ("You look again. {focus}", 0.3),
    ("Second time round, it's {d2} you notice.", 0.7),
    ("{now} Otherwise the {noun} is as you left it.", 0.8),
    ("Nothing has changed that you can see. {focus}", 0.5),
    ("You give the {noun} a longer look. {sig}", 0.5),
    ("{focus}", 1.0),
    ("{sig}", 1.0),
    ("This time it's {d2} that you notice. {focus}", 0.8),
    ("Something you missed before: {d2}.", 0.8),
    ("The longer you look, the more there is. {sig}", 0.6),
    ("{now} {sig}", 0.9),
    ("This time you see {d2}. {focus}", 0.9),
    ("Back at the {noun}, you see what you saw before, and one thing more: {focus_l}", 0.6),
    ("You run your eye over the {noun} once more. {focus}", 0.5),
    ("{sig} You hadn't noticed that before.", 0.7),
]

# ---------------------------------------------------------------- climbing
CLIMB_HOW = {
    "tree": ["You go up the {noun} branch by branch until the trunk starts to sway with you.",
             "You get a knee into the fork of the {noun} and pull yourself up into its crown.",
             "Bark comes away under your fingers, but the {noun} holds, and you climb.",
             "You climb the {noun} until the branches get too thin to trust."],
    "stone": ["You find handholds in the weathered {noun} and pull yourself up.",
              "The {noun} is rough enough to climb; you scrape a knee on the way and decide it was worth it.",
              "You scramble up the {noun}, testing each hold before you trust it.",
              "Up the {noun} you go, fingers in cracks, boots on ledges no wider than a coin."],
    "built": ["You scramble up the {noun}, which complains about it.",
              "You climb onto the {noun} carefully, keeping your weight on the posts.",
              "The {noun} takes your weight, just. You get up onto the top of it."],
    "earth": ["You walk up onto the {noun}; the turf is steep at the top and you need your hands.",
              "It's more of a steep walk than a climb, up the side of the {noun}.",
              "You climb the bank of the {noun}, slipping once on the turf."],
    "ice": ["You cut steps in the {noun} with your heel and climb a little way, carefully."],
    "plant": ["You push through to the highest part of the {noun} and stand on a tussock."],
}
# landmarks whose family's climbing words don't fit them
CLIMB_KIND = {
    "bog oak": ["You clamber onto the black trunk of the {noun}; it doesn't lift you far.", "You stand on the {noun}, balancing on wood as hard as stone."],
    "chalk figure": ["You climb the steep turf to the top of the {noun}, the chalk slippery under your boots.", "Up the slope beside the {noun} you go, on hands as much as feet."],
    "reed island": ["You push through to the highest tussock of the {noun} and stand there, swaying with it."],
    "gibbet": ["You climb the {noun}'s post, trying not to touch the chains.", "You haul yourself up the {noun}. The chains clink below you."],
    "eyrie": ["You climb towards the {noun} until the rock gets too sheer, and stop on a ledge below it.", "You scramble up the crag to just below the {noun}; something up there watches you."],
    "glacier": ["You cut steps in the {noun} with your heel and climb a little way, carefully."],
}
CLIMB_HIGH = {"oak", "yew", "willow", "rowan", "standing stone", "outcrop", "eyrie", "hill fort", "glacier", "dovecote", "stone circle", "gibbet"}

VISTA_CLEAR = ["The country opens out below you.", "Below, the land lays itself out like a map.",
               "From the top you can see for miles.", "Now you can see where you are.",
               "The view goes on further than you expected.", "You can see the shape of the land at last.",
               "Up here the wind finds you, and so does the view."]
VISTA_DULL = ["The light is flat, but you can see a fair way.", "Grey distances fold one behind another.",
              "The view is muted, colours drained, but it's there."]
VISTA_NONE = ["It's country you've already walked; nothing new shows.", "Everything in sight you already know.",
              "No surprises: the land around is all familiar now.", "You see nothing you haven't seen from the ground."]
VISTA_FOG = ["The fog closes in a stone's throw away; there's nothing to see but white.",
             "Fog fills every hollow; you are standing on an island in a grey sea.",
             "You can barely see the ground you climbed from. The fog has everything else."]
VISTA_DARK = ["In the dark, the land is shapes and guesses.", "There's no moonlit panorama, just darkness and the wind.",
              "The night has swallowed the view."]
CLIMB_DOWN = ["Getting down is slower than getting up.", "You come down carefully, feeling for each hold.",
              "You slide the last bit and land harder than you meant to.", "You stay up there a while before you climb down.",
              "Coming down, you miss a hold and catch it again, heart thumping.", "You climb down with green on your hands and knees.",
              "Down again, the world shrinks back to its usual size.", "You jump the last part and stagger."]

# how a revealed place is phrased: {what} "a village", {dir} "north-west", {far} "a short walk"
SEEN_FRAMES = ["{what} {far} to the {dir}", "to the {dir}, {far} off, {what}", "{what} away {dir}ward"]
SEEN_LIGHT = ["lights {far} to the {dir} - lamplit windows, a village", "a scatter of firelight to the {dir}, {far} off",
              "the glow of hearths {far} to the {dir}"]
HEARD = ["Somewhere {far} to the {dir} a dog barks, and a bell answers: a village, out there in the white.",
         "Through the fog, from the {dir}, comes the sound of an axe on wood. People, {far} off.",
         "Off to the {dir} you hear voices calling, faint and flattened by the fog."]
GOAL_SEEN = ["And there, {dir}ward, is {place}: the place your errand points to.",
             "You can pick out {place} to the {dir} from here, where your journal says you're going.",
             "{place} lies {far} to the {dir}; that's where you need to be, for '{title}'."]

# ---------------------------------------------------------------- searching
FINDS = {
    "tree": ["beetles", "a snail shell", "a scatter of owl pellets", "dry leaves", "a jay's feather", "the husk of a nut", "spiders",
             "a rusty nail", "a squirrel's cache of beech mast", "a child's lost button", "a woodpecker's chips"],
    "water": ["smooth stones", "a startled fish", "weed", "silt", "a broken clay pipe", "a freshwater mussel shell", "a drowned beetle",
              "a lost fishing hook", "a crayfish that backs away from you"],
    "stone": ["lichen", "a spider's egg-sac", "chips of stone", "a lost button", "an old fire-blackened stone", "sheep droppings",
              "a fossil shell", "a scrap of wool", "a wren's empty nest", "a flint scraper, very old"],
    "log": ["woodlice", "a toad", "owl pellets", "beetle galleries", "a dormouse's empty nest", "rotten wood", "fungus", "a fox's droppings",
            "a slow-worm, which slides away"],
    "earth": ["roots", "flints", "a worm or two", "rabbit droppings", "a cracked bead", "loose soil", "a sherd of old pot", "a mole's tunnel"],
    "built": ["rot", "nettles", "a mouse's nest", "a broken buckle", "rotten rope", "old straw", "a bent nail", "a wasps' nest, long empty",
              "a scratched tally of days"],
    "ice": ["cold", "blue depths", "grit locked in the ice"],
    "fungus": ["the soft give of the caps", "a sweet, earthy smell", "spores like brown dust"],
    "plant": ["grass", "a lark's empty nest", "a curl of snakeskin", "the flattened place where a deer lay", "a lost glove, sodden"],
}
SEARCH = [
    "You search the {noun} carefully: {finds}.",
    "{Finds} - that's all the {noun} gives up.",
    "You work your way round the {noun}. {Finds}, and nothing else.",
    "Under and around the {noun}: {finds}.",
    "It takes a while. In the end the {noun} yields {finds}.",
    "You go over the {noun} inch by inch and find {finds}.",
    "For a moment you think you've found something. It's only {one}.",
    "Nothing much. {Finds}.",
    "Your hands come away dirty and the {noun} keeps its secrets, if it has any. {Finds}.",
    "A thorough search of the {noun} turns up {finds}.",
]
SEARCHED = ["You have already been over the {noun} thoroughly.", "There's nothing more to find at the {noun}.",
            "You search the {noun} again, but you were thorough the first time.",
            "The {noun} has nothing left to show you.", "You've turned over every stone at the {noun} already.",
            "A second search finds the marks of your first, and nothing else."]
CACHE_WHERE = {"tree": "in a hollow among the roots", "stone": "behind a loose stone", "built": "under a rotten board",
               "earth": "a hand's depth down in the soft ground", "log": "in the dry hollow under the trunk"}
CACHE = [
    "{Where} at the {noun} you find a bundle someone hid and never came back for: {loot}.",
    "Your fingers close on oilcloth {where}. Inside: {loot}.",
    "{Where} there's a leather bag, stiff with age. Someone's savings, maybe: {loot}.",
    "You almost miss it - {where}, a wrapped bundle. {Loot}, no name, no note.",
    "Someone meant to come back to the {noun}. {Where} they left {loot}, and never returned for it.",
    "A cache! {Where}, tied up in sacking: {loot}.",
]

# when a landmark can't be climbed
NO_CLIMB = ["There's no climbing the {noun}.", "The {noun} isn't something you can climb.",
            "You look the {noun} over for a way up. There isn't one.", "Climb the {noun}? There's nothing to climb.",
            "The {noun} offers no way up.", "You'd need wings, not hands, to get above the {noun}."]
