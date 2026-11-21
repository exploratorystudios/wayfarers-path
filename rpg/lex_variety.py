"""Variety pass, driven by tools/variety.py.

REPLACE swaps out thin symbols entirely; EXTEND appends to existing ones.
"""

REPLACE = {
    # ---------------------------------------------------------------- exits
    "forest:land": ["the wood", "the trees", "the forest", "the woodland"],
    "marsh:land": ["the fen", "the marsh", "the mire", "the wetland"],
    "plains:land": ["the open land", "the heath", "the grassland", "the downs"],
    "hills:land": ["the hills", "the high ground", "the hill country"],
    "peaks:land": ["the crags", "the mountains", "the bare rock"],
    # {land} and {glimpse} may be singular ("the fen") or plural ("the hills", "jagged peaks"), so they are
    # never the subject of a present-tense verb in these frames.
    "exit_surround": ["You are hemmed in by {land}{but}.", "On every side, nothing but {land}{but}.", "Wherever you look, you see {land}{but}.",
                      "You stand in the midst of {land}{but}.", "{region.cap} lies all about you{but}.", "Turn any way you like and you will find {land}{but}.",
                      "All around you is more of {land}{but}.", "You could walk a long way in any direction and not leave {land}{but}."],
    "exit_same": ["To the {dirs}, {continues}.", "{dirs.cap}, {continues}.", "There is more of {land} to the {dirs}.", "There is more of {region} to the {dirs}.",
                  "Heading {dirs} would keep you in {region}.", "{region.cap} continues {dirs} of here.", "{dirs.cap} of you is more of {land}.",
                  "Go {dirs} and you will only go deeper into {land}.", "{dirs.cap}, more of {land} stretches away.", "Further {dirs}, you can see more of {land}."],
    "exit_diff": ["To the {dirs}, you see {glimpse}.", "Looking {dirs}, you can make out {glimpse}.", "The way {dirs} leads toward {glimpse}.",
                  "{dirs.cap}, the land gives way to {glimpse}.", "Away to the {dirs} is a view of {glimpse}.", "Off to the {dirs}, you glimpse {glimpse}.",
                  "{dirs.cap}, the country changes: {glimpse}.", "{dirs.cap}, the land changes to {glimpse}.", "Beyond, to the {dirs}, you can see {glimpse}.",
                  "You can see {glimpse} {dirs} of here.", "{dirs.cap} of you, you can make out {glimpse}.", "Past the edge of this place, to the {dirs}: {glimpse}."],
    "exit_diff_named": ["To the {dirs} the way opens onto {glimpse} - {region}.", "{dirs.cap}, {region} starts with {glimpse}.",
                        "The way {dirs} leads into {region}, {glimpse}.", "{region.cap} begins to the {dirs}: {glimpse}.", "Off to the {dirs} is {region}, {glimpse}.",
                        "The edge of {region} is just {dirs} of here.", "Step {dirs} and you will be in {region}.", "{region.cap} lies to the {dirs}, {glimpse}.",
                        "You can see where {region} starts, {dirs} of here: {glimpse}."],
    "exit_pair": ["There is more of {land} to the {sdirs}; to the {ddirs} the land gives way to {glimpse}.",
                  "There is more of {land} to the {sdirs}, but to the {ddirs} you can see {glimpse}.",
                  "To the {sdirs}, more of {land}; to the {ddirs}, {glimpse}.",
                  "The way {sdirs} keeps to {land}; the way {ddirs} leads to {glimpse}.",
                  "{sdirs.cap} of here is more of {land}, and to the {ddirs} the country changes to {glimpse}."],
    "exit_water": ["To the {dirs}, the way is barred by {glimpse}.", "{dirs.cap} there is only {glimpse}; you cannot go that way.",
                   "Any path to the {dirs} is cut off by {glimpse}.", "The way {dirs} ends at {glimpse}.", "{dirs.cap}, the land runs out at {glimpse}.",
                   "There is no going {dirs}: {glimpse} would stop you.", "To the {dirs}, the ground stops at {glimpse}.",
                   "{dirs.cap} of here, the land ends at {glimpse}, too deep and wide to cross."],
    "joiner": ["; ", " - ", ", and ", ", while ", "; meanwhile, "],
    # ---------------------------------------------------------------- loot
    "coin_find": ["You find {coins} coins nearby - some earlier victim's, perhaps.", "Something glints in the grass: {coins} coins.",
                  "Among the leavings of the fight you turn up {coins} coins.", "A few coins lie scattered nearby - {coins} in all.",
                  "You come away {coins} coins richer; who dropped them, you'll never know.", "There are {coins} coins in the dirt here, long since lost by someone."],
}

EXTEND = {
    # ---------------------------------------------------------------- second pass (audit hot spots)
    "onward": ["You keep on {dir}; {region} does not end yet.", "{dir.cap} you go, the country of {region} unchanged.", "A little further {dir}, and still {region}.",
               "You put more of {region} behind you, heading {dir}.", "Your path bends {dir}, through more of {region}."],
    "forest:land": ["the greenwood", "the wildwood"], "marsh:land": ["the bog", "the reed-beds"], "plains:land": ["the moor", "the open country"],
    "hills:land": ["the fells", "the slopes", "the uplands"], "peaks:land": ["the heights", "the rock and ice"],
    "morning:time_life": ["The world feels busy and newly begun.", "Somewhere, someone is lighting a fire against the morning chill.", "Spiders' webs glitter in the low light."],
    "midday:time_life": ["The middle of the day lies heavy and still.", "Flies drone lazily.", "It is the hour when everything that can rest, does."],
    "afternoon:time_life": ["The day has settled into its long middle.", "Shadows have begun, slowly, to lengthen.", "A lazy warmth hangs in the air."],
    "evening:time_life": ["The day's noise is giving way to the night's.", "A bat flickers past, then another.", "The air cools quickly now."],
    "deepnight:time_life": ["The silence has weight to it.", "Every sound seems louder in the dead of night.", "It is the loneliest hour."],
    "dawn:time_life": ["Birds begin, one by one, then all at once.", "The grass is grey with dew."],
    "dusk:time_life": ["The light is going fast.", "Colours drain from the land one by one."],
    "night:time_life": ["The dark is full of small rustlings.", "An owl calls, and is answered."],
    "hold:intent_presence": ["{a_c.cap} won't take its eyes off you, and won't give an inch.", "{a_c.cap} has claimed this place, and makes sure you know it.",
                             "{a_c.cap} blocks the way, hackles up.", "{a_c.cap} stands squarely on its ground, daring you."],
    "enemy_hit": ["{attacker.cap} {attackverb} you, and it hurts.", "{attacker.cap} {attackverb} you and draws blood from your {bodypart}.", "Your guard slips; {attacker} {attackverb} you, catching your {bodypart}."],
    "enemy_miss": ["{attacker.cap} {attackverb} you, but you're already gone.", "{attacker.cap} {attackverb} you; you sway back just in time.", "You read the move, and {attacker}'s attack goes wide."],
    "you_notice": ["Close by is", "You catch sight of", "Your attention is drawn to", "Not far away is", "Something catches your eye:"],
    "ask_name": ["\"And you'd be?\" \"{player},\" you answer. \"Hm. {player}. Right.\"", "\"Got a name, traveller?\" You give it: {player}.",
                 "{he.cap} squints at you. \"Who are you, then?\" \"{player}.\""],

    # ---------------------------------------------------------------- continues / glimpse
    "forest:continues": ["the trees close ranks", "the canopy keeps its hold on the light", "the trunks crowd on and on", "the shade goes on unbroken"],
    "marsh:continues": ["the reeds whisper on", "pool after pool glints away", "the ground stays soft and treacherous", "the bog keeps its grip"],
    "plains:continues": ["the grass runs on under the sky", "the land swells and dips onward", "the horizon keeps its distance", "the wind has the open land to itself"],
    "hills:continues": ["slope follows slope", "the ground keeps rising and falling", "the stony hillsides roll onward", "more ridges wait beyond this one"],
    "peaks:continues": ["the rock climbs on", "the crags pile higher", "the mountains go on, bare and cold"],
    "forest:glimpse": ["a darker line of trees", "woodland, thick and dark", "old trees crowding a slope", "the first trunks of a wood"],
    "marsh:glimpse": ["reeds and standing water", "low, wet country glinting with pools", "a sour-smelling fen", "the flat green of a bog"],
    "plains:glimpse": ["grass rolling away under the sky", "open country, bare to the wind", "a pale sweep of heath", "pasture dotted with sheep"],
    "hills:glimpse": ["a hillside streaked with scree", "grey-green hills folding together", "a ridge crowned with stones", "slopes of bracken and rock"],
    "peaks:glimpse": ["mountains shouldering into the cloud", "a wall of bare rock", "snow-veined crags", "a jagged line of summits"],
    "lake:glimpse": ["grey water stretching away", "a reedy shore and the water beyond", "a wide lake, wind-ruffled", "a dark tarn, utterly still"],

    # ---------------------------------------------------------------- weather (more lines per state)
    "clear:weather_line": ["The sky is a clean, hard blue.", "There isn't a cloud anywhere.", "The air is so clear that distant things look close.",
                           "A bright, empty sky arches overhead.", "The day is clear and still.", "Sunlight lies on everything."],
    "cloudy:weather_line": ["White clouds sail past, unhurried.", "The sun comes and goes behind tall clouds.", "Clouds pile up in towers on the horizon.",
                            "Broken cloud lets the light through in shafts.", "A fleet of clouds drifts east."],
    "overcast:weather_line": ["The sky has closed over, grey from edge to edge.", "Heavy grey cloud sits low over the land.", "No sun shows through the dull grey ceiling.",
                              "The day is muffled under a blanket of cloud.", "Grey cloud hangs over everything, still and thick."],
    "drizzle:weather_line": ["A thin mizzle drifts on the air.", "The drizzle never quite becomes rain, and never quite stops.", "Fine wet hangs everywhere, like breath on glass.",
                             "A soft grey drizzle blurs the distance.", "Drizzle settles on you like cold dew."],
    "rain:weather_line": ["The rain comes down hard and steady.", "Rain rattles on every leaf and stone.", "It is pouring.", "Water streams off your hood in a steady drip.",
                          "Rain blurs the world into greys and greens.", "The downpour flattens the grass."],
    "storm:weather_line": ["Thunder rolls across the sky like barrels down a stair.", "The storm howls, and the rain stings like thrown gravel.",
                           "Lightning splits the sky, and the world flashes white.", "Wind and rain lash at you without pause."],
    "fog:weather_line": ["The fog is so thick you can barely see your own feet.", "Everything beyond a stone's throw has dissolved into white.",
                         "Fog drifts in slow, cold banks.", "The world has shrunk to a little room of grey."],
    "wind:weather_line": ["The wind gusts hard, then drops, then gusts again.", "A cold wind pushes at your back.", "The wind hums in your ears.",
                          "Gusts tear at your cloak."],
    "snow:weather_line": ["Snowflakes drift down, slow and silent.", "The snow is coming thicker now.", "A fine snow hisses down.", "Snow blurs the edges of the world."],
    "clear:weather_detail": ["The light makes every colour sharp.", "Shadows lie crisp and black.", "Far-off things stand out as if cut from paper."],
    "cloudy:weather_detail": ["The light keeps changing as the clouds pass.", "A patch of sun slides across the ground toward you, then away.", "The day can't decide what kind of day to be."],
    "overcast:weather_detail": ["Colours look washed out in the grey light.", "The light is the same dull grey everywhere.", "Under that sky, everything looks a little tired."],
    "drizzle:weather_detail": ["Droplets bead on your sleeves.", "The damp gets into everything.", "Your hair is plastered to your forehead."],
    "rain:weather_detail": ["The ground has turned to mud.", "Every hollow is filling with water.", "Your boots squelch with each step."],
    "fog:weather_detail": ["Shapes loom up and turn out to be nothing.", "The fog beads on your cloak like sweat.", "Even your footsteps sound muffled."],
    "wind:weather_detail": ["Your eyes water in the wind.", "The wind snatches at your words before you can say them."],
    "storm:weather_detail": ["The air tastes of iron.", "Water runs down your neck no matter how you hunch."],
    "snow:weather_detail": ["Snow gathers in the creases of your cloak.", "The world has gone hushed and white."],

    # ---------------------------------------------------------------- light
    "dawn_bright:light_line": ["The sky is paling in the east.", "Dawn is breaking, cool and clean.", "The first sun catches the tops of things and gilds them."],
    "dawn_dull:light_line": ["Grey light leaks into the world.", "It is dawn, more or less.", "Morning comes on slowly, as if reluctant."],
    "morning_bright:light_line": ["The morning is fresh and full of light.", "The early sun is still low and kind."],
    "morning_dull:light_line": ["The morning is dim and damp.", "There is little cheer in this grey morning.", "Morning, though it could as easily be evening."],
    "midday_bright:light_line": ["The sun is at its height.", "It is noon, and hot where the sun falls.", "Midday light flattens the land."],
    "midday_dull:light_line": ["It is about midday, by the dull glow overhead.", "Noon passes almost unnoticed under the cloud.", "The middle of the day is as grey as the start of it."],
    "afternoon_bright:light_line": ["The afternoon sun throws long, soft shadows.", "It is a clear afternoon, the light turning golden."],
    "afternoon_dull:light_line": ["The afternoon is wearing on, dim and grey.", "A long, colourless afternoon stretches ahead.", "The light is already fading, though it is only afternoon.", "Grey afternoon light lies flat on the land."],
    "dusk_bright:light_line": ["The sun touches the horizon, and colour floods the sky.", "Evening is coming in gold and rose."],
    "dusk_dull:light_line": ["The grey day greys further into dusk.", "It is getting dark, and early.", "Dusk smudges the edges of everything."],
    "evening_bright:light_line": ["The last glow lingers low in the west.", "Stars appear one by one."],
    "evening_dull:light_line": ["Evening gathers, damp and dark.", "Night is coming on, and the cloud brings it sooner.", "It is nearly too dark to see the path."],
    "night_dull:light_line": ["The dark is thick enough to touch.", "Night, and not a glimmer anywhere."],
    "deepnight_dull:light_line": ["It is the black middle of the night.", "Hours yet until dawn, and not a star to steer by.", "The night is deep and starless."],

    # ---------------------------------------------------------------- seasons
    "spring:season_line": ["New growth pushes up everywhere you look.", "Birds are nesting; the air is full of their business.", "There's a raw, hopeful smell of spring."],
    "summer:season_line": ["The year is at its fullest.", "Seed-heads and long grass mark the height of summer.", "The summer air is thick with pollen."],
    "autumn:season_line": ["Leaves drift down whenever the wind stirs.", "Everything is turning brown and gold.", "The air has autumn's damp, smoky edge."],
    "winter:season_line": ["The cold bites at your fingers.", "Frost lingers in every shadow.", "The short winter day is already hurrying on."],

    # ---------------------------------------------------------------- senses & terrain
    "terrain": ["The ground underfoot is {ground}.", "You cross {ground}.", "It's {ground} here, and slow going.", "Underfoot: {ground}.", "Your feet find {ground}."],
    "sense_smell": ["There's a whiff of {smell}.", "{smell.cap} - the smell is everywhere here.", "Your nose catches {smell}.", "The breeze brings {smell}."],
    "sense_sound": ["Somewhere, {sound}.", "{sound.cap}, and then quiet.", "In the quiet, you notice {sound}.", "You keep hearing {sound}."],

    # ---------------------------------------------------------------- combat
    "hit": ["You {hitverb} {target}'s {part}, and it {react}.", "Your blow lands on {target}'s {part}.", "You catch {target} squarely on the {part}.",
            "{weapon.cap} connects with {target}'s {part}. It {react}."],
    "crit": ["A brutal blow! You {hitverb} {target}'s {part}, and it {react_big}.", "You put everything into it: {weapon} smashes into {target}'s {part}.",
             "A clean, deadly strike to {target}'s {part}. It {react_big}."],
    "graze": ["You barely touch {target}'s {part}.", "{weapon.cap} skims {target}'s {part}, drawing a little blood."],
    "miss": ["{target.cap} is too quick; your {attack_noun} finds nothing.", "You overreach, and {target} slips past your {attack_noun}.", "Your {attack_noun} hits only the ground."],
    "warn": ["{the_c.cap} rears up, making itself huge. Its meaning is plain: go.", "{the_c.cap} stands its ground and stares you down.",
             "{the_c.cap} gives a warning you'd be foolish to ignore."],
}

# Village trades, by the land around them, and concrete signs of each (two become fixed facts per village).
ECONOMY = {
    "forest": ["charcoal-burning", "woodcutting", "bee-keeping", "pig-keeping", "bodging"],
    "marsh": ["eel-fishing", "peat-cutting", "reed-cutting", "wildfowling", "basket-making"],
    "plains": ["sheep-farming", "weaving", "brewing", "apple-growing", "horse-breeding"],
    "hills": ["quarrying", "lead-mining", "goat-herding", "sheep-farming", "stone-walling"],
}
ECONOMY_SIGNS = {
    "charcoal-burning": ["A haze of blue smoke hangs over the rooftops from the charcoal clamps.", "Sacks of charcoal are stacked by every door, and the people's hands are grey with it."],
    "woodcutting": ["Stacks of split logs line the lanes.", "The sound of axes carries from the edge of the trees.", "A sawpit stands open beside the track, heaped with sawdust."],
    "bee-keeping": ["Straw skeps line a south-facing wall, humming.", "The air smells of beeswax, and bees drift lazily between the houses."],
    "pig-keeping": ["Pigs root in a muddy pen behind the houses.", "A swineherd's horn sounds somewhere among the trees."],
    "bodging": ["Chair-legs, turned on pole-lathes, dry in neat rows under an awning.", "Green wood shavings curl in drifts outside a workshop."],
    "eel-fishing": ["Wicker eel traps are stacked by the doors, and the smell of smoked eel hangs over everything.", "Eels hang in long rows over a smoking fire."],
    "peat-cutting": ["Stacks of cut turf dry against every wall.", "Blocks of drying peat are piled in neat walls between the houses.", "The smoke here is thick and sweet with burning peat."],
    "reed-cutting": ["Bundles of cut reed are stacked like sheaves beside the lanes.", "Someone is re-thatching a roof with fresh-cut reed."],
    "wildfowling": ["Strings of ducks and geese hang from the eaves.", "Nets and decoy birds are piled outside a hut."],
    "basket-making": ["Half-finished baskets sit on every doorstep.", "Willow withies soak in a trough by the well."],
    "sheep-farming": ["Sheep crowd a fold at the edge of the houses, and tufts of wool snag on every hedge.", "A shearing-board stands outside a barn, strewn with wool."],
    "weaving": ["The clack of looms comes from open doorways.", "Lengths of dyed cloth dry on racks in the sun."],
    "brewing": ["The warm, yeasty smell of a brewhouse fills the lane.", "Barrels are stacked outside the biggest house."],
    "apple-growing": ["An orchard of gnarled apple trees crowds behind the houses.", "Baskets of apples sit by the doors, and wasps hum over the windfalls."],
    "horse-breeding": ["Horses graze in a paddock ringed with a rough fence.", "A forge rings out, and a farrier is shoeing a cob."],
    "quarrying": ["Pale stone dust coats everything, from the roofs to the people.", "The quarry face looms over the houses, scarred and bright."],
    "lead-mining": ["Spoil heaps scar the hillside above the houses.", "The people here have a grey, drawn look - miners, every one."],
    "goat-herding": ["Goats wander the lanes as if they own them.", "A goat stands on a roof, chewing something it shouldn't."],
    "stone-walling": ["Every field is ringed with neat drystone walls.", "Piles of sorted stone wait beside half-built walls."],
}
ECONOMY_NAMED = ["The folk here live by {economy}.", "This is a {economy} place, and it shows.", "{economy.cap} keeps the place fed.",
                 "Most here make their living by {economy}."]

# ---------------------------------------------------------------- the opening scene
INTRO = {
    # past: a noun phrase ("a knight whose lord died...")
    "intro_frame": [
        "You are {name}, once {past}. {arrival}",
        "{arrival} You are {name}. Once you were {past}; that life is behind you now.",
        "Your name is {name}. Before the road took you, you were {past}. {arrival}",
        "{arrival} Not so long ago you were {past}; these days, you are only {name}, another traveller.",
        "{name}, they called you, back when you were {past}. {arrival}",
        "{name}: once {past}, now a wanderer with an empty purse. {arrival}",
        "{arrival} You - {name}, lately {past} - have nowhere else to be.",
    ],
    "intro_motive": [
        "You have heard there might be work here.", "You need a roof, a meal, and a reason to keep going.", "You came because the road happened to lead here.",
        "You are not sure what you are looking for, only that it isn't behind you.", "Someone back on the road said this place needed help.",
        "You mean to rest a night, perhaps two, and move on.", "", "",
    ],
    "intro_kit": [
        "You carry {kit}, and little else.", "All you own is {kit}.", "Your pack is light: {kit}.", "", "",
    ],
}
ARRIVAL = {
    "dawn:intro_arrival": ["You reach {village} as the first light touches its roofs.", "Dawn finds you at the edge of {village}, stiff from a night on the road.", "{village} is just waking as you arrive."],
    "morning:intro_arrival": ["You walk into {village} in the middle of the morning.", "It is morning when {village} comes into view.", "You arrive in {village} with the morning half gone."],
    "midday:intro_arrival": ["You trudge into {village} at noon, hungry.", "{village} drowses in the midday as you arrive.", "The sun is high when you reach {village}."],
    "afternoon:intro_arrival": ["The afternoon is wearing on by the time you reach {village}.", "You come to {village} in the long part of the afternoon."],
    "dusk:intro_arrival": ["You reach {village} at dusk, as the lamps are being lit.", "{village} is settling for the evening when you walk in."],
    "evening:intro_arrival": ["It is evening when you finally reach {village}.", "You stumble into {village} after dark, guided by its fires."],
    "night:intro_arrival": ["You reach {village} in the dead of night; only a dog notices.", "{village} is asleep when you arrive."],
    "deepnight:intro_arrival": ["You reach {village} long after midnight, more asleep than awake.", "{village} is dark and silent when you come to it."],
    "rain:intro_arrival": ["You squelch into {village} through the rain, soaked to the skin.", "Rain drives you the last mile into {village}."],
    "storm:intro_arrival": ["The storm all but blows you into {village}.", "You reach {village} half-drowned, with thunder at your heels."],
    "fog:intro_arrival": ["{village} looms out of the fog, closer than you expected.", "You almost walk straight past {village} in the fog."],
    "snow:intro_arrival": ["You trudge into {village} through falling snow.", "Snow has turned {village}'s roofs white by the time you arrive."],
    "intro_arrival": ["The road has brought you, footsore, to {village}.", "Your road ends, for now, at {village}.", "At last you come to {village}."],
}

# ======================================================================== fact pools
# Village trades: ~11 per kind of land. Each village gets a main and a side trade.
ECONOMY = {
    "forest": ["charcoal-burning", "woodcutting", "bee-keeping", "pig-keeping", "bodging", "bark-stripping for the tanners", "trapping and furs",
               "hazel coppicing", "mushroom-gathering", "pitch-boiling", "bowyery", "hurdle-making"],
    "marsh": ["eel-fishing", "peat-cutting", "reed-cutting", "wildfowling", "basket-making", "salt-boiling", "leech-gathering", "osier-growing",
              "punt-building", "cranberry-picking", "fish-smoking"],
    "plains": ["sheep-farming", "weaving", "brewing", "apple-growing", "horse-breeding", "flax-growing", "cheese-making", "dyeing", "milling",
               "goose-rearing", "rope-making", "cider-pressing"],
    "hills": ["quarrying", "lead-mining", "goat-herding", "sheep-farming", "stone-walling", "slate-splitting", "copper-smelting", "wool-combing",
              "cattle-droving", "lime-burning", "flint-knapping"],
}
ECONOMY_SIGNS.update({
    "bark-stripping for the tanners": ["Curls of oak bark are stacked to dry under rough shelters.", "Bundles of stripped bark wait by the track for a cart."],
    "trapping and furs": ["Pelts are stretched on frames outside the houses.", "Snares and traps hang in neat rows by a door."],
    "hazel coppicing": ["Bundles of straight hazel rods lean against the walls.", "Beyond the houses, the hazel has been cut back to neat stools."],
    "mushroom-gathering": ["Strings of mushrooms dry under the eaves.", "Baskets of fungi, sorted by kind, sit on a trestle."],
    "pitch-boiling": ["A black cauldron of pitch bubbles over a fire, reeking of pine.", "Everything is faintly sticky and smells of resin."],
    "bowyery": ["Bow-staves season in racks under a long roof.", "A bowyer works at a stave on a bench, shaving it thin."],
    "hurdle-making": ["Woven hurdles are stacked like giant baskets.", "Someone is weaving a hurdle from split hazel, quick and sure."],
    "salt-boiling": ["Broad pans steam over fires, and the air tastes of salt.", "Mounds of grey salt are heaped under a thatched shelter."],
    "leech-gathering": ["Jars of leeches line a windowsill, squirming.", "The women here wade the pools bare-legged, gathering leeches."],
    "osier-growing": ["Beds of tall willow crowd the wet ground beyond the houses.", "Bundles of peeled osiers gleam white in the sun."],
    "punt-building": ["A half-built punt sits on trestles by the water.", "Planks steam in a long box, being bent for a boat."],
    "cranberry-picking": ["Baskets of red berries stand by the doors.", "Fingers here are stained crimson from the bog berries."],
    "fish-smoking": ["Rows of split fish hang in a smokehouse.", "The smell of smoking fish is everywhere."],
    "flax-growing": ["Bundles of flax soak in a retting pond, smelling foul.", "A field of blue flax flowers runs right up to the houses."],
    "cheese-making": ["Wheels of cheese ripen on shelves in an open shed.", "The sour smell of curds hangs about the lane."],
    "dyeing": ["Vats of blue and red dye steam outside a workshop.", "The stream below the houses runs faintly blue."],
    "milling": ["A mill wheel turns slowly, creaking, beside the stream.", "Flour dusts the doorways, and sacks wait for carts."],
    "goose-rearing": ["Geese patrol the lanes, hissing at strangers.", "A gaggle of geese is being driven toward the pond."],
    "rope-making": ["A long ropewalk runs behind the houses, strung with half-twisted cord.", "Coils of rope are piled beside a barn."],
    "cider-pressing": ["A wooden press stands in a yard, sticky and buzzing with wasps.", "The air smells sharply of crushed apples."],
    "slate-splitting": ["Grey slates are stacked in leaning piles.", "The tap of slate-splitters' hammers rings out."],
    "copper-smelting": ["A small furnace glows, and the air tastes of metal.", "Green-stained slag is heaped by the track."],
    "wool-combing": ["Heaps of combed wool sit in baskets like clouds.", "The combers' benches are set out in the sun."],
    "cattle-droving": ["A broad drove road runs through the middle of the houses, churned by hooves.", "Shaggy cattle graze on the slope, waiting to be driven to market."],
    "lime-burning": ["A squat lime kiln smokes at the edge of the houses.", "White lime-dust coats the walls and the people alike."],
    "flint-knapping": ["Flakes of flint litter the ground, sharp as glass.", "Someone is knapping flint on a doorstep, chip by chip."],
})
ECONOMY_SIGNS.setdefault("sheep-farming", ["Sheep crowd a fold at the edge of the houses."])

FACT_POOLS = {
    # village
    ("VILLAGE", "size"): ["thorp", "cluster", "straggle", "township", "clutch of farms"],
    ("VILLAGE", "material"): ["limewashed", "half-timbered", "drystone", "turf-walled", "weatherboarded", "rubble-stone", "clay-walled", "log-built", "chalk-block", "red-brick",
                              "ochre-washed", "cobble-walled", "pole-and-daub", "tarred-timber", "green-slate", "smoke-blackened"],
    ("VILLAGE", "roof"): ["heather thatch", "stone slabs", "moss-grown thatch", "oak shingles", "sod", "rush thatch", "pegged tiles",
                          "patched thatch", "grey slate", "bark shingles", "weighted straw", "sagging thatch", "red tiles"],
    ("VILLAGE", "around"): [", behind a bank of piled earth", ", around a small green", ", where two tracks cross", ", along a stream", ", on a low knoll",
                            ", hedged with blackthorn", ", among a scatter of old orchards", ", half-hidden in a fold of the land"],
    ("VILLAGE", "centre"): ["a duck pond, green with weed", "a stone cross worn faceless by weather", "a maypole stripped of ribbons", "a horse-trough fed by a spring",
                            "a tithe barn with a sagging roof", "a ring of benches around a firepit", "a gallows, thankfully empty", "a squat stone church with a wooden tower",
                            "a market hall on stone pillars", "an ancient yew, hollow and propped with posts", "a smithy, its forge glowing", "a covered well with a little roof",
                            "a stocks, empty but well used", "a standing stone that the village has grown around"],
    ("VILLAGE", "mood"): ["busy", "wary", "sleepy", "mournful"],
    # ruins
    ("RUIN", "purpose"): ["mill", "lazar-house", "bathhouse", "beacon tower", "abbey", "fortified farmhouse", "gatehouse", "chantry", "manor chapel",
                          "observatory", "mausoleum", "bridge-keep", "hunting lodge", "tithe barn", "court-house"],
    ("RUIN", "stone"): ["green-veined slate", "rough fieldstone", "honey-coloured stone", "black basalt", "chalk and flint", "weathered sandstone", "soot-dark granite"],
    ("RUIN", "state"): ["gutted", "roofless and open to the rain", "split by an old earthquake", "slumped into its own cellars", "picked clean by stone-robbers", "shored up with rotting timbers"],
    ("RUIN", "overgrown"): ["wrapped in old-man's-beard", "carpeted in moss", "pushed apart by tree roots", "strung with dog-rose", "shaggy with ferns", "smothered in bindweed"],
    ("RUIN", "carving"): ["a hare with a human face", "three linked rings", "a bearded king with his eyes scratched out", "a ship on stylised waves", "a tree whose roots are snakes",
                          "a dancing skeleton", "a long inscription, defaced", "a woman holding a lamp"],
    ("RUIN", "interior"): ["a cracked font holds black water", "bats hang in the rafters that remain", "someone has camped in the corner, long ago",
                           "a mosaic floor shows through the dirt", "a broken bell lies in the rubble", "frescoes flake from the walls"],
    # shrines
    ("SHRINE", "form"): ["rag-tree", "spring under a stone lintel", "ring of small stones", "carved stone head", "hollow oak", "clay figure in a niche", "wayside cross", "stone basin"],
    ("SHRINE", "spirit_pre"): ["Bright", "Little", "Saint", "Old Man", "Sister", "Blind", "Black", "Wise"],
    ("SHRINE", "spirit_name"): ["Aldwen", "Morrow", "Ethne", "Gorvan", "Tilda", "Bracca", "Oswy", "Senna", "Ludd", "Hywel"],
    ("SHRINE", "domain"): ["who keeps travellers from harm", "lady of the green springs", "who finds the lost", "guardian of the herds", "who carries the dying across",
                           "keeper of oaths", "who mends broken things", "watcher of the boundary stones"],
    ("SHRINE", "offerings"): ["Knots of hair", "Iron nails", "Smooth white pebbles", "Bread crusts", "Scraps of written prayer", "Wooden charms", "Little bundles of wool"],
}
LIST_POOLS = {
    ("E", "OCCUPATIONS_folk"): ["cooper", "potter", "tanner", "chandler's boy", "net-mender", "drover", "wise-woman", "carter", "fletcher",
                                "ploughman", "goose-girl", "hurdle-maker", "rat-catcher", "gravedigger", "tinsmith", "wheelwright"],
    ("E", "OCCUPATIONS_merchant"): ["packman", "cloth-seller", "spice-trader", "horse-coper"],
    ("E", "GIVEN"): ["Alys", "Beorn", "Cuthbert", "Dilys", "Eadric", "Frideswide", "Gilbert", "Hawise", "Idony", "Jocelyn", "Leofric", "Mabyn", "Nesta",
                     "Odo", "Petronel", "Ralf", "Sigrid", "Thurstan", "Wulfric", "Avice", "Benedict", "Cecily", "Drogo", "Elfrida", "Fulk", "Gunhild"],
    ("E", "SURNAME_PRE"): ["Fen", "Oak", "Moor", "Holly", "Rook", "Barrow", "Ditch", "Gold", "Crow", "Ash", "Lark", "Reed"],
    ("E", "SURNAME_SUF"): ["wick", "stead", "hayes", "thwaite", "cote", "bridge", "more", "wood", "hurst", "low"],
    ("E", "AGE"): ["youthful", "greying", "white-haired", "careworn", "ageless-seeming", "silver-haired", "time-worn", "fresh-faced"],
    ("E", "BUILD"): ["rawboned", "willowy", "barrel-chested", "hunched", "lanky", "compact", "heavy-handed", "slight"],
    ("E", "HAIR"): ["copper curls tied back with string", "hair cropped close for lice", "a single thick braid", "a tangle of iron-grey hair", "hair the colour of wet sand",
                    "a fringe cut straight across", "a balding crown and a fierce beard", "dark hair streaked with white", "hair hidden under a felt cap"],
    ("E", "CLOTHES"): ["a smock patched at both elbows", "a coat sewn from mismatched hides", "a good wool cloak gone thin at the hem", "a dyer's stained apron",
                       "clogs and a heavy russet gown", "a soldier's old jerkin", "a shawl knitted in bright stripes", "a rough hemp tunic"],
    ("E", "MARK"): ["one blue eye and one brown", "a laugh like a crow's", "a habit of humming", "fingers missing from one hand", "a tattooed line across the chin",
                    "a pipe that never seems to go out", "a quiet, watchful stillness", "freckles like spilled grain", "a slow, careful way of speaking",
                    "a limp from an old break", "a silver ring worn on a thumb"],
    ("E", "RELIC_NOUN"): ["bell", "cup", "comb", "spindle", "circlet", "shield-boss", "key", "book", "staff", "brooch", "drinking horn", "censer"],
    ("E", "RELIC_ADJ"): ["Winter", "Singing", "Bloodless", "Starlit", "Hearthfire", "Quiet", "Thousand-Year", "Wyrm-Bound", "Salt", "Morning", "Unsleeping", "Iron"],
    ("L", "NAME_PRE"): ["Ald", "Bly", "Cran", "Dray", "Egg", "Frith", "Gort", "Holm", "Ickle", "Kell", "Lang", "Mal", "Nor", "Pen", "Quen", "Ris", "Sel", "Tor", "Ulver", "Wend", "Yar", "Swal", "Thrim", "Bleak"],
    ("L", "NAME_SUF"): ["hythe", "garth", "wold", "fold", "barrow", "minster", "hope", "shaw", "beck", "marsh", "heath", "field", "wich", "nell", "grave", "toft"],
    ("L", "NAME_ADJ"): ["Forgotten", "Moaning", "Restless", "Briar", "Raven's", "Broken", "Burning", "Hushed", "Fallow", "Thorny", "Witching", "Gallows", "Sunken", "Hollowed"],
}

_APPLIED = False


def apply_fact_pools(L, E):
    """Extend the generators' fact pools (once)."""
    global _APPLIED
    if _APPLIED:
        return
    _APPLIED = True
    tables = {"VILLAGE": E.VILLAGE, "RUIN": E.RUIN, "SHRINE": E.SHRINE}
    for (table, key), values in FACT_POOLS.items():
        pool = tables[table].setdefault(key, [])
        pool.extend(v for v in values if v not in pool)
    mods = {"E": E, "L": L}
    for (mod, name), values in LIST_POOLS.items():
        if name.startswith("OCCUPATIONS_"):
            pool = E.OCCUPATIONS[name.split("_", 1)[1]]
        else:
            pool = getattr(mods[mod], name)
        pool.extend(v for v in values if v not in pool)


# ---------------------------------------------------------------- the sky after dark
# Used instead of the ordinary weather lines from evening until dawn, so a clear
# night is described by stars and cold rather than blue sky and crisp shadows.
DARK = {
    "dark_clear:weather_line": ["The sky is clear and full of stars.", "Not a cloud hides the stars tonight.", "The night is clear and sharp with cold.",
                                "Stars crowd the sky, more than you could ever count.", "The sky is open and black and glittering."],
    "dark_clear:weather_detail": ["Your breath shows in the starlight.", "The cold sharpens as the last warmth leaves the ground.",
                                  "Every star burns hard and steady.", "Without cloud, the night grows colder by the hour."],
    "dark_cloudy:weather_line": ["Clouds slide across the stars, hiding and showing them.", "Ragged cloud hurries across the dark.",
                                 "Stars appear in the gaps between clouds, then vanish again.", "The night sky is patched with cloud."],
    "dark_cloudy:weather_detail": ["Now and then a gap in the cloud lets a little starlight through.", "The darkness thickens and thins as the clouds pass."],
    "dark_overcast:weather_line": ["Cloud has shut out every star.", "The sky is a lid of black cloud.", "There is no sky at all, only a low, starless dark.",
                                   "Thick cloud smothers the night."],
    "dark_overcast:weather_detail": ["It is as dark as the inside of a sack.", "Without moon or stars you have to feel your way."],
    "dark_drizzle:weather_line": ["A fine drizzle falls, unseen in the dark.", "Drizzle drifts out of the blackness.", "The night is wet with a thin, cold drizzle."],
    "dark_drizzle:weather_detail": ["You feel the drizzle more than you see it.", "Damp creeps into everything in the dark."],
    "dark_rain:weather_line": ["Rain falls out of the darkness, hard and cold.", "The rain comes down steady and unseen.", "Rain hisses in the dark all around you."],
    "dark_rain:weather_detail": ["You can hear the rain far better than you can see it.", "Water runs underfoot in the dark."],
    "dark_storm:weather_line": ["Lightning rips the night open, and then the dark slams shut again.", "Thunder rolls through the black night.",
                                "The storm howls in the dark, and the rain comes sideways."],
    "dark_storm:weather_detail": ["Each flash shows the land for an instant, white and strange.", "Between flashes you are blind."],
    "dark_fog:weather_line": ["Fog and darkness together leave you almost blind.", "The night fog presses close and cold.", "Fog fills the dark like wet wool."],
    "dark_fog:weather_detail": ["You can barely see your own hands.", "Sounds come muffled and from nowhere in the fog."],
    "dark_wind:weather_line": ["The wind moans through the dark.", "A cold night wind gusts and drops.", "The wind is loud in the dark."],
    "dark_wind:weather_detail": ["Unseen things creak and knock in the wind.", "The wind snatches at your cloak in the darkness."],
    "dark_snow:weather_line": ["Snow falls silently through the dark.", "Snowflakes drift out of the night.", "The snow glows faintly, the only light there is."],
    "dark_snow:weather_detail": ["The snow muffles every sound.", "Snow gathers on your shoulders in the dark."],
}
