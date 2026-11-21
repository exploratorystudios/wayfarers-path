"""Landscape & atmosphere vocabulary.

Conventions: lowercase symbols ending in a noun phrase are fragments; symbols
named *_line, opening, smalllife are complete sentences.
Scope prefixes: biome (forest, marsh, plains, hills, peaks, lake), season,
weather, time, "<time>_<bright|dull>", mood.
"""

RULES = {
    # ------------------------------------------------------------------ shared
    "dim": ["dim", "dusky", "grey", "shadowed", "muted", "hazy", "uncertain"],
    "vast": ["vast", "broad", "sweeping", "endless-seeming", "wide", "open"],
    "old": ["old", "ancient", "age-worn", "weathered", "time-gnawed", "venerable"],
    "quiet_adj": ["hushed", "still", "quiet", "muffled", "drowsy", "breathless"],
    "colour_grey": ["slate", "pewter", "ash", "dove-grey", "iron-grey", "smoke-grey"],
    "autumn_colour": ["copper", "amber", "rust", "ox-blood", "tawny gold", "burnt orange", "russet"],
    "far": ["far off", "in the distance", "somewhere beyond sight", "a long way off", "faintly"],
    "you_notice": ["You notice", "You spot", "Your eye falls on", "You make out", "There is", "Nearby is"],

    # ------------------------------------------------------------- seasons
    "spring:leaves": ["new leaves pale as lime peel", "tight green buds", "fresh, almost luminous foliage", "leaves still crumpled from the bud"],
    "summer:leaves": ["heavy, dark summer leaves", "dense green leaf", "dusty midsummer foliage", "full-grown leaves"],
    "autumn:leaves": ["{autumn_colour} leaves", "leaves turning {autumn_colour}", "foliage gone {autumn_colour} and brittle", "the last {autumn_colour} leaves"],
    "winter:leaves": ["a few dead, rattling leaves", "frost-blackened leaves", "bare twigs", "nothing but bare wood"],
    "spring:bloom": ["primroses", "wood anemones", "celandines", "violets", "blackthorn blossom"],
    "summer:bloom": ["foxgloves", "meadowsweet", "campion", "dog-roses", "willowherb"],
    "autumn:bloom": ["late scabious", "the seedheads of thistles", "rose-hips", "michaelmas daisies", "haws red as blood-drops"],
    "winter:bloom": ["frost-rimed seedheads", "a few stubborn snowdrops", "brittle dead stalks", "holly berries", "crusts of hoarfrost"],
    "spring:season_line": ["The air carries the sappy restlessness of spring.", "Everything here seems freshly made, raw and green.", "Spring is only half-awake here, the green still tentative."],
    "summer:season_line": ["High summer has made the land heavy and drowsy.", "Insects drone in the thick summer air.", "The season's heat lingers in everything you touch."],
    "autumn:season_line": ["Autumn is gnawing at the edges of things.", "There is a smell of endings in the autumn air.", "The year is clearly turning toward its close."],
    "winter:season_line": ["Winter has stripped the land down to its bones.", "The cold gets into your joints and settles there.", "Your breath smokes in the winter air."],

    # ------------------------------------------------------------- weather
    "clear:weather_line": ["The sky is clear, scrubbed clean of cloud.", "Not a cloud mars the sky.", "The air is clean and sharp, the sky open.", "Visibility is good; the sky is clear and wide."],
    "cloudy:weather_line": ["Clouds drift overhead in slow, ragged herds.", "Patches of blue show between heaped clouds.", "Cloud-shadows slide across the land.", "The sky is a patchwork of cloud and brief light."],
    "overcast:weather_line": ["A lid of {colour_grey} cloud presses down on everything.", "The sky is a single unbroken sheet of {colour_grey}.", "Low cloud has swallowed the sky whole.", "The overcast flattens every colour."],
    "drizzle:weather_line": ["A fine drizzle hangs in the air, more felt than seen.", "Drizzle beads on your sleeves and eyelashes.", "A thin, persistent drizzle soaks everything slowly.", "The air is full of a soft, needling drizzle."],
    "rain:weather_line": ["Rain falls steadily, drumming on every surface.", "Rain hisses down in long grey ropes.", "The rain is relentless, and water finds its way down your collar.", "Rain sweeps across the land in curtains."],
    "storm:weather_line": ["Thunder grinds overhead and the rain comes sideways.", "A storm is breaking: wind howls and lightning stitches the clouds.", "The storm batters you; every gust feels like a shove.", "Lightning flickers, and the thunder that follows rattles your teeth."],
    "fog:weather_line": ["Fog has stolen the world beyond a few dozen paces.", "A thick fog muffles sound and swallows distance.", "Shapes loom out of the fog and dissolve again.", "The fog is cold and wet against your face."],
    "wind:weather_line": ["A hard wind tugs at your clothes.", "The wind is up, gusting and veering without warning.", "Wind roars past your ears, carrying grit and leaves.", "A restless wind combs the land."],
    "snow:weather_line": ["Snow falls in slow, fat flakes.", "Snow drifts down, softening every edge.", "Fine snow whirls in the air.", "The snow falls thick, muffling the world."],

    # ------------------------------------------------------------- light by time
    "dawn_bright:light_line": ["The sun is just lifting, laying long {dawn_colour} light across the land.", "Dawn spills over the horizon, gilding every edge.", "First light paints the world in {dawn_colour} and blue.", "The early sun throws your shadow out impossibly long."],
    "dawn_dull:light_line": ["Dawn arrives grudgingly, a slow greying of the dark.", "The light grows without ever quite becoming day.", "A sullen dawn seeps through the murk."],
    "dawn_colour": ["rose", "apricot", "pale gold", "salmon-pink", "honey"],
    "morning_bright:light_line": ["Morning light is clean and bright.", "The morning sun warms your face.", "Bright morning light picks out every detail."],
    "morning_dull:light_line": ["The morning light is flat and colourless.", "It is morning, though the light hardly admits it.", "A grey morning light lies over everything."],
    "midday_bright:light_line": ["The sun stands high, and shadows have shrunk to puddles at your feet.", "Noon light glares down without mercy.", "It is midday; the light is hard and white."],
    "midday_dull:light_line": ["It is midday, but the sun is only a pale smear behind the murk.", "Noon brings no warmth, only a brighter grey.", "The day has reached its height, such as it is."],
    "afternoon_bright:light_line": ["Afternoon light slants warm and golden.", "The sun has begun its long slide westward.", "The light is mellow, the shadows lengthening."],
    "afternoon_dull:light_line": ["The afternoon drags on beneath a dull sky.", "The light of the afternoon is already tiring.", "A drab afternoon light hangs over the land."],
    "dusk_bright:light_line": ["The sun is sinking in a blaze of {dusk_colour}.", "Dusk gathers; the western sky burns {dusk_colour}.", "The last light turns everything {dusk_colour} before it fails.", "Long shadows reach eastward as the sun goes down."],
    "dusk_dull:light_line": ["Dusk comes on early, the grey thickening into gloom.", "The light drains away without ceremony.", "Twilight seeps in from every side."],
    "dusk_colour": ["crimson", "molten copper", "violet and gold", "bruised purple", "ember-orange"],
    "evening_bright:light_line": ["The sky has deepened to indigo, and the first stars prick through.", "Evening has come; the west still holds a seam of light.", "{moon_line}"],
    "evening_dull:light_line": ["Evening darkness closes in, starless and damp.", "It is growing dark, and the cloud hides any hope of stars.", "The evening murk makes shapes hard to judge."],
    "night_bright:light_line": ["{moon_line}", "Stars crowd the sky, cold and numberless.", "The night is clear; the stars wheel overhead.", "{moon_line} Stars scatter the dark around it."],
    "night_dull:light_line": ["The night is thick and moonless; you can barely see your hands.", "Darkness presses in, absolute beneath the cloud.", "It is night, and the cloud has smothered every star.", "You move almost blind through the overcast dark."],
    "deepnight_bright:light_line": ["It is the dead hour of the night. {moon_line}", "The stars have turned far round; dawn is still hours away.", "The deep of night holds everything still. {moon_line}"],
    "deepnight_dull:light_line": ["It is the darkest part of the night, and the dark is total.", "The small hours drag past in a smothering black.", "Nothing moves in the heavy dark of the deep night."],

    # ------------------------------------------------------------- moods
    "eerie:mood_line": ["Something about this place makes the skin on your neck prickle.", "You have the uneasy sense of being watched.", "Even the silences here feel deliberate.", "The place feels like it is holding its breath."],
    "serene:mood_line": ["There is a deep, unhurried peace here.", "For a moment the world seems kind.", "It is the sort of place where shoulders loosen of their own accord.", "Calm settles over you like a cloak."],
    "desolate:mood_line": ["It is a lonely place, empty of comfort.", "Nothing here seems to care whether you live or die.", "The emptiness is almost a presence in itself.", "You feel very small and very far from anywhere."],
    "lush:mood_line": ["Life crowds in from every side, green and teeming.", "Everything here grows with a kind of greedy vigour.", "The place hums with small, busy life."],
    "ominous:mood_line": ["A sense of threat hangs over the place.", "Your hand drifts toward your weapon without being told.", "Something happened here once, and the land remembers.", "The air feels heavy, as if before a storm."],

    # =================================================================== FOREST
    "forest:tree": ["oak", "beech", "ash", "hornbeam", "yew", "birch", "alder", "elm", "lime", "rowan", "sweet chestnut"],
    "forest:canopy": ["a canopy so dense that the light arrives green and secondhand", "{tree} boughs locked overhead into a vaulted roof", "high branches that sway and creak", "a ceiling of {leaves}", "a lattice of limbs heavy with {leaves}"],
    "forest:winter:canopy": ["bare {tree} limbs scratching at the sky", "a tangle of leafless branches", "a skeletal canopy hung with dripping twigs", "black boughs etched against the sky"],
    "forest:autumn:canopy": ["{tree} boughs burning {autumn_colour}", "a canopy shedding {autumn_colour} leaves with every breath of wind", "branches thinning to a {autumn_colour} lace"],
    "forest:ground": ["a deep litter of {litter}", "soft loam threaded with roots", "moss so thick it swallows your footsteps", "a carpet of {floorplant}", "black earth stippled with {fungus}", "a mat of twigs and old leaves", "roots that knot and buckle the path"],
    "forest:winter:ground": ["frozen leaf litter that crunches like glass", "hard earth glazed with frost", "{litter} rimed with hoarfrost", "a thin crust of snow over roots and rot"],
    "forest:litter": ["last year's leaves", "beech mast", "acorn cups", "broken twigs", "curled {tree} leaves"],
    "forest:floorplant": ["bluebells", "wild garlic", "dog's mercury", "wood sorrel", "ferns", "ivy"],
    "forest:winter:floorplant": ["dead bracken", "brown, collapsed ferns", "ivy", "frost-blackened nettles"],
    "fungus": ["pale toadstools", "bracket fungus", "ink-caps", "orange rust-cups", "puffballs", "wrinkled black jelly fungus", "chanterelles"],
    "forest:undergrowth": ["brambles", "holly thickets", "bracken taller than your waist", "hazel scrub", "tangled honeysuckle", "young saplings fighting for light"],
    "forest:flora_line": ["{tree.s.cap} crowd close, their trunks {trunk_desc}.", "Between the trunks grow {undergrowth} and, here and there, {bloom}.", "{undergrowth.cap} chokes the spaces between the {tree.s}.", "You look up into {canopy}.", "The {tree.s} here are {old}, their trunks {trunk_desc}.", "The wood is mostly {tree}, with the odd {tree} pushing through."],
    "trunk_desc": ["furred with moss", "silvered with lichen", "split by old lightning", "wound about with ivy", "scarred where deer have stripped the bark", "thick as cottage chimneys", "pale and smooth as bone", "fissured like old leather"],
    "forest:sound": ["a woodpecker drumming somewhere out of sight", "the creak of limbs rubbing together", "the endless whisper of leaves", "a wood pigeon's throaty, repeating call", "twigs snapping under some unseen animal", "a wren scolding from the undergrowth", "the drip of water from leaf to leaf"],
    "forest:night:sound": ["a tawny owl calling, answered from far off", "the scuffle of something small in the leaves", "the creak of branches in the dark", "a vixen's scream, raw and unsettling"],
    "forest:deepnight:sound": ["an owl's quavering call", "a rustling that stops when you stop", "the slow groan of a settling tree"],
    "forest:smell": ["leaf mould and damp bark", "the sharp green tang of crushed fern", "fungus and old rain", "resin and wet earth", "wild garlic, pungent underfoot", "rotting wood, sweet and heavy"],
    "forest:smalllife": ["A squirrel freezes on a trunk, then pours itself around to the far side.", "A jay shrieks an alarm and flashes away through the branches.", "Midges dance in a shaft of light.", "A beetle trundles across a fallen leaf, glossy as a jewel.", "Somewhere, a deer crashes off through the undergrowth.", "A spider's web, strung between two saplings, is beaded with moisture."],
    "forest:winter:smalllife": ["A squirrel freezes on a trunk, then pours itself around to the far side.", "A jay shrieks an alarm and flashes away through the branches.", "A wren ticks at you from a heap of dead bracken.", "Somewhere, a deer crashes off through the undergrowth.", "A robin follows you a little way, hoping you'll turn up something to eat."],
    "forest:vista": ["Between the trunks the wood recedes into {dim} ranks of grey pillars.", "The trees go on in every direction, swallowing distance.", "You cannot see more than a stone's throw for the press of trunks.", "Shafts of light fall through gaps in the canopy like slanted columns."],
    "forest:opening": ["You stand among {tree.s}, beneath {canopy}.", "The wood closes around you.", "You are deep among the trees.", "Trees rise on every side, {old} and silent.", "The path, such as it is, threads between {tree} trunks.", "You push through into a stretch of {tree} woodland."],
    "forest:glimpse": ["a dark wall of {tree.s}", "the shadowed eaves of a wood", "a ragged treeline", "woodland thickening into gloom", "the edge of a {tree} wood"],
    "forest:continues": ["the wood goes on, trunk after trunk", "the trees crowd closer still", "more forest, much the same", "the woodland stretches on"],

    # =================================================================== MARSH
    "marsh:ground": ["sucking black mud", "spongy moss that quakes under your weight", "tussocks of sedge with brown water between", "a rotten causeway of half-sunk logs", "peat that oozes water at every step", "a crust of dried mud over who-knows-what"],
    "marsh:winter:ground": ["mud frozen into ruts and ridges", "ice-skinned pools between stiff tussocks", "frost-bitten sedge over half-frozen peat"],
    "marsh:plant": ["reeds", "bulrushes", "sedge", "bog myrtle", "cotton-grass", "sphagnum moss", "marsh marigolds", "stunted willows"],
    "marsh:flora_line": ["{plant.cap} grow in dense ranks, rattling faintly.", "Stands of {plant} rise from the water, and {plant} crowds the margins.", "Here and there a stunted {marsh_tree} leans out of the mire, {trunk_desc}.", "Pools of dark water lie between islands of {plant}.", "The water is skinned with duckweed and {pool_desc}."],
    "marsh_tree": ["alder", "willow", "birch", "black poplar"],
    "pool_desc": ["oily rainbows", "the reflection of a {colour_grey} sky", "drowned leaves", "bubbles that rise from somewhere deep", "a film of pollen"],
    "marsh:sound": ["frogs croaking in a ragged chorus", "the boom of a bittern, like breath across a jug", "the slow plop of rising gas", "reeds hissing against each other", "the whine of mosquitoes", "the gurgle of water moving underground"],
    "marsh:winter:sound": ["the creak of ice settling", "the dry rattle of dead reeds", "a heron's harsh croak"],
    "marsh:night:sound": ["frogs, loud and endless", "a splash out in the dark", "the sucking of mud settling"],
    "marsh:smell": ["rot and stagnant water", "the eggy reek of marsh gas", "wet peat and bog myrtle", "mud, green and fecund", "decaying reeds"],
    "marsh:smalllife": ["A heron lifts away on slow, ragged wings.", "Water boatmen skate across a still pool.", "Something long and dark slides off a tussock into the water.", "A dragonfly hangs motionless, then is simply gone.", "Bubbles rise and burst in a pool beside you.", "A frog leaps from under your foot with a plop."],
    "marsh:winter:smalllife": ["A heron stands motionless at the edge of the ice.", "Crows squabble over something half-frozen in the mud.", "A snipe bursts up from the sedge and zigzags away."],
    "plains:winter:smalllife": ["A hare in its winter coat bolts from almost under your feet.", "Rabbits scatter for their burrows, white tails flashing.", "A kestrel hangs on the wind, wings trembling, watching the grass.", "A flock of fieldfares clacks up from a thorn and settles further off.", "Crows walk the frozen ground, stabbing at it."],
    "marsh:vista": ["The marsh stretches away flat and featureless, glinting with water.", "Reeds rise taller than your head, closing off any view.", "Mist clings low over the distant pools.", "A line of pollarded willows marks some forgotten boundary in the distance."],
    "marsh:opening": ["You are in the marsh, where land and water have never settled their quarrel.", "The ground turns treacherous; you have come into the fen.", "Mud and reeds stretch around you.", "You pick your way through boggy ground.", "The air thickens as you wade into the mire.", "You stand on a hummock of firmer ground amid the marsh."],
    "marsh:glimpse": ["a reed-choked fen", "flat, glistening marshland", "a stretch of bog bristling with reeds", "wet ground and dark pools", "the grey sprawl of a mire"],
    "marsh:continues": ["the marsh goes on, wet and unforgiving", "more reeds and treacherous pools", "the mire stretches onward", "the ground stays sodden"],

    # =================================================================== PLAINS
    "plains:ground": ["springy turf", "tussocky grass", "thin soil over chalk", "close-cropped grass dotted with rabbit droppings", "heather and wiry bilberry", "a sheep-track worn bare and hard"],
    "plains:winter:ground": ["frozen turf, white with frost", "brittle, frost-silvered grass", "a skim of snow over tussocks"],
    "plains:grass": ["long grass", "heather", "gorse", "bracken", "ox-eye daisies", "harebells", "rough pasture"],
    "plains:flora_line": ["The wind sends long waves rolling through the {grass}.", "Clumps of gorse, {gorse_state}, break up the {grass}.", "A lone {lone_tree} stands in the open, {lone_desc}.", "The open land is spotted with {bloom}.", "{grass.cap} and {grass} cover the gentle swells of the land."],
    "gorse_state": ["yellow with coconut-scented flowers", "black and spiky", "humming with bees", "burnt to stumps by some old fire"],
    "lone_tree": ["hawthorn", "oak", "ash", "crab apple", "pine"],
    "lone_desc": ["bent permanently away from the wind", "its branches hung with sheep's wool", "dead on one side and green on the other", "a crow perched in its crown", "older than any village you know"],
    "plains:sound": ["a skylark pouring out song high overhead", "the hiss of wind through grass", "the bleat of distant sheep", "the hum of bees in the gorse", "a buzzard mewing as it circles", "nothing but wind"],
    "plains:night:sound": ["the wind, and nothing else", "a fox barking far off", "the churr of a nightjar", "crickets in the grass"],
    "plains:smell": ["warm grass and thyme", "sheep and wild herbs", "gorse, sweet as coconut", "clean wind", "crushed chamomile underfoot"],
    "plains:winter:smell": ["frost and distant woodsmoke", "cold, clean wind", "damp earth"],
    "plains:smalllife": ["A hare bolts from almost under your feet, jinking away.", "Rabbits scatter for their burrows, white tails flashing.", "A kestrel hangs on the wind, wings trembling, watching the grass.", "Grasshoppers ricochet away from your boots.", "A flock of starlings wheels overhead in a single shape-changing mass."],
    "plains:vista": ["The land opens out, and you can see for miles.", "Under the great bowl of sky, the land rolls away in gentle swells.", "The horizon is wide and low, broken only by the odd tree.", "Burial mounds hump the skyline in the distance."],
    "plains:opening": ["You walk across open country.", "The land opens out around you into rolling grassland.", "You are on open heath, exposed to the sky.", "The wind finds you at once on this open ground.", "You stand on a broad, grassy rise.", "Open downland surrounds you."],
    "plains:glimpse": ["open grassland", "rolling heath", "a broad swell of downland", "wind-combed pasture", "a stretch of open moor"],
    "plains:continues": ["the open land rolls onward", "more grass and sky", "the heath goes on", "the downs roll away"],

    # =================================================================== HILLS
    "hills:ground": ["stony ground and thin grass", "a scree-scattered slope", "bracken over loose rock", "a sheep-path cut into the hillside", "outcrops of grey stone poking through the turf", "rough heather over hidden boulders"],
    "hills:winter:ground": ["iced rock and frozen turf", "snow-crusted stones", "slick, frozen scree"],
    "hills:flora_line": ["Bracken clothes the slopes, {bracken_state}.", "Lichen crusts the boulders in {lichen_colour} rosettes.", "Wind-stunted thorn trees cling to the slope.", "Heather and bilberry fight for the thin soil.", "A drystone wall, {wall_state}, runs straight up the hill and over it."],
    "bracken_state": ["green and head-high", "rust-brown and rattling", "crushed flat where something has slept", "uncurling in tight fists"],
    "lichen_colour": ["mustard-yellow", "sage-green", "orange", "bone-white", "grey-green"],
    "wall_state": ["tumbled in places", "furred with moss", "built by hands long dead", "patched with newer stone"],
    "hills:sound": ["a raven's guttural croak", "the trickle of water off the hillside", "the wind keening over the ridge", "stones clattering somewhere upslope", "a curlew's bubbling cry"],
    "hills:smell": ["wet stone and sheep", "thyme crushed underfoot", "peat and rain", "clean, thin air"],
    "hills:smalllife": ["A wheatear flits from rock to rock ahead of you.", "Sheep stare at you, then go back to their grazing.", "A raven tumbles through the air, apparently for the fun of it.", "A lizard flicks off a warm stone into a crevice."],
    "hills:winter:smalllife": ["Sheep stare at you, then go back to their grazing.", "A raven tumbles through the air, apparently for the fun of it.", "Sheep huddle in the lee of a wall, backs to the wind.", "A buzzard sits hunched on a fence-post and lets you pass."],
    "hills:vista": ["From up here you can see the land spread out below like a map.", "Ridges fold one behind another, each paler than the last.", "The hills roll away, green and grey, into the distance.", "Far below, a stream glints in its valley."],
    "hills:opening": ["You climb through hill country.", "The land rises and folds around you into hills.", "You are on a hillside, breathing hard.", "You crest a ridge among the hills.", "Hills hump around you, scarred with stone."],
    "hills:glimpse": ["rising hills", "a stony ridge", "green slopes climbing away", "the shoulder of a hill", "hill country, grey with stone"],
    "hills:continues": ["the hills go on, ridge after ridge", "more slopes, more stone", "the high ground continues", "the land keeps folding upward"],

    # =================================================================== PEAKS
    "peaks:ground": ["bare rock, cracked by frost", "shifting scree", "a narrow ledge above a sheer drop", "ice-polished slabs", "gravel and shattered stone"],
    "peaks:flora_line": ["Almost nothing grows here but lichen and {alpine_plant}.", "A few cushions of {alpine_plant} cling to cracks in the rock.", "A single twisted pine grows from a crack, defying everything.", "The rock is bare, scoured by wind and ice."],
    "alpine_plant": ["moss campion", "saxifrage", "thrift", "dwarf willow", "wiry grass"],
    "peaks:sound": ["the wind howling between the crags", "the crack and rattle of falling stones", "an eagle's thin scream", "a deep, ringing silence", "meltwater dripping from an overhang"],
    "peaks:smell": ["cold stone and snow", "thin, metallic air", "nothing at all, only cold"],
    "peaks:smalllife": ["An eagle circles far overhead, lazy and patient.", "A chough flips past on red legs, calling.", "Pebbles skitter down from somewhere above.", "A mountain hare in mottled coat freezes, then bounds away."],
    "peaks:vista": ["The world falls away beneath you, dizzying and vast.", "Clouds drift past below the level of your feet.", "Jagged summits march away like broken teeth.", "The view is enormous, the air so clear it hurts."],
    "peaks:opening": ["You are high among the crags.", "The mountains rear around you, gaunt and cold.", "You clamber through a landscape of naked rock.", "Wind and stone - there is little else up here.", "You stand on a high, exposed shoulder of mountain."],
    "peaks:glimpse": ["jagged peaks", "a wall of grey crags", "mountains, snow-streaked and stark", "towering cliffs", "the rising teeth of the mountains"],
    "peaks:continues": ["the crags go on, higher and colder", "more rock and wind", "the peaks rise further still"],

    # =================================================================== LAKE (seen, not entered)
    "lake:glimpse": ["open water, {lake_surface}", "the shore of a wide lake", "a mere stretching off grey and cold", "deep water lapping at a stony shore", "a lake, {lake_surface}"],
    "lake_surface": ["ruffled by wind", "flat as beaten pewter", "glittering in the light", "dark and unreadable", "rippled by rising fish", "fringed with reeds"],

    # =================================================================== exits & framing
    "exit_same": ["To the {dirs}, {continues}.", "{dirs.cap}, {continues}.", "Heading {dirs}, {continues}."],
    "exit_diff": ["To the {dirs}, you see {glimpse}.", "Looking {dirs}, you can make out {glimpse}.", "The way {dirs} leads toward {glimpse}.", "{dirs.cap}, the land gives way to {glimpse}.", "Away to the {dirs} is a view of {glimpse}."],
    "exit_diff_named": ["To the {dirs} the way opens onto {glimpse} - {region}.", "{dirs.cap}, you can make out {glimpse}; folk call it {region}.", "The way {dirs} leads into {region}, {glimpse}."],
    "exit_water": ["To the {dirs}, {glimpse} bars the way.", "{dirs.cap} there is only {glimpse}; you cannot go that way.", "{glimpse.cap} blocks any path to the {dirs}."],

    "sense_sound": ["You hear {sound}.", "The only sound is {sound}.", "From {far} comes {sound}.", "Somewhere close, {sound}.", "{sound.cap} fills the air.", "Listening, you pick out {sound}."],
    "sense_smell": ["The air smells of {smell}.", "You catch the scent of {smell}.", "It smells of {smell} here.", "A breath of {smell} drifts past."],
    "terrain": ["You pick your way over {ground}.", "Your boots find {ground}.", "You tread carefully across {ground}.", "Your path crosses {ground}.", "Every step lands on {ground}.", "You make your way over {ground}."],
}

# Feature archetypes: fixed facts chosen at world generation, re-phrased on every look.
FEATURES = {
    "forest": [
        dict(kind="fallen tree", noun=["oak", "beech", "elm", "ash"], adj=["fallen", "uprooted", "storm-felled"], adj2=["moss-furred", "rotting", "beetle-bored", "huge"],
             verb=["lies", "sprawls"], where=["across the path", "among the bracken", "in the gap it tore in the canopy"],
             detail=["its root-plate standing taller than a man", "its bark sloughing off in great plates", "shelves of bracket fungus climbing its flank", "a pool of rainwater gathered in its torn roots", "nettles growing thickly where it fell"]),
        dict(noun=["stream", "brook", "rill"], adj=["clear", "peat-brown", "chattering", "sluggish"], adj2=["narrow", "shallow", "stony"],
             verb=["runs", "winds", "trickles"], where=["through a shallow gully", "between mossy banks", "over a bed of pebbles"],
             detail=["watercress thick along its edges", "small trout flicking in its pools", "an old stepping-stone crossing half sunk", "its banks undercut and tangled with roots"]),
        dict(noun=["ring of toadstools", "fairy ring", "circle of mushrooms"], adj=["perfect", "pale", "spotted red"], adj2=["unsettling", "wide", "dew-wet"],
             verb=["grows", "spreads"], where=["in a small clearing", "around the base of an old oak", "on a patch of bare earth"],
             detail=["the grass inside it strangely untrodden", "no leaves fallen within its border", "a faint sweet smell rising from it", "a single white feather lying at its centre"]),
        dict(noun=["charcoal-burner's mound", "charcoal clamp"], adj=["abandoned", "cold", "grass-grown"], adj2=["low", "blackened"],
             verb=["sits", "squats"], where=["in a cleared hollow", "beside a stack of rotten cordwood", "at the edge of the trees"],
             detail=["the soil around it still black", "a broken rake leaning against it", "nettles thriving in the rich ash", "a smell of old burning clinging to it"]),
        dict(noun=["yew", "oak"], adj=["hollow", "colossal", "split"], adj2=["ancient", "gnarled", "sprawling"],
             verb=["stands", "towers", "broods"], where=["alone in a clearing", "where two paths meet", "at the heart of the grove"],
             detail=["a hollow at its base big enough to shelter in", "rags and ribbons tied to its lower boughs", "initials carved into its bark by many hands", "a woodpecker's holes stitching its trunk"]),
    ],
    "marsh": [
        dict(noun=["causeway", "trackway"], adj=["sunken", "half-drowned", "timber"], adj2=["ancient", "rotten", "slippery"],
             verb=["runs", "snakes", "stretches"], where=["out across the bog", "between the pools", "into the reeds"],
             detail=["its planks black and soft as cheese", "posts at intervals carved with worn faces", "gaps where the timbers have sunk away entirely", "green slime coating every surface"]),
        dict(noun=["pool", "mere", "sump"], adj=["black", "still", "bottomless-looking"], adj2=["wide", "deep", "stagnant"],
             verb=["lies", "spreads", "waits"], where=["among the sedge", "at the foot of a hummock", "where the ground dips"],
             detail=["its surface unbroken by any ripple", "bubbles rising lazily from its depths", "bones of some animal visible in the shallows", "lily pads crowding its edges"]),
        dict(noun=["willow", "alder"], adj=["drowned", "pollarded", "leaning"], adj2=["skeletal", "pale", "twisted"],
             verb=["stands", "leans", "crouches"], where=["out in the water", "on a mud bank", "over a channel"],
             detail=["its roots exposed like grasping fingers", "a heron's untidy nest in its crown", "its bark peeled away to grey wood", "strands of weed hanging from its branches"]),
        dict(noun=["peat cutting", "turf bank"], adj=["old", "flooded", "abandoned"], adj2=["square-edged", "deep"],
             verb=["lies", "opens"], where=["beside the path", "in the side of a hummock", "a little way off"],
             detail=["a rusted spade left stuck in its wall", "neat stacks of turf rotting beside it", "brown water filling its bottom", "the tool marks still sharp on its sides"]),
    ],
    "plains": [
        dict(noun=["standing stone", "menhir"], adj=["tall", "leaning", "lichen-crusted"], adj2=["lonely", "weathered", "ancient"],
             verb=["stands", "rises", "leans"], where=["on a low crest", "alone in the grass", "beside the track"],
             detail=["worn spirals carved into its face", "a hollow at its foot full of small offerings", "sheep-wool snagged on its rough edges", "a crack running down its length"]),
        dict(noun=["barrow", "burial mound"], adj=["long", "grassy", "round"], adj2=["low", "rabbit-holed", "ancient"],
             verb=["humps", "rises", "lies"], where=["against the skyline", "close by the track", "in a hollow of the land"],
             detail=["a sunken entrance blocked by fallen stone", "a ring of small stones around its base", "rabbit-scrapes turning up pale chalk", "a hawthorn growing from its summit"]),
        dict(noun=["track", "drove road"], adj=["old", "rutted", "sunken"], adj2=["broad", "grassy", "empty"],
             verb=["runs", "crosses", "winds"], where=["across the open land", "away over the downs", "between low banks"],
             detail=["cart-ruts deep enough to twist an ankle", "hoofprints pressed into the mud", "a milestone with its numbers worn away", "hawthorn hedges grown wild along it"]),
        dict(noun=["dew pond", "pond"], adj=["round", "shallow", "still"], adj2=["clay-lined", "small", "reflecting"],
             verb=["lies", "sits", "shines"], where=["in a shallow dip", "at the foot of the rise", "near the track"],
             detail=["the ground around it trampled by hooves", "its surface holding the sky", "a moorhen paddling across it", "rushes crowding one side"]),
    ],
    "hills": [
        dict(noun=["cairn", "pile of stones"], adj=["tall", "tumbled", "conical"], adj2=["grey", "lichened", "careful"],
             verb=["stands", "rises", "sits"], where=["on the summit", "at the top of the path", "on a shoulder of the hill"],
             detail=["every stone placed by a passing hand", "a flat capstone balanced on top", "a few coins wedged between the stones", "a sheltered side where someone has slept"]),
        dict(noun=["waterfall", "force", "cascade"], adj=["small", "roaring", "slender"], adj2=["white", "cold", "noisy"],
             verb=["falls", "tumbles", "plunges"], where=["down a cleft in the rock", "into a dark pool", "over a ledge of black stone"],
             detail=["spray hanging in the air around it", "ferns dripping on the wet rock", "a rainbow flickering in its mist", "a deep, cold pool beneath it"]),
        dict(noun=["sheepfold", "shepherd's hut"], adj=["ruined", "roofless", "drystone"], adj2=["old", "small", "sheltered"],
             verb=["stands", "huddles", "sits"], where=["in the lee of the hill", "beside a spring", "on a flat terrace"],
             detail=["its gateway blocked with a hurdle", "nettles filling its interior", "a hearthstone still black with soot", "a shepherd's mark cut over the door"]),
        dict(noun=["outcrop", "tor"], adj=["jagged", "stacked", "massive"], adj2=["granite", "weather-carved", "grey"],
             verb=["rises", "juts", "looms"], where=["from the hillside", "above you", "on the ridge"],
             detail=["its rocks piled like giant cheeses", "a cleft running through it like a doorway", "basins worn into its top by rain", "a ravens' roost in its crevices"]),
    ],
    "peaks": [
        dict(noun=["glacier", "snowfield", "ice-tongue"], adj=["blue-white", "crevassed", "dirty"], adj2=["vast", "groaning", "frozen"],
             verb=["creeps", "spills", "lies"], where=["into the hollow below", "down a gully", "between two summits"],
             detail=["meltwater roaring somewhere beneath it", "rocks embedded in its surface", "a deep blue glow in its cracks", "its edge calving off in chunks"]),
        dict(noun=["chasm", "gorge", "crevasse"], adj=["deep", "narrow", "sheer-sided"], adj2=["dark", "echoing", "dizzying"],
             verb=["cuts", "opens", "yawns"], where=["into the mountainside", "across your way", "in the rock beside the path"],
             detail=["a cold wind breathing up from its depths", "a stream roaring far below", "a rope bridge hanging in tatters across it", "pebbles falling for a long time before you hear them land"]),
        dict(noun=["cave mouth", "overhang"], adj=["dark", "low", "wide"], adj2=["sheltered", "dripping", "draughty"],
             verb=["opens", "gapes", "yawns"], where=["in the cliff", "beneath a slab of rock", "at the base of the crag"],
             detail=["old bones scattered at its entrance", "a smoke-blackened ceiling", "water dripping steadily from its lip", "a smell of animal drifting from it"]),
    ],
}

BIOME_NAMES = {
    "forest": ["Wood", "Weald", "Holt", "Forest", "Wildwood", "Greenwood"],
    "marsh": ["Fen", "Mire", "Marsh", "Carr", "Moss", "Bog"],
    "plains": ["Downs", "Heath", "Lea", "Moor", "Wold", "Fields"],
    "hills": ["Hills", "Fells", "Knolls", "Rise", "Edge", "Tops"],
    "peaks": ["Crags", "Teeth", "Peaks", "Spires", "Heights"],
    "lake": ["Mere", "Water", "Lake", "Tarn"],
}
NAME_PRE = ["Ash", "Bram", "Cold", "Elder", "Grey", "Hollow", "Raven", "Thorn", "Black", "Stag", "Wyn", "Hart",
            "Oak", "Rook", "Sallow", "Wick", "Dun", "Kel", "Mor", "Bar", "Whit", "Hag", "Crow", "Brack", "Gal",
            "Ely", "Stan", "Wold", "Fern", "Har", "Lud", "Tam", "Ost", "Wren"]
NAME_SUF = ["mere", "wick", "combe", "ford", "ley", "stead", "holt", "by", "thorpe", "den", "more", "worth",
            "hale", "cot", "bury", "ton", "dale", "low", "well", "ridge"]
NAME_ADJ = ["Weeping", "Drowned", "Whispering", "Gloaming", "Bitter", "Sleeping", "Hollow", "Grey", "Wending",
            "Lantern", "Hanging", "Shivering", "Crooked", "Bleak", "Silver", "Ember", "Barrow", "Old", "Lost"]

MOODS = {
    "forest": ["serene", "eerie", "lush", "ominous"],
    "marsh": ["eerie", "desolate", "ominous", "lush"],
    "plains": ["serene", "desolate", "serene", "lush"],
    "hills": ["serene", "desolate", "ominous"],
    "peaks": ["desolate", "ominous", "serene"],
}

# merge in the extra landmark archetypes
from .lex_more import FEATURES_MORE as _FM  # noqa: E402
for _b, _fs in _FM.items():
    FEATURES[_b].extend(_fs)
from .lex_landmarks import NEW_FEATURES as _NF  # noqa: E402
for _b, _fs in _NF.items():
    FEATURES[_b].extend(_fs)
# each archetype is known by its first noun; any noun leads back to it
FEATURE_KIND = {}
for _b, _fs in FEATURES.items():
    for _a in _fs:
        _a.setdefault("kind", _a["noun"][0])
        for _n in _a["noun"]:
            if _a["kind"] != "fallen tree":      # a plain "oak" means a standing one
                FEATURE_KIND.setdefault(_n, _a["kind"])
