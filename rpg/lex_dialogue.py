"""Everyday talk as sentence shapes: work, village talk, closing remarks, errands, directions, what they
notice about you, greetings and the gossip about your deeds.

Two kinds of table:
  * shapes for sentences.py (talk.py and speech.py use these): slots filled from LEX and from roles,
    with verbs made to agree. Work talk is built from each trade's seasonal *tasks*, stored as verb
    phrases ('break the ice on the troughs'), so one shape gives 'I've been breaking the ice on the
    troughs since first light' and 'If I'm not carrying hay out to the fold, I'm mending harness'.
  * GRAMMAR, added to the narrator's grammar (greetings, deed gossip, news openers): the same idea in the
    description grammar's own form, parts built from sub-rules (all named 'd_...').
"""
from .lex_speech import LEX as _SPEECH_LEX

# =============================================================================================== work
# What each kind of work means in each season, as verb phrases. A trade's own tasks come first; the
# kind of work (land, craft, water...) fills in.
GROUP_TASKS = {
    "land": {"spring": ["walk the lambing pens at night", "sow the barley", "mend the hedges the deer broke", "drive the stock out to the new grass",
                        "harrow the top field"],
             "summer": ["cut the hay", "shear the flock", "turn the hay before the rain comes", "chase the stock out of the corn", "carry water to the troughs"],
             "autumn": ["get the harvest in", "bring the flock down off the tops", "thresh the last of the oats", "turn the pigs out on the acorns", "plough the stubble"],
             "winter": ["break the ice on the troughs", "carry hay out to the fold", "mend harness by the fire", "dig sheep out of the drifts", "muck out the byre"]},
    "craft": {"spring": ["mend everything that broke over the winter", "work through a stack of orders as high as the door", "fit new handles to old tools",
                         "fix the ploughshares folk forgot about till now"],
              "summer": ["work with the door wide open", "make what folk will want at harvest", "keep up with the orders", "work till the light goes"],
              "autumn": ["get ready for the winter orders", "mend harvest tools", "lay in stock for the cold months", "fill orders for the fair"],
              "winter": ["work close to the fire", "get through the jobs I put off all year", "teach the apprentice", "work by lamplight"]},
    "water": {"spring": ["mend nets", "watch the river rise", "check the traps at dawn", "caulk the boat"],
              "summer": ["fish the shallows", "pull weed from the channels", "sell the catch before it turns", "ferry folk over to the fair"],
              "autumn": ["set the eel traps for the run", "smoke the catch", "haul the boat up for the winter", "fish the deep pools"],
              "winter": ["break the ice at the landing", "mend nets by the fire", "watch the floods", "set lines under the ice"]},
    "wood": {"spring": ["coppice the hazel", "peel bark for the tanners", "clear the windfalls", "mark the trees for felling"],
             "summer": ["burn charcoal", "stack the cordwood", "sleep in the woods by the clamp", "split logs"],
             "autumn": ["fell the marked trees", "gather mast for the pigs", "haul timber down to the road", "build the clamps"],
             "winter": ["fell timber while the sap's down", "cut firewood for half the village", "drag logs through the snow", "split kindling"]},
    "healer": {"spring": ["gather the first green herbs", "sit up with fevers", "bring the spring babies in", "dose the children for worms"],
               "summer": ["dry herbs from the rafters", "bind scythe cuts", "treat sunstroke at the haymaking", "gather elder-flower"],
               "autumn": ["make syrups for the winter", "dig roots", "set bones broken at harvest", "brew the cough draughts"],
               "winter": ["nurse chest-rattles", "treat chilblains", "sit up with the old ones", "walk miles through the snow to a bedside"]},
    "road": {"spring": ["walk the roads again after the thaw", "restock from the markets", "dodge the mud", "mend the cart"],
             "summer": ["go from fair to fair", "sell in the heat", "walk the high roads while they're dry", "haggle"],
             "autumn": ["follow the harvest fairs", "lay in stock for the winter", "get my rounds done before the roads close", "count what's left"],
             "winter": ["sit out the snow", "sell what I can to the villages I can reach", "mend packs", "wait for the roads to open"]},
    "elder": {"spring": ["settle boundary quarrels", "see the fields shared out", "hear complaints", "count who came through the winter"],
              "summer": ["keep the peace at haymaking", "settle disputes before breakfast", "see the common grazed fair", "hear the moot"],
              "autumn": ["tally the stores", "share out the harvest", "settle who owes what", "plan for the winter"],
              "winter": ["see that nobody starves", "visit the old ones", "ration the stores", "keep folk from each other's throats"]},
}
JOB_TASKS = {
    "shepherd": {"spring": ["sit up with the lambing ewes", "bottle-feed the orphan lambs"], "summer": ["shear the flock", "drive the ewes up to the high pasture"],
                 "autumn": ["bring the flock down", "pick out the ewes for the tup"], "winter": ["carry hay up to the fold", "dig ewes out of the drifts"]},
    "smith": {"spring": ["shoe every horse in the parish", "mend ploughshares"], "summer": ["sharpen scythes", "make sickles for the harvest"],
              "autumn": ["mend harvest tools", "make nails for the winter roofing"], "winter": ["make hinges and pothooks", "keep the forge hot for anyone who'll pay"]},
    "miller": {"spring": ["dress the millstones", "clear the race of winter wrack"], "summer": ["grind what's left of last year's grain", "fight the eels for the sluice"],
               "autumn": ["grind the new corn day and night", "keep the queue of carts in order"], "winter": ["chip ice off the wheel", "grind by lamplight"]},
    "weaver": {"spring": ["weave the winter's spinning", "set up a new warp"], "summer": ["work by the open door", "finish the wedding linen"],
               "autumn": ["weave cloth for winter coats", "dye with walnut and onion skin"], "winter": ["weave from dawn to dark", "work with cold fingers"]},
    "potter": {"spring": ["dig fresh clay", "throw pots for the dairies"], "summer": ["fire the kiln", "dry pots in a day"],
               "autumn": ["make crocks for the pickling", "make jars for the honey"], "winter": ["work clay that won't warm", "nurse the kiln through the frost"]},
    "thatcher": {"spring": ["patch the winter's holes", "cut fresh reed"], "summer": ["strip and re-thatch", "work up on the ridges"],
                 "autumn": ["get every roof tight before the gales", "bind reed into bundles"], "winter": ["climb out to storm damage", "split hazel for spars"]},
    "beekeeper": {"spring": ["feed the hives through the cold snaps", "chase swarms across the parish"], "summer": ["take the honey", "chase swarms"],
                  "autumn": ["wrap the hives", "render the wax"], "winter": ["listen at the hives", "make candles from the wax"]},
    "brewer": {"spring": ["brew the light ale for the ploughmen", "scour the vats"], "summer": ["brew for the haymaking", "keep the ale from turning in the heat"],
               "autumn": ["brew the harvest ale", "malt the new barley"], "winter": ["brew the strong ale for midwinter", "keep the mash warm"]},
    "tanner": {"spring": ["soak hides in the pits", "scrape hides"], "summer": ["work upwind of the village", "dry leather"],
               "autumn": ["take in hides from the killing", "fill the bark pits"], "winter": ["break ice on the pits", "curry leather by the fire"]},
    "carter": {"spring": ["haul seed corn", "dig the cart out of the mud"], "summer": ["haul hay", "carry folk to the fairs"],
               "autumn": ["haul the harvest", "carry timber"], "winter": ["haul firewood", "wait out the snow"]},
    "ferryman": {"spring": ["ferry folk over the flood", "mend the rope"], "summer": ["ferry folk to the fairs", "scrape the hull"],
                 "autumn": ["ferry the harvest carts", "watch the river rise"], "winter": ["break ice at the landing", "refuse fools who want crossing in a gale"]},
    "eel-catcher": {"spring": ["mend the eel traps", "watch the floods go down"], "summer": ["set lines in the shallows", "sell eels at the fair"],
                    "autumn": ["take the autumn run", "smoke eels"], "winter": ["dig eels out of the mud", "mend traps by the fire"]},
    "woodcutter": {"spring": ["coppice the hazel", "clear the windfalls"], "summer": ["stack the cordwood", "split logs"],
                   "autumn": ["fell the marked trees", "haul timber"], "winter": ["fell while the sap's down", "cut firewood for half the village"]},
    "charcoal-burner": {"spring": ["cut wood for the clamps", "build the first clamp"], "summer": ["watch the clamps day and night", "sleep beside the clamp"],
                        "autumn": ["burn the last clamps", "sell charcoal to the smiths"], "winter": ["cut wood for spring", "keep my hut from blowing down"]},
    "midwife": {"spring": ["bring the spring babies in", "sit with mothers near their time"], "summer": ["bring the babies in", "walk out to the farms"],
                "autumn": ["sit up with the lying-in", "dose the children before winter"], "winter": ["bring babies in by candlelight", "walk through the snow to a birth"]},
    "hedge-witch": {"spring": ["gather nettles and cleavers", "brew the spring tonics"], "summer": ["dry herbs", "gather what grows at midsummer"],
                    "autumn": ["dig roots", "make the winter syrups"], "winter": ["nurse coughs", "sell charms to folk who swear they don't believe in them"]},
    "swineherd": {"spring": ["watch the sows farrow", "ring the pigs' noses"], "summer": ["keep the pigs out of the corn", "wallow the pigs at the mere"],
                  "autumn": ["drive the pigs out on the acorns", "pick the pigs for the killing"], "winter": ["feed the pigs on scraps", "help with the salting"]},
    "goose-girl": {"spring": ["guard the goslings from the foxes", "drive the geese to the green"], "summer": ["drive the geese to the stubble", "pluck down"],
                   "autumn": ["fatten the geese for the feast", "drive the geese to market"], "winter": ["shut the geese in early", "keep the geese out of the snow"]},
    "cooper": {"spring": ["make butter churns", "mend water barrels"], "summer": ["make casks for the harvest ale", "fit hoops"],
               "autumn": ["make barrels for the salting", "make casks for the cider"], "winter": ["make tubs and pails", "season the staves"]},
    "wheelwright": {"spring": ["mend cart wheels cracked by the frost", "fit new spokes"], "summer": ["build wheels for the harvest carts", "shrink tyres"],
                    "autumn": ["mend wheels between harvest loads", "season timber"], "winter": ["build new carts for the spring", "work oak by the fire"]},
    "chandler": {"spring": ["dip candles", "render tallow"], "summer": ["keep the tallow from going soft", "make rushlights"],
                 "autumn": ["lay in tallow from the killing", "make candles for the winter"], "winter": ["sell candles faster than I can dip them", "dip candles all day"]},
    "fletcher": {"spring": ["cut arrow shafts", "trade for goose feathers"], "summer": ["fletch arrows for the butts", "straighten shafts"],
                 "autumn": ["make arrows for the hunting", "fit heads"], "winter": ["work by the fire", "glue fletchings"]},
    "net-mender": {"spring": ["mend the winter's tears", "tar the nets"], "summer": ["mend nets on the shore", "make new nets"],
                   "autumn": ["mend nets for the eel run", "dry nets"], "winter": ["knot nets by the fire", "make nets for spring"]},
    "horse-coper": {"spring": ["break the young horses", "sell plough horses"], "summer": ["take horses to the fairs", "swim the horses in the river"],
                    "autumn": ["buy at the horse fairs", "fatten horses for sale"], "winter": ["feed horses I can't sell", "doctor coughs"]},
    "drover": {"spring": ["drive the stock out to the summer pasture", "buy in young stock"], "summer": ["drive cattle to the fairs", "walk the drove roads"],
               "autumn": ["drive cattle to the autumn fair", "drive stock down from the hills"], "winter": ["winter the beasts", "sit by the fire and count my blisters"]},
    "ploughman": {"spring": ["plough the spring fields", "harrow"], "summer": ["mow", "help with the hay"], "autumn": ["plough the stubble", "sow the winter wheat"],
                  "winter": ["mend harness", "lead out the dung carts"]},
}
JOB_TASKS["goose-boy"] = JOB_TASKS["goose-girl"]
JOB_TASKS["chandler's boy"] = JOB_TASKS["chandler's girl"] = JOB_TASKS["chandler"]

WORK_SHAPES = [
    "It's all {task1.ing} [this time of year|just now|at the moment|from dawn to dark].",
    "I've been {task1.ing} since [first light|before dawn|breakfast|the cock crowed].",
    "If I'm not {task1.ing}, I'm {task2.ing}.",
    "[This week|Today|All week] it's {task1.ing}. [Tomorrow|Next week] it'll be {task2.ing}.",
    "I {task1} in the morning and {task2} in the afternoon, and [sleep|eat|sit down] when I can.",
    "[There's|I've got] {task1.ing} to do, and {task2.ing} after it[, and nobody to help|, and then it's dark|].",
    "You've caught me between {task1.ing} and {task2.ing}.",
    "{season_cap}'s for {task1.ing}. [Always has been.|And {task2.ing}.|That's the year for you.]",
    "[Somebody has to|Someone's got to] {task1}. [It's me, as usual.|Guess who.|This year, me.]",
]
WORK_TAIL = ["{work_comment}"]

# =============================================================================================== village
TROUBLE_SHAPES = [
    "[And with|What with] {trouble}, nobody in {village} is [sleeping easy|sleeping well|easy].",
    "Of course, there's {trouble}, and nobody [seems able to do|can do|is doing] anything about it.",
    "[Not that anyone's thinking of anything but|Nobody talks of anything but|All anyone talks of is] {trouble} [just now|these days|this week].",
    "Everyone's [on edge|jumpy|short with each other], what with {trouble}.",
    "I'd talk more cheerfully, but there's {trouble}, and it [weighs on everyone|sits on the whole village|is all anyone thinks about].",
]
# what the weather's going to do, said with words chosen to fit the season (lex_words.py)
FORECAST_SHAPES = [
    "{@noun:weather,bad,now.subj.cap>wx} {~is|are} {@verb:approach,with=wx.ing}, by the look of the sky.",
    "[There's|I'd say there's] {@noun:weather,bad,now>wx} on the way. [Mark me.|You'll see.|My bones say so.]",
    "Looks like {@noun:weather,bad,now.subj>wx} {~is|are} {@verb:approach,with=wx.ing} [tonight|by morning|before dark|for the week].",
    "[The birds are low.|The cows are lying down.|The smoke's going straight down.] {@noun:weather,bad,now.subj.cap>wx} {~is|are} {@verb:approach,with=wx.ing}.",
]
FESTIVAL_SHAPES = [
    "It's {festival}, [mind|anyway], so [you'll eat well tonight|there'll be dancing later|even I'll be merry by dark].",
    "Still, it's {festival}. [Even I can manage a smile.|The ale's flowing.|Hard to stay glum.|The children have been up since dawn.]",
    "[You've come at a good time|Good timing]: it's {festival}. [Stay for it.|There'll be food.|Mind the dancing.]",
]
VILLAGE_SHAPES = [
    "{village} has lived by {economy} [since my grandfather's time|as long as anyone remembers|since before the road came].",
    "{village} lives by {economy}, and [always will|always has|that's all there is to it].",
    "There's not much to {village} but {economy} and [gossip|the alehouse|weather], and we're short of neither.",
    "The {economy} keeps {village} [fed|going|alive], [most years|just about|when it's kind].",
    "{village}'s an old place. Older than the road, [the old ones say|they reckon|so my {pkin} said].",
    "Nothing much happens in {village}. [That's how we like it.|We'd like to keep it that way.|Or it didn't, till lately.]",
    "Folk from {village} don't leave much, and when they do, they come back.",
    "They laugh at us in the next valley for the {economy}. They buy it all the same.",
]

# =============================================================================================== closing remarks
TAIL_SHAPES = {
    "nervous": ["Sorry. I'm [talking too much|going on|babbling]. I do that.", "Don't mind me. I'll be all right. [I'm always all right.|I will.|Really.]",
                "I'll stop. You've [places to be|things to do|a road to walk].", "I checked the door [twice|three times] this morning. Never mind.",
                "Is that someone coming? No. No, it isn't."],
    "suspicious": ["Not that it's any of your business.", "Why do you want to know, [anyway|exactly|all of a sudden]?", "And that's all you'll get out of me.",
                   "Anyway. I've said [enough|more than I meant to].", "You ask a lot of questions, for someone [just passing|passing through|who's leaving]."],
    "gruff": ["Not that anyone thanks me for it.", "Well. Work won't do itself.", "Enough talk.", "There. Now you know.", "That's it. [That's the news.|That's all.]"],
    "warm": ["But here's me going on. How are you keeping?", "You'll stay for a bite, won't you? [There's always too much.|I've made extra.]",
             "Sit a while, if you like. [The step's warm.|There's room.|Nobody's hurrying you.]",
             "Here - your cloak's torn at the hem. Leave it with me a minute.", "You've a look of my [sister|cousin|mother] about you. Round the eyes."],
    "cheerful": ["Ha! Listen to me.", "Mustn't grumble. Well, I must, but I mustn't.", "Still, the sun comes up. Most days.",
                 "Anyway! What's the news from out there?", "And I'd do it all again tomorrow. [Probably will.|Most likely.]"],
    "melancholy": ["It was easier once. Everything was.", "Still. Nothing lasts.", "I don't know why I'm telling you this.",
                   "My mother used to say the same. She's been gone [nine|eleven|twenty] winters.", "Ah well. It passes the days."],
    "shrewd": ["Remember that, if you're buying.", "Worth knowing, that.", "There's money in it, for someone who keeps their ears open.",
               "I'll say no more. Not for nothing, anyway.", "You didn't hear it from me. But you did hear it."],
    "dreamy": ["Or so it seems to me, anyway.", "The days go by like water.", "Do you ever feel the days belong to someone else?",
               "There was a [heron|hare|white owl] on the roof this morning. I took it as a [good sign|sign|message].",
               "Sometimes I think the work does itself, and I only watch."],
}

# =============================================================================================== errands
CHECKIN_SHAPES = {
    "warm": ["[Any|Is there any] [news|word|sign] of {obj}? [I've kept a candle in the window.|I've hardly slept.|Sit down and tell me.]",
             "Come in - [any news of|have you heard anything of|is there word of] {obj}?"],
    "cheerful": ["[Back already?|There you are!] Tell me you've found {obj}!", "[Well?|So?] [Any luck with|How goes it with] {obj}?"],
    "gruff": ["Well? {obj_cap}?", "[Found|Any sign of] {obj} yet?", "[Still nothing?|Nothing?] {obj_cap}?"],
    "nervous": ["You've not given up? On {obj}? [Please say you've not.|Please.]", "Is there - is there news? Of {obj}?"],
    "suspicious": ["Well? You said you'd see to {obj}.", "[So.|Well.] {obj_cap}. What's happened?"],
    "melancholy": ["Any news of {obj}? Don't spare me.", "I suppose there's nothing. Of {obj}."],
    "shrewd": ["[How goes it|Where are we] with {obj}?", "{obj_cap}. Tell me what you know."],
    "dreamy": ["I dreamed of {obj} last night. Have you [found|seen] them?", "{obj_cap}... [is there news?|did you find the way?]"],
}
NUDGE_SHAPES = {
    "ask": ["Did you [speak to|find|go and see] {far} in {fvillage} yet?", "{far} in {fvillage} is [the one to ask|who you want]. [Don't let {fhim} put you off.|Have you been?]"],
    "deal": ["{far} in {fvillage} will want something for it, mind. {fhe.cap} always does.", "[Did|Has] {far} [name|named] {fhis} price yet?"],
    "bring": ["{far} won't help without what {fhe} asked for. [Have you found it?|Have you got it yet?]", "Did you get {far} what {fhe} wanted?"],
    "search": ["Have you been out to the {lm} yet?", "[Look at|Go back to] the {lm} again, if you've been. Things hide in plain sight."],
    "slay": ["Is that {guard} still [on the way|in the way|out there]? Be careful of it.", "[Mind|Watch out for] that {guard}."],
    "deliver": ["Did they take my token at {fvillage}?", "[Have you been to|Did you get to] {fvillage} with my token?"],
    "go": ["You'll need to go by {region}. Mind yourself there.", "The way goes through {region}. [Go carefully.|Keep to the path.]"],
    "climax": ["It's out there, {dir}. I know it is.", "[Not far now.|Nearly there.] {dir_cap}. I can feel it."],
}
NEED_PERSON_SHAPES = [
    "[I hear|Word gets round|They tell me] you're [looking for|after|asking after] {far}. {fhe.cap}'s the {fjob} in {fvillage}. {manner}",
    "{far}, is it? I know {fhim}. The {fjob} [in|over in|at] {fvillage}. {manner}",
    "[You want|If it's] {far} [you're after|you want], {fhe}'s the {fjob} at {fvillage}. {manner}",
]
NEED_PLACE_SHAPES = [
    "[They say|I hear|Word is] you're bound for {place}. That's {dir}. {how} {about}",
    "You're going to {place}? It's {dir}. {how} {about}",
    "If it's {place} you want, it's {dir}. {how} {about}",
    "{place}? [That's|You'll find it] {dir}. {how} {about}",
]
NEED_BEAST_SHAPES = [
    "[I hear|They say] you're after that {beast}. It's been seen out in {region}, {dir}. [You'll know it by|Look for|Mind] {mark}.",
    "{beast_cap}, you say? Something like it was seen in {region}, {dir}. [Look for|You'll know it by] {mark}.",
    "That {beast}? [A shepherd saw it|Someone saw one] in {region}, {dir}, [not long ago|last week|a few days back]. {mark_cap}, they said.",
]
MANNER = {
    "suspicious": ["{fhe.cap} doesn't trust strangers. [Don't take it to heart.|Give {fhim} time.]", "Wary sort. [Keep your hands where {fhe} can see them.|Go slow.]"],
    "gruff": ["Short with everyone. It's nothing personal.", "[Grunts more than talks.|Not one for talk.] [Don't mind it.|{fhe.cap} means well.]"],
    "warm": ["Kind soul. You'll be fed before you've asked anything.", "[Heart of gold.|Good as bread.] [You'll like {fhim}.|{fhe.cap}'ll help if {fhe} can.]"],
    "cheerful": ["Laughs at everything. You'll like {fhim}.", "[Always a joke.|Never stops talking.] [You'll be friends in a minute.|Good company.]"],
    "melancholy": ["A sad sort, these days. Go gently.", "[Low in spirits.|Not been the same lately.] [Be kind.|Go gently with {fhim}.]"],
    "shrewd": ["Sharp as a tack. Count your coins after.", "[Clever.|Knows the price of everything.] [Don't let {fhim} sell you anything.|Keep your wits about you.]"],
    "dreamy": ["Head in the clouds, but {fhe} sees more than you'd think.", "[Away with the fairies,|Odd,] [but kind|but not daft|but {fhe} notices things]."],
    "nervous": ["Jumps at {fhis} own shadow. Speak softly.", "[Easily frightened.|A bit timid.] [Don't loom.|Go quietly.]"],
}
HOW_ROAD = ["The road will take you there.", "There's a road the whole way.", "Keep to the road and you can't miss it.", "Follow the road. It goes right there."]
HOW_WILD = ["There's no road the whole way; you'll go across country for some of it.", "You'll be off the road for part of it. [Mind the bogs.|Go carefully.]",
            "No road for some of the way. [Ask a shepherd.|Follow the streams.]"]
ABOUT = ["They live by {economy} there.", "It's {economy} country, that.", "Good folk, mostly. {economy_cap}, and not much else.",
         "[Decent sorts.|Fair folk.] [Mostly {economy}.|All {economy} there.]", "You'll smell the {economy} before you see the place."]

# =============================================================================================== noticing you
REACT = {
    "hurt": {
        "warm": ["Sit down before you fall down. Is that blood?", "Look at the state of you. [Here - sit.|Come in, come in.]", "[Oh, my dear|Oh, love], you're hurt."],
        "cheerful": ["You look like you lost an argument with a [bramble|bear|mangle]. A big one.", "Someone's been in the wars!"],
        "gruff": ["You're bleeding on my step.", "Get that seen to.", "[That wants|You want that] binding."],
        "melancholy": ["You're hurt. Everyone's hurt, these days.", "That wants binding. Doesn't everything."],
        "suspicious": ["Who did that to you? And are they following?", "Blood. Yours, I hope, and not someone else's."],
        "nervous": ["Is - is that blood? Yours?", "Oh, you're hurt. Oh dear. [Oh dear.|Sit down.]"],
        "dreamy": ["You've been somewhere sharp.", "There's red on you. Like a robin."],
        "shrewd": ["That wants a poultice. The hedge-witch charges, mind.", "You'll want to be careful, bleeding like that out there."]},
    "wet": {
        "warm": ["You're wet through. [Come in under the eaves.|Come and stand by the fire.]", "Look at you, soaked."],
        "cheerful": ["Lovely weather for ducks, eh?", "Swim here, did you?"], "gruff": ["Shake that off somewhere else.", "You're dripping."],
        "melancholy": ["It's set in for the day, this.", "Wet again. It's always wet."],
        "suspicious": ["Bad weather for travelling. Bad weather for anything.", "Nobody walks in this without a reason."],
        "nervous": ["You're soaked - do you want - I've a cloth somewhere.", "Oh, you're dripping."],
        "dreamy": ["The rain's been following you, I think.", "You smell of rain."],
        "shrewd": ["Wet roads, short tempers. Mind how you go.", "Rain's good for one trade only, and it's not mine."]},
    "snow": {"*": ["There's snow on your shoulders.", "You've brought the snow in with you.", "Stamp your feet - you'll lose your toes in this.",
                   "[Look at you|Look at the state of you] - white as a miller."]},
    "late": {
        "warm": ["At this hour? You'll want a bed, surely.", "You're out late, my dear."], "cheerful": ["Night owl, are you?", "Can't sleep either? Ha!"],
        "gruff": ["It's late.", "Folk are abed. So should you be."], "melancholy": ["Can't sleep either?", "The nights are the worst. Aren't they."],
        "suspicious": ["What brings anyone round at this hour?", "Odd time to come calling."], "nervous": ["You gave me a turn - it's so dark."],
        "dreamy": ["The night's the best of it. Everyone else is asleep."], "shrewd": ["Late business is the best business. Or the worst."]},
    "class": {
        "knight": ["That's a lot of iron to carry about.", "You'll be a soldier, then. Or were.", "I can hear you coming a mile off, in that.",
                   "[Where did you get|Who made] armour like that?"],
        "ranger": ["You've the walk of someone who sleeps out of doors.", "There's half the forest on your boots.", "You've a hunter's eyes. Always looking past me."],
        "wizard": ["Ink on your fingers. A scholar, then.", "You've the look of someone who reads.", "What's in all those pockets? No - don't tell me."],
        "rogue": ["Quick eyes. I'll keep mine on my purse.", "You've a light step. Too light, maybe.", "I've met your sort. Some of them were all right."],
        "cleric": ["A priest? We've not had one through since the old one died.", "Will you bless the well while you're here? It's been sulking.",
                   "You've the look of someone who prays. Pray for rain, would you?"]},
}

# =============================================================================================== shared words
LEX = dict(_SPEECH_LEX)
LEX.update({
    "work_comment": ["My back knows all about it.", "Not that anyone notices till it's not done.", "Good, honest, aching work.",
                     "It never ends, and I'd not know what to do if it did.", "My {pkin} did it before me, and grumbled the same.",
                     "I'd not swap it. Most days."],
})

# =============================================================================================== description grammar
# Built from sub-rules, so a greeting or a piece of gossip is put together, not picked whole.
GRAMMAR = {
    # first greetings, by temperament
    "d_warm_hi": ["Well met!", "Hello, hello!", "A new face!", "Welcome!", "There now - a traveller!", "Hello there!"],
    "d_warm_offer": ["Sit, rest your feet.", "You'll want something warm in you.", "Come and sit a while.", "You look like you've walked a long way.",
                     "The road's been kind to bring you."],
    "d_cheer_hi": ["Ha!", "Well, hello!", "Hello there!", "Look at this!", "A visitor!"],
    "d_cheer_more": ["Things are looking up.", "Grand day for it, whatever it is.", "Come, have you news?", "Where've you blown in from?", "Another traveller!"],
    "d_gruff_hi": ["Hm.", "Well?", "Aye?", "What."],
    "d_gruff_more": ["If you're going to talk, talk.", "Busy. Make it quick.", "Out with it.", "Say what you want."],
    "d_susp_hi": ["What do you want?", "Yes?", "Stop there."],
    "d_susp_more": ["I don't know you.", "Strangers bring trouble, in my experience.", "Say your business.", "Keep your hands where I can see them."],
    "d_nerv_hi": ["Oh!", "Oh - hello.", "Sorry, sorry.", "Ah!"],
    "d_nerv_more": ["You startled me.", "I didn't hear you coming.", "Is something wrong?", "I'm a bit on edge today."],
    "d_mel_hi": ["Ah.", "Oh. A traveller.", "Mm.", "Hello."],
    "d_mel_more": ["We don't get many now.", "Another day, another face.", "You should have come in better times.", "Good day, if it is one."],
    "d_shrewd_hi": ["Well now.", "A traveller.", "Now then."],
    "d_shrewd_more": ["What have we here?", "And what might you be worth to me, I wonder?", "You've a look about you.", "You'll be wanting something."],
    "d_dream_hi": ["Oh - hello.", "Oh.", "Hello."],
    "d_dream_more": ["I was somewhere else.", "Were you in my dream? No, never mind.", "The wind told me someone would come.", "Did you see the clouds this morning?"],
    # gossip about your deeds
    "d_heard": ["Heard", "They're saying", "Word is", "A carter told me", "I hear", "Someone said", "Folk are saying"],
    "d_killed": ["put down", "killed", "did for", "finished off", "saw off", "dealt with"],
    "d_where": ["out in {where}", "near {where}", "up by {where}", "over in {where}"],
    "d_deed_react": ["Good riddance.", "Is it true?", "About time somebody did.", "I'll sleep easier.", "Was it as big as they say?", "Well done, if it's true.",
                     "That's one less to worry about."],
    "d_boss_react": ["The whole country's talking.", "Is it true?", "They'll be singing about it.", "I never thought I'd hear it.", "Gods be good."],
    "d_story_tail": ["That right?", "Is it true?", "Good for you.", "That was kind.", "I'd not have thought it."],
    # news from elsewhere
    "d_news_open": ["Did you hear?", "You'll not have heard, then:", "Here's news:", "Word came yesterday:", "A carter came through with news:",
                    "Mark me -", "I'll tell you this much:", "They say", "Word is,"],
    # a long time away
    "d_gap_where": ["Where've you been all this time?", "I'd half thought you dead, it's been that long.", "Look who it is, after all this time.",
                    "I was beginning to wonder about you.", "Long time.", "You've been away a good while."],
}
GRAMMAR_EXTEND = {
    "warm:greet": ["\"{d_warm_hi} {d_warm_offer}\""], "cheerful:greet": ["\"{d_cheer_hi} {d_cheer_more}\""], "gruff:greet": ["\"{d_gruff_hi} {d_gruff_more}\""],
    "suspicious:greet": ["\"{d_susp_hi} {d_susp_more}\""], "nervous:greet": ["\"{d_nerv_hi} {d_nerv_more}\""], "melancholy:greet": ["\"{d_mel_hi} {d_mel_more}\""],
    "shrewd:greet": ["\"{d_shrewd_hi} {d_shrewd_more}\""], "dreamy:greet": ["\"{d_dream_hi} {d_dream_more}\""],
    "mem_deed_kill": [(3, "\"{d_heard} you {d_killed} {a_thing} {d_where}. {d_deed_react}\"")],
    "mem_deed_boss": [(2, "\"{d_heard} you {d_killed} {thing}! {d_boss_react}\"")],
    "mem_deed_story": [(2, "\"{d_heard} {story}. {d_story_tail}\"")],
    "rumour_frame": [(4, "\"{d_news_open} {rumour}\"")],
    "mem_long_gap": [(3, "\"{d_gap_where}\"")],
}
