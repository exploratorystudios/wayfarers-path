"""Landmarks in the moment, and more kinds of landmark.

Every landmark has a kind (its archetype) and a tag (what it is made of:
tree, water, stone, earth, built, ice, fungus, plant). When a landmark is
described, one line may show how it looks *right now*: lookup tries
"lm:<kind>:<condition>" first, then "lm:<tag>:<condition>".

Conditions, most striking first: storm, rain, snow, fog, wind, frost, fullmoon,
dark, dawn, dusk, then the season.
"""

# ---------------------------------------------------------------- new landmark kinds
# Facts here must hold in any season and at any hour (the moment lines do the rest).
NEW_FEATURES = {
    "forest": [
        dict(noun=["fallen beech", "windthrow"], adj=["huge", "uprooted", "toppled"], adj2=["grey-barked", "moss-sheathed", "rotting"],
             verb=["lies", "sprawls"], where=["across a gully", "among the standing trees", "with its root-plate reared up like a wall"],
             detail=["a pit where its roots tore free", "bracket fungus stepping up its flank", "a hollow under the trunk where something sleeps", "its upturned roots still gripping stones"]),
        dict(noun=["holy well", "wishing well", "spring-head"], adj=["moss-lipped", "stone-ringed", "tiny"], adj2=["clear", "cold", "quiet"],
             verb=["rises", "wells up", "lies"], where=["at the foot of a bank", "under a carved stone lintel", "between the roots of an ash"],
             detail=["pins and coins glinting on its bed", "a tin cup chained to a post beside it", "a worn face carved above the water", "rags tied to the nearest branches"]),
        dict(noun=["hunter's hide", "deer-hide"], adj=["low", "brushwood", "half-hidden"], adj2=["old", "weathered", "cunning"],
             verb=["stands", "crouches", "waits"], where=["at the edge of a ride", "in a holly thicket", "above a game trail"],
             detail=["a peephole cut toward the trail", "bones of old kills buried nearby", "a rotten ladder leading up to it", "a carved tally of notches on its frame"]),
    ],
    "marsh": [
        dict(noun=["bog oak", "sunken trunk"], adj=["half-buried", "huge", "ancient"], adj2=["peat-stained", "iron-hard", "glistening"],
             verb=["lies", "rises", "juts"], where=["out of the peat", "half-swallowed by the mire", "beside a channel"],
             detail=["wood turned black as jet by the bog", "the stumps of branches like broken teeth", "old axe-marks where someone tried to cut it", "strange marks scratched into the dark wood"]),
        dict(noun=["sunken punt", "drowned boat"], adj=["rotted", "waterlogged", "abandoned"], adj2=["flat-bottomed", "weed-grown", "small"],
             verb=["lies", "settles", "wallows"], where=["in a reedy channel", "against a mud bank", "in the shallows"],
             detail=["a pole still lying across its thwarts", "a name painted on its side, nearly gone", "a nest of reeds built in its stern", "its bottom staved in as if on purpose"]),
        dict(noun=["reed island", "hummock"], adj=["small", "raised", "tussocky"], adj2=["solid", "lonely", "secret"],
             verb=["rises", "sits", "floats"], where=["out in the open water", "beyond a fringe of sedge", "at the end of a line of posts"],
             detail=["the remains of a fire on its crown", "a single stunted birch on top", "a ring of posts driven into its edge", "the only dry ground for a long way"]),
    ],
    "plains": [
        dict(noun=["chalk figure", "hill figure"], adj=["vast", "white", "strange"], adj2=["ancient", "half-grown-over", "staring"],
             verb=["sprawls", "gallops", "lies"], where=["on the scarp", "across the slope below you", "on the face of the down"],
             detail=["a horse, or something like one, cut in the turf", "a giant with a raised club", "a great pale eye that seems to follow you", "lines that only make sense from far off"]),
        dict(noun=["gibbet", "gallows-tree"], adj=["old", "crooked", "lonely"], adj2=["iron-banded", "weathered", "creaking"],
             verb=["stands", "leans", "looms"], where=["at a crossroads", "on a rise by the track", "where three parishes meet"],
             detail=["an empty iron cage swinging from its arm", "a chain worn bright at one link", "flowers left at its foot by someone", "a name cut into the post and scratched out"]),
        dict(noun=["dovecote", "columbarium"], adj=["round", "ruined", "squat"], adj2=["stone", "roofless", "honeycombed"],
             verb=["stands", "sits", "rises"], where=["near an old field wall", "on its own in the grass", "beside the track"],
             detail=["hundreds of nesting holes in its inner wall", "a potence ladder still turning on its post", "feathers drifted in the doorway", "a lintel carved with a pair of birds"]),
    ],
    "hills": [
        dict(noun=["stone circle", "henge"], adj=["small", "broken", "perfect"], adj2=["grey", "lichened", "silent"],
             verb=["stands", "sits", "crowns"], where=["on a level shelf of hillside", "on the ridge", "in a high hollow"],
             detail=["one of its uprights fallen across the centre", "a taller monolith set apart like a watcher", "the turf inside cropped short as a lawn", "one upright that rings like a bell when struck"]),
        dict(noun=["old mine", "adit"], adj=["dark", "timbered", "abandoned"], adj2=["narrow", "dripping", "forgotten"],
             verb=["opens", "burrows", "gapes"], where=["in the hillside", "behind a spoil heap", "above a stained stream"],
             detail=["rotten pit-props sagging in the entrance", "rust-red water seeping out of it", "a heap of grey spoil sparkling with ore", "a miner's lamp hanging on a nail"]),
        dict(noun=["rowan", "mountain ash"], adj=["lone", "wind-bent", "slender"], adj2=["grey-barked", "tough", "sacred"],
             verb=["grows", "clings", "stands"], where=["out of a crack in the rock", "above a stream", "beside a ruined wall"],
             detail=["a cross of its twigs tied with red thread hanging from it", "its roots gripping bare stone", "the only tree for a mile", "a horseshoe nailed to its trunk"]),
    ],
    "peaks": [
        dict(noun=["eyrie", "eagle's eyrie"], adj=["high", "huge", "wind-scoured"], adj2=["bone-strewn", "untidy", "lofty"],
             verb=["clings", "perches", "sits"], where=["on a ledge above you", "on a crag", "high on the cliff face"],
             detail=["a nest of branches the size of a cart", "bones of hares and lambs below it", "white streaks down the rock beneath", "a single great feather caught on a thorn"]),
        dict(noun=["hermit's cell", "anchorhold"], adj=["tiny", "stone-built", "lonely"], adj2=["low", "cold", "patient"],
             verb=["huddles", "clings", "sits"], where=["under an overhang", "beside the path", "in a fold of the mountain"],
             detail=["a cross scratched over its doorway", "a stone bench worn smooth", "a little walled plot where nothing grows", "a bell hanging silent at the door"]),
        dict(noun=["hot spring", "steaming pool"], adj=["bubbling", "milky", "small"], adj2=["sulphurous", "warm", "mineral-crusted"],
             verb=["bubbles", "steams", "lies"], where=["in a basin of rock", "at the foot of the cliff", "among yellow-stained stones"],
             detail=["a yellow crust of sulphur round its rim", "rocks around it crusted orange and white", "the water too hot to keep a hand in", "a stone seat someone set at its edge"]),
    ],
}

# what each landmark is made of (keyed by the archetype's first noun)
TAG = {
    "oak": "tree", "yew": "tree", "willow": "tree", "hawthorn": "tree", "fallen beech": "log", "fallen tree": "log", "bog oak": "earth", "rowan": "tree",
    "stream": "water", "pool": "water", "dew pond": "water", "waterfall": "water", "tarn": "water", "holy well": "water", "hot spring": "water",
    "ring of toadstools": "fungus",
    "glade": "plant", "reed island": "plant",
    "standing stone": "stone", "cairn": "stone", "outcrop": "stone", "chasm": "stone", "cave mouth": "stone", "stone circle": "stone", "eyrie": "stone",
    "charcoal-burner's mound": "earth", "badger sett": "earth", "peat cutting": "earth", "barrow": "earth", "hill fort": "earth", "chalk figure": "earth", "old mine": "earth",
    "causeway": "built", "eel trap": "built", "track": "built", "sheepfold": "built", "hunter's hide": "built", "sunken punt": "built", "gibbet": "built",
    "dovecote": "built", "hermit's cell": "built",
    "glacier": "ice",
}

# ---------------------------------------------------------------- the moment, by tag
_TAGS = {
    "tree": {
        "spring": ["Fresh leaves are breaking on the {noun}, small and bright as new coins.", "Buds are swelling all along the {noun}'s twigs.", "Birds are busy in the {noun}, building."],
        "summer": ["The {noun} is in full leaf, and the shade beneath it is deep and cool.", "Insects drone in the {noun}'s crown.", "The {noun}'s leaves hang heavy and dark in the heat."],
        "autumn": ["The {noun} is turning, and leaves come down from it one at a time.", "Fallen leaves from the {noun} lie in drifts around its roots.", "The {noun} has gone the colour of rust and old gold."],
        "winter": ["The {noun} stands bare, every twig drawn black against the sky.", "Without its leaves, the {noun} looks like a hand held up against the cold.", "The {noun} is leafless now, and the wind goes straight through it."],
        "rain": ["Rain runs down the {noun}'s bark in dark streams.", "Water drips steadily from the {noun}.", "The {noun} hisses under the rain."],
        "storm": ["The {noun} thrashes and groans in the storm.", "Each gust makes the {noun} heave like a ship's mast."],
        "snow": ["Snow has lodged along every branch of the {noun}.", "The {noun} wears a thin coat of snow on its windward side."],
        "frost": ["Frost has furred every twig of the {noun} white.", "The {noun} glitters with rime."],
        "fog": ["The {noun} is only a darker shape in the fog.", "Fog beads on the {noun} and drips from its twigs."],
        "wind": ["The wind combs through the {noun}, and it answers with a long sigh.", "The {noun}'s branches toss and creak in the wind."],
        "dark": ["In the dark the {noun} is only a black shape against blacker sky.", "Something moves in the {noun}'s branches - an owl, perhaps.", "The {noun} creaks softly in the night."],
        "fullmoon": ["Moonlight silvers the {noun}, and its shadow lies sharp as ink.", "Under the full moon the {noun} looks carved from pewter."],
        "dawn": ["The first light catches the top of the {noun} before anything else.", "Birds start up in the {noun}, one and then dozens."],
        "dusk": ["Rooks are settling noisily into the {noun} for the night.", "The {noun} goes black against the fading sky."],
    },
    "water": {
        "spring": ["The {noun} runs full and loud with snowmelt.", "Frogspawn clouds the shallows of the {noun}."],
        "summer": ["Dragonflies stitch back and forth over the {noun}.", "The {noun} has shrunk in the heat, leaving a rim of cracked mud."],
        "autumn": ["Fallen leaves turn slowly on the {noun}'s surface.", "The {noun} is dark and cold with the year's turning."],
        "winter": ["Ice has crept out from the edges of the {noun}.", "The {noun} steams faintly in the cold air.", "A thin skin of ice covers the {noun} where the water is still."],
        "rain": ["Rain pocks the surface of the {noun} into a thousand rings.", "The {noun} is rising with the rain.", "The {noun} has gone brown and loud with rain."],
        "storm": ["The {noun} churns, brown and angry.", "Lightning flashes off the {noun} for an instant."],
        "snow": ["Snow falls into the {noun} and vanishes.", "The {noun} is a dark gap in the white."],
        "frost": ["Frost rims the stones around the {noun}.", "The {noun} smokes with cold."],
        "fog": ["Fog lies on the {noun} like a held breath.", "You hear the {noun} before you see it in the fog."],
        "wind": ["The wind ruffles the {noun} into hurrying ripples.", "Spray blows off the {noun} in the wind."],
        "dark": ["The {noun} is black, and you can only hear it.", "Stars tremble on the surface of the {noun}."],
        "fullmoon": ["The full moon lies on the {noun} like a coin.", "Moonlight makes a path across the {noun}."],
        "dawn": ["Mist lifts off the {noun} in the first light.", "The {noun} catches the dawn and turns pink and gold."],
        "dusk": ["The {noun} holds the last light long after the land has gone dark.", "Midges dance over the {noun} in the dusk."],
    },
    "stone": {
        "spring": ["New green moss creeps over the {noun}.", "Small flowers have rooted in the cracks of the {noun}."],
        "summer": ["The {noun} is warm to the touch, holding the day's heat.", "Lizards bask on the {noun}."],
        "autumn": ["Dead bracken lies rust-red around the {noun}.", "The {noun} is cold and damp under a low sun."],
        "winter": ["The {noun} is crusted with old snow in its shadowed places.", "Cold comes off the {noun} like breath."],
        "rain": ["Rain darkens the {noun} and runs off it in sheets.", "The {noun} shines black with rain."],
        "storm": ["Rain beats on the {noun}, and the wind screams over it.", "The {noun} stands unmoved while the storm breaks over it."],
        "snow": ["Snow is settling on the {noun}, softening its edges.", "The {noun} pokes darkly out of the snow."],
        "frost": ["Frost has drawn ferns of ice across the {noun}.", "The {noun} is white with hoarfrost."],
        "fog": ["The {noun} looms out of the fog all at once.", "In the fog the {noun} looks taller than it can be."],
        "wind": ["The wind moans over the {noun}.", "The wind whistles in the gaps of the {noun}."],
        "dark": ["In the dark the {noun} feels more present than it did by day.", "The {noun} is a blot of deeper black."],
        "fullmoon": ["Under the full moon the {noun} casts a long, sharp shadow.", "The {noun} looks pale and strange in the moonlight."],
        "dawn": ["The {noun} catches the first light and glows faintly red.", "Dew has beaded on the {noun} overnight."],
        "dusk": ["The {noun} throws a long shadow in the low light.", "The {noun} goes from grey to blue to black as the light fails."],
    },
    "log": {
        "spring": ["Ferns are uncurling along the {noun}'s flank.", "Moss on the {noun} has gone a bright, wet green."],
        "summer": ["Ants run in lines along the {noun}'s split bark.", "The {noun} smells warm and mushroomy in the heat."],
        "autumn": ["Fungus has sprouted in tiers along the {noun}.", "Fallen leaves have drifted deep against the {noun}."],
        "winter": ["The {noun} lies black against the frozen ground.", "Ice has formed in the pockets of the {noun}'s torn roots."],
        "rain": ["Rain darkens the {noun}, and water pools in the pit its roots left.", "The {noun} is slick and black with rain."],
        "storm": ["The storm roars through the standing trees around the {noun}, and you wonder which will fall next.", "Rain sheets off the {noun}."],
        "snow": ["Snow lies along the top of the {noun} like a white spine.", "Snow has drifted against the {noun}."],
        "frost": ["Frost furs the moss on the {noun}.", "The {noun}'s bark is stiff and white with rime."],
        "fog": ["The {noun} is a long dark shape lying in the fog.", "Fog beads on the {noun} and drips from its roots."],
        "wind": ["The wind whistles through the {noun}'s upturned roots.", "Dead leaves skitter along the {noun} in the wind."],
        "dark": ["In the dark the {noun} looks like some great beast asleep.", "Something rustles in the hollow under the {noun}."],
        "fullmoon": ["Moonlight lies along the length of the {noun}.", "Under the full moon the {noun}'s roots throw a tangle of shadow."],
        "dawn": ["Dew beads the moss on the {noun}.", "A wren is already busy in the {noun}'s roots."],
        "dusk": ["Long shadows gather under the {noun}.", "A blackbird scolds from the {noun}'s roots as the light goes."],
    },
    "earth": {
        "spring": ["New grass is pushing up over the {noun}.", "Primroses have opened in the shelter of the {noun}."],
        "summer": ["The {noun} is dry and dusty, its grass burnt pale.", "Bees work the flowers on the {noun}."],
        "autumn": ["The {noun} is soft and dark after the autumn rains.", "Brambles around the {noun} hang heavy with fruit."],
        "winter": ["The {noun} is frozen hard.", "The {noun} is a dark hump in the winter-bleached grass."],
        "rain": ["Water stands in pools around the {noun}.", "The {noun} is turning to mud in the rain."],
        "storm": ["Rain sluices down the {noun}, carving little channels.", "The storm batters the {noun}."],
        "snow": ["Snow has smoothed the {noun} into a soft white shape.", "Snow fills the hollows of the {noun}."],
        "frost": ["Frost silvers the grass on the {noun}.", "The {noun} crunches with frost underfoot."],
        "fog": ["The {noun} is a vague shape in the fog.", "Fog clings to the {noun} like smoke."],
        "wind": ["The wind flattens the grass on the {noun}.", "Dry soil blows from the {noun} in the wind."],
        "dark": ["In the dark the {noun} could be anything.", "You hear small things moving around the {noun} in the dark."],
        "fullmoon": ["Under the full moon the {noun} looks like a sleeping animal.", "Moonlight picks out every hump and hollow of the {noun}."],
        "dawn": ["Dew lies heavy on the {noun}.", "The {noun} steams faintly as the sun reaches it."],
        "dusk": ["Long shadows pool around the {noun}.", "Bats begin to flit over the {noun}."],
    },
    "built": {
        "spring": ["Nettles and new grass crowd the foot of the {noun}.", "Swallows are nesting in the {noun}."],
        "summer": ["The {noun} bakes in the heat, and its timbers smell of dust and tar.", "Weeds stand tall around the {noun}."],
        "autumn": ["Dead leaves have drifted against the {noun}.", "The {noun} is damp and green with the autumn wet."],
        "winter": ["The {noun} is rimed with old frost and empty of life.", "The {noun} looks bleak and abandoned in the winter light."],
        "rain": ["Rain drips through the gaps in the {noun}.", "The {noun} is black and sodden in the rain."],
        "storm": ["The {noun} creaks and rattles in the storm.", "Water pours off the {noun} in the storm."],
        "snow": ["Snow has heaped against the {noun}.", "The {noun} wears a cap of snow."],
        "frost": ["Frost has crept over the {noun}.", "The {noun} is stiff and white with rime."],
        "fog": ["The {noun} comes and goes in the fog.", "In the fog the {noun} seems farther off than it is."],
        "wind": ["The wind rattles something loose on the {noun}.", "The {noun} groans in the wind."],
        "dark": ["The {noun} is just a hulk of darkness.", "Something creaks in the {noun} in the night."],
        "fullmoon": ["The full moon lights the {noun} like a stage.", "The {noun} throws a hard black shadow in the moonlight."],
        "dawn": ["Dew drips from the {noun} as the light comes.", "The {noun} emerges from the dark grey and cold."],
        "dusk": ["The {noun} is losing its edges in the dusk.", "The last light slants through the {noun}."],
    },
    "ice": {
        "summer": ["Meltwater streams off the {noun} in a hundred threads.", "The {noun} sags and drips in the brief mountain summer."],
        "winter": ["The {noun} is buried under fresh snow, its cracks hidden.", "The {noun} is silent and locked in winter."],
        "spring": ["The {noun} groans as it wakes from winter.", "Avalanches of wet snow slide off the {noun}."],
        "autumn": ["The {noun} is grey and dirty at summer's end.", "Fresh snow dusts the {noun} after the first autumn storms."],
        "rain": ["Rain runs in rivulets over the {noun}.", "The {noun} is slick and grey in the rain."],
        "snow": ["Snow is filling the cracks in the {noun}.", "The {noun} vanishes into the falling snow."],
        "fog": ["The {noun} glows a ghostly blue through the fog.", "You hear the {noun} cracking somewhere in the fog."],
        "wind": ["Spindrift streams off the {noun}.", "The wind howls across the {noun}."],
        "dark": ["The {noun} gives off a faint pale glow in the dark.", "The {noun} cracks like a gunshot in the night."],
        "dawn": ["The {noun} turns rose-pink at dawn.", "The first sun sets the {noun} glittering."],
        "dusk": ["The {noun} goes blue, then grey, as the light dies.", "The {noun} holds the last light longest of all."],
    },
    "fungus": {
        "spring": ["Only a few small caps show in the {noun} this early in the year.", "The {noun} is barely there, a hint in the new grass."],
        "summer": ["The {noun} is ragged and drying in the heat.", "Flies buzz around the {noun}."],
        "autumn": ["The {noun} is at its fullest, fat caps crowding shoulder to shoulder.", "New caps have pushed up in the {noun} overnight."],
        "winter": ["The {noun} has collapsed into black mush with the cold.", "Only a dark circle in the grass marks where the {noun} grows."],
        "rain": ["The {noun} glistens in the rain.", "Rain has plumped the caps of the {noun}."],
        "fog": ["Fog gathers inside the {noun} and does not drift out.", "In the fog the {noun} seems larger."],
        "dark": ["The {noun} glows faintly, palely, in the dark.", "You could swear you hear faint music near the {noun}."],
        "fullmoon": ["Under the full moon the grass inside the {noun} seems to stir by itself.", "The {noun} is ringed with a faint green light in the moonlight."],
        "dawn": ["Dew stands in every cap of the {noun}.", "A hare sits in the middle of the {noun}, and bolts as you look."],
        "dusk": ["The {noun} seems to brighten as the light fails.", "Moths gather over the {noun} at dusk."],
    },
    "plant": {
        "spring": ["Bluebells haze the {noun} with blue.", "Everything in the {noun} is new and green."],
        "summer": ["The {noun} is thick with tall grass and foxgloves.", "Butterflies drift across the {noun}."],
        "autumn": ["The {noun} has gone tawny and brown.", "Seed heads rattle in the {noun}."],
        "winter": ["The {noun} is flattened and dun with winter.", "Dead stalks stand stiff in the {noun}."],
        "rain": ["The {noun} is soaked, every blade bowed with water.", "Rain hisses across the {noun}."],
        "snow": ["Snow lies unbroken across the {noun}.", "The {noun} is white and quiet under snow."],
        "frost": ["Frost has turned every blade in the {noun} white.", "The {noun} crackles with frost."],
        "fog": ["Fog fills the {noun} like milk in a bowl.", "The {noun} fades into fog a few paces in."],
        "wind": ["The wind runs through the {noun} in waves.", "The {noun} hisses and bends in the wind."],
        "dark": ["The {noun} is full of small rustlings in the dark.", "Glow-worms prick the dark of the {noun}."],
        "fullmoon": ["The {noun} lies silver under the full moon.", "Moonlight fills the {noun} so brightly you could read by it."],
        "dawn": ["The {noun} is grey with dew, and a deer lifts its head from it.", "Mist lies low across the {noun} at dawn."],
        "dusk": ["Moths rise from the {noun} in the dusk.", "The {noun} goes blue with evening."],
    },
}

# ---------------------------------------------------------------- the moment, by kind (overrides)
_KINDS = {
    "oak": {"autumn": ["Acorns crunch underfoot around the {noun}.", "Jays are squabbling over acorns in the {noun}."],
            "spring": ["The {noun} is late to leaf, still mostly bare among greener neighbours."]},
    "yew": {"winter": ["The {noun} is dark and green when everything else is bare.", "Snow cannot settle under the dense dark {noun}."],
            "autumn": ["Red berries glow among the {noun}'s dark needles.", "Thrushes are gorging on the {noun}'s red berries."],
            "summer": ["Under the {noun} it is as dark and cool as a church."], "spring": ["The {noun} sheds clouds of yellow pollen when the wind touches it."]},
    "hawthorn": {"spring": ["The {noun} is foaming with white blossom, heavy-scented.", "Blossom drifts from the {noun} like snow."],
                 "autumn": ["The {noun} is spattered with dark red haws.", "Fieldfares are stripping the haws from the {noun}."],
                 "winter": ["The {noun} is a black tangle of thorns."]},
    "willow": {"spring": ["Catkins hang yellow on the {noun}.", "The {noun} has a green haze of new leaves."]},
    "rowan": {"autumn": ["The {noun} blazes with scarlet berries.", "Birds squabble over the {noun}'s scarlet berries."],
              "spring": ["The {noun} is opening its flat white flowers."]},
    "stream": {"winter": ["Ice has formed in the slack water at the edges of the {noun}.", "The {noun} runs black and cold between banks of frost."],
               "summer": ["The {noun} has dropped to a trickle between dry stones."], "rain": ["The {noun} has burst its banks in places."]},
    "waterfall": {"winter": ["Icicles hang like organ pipes on either side of the {noun}.", "The {noun} is half-frozen into long white beards."],
                  "summer": ["The {noun} is a thin silver thread in the dry weather."], "rain": ["The {noun} is roaring, brown and swollen with rain."],
                  "midday_clear": ["A rainbow hangs in the spray of the {noun}."]},
    "dew pond": {"summer": ["The {noun} has shrunk to a cracked saucer of mud.", "Swallows dip to drink at the {noun}."],
                 "winter": ["The {noun} is frozen over, white and opaque."]},
    "pool": {"winter": ["The {noun} is skinned with black ice.", "Reeds stand frozen into the {noun}."],
             "summer": ["Water-lilies have opened on the {noun}.", "A heron stands motionless at the edge of the {noun}."]},
    "tarn": {"winter": ["The {noun} is frozen solid and dusted with snow."], "summer": ["The {noun} is so clear you can see the stones on its bottom."]},
    "holy well": {"fullmoon": ["The water of the {noun} seems to give off its own faint light.", "The full moon looks back at you out of the {noun}."],
                  "dawn": ["Someone has left a fresh flower beside the {noun} in the night."]},
    "hot spring": {"winter": ["The {noun} steams fiercely, and the snow has melted in a wide ring around it.", "Steam from the {noun} rises in a tall column in the cold."],
                   "snow": ["Snowflakes vanish into the steam above the {noun}."], "summer": ["The {noun} is barely steaming in the warm air."]},
    "ring of toadstools": {"autumn": ["The {noun} has swollen overnight, fat caps crowded edge to edge.", "The caps of the {noun} are at their fattest and brightest."]},
    "glade": {"spring": ["Bluebells carpet the {noun} so thickly the ground looks flooded.", "Wood anemones star the {noun}."],
              "summer": ["Foxgloves crowd the edges of the {noun}.", "Butterflies drift in the warm air of the {noun}."]},
    "barrow": {"fullmoon": ["Under the full moon something seems to stir in the sunken entrance of the {noun}.", "The {noun} looks hollow and listening in the moonlight."],
               "fog": ["The {noun} rises out of the fog like a sleeping beast's back."]},
    "standing stone": {"dawn": ["The sun rises exactly behind the {noun}, as if it had been set there to mark it."],
                       "fullmoon": ["The {noun} seems to lean toward you in the moonlight."]},
    "stone circle": {"dawn": ["The first light falls through the gap between two stones of the {noun}, straight across its centre."],
                     "fullmoon": ["Under the full moon the {noun} seems to hum.", "In the moonlight you count the stones of the {noun} twice and get two different answers."],
                     "fog": ["The uprights of the {noun} come and go in the fog like figures keeping watch."]},
    "gibbet": {"wind": ["The empty cage on the {noun} squeals as it swings in the wind.", "The {noun}'s chain clanks in the wind."],
               "dark": ["The {noun}'s cage creaks in the dark, though there is no wind."], "fog": ["The {noun} looms out of the fog, its cage swinging."]},
    "chalk figure": {"winter": ["Snow has filled the {noun}'s outlines, and it has vanished into the white hillside."],
                     "dawn": ["The low light makes the {noun} leap out of the hillside."], "fog": ["The {noun} is hidden in the fog, all but one white leg."]},
    "chasm": {"snow": ["Snow swirls down into the {noun} and is gone.", "The lip of the {noun} is hidden under snow - a deadly place to misstep."],
              "rain": ["Water pours over the lip of the {noun} in a dozen threads.", "The roar from the bottom of the {noun} has grown with the rain."],
              "frost": ["Frost rims the lip of the {noun}."], "fog": ["The {noun} is full of fog to the brim, as if it had no bottom at all."],
              "winter": ["Icicles hang from the walls of the {noun}.", "The {noun} breathes out cold like a cellar."],
              "summer": ["Swifts scream in and out of the {noun}."], "dark": ["The {noun} is a seam of perfect black."]},
    "fallen beech": {"autumn": ["Beech-mast lies thick around the {noun}, and squirrels are busy in it."], "spring": ["Seedlings have sprung up in the light where the {noun} fell."]},
    "glacier": {"midday_clear": ["The {noun} is too bright to look at in the sun."]},
    "eyrie": {"spring": ["An eagle is sitting tight on the {noun}.", "Something big feeds in the {noun}, and a shriek comes down."],
              "summer": ["A great fledgling flaps clumsily on the {noun}."]},
    "dovecote": {"dusk": ["Pigeons are coming home to the {noun} in a clatter of wings."], "dawn": ["Pigeons burst out of the {noun} in a grey cloud."]},
    "sheepfold": {"spring": ["Lambs bleat inside the {noun}.", "Ewes and lambs crowd the {noun}."], "winter": ["Snow has drifted deep into the {noun}."]},
    "hermit's cell": {"dark": ["A light flickers in the {noun}, though no one seems to live there now."],
                      "dawn": ["The bell at the {noun} sways slightly, though no one rings it."]},
    "eel trap": {"autumn": ["The {noun} is set for the autumn eel-run, its willow mouths open to the current."]},
    "peat cutting": {"summer": ["Turves are stacked to dry beside the {noun}."], "winter": ["The {noun} is full of black ice."]},
    "track": {"rain": ["The {noun} has turned to a river of mud.", "Water stands in the ruts of the {noun}."],
              "summer": ["Dust lifts from the {noun} with every step."]},
}


def rules():
    """Grammar rules: lm:<tag>:<cond> and lm:<kind>:<cond>."""
    out = {}
    for tag, conds in _TAGS.items():
        for cond, lines in conds.items():
            out[f"lm:{tag}:{cond}"] = lines
    for kind, conds in _KINDS.items():
        for cond, lines in conds.items():
            out[f"lm:{kind}:{cond}"] = lines
    return out


def conditions(w):
    """The current conditions, most striking first."""
    weather, t, s = w.weather, w.time_of_day, w.season
    dark = w.is_dark
    out = []
    if weather == "storm":
        out.append("storm")
    if weather in ("rain", "drizzle", "storm"):
        out.append("rain")
    if weather in ("snow", "fog", "wind"):
        out.append(weather)
    if s == "winter" and weather in ("clear", "cloudy") and (dark or t == "dawn"):
        out.append("frost")
    if dark and weather in ("clear", "cloudy") and "full" in w.moon_line:
        out.append("fullmoon")
    if dark:
        out.append("dark")
    elif t in ("dawn", "dusk"):
        out.append(t)
    elif t == "midday" and weather == "clear":
        out.append("midday_clear")
    out.append(s)
    return out
