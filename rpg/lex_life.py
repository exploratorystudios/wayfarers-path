"""What people talk about: their own lives, their neighbours, your errands. Data for rpg/talk.py.

A person's talk is put together from parts, the way the descriptions are: what their work is
like this season (by trade, or by the kind of trade), a word about a neighbour or the state of
the village, and a closing remark in their own temperament. Everything runs through the
narrator, so a line that clashes with the season or weather is re-rolled.

Slots: {tool} (what's in their hands), {village}, {economy} (what the village lives by),
{other}/{ojob}/{ohe}/{ohim}/{ohis} (a neighbour), {trouble} (what's wrong in the village).
"""

# which kind of work each trade is, for the lines below (a trade with its own lines in JOB_SEASON uses those)
GROUP = {
    "shepherd": "land", "drover": "land", "ploughman": "land", "swineherd": "land", "goose-girl": "land", "goose-boy": "land",
    "smith": "craft", "tinsmith": "craft", "fletcher": "craft", "cooper": "craft", "wheelwright": "craft", "potter": "craft",
    "tanner": "craft", "weaver": "craft", "thatcher": "craft", "hurdle-maker": "craft", "chandler": "craft",
    "chandler's boy": "craft", "chandler's girl": "craft",
    "eel-catcher": "water", "ferryman": "water", "net-mender": "water",
    "woodcutter": "wood", "charcoal-burner": "wood",
    "midwife": "healer", "hedge-witch": "healer", "wise-woman": "healer", "wise-man": "healer",
    "carter": "road", "pedlar": "road", "packman": "road", "trader": "road", "huckster": "road", "tinker": "road",
    "spice-trader": "road", "cloth-seller": "road", "horse-coper": "road",
}

WORK = {
    "land": {
        "spring": ["Lambing's nearly done. I've slept in the fold more nights than my own bed this month.",
                   "The ewes are dropping twins this year. Good for the purse, hard on the knees.",
                   "Every field wants seeing to at once, and the ground's still heavy from the thaw."],
        "summer": ["Shearing soon, if the weather holds. Then my back won't be my own till harvest.",
                   "The grass is good this year. The beasts are fat and lazy, and so am I.",
                   "Flies. You'd not believe the flies. The beasts stand nose to tail all day, swishing."],
        "autumn": ["We'll bring the beasts down off the tops soon, before the weather turns on us.",
                   "Market's coming. I'll sell what I can't feed through the winter, and hate doing it.",
                   "The tups are in with the ewes. Next year's flock starts now, if all goes well."],
        "winter": ["I've been carrying hay out since before light. They'd eat the hedges if I let them.",
                   "Lost two in the last cold snap. You get used to it. You don't, really.",
                   "Breaking the ice on the troughs, morning and evening. That's the whole of winter, that."],
    },
    "craft": {
        "spring": ["Every tool in the parish broke at once. They always do, come spring.",
                   "Folk find everything that broke over the winter, and bring it to me in the same week."],
        "summer": ["Quiet season. Everyone's out in the fields, and nobody's breaking anything.",
                   "I start before dawn and stop at noon. Any later and I'd cook at the bench."],
        "autumn": ["Everyone wants their gear mended before the cold. I've orders enough to see me to midwinter.",
                   "Busiest time of the year, this. I've not sat down to a hot meal in a week."],
        "winter": ["Cold hands make bad work. I keep the fire going and do what I can.",
                   "Long nights. I work by rushlight and ruin my eyes doing it."],
    },
    "water": {
        "spring": ["The water's high with the melt. Nothing to do but mend nets and wait.",
                   "Spring floods took two of my traps. I'll find them in a hedge in June, I expect."],
        "summer": ["The water's low and warm, and the eels lie deep in the mud and sulk.",
                   "Easy season on the water. Too easy. The fish know it."],
        "autumn": ["Best time on the water, this. The eels run down to the sea on dark nights, and I'm waiting for them.",
                   "The autumn run's started. I've not been dry in a week, and I don't care."],
        "winter": ["The edges freeze every night. I break the ice to get the boat out.",
                   "Nothing moves in the water in this cold, and neither do I if I can help it."],
    },
    "wood": {
        "spring": ["Sap's rising. No time to fell timber, so I coppice and mend.",
                   "The woods are waking up. Everything's green and nothing's worth cutting."],
        "summer": ["I've a burn going in the clearing. I've not slept a whole night in four.",
                   "Dry weather's good for the wood and bad for the nerves. One spark and the lot goes."],
        "autumn": ["Felling season. You can hear my axe from the village, they tell me.",
                   "Stacking wood for half the parish. They'll all be glad of it in a month."],
        "winter": ["Cold enough that folk buy wood faster than I can split it.",
                   "The woods are quiet in winter. You hear things you'd not hear in summer."],
    },
    "healer": {
        "spring": ["Every child in the village has the spring cough. I've been up three nights running.",
                   "I'm out at first light for the young nettles and the coltsfoot. They're best now."],
        "summer": ["Summer fevers, and sunstroke from fools who won't wear a hat.",
                   "The herbs are at their strongest. I'm drying them on every line in the house."],
        "autumn": ["I'm digging roots while they're strong, before the ground freezes.",
                   "Elderberries for the winter syrup. I've purple hands to the elbow."],
        "winter": ["Winter's my hard season. The old ones feel it in their chests.",
                   "Three births this month, all at night. Babies never come at a sensible hour."],
    },
    "road": {
        "spring": ["The roads are mud to the axle. I lost a wheel on the way here.",
                   "First time out after the winter. Everyone's glad to see me, which makes a change."],
        "summer": ["Good weather for the road. I've come further this month than all winter.",
                   "Dust, and more dust. But the roads are open and folk are buying."],
        "autumn": ["One more round of the villages before the roads close for the winter.",
                   "Folk are stocking up for the winter. Good for trade, if you've the goods."],
        "winter": ["I'd not be on the road at all in this, but folk still need things.",
                   "Half the tracks are drifted shut. I came the long way round."],
    },
    "elder": {
        "spring": ["There's the spring moot to see to. Everyone wants the same field, every year.",
                   "Planting, and boundaries, and who owes what. Spring's all quarrels."],
        "summer": ["Haymaking. Every pair of hands in the village is in the meadows, and mine would be if I could bend.",
                   "Long days and short tempers. I settle three disputes before breakfast."],
        "autumn": ["I'm tallying the stores for the winter. We'll manage, if it's not too hard a one.",
                   "Harvest's in, mostly. Now we see whether it's enough."],
        "winter": ["Winter's when everyone brings me their quarrels. Shut folk in together and they find things to argue about.",
                   "I count the stores every week now, and count them again."],
    },
}

# trades with lines of their own
JOB_SEASON = {
    "miller": {"spring": ["The millpond's full with the melt. Good water, and nothing to grind for months."],
               "summer": ["The wheel wants new paddles before the harvest comes in. Always something."],
               "autumn": ["Harvest's in, and every soul in the valley wants their grain ground yesterday."],
               "winter": ["The race froze last week. A mill with a frozen wheel is just a cold house."]},
    "brewer": {"spring": ["The new ale's nearly ready. I'll want someone to tell me it's good."],
               "summer": ["Hot weather sours the brew if you look at it wrong. I've been sleeping in the cellar."],
               "autumn": ["The barley's in. I'll be malting till my arms drop off."],
               "winter": ["Folk drink more in the dark months. I'm not complaining."]},
    "beekeeper": {"spring": ["The bees are out on the blackthorn already. A good sign."],
                  "summer": ["They swarmed twice this week. I spent half a morning up a tree with a skep."],
                  "autumn": ["I'm taking the honey now, and leaving them enough to winter on. You learn the hard way how much is enough."],
                  "winter": ["The hives are quiet. Some mornings I put my ear to them, just to hear them hum."]},
    "gravedigger": {"spring": ["The ground's soft now. Easy digging, which is a mercy, given the winter we had."],
                    "summer": ["Quiet season for me, thank the spirits. I tend the yard and wait."],
                    "autumn": ["The ground's still soft, but it won't be for long. I dig a spare, some years. Just in case."],
                    "winter": ["Ground like iron. When someone dies in winter they wait in the cold-house for the thaw."]},
    "rat-catcher": {"spring": ["The rats come out of the thatch in spring, hungry and bold."],
                    "summer": ["Rats in the grain stores already. The year's been kind to them."],
                    "autumn": ["Harvest means grain, and grain means rats. Good for trade."],
                    "winter": ["The rats come indoors out of the cold. So do I."]},
}

# a word about the village or a neighbour
NEIGHBOUR = [
    "{other} the {ojob} reckons it'll be a hard winter. {ohe.cap} always reckons that.",
    "{other} the {ojob} was asking after travellers. You might look {ohim} up.",
    "If you want to know anything about {village}, ask {other} the {ojob}. {ohe.cap} knows everyone's business.",
    "{other} the {ojob} has been good to me this year. I'll not forget it.",
    "Don't let {other} the {ojob} talk your ear off. Or do. {ohe.cap}'s lonely, I think.",
    "{other} the {ojob} and I don't speak. It's a long story, and not a good one.",
    "{other} the {ojob} sings while {ohe} works. You'll hear {ohim} if you stay the night.",
]
NEIGHBOUR_TEMPER = {
    "suspicious": ["{other} the {ojob}'s been acting strange lately. I'm only saying.", "Watch {other} the {ojob}. That's all I'll say."],
    "gruff": ["{other} the {ojob} still owes me for last winter. Tell {ohim} I said so."],
    "shrewd": ["{other} the {ojob} charges too much. Come to me first."],
    "warm": ["{other} the {ojob} will see you right, if you need anything. Good heart, that one."],
    "cheerful": ["{other} the {ojob} fell in the millpond last week. You should have seen {ohis} face!"],
    "melancholy": ["{other} the {ojob} lost {ohis} mother in the spring. Be kind to {ohim}, if you meet."],
    "dreamy": ["{other} the {ojob} has a cat that I think understands every word we say."],
    "nervous": ["{other} the {ojob} frightens me a little. Not that {ohe} means to."],
}
VILLAGE = [
    "{village} lives by {economy}, and has since my grandfather's time.",
    "There's not much to {village} but {economy} and gossip, and we're short of neither.",
    "The {economy} keeps {village} fed, most years.",
]
TROUBLE = [
    "And with {trouble}, nobody in {village} is sleeping easy.",
    "Of course, {trouble}, and nobody seems able to do anything about it.",
    "Not that anyone's thinking of anything but {trouble} just now.",
]
FESTIVAL = ["It's {festival}, mind, so you'll eat well tonight.", "Still, it's {festival}. Even I can manage a smile."]

# how they close, in their own temperament
TAIL = {
    "nervous": ["Not that I'm complaining. I'm not, really.", "I worry, that's all. I always worry."],
    "suspicious": ["Not that it's any of your business.", "Why do you ask, anyway?"],
    "gruff": ["Not that anyone thanks me for it.", "That's all there is to say about it."],
    "warm": ["But here's me going on. How are you keeping?", "Still, there are worse lives. Sit a while, if you like."],
    "cheerful": ["Still, can't complain! Well, I can, but nobody listens.", "Ah, it's a good life, mostly."],
    "melancholy": ["It was easier once. Everything was.", "Ah well. It passes the days."],
    "shrewd": ["There's money in it, if you're clever about it.", "A sensible person could do well round here, mind."],
    "dreamy": ["Sometimes I think the work does itself, and I only watch.", "The days go by like water."],
}

# ---------------------------------------------------------------- your errands, in their mouths
# they asked you for something: how they ask after it
CHECKIN = {
    "nervous": ["Any sign of {obj}? I've thought of nothing else.", "Did you - is there any news of {obj}?"],
    "suspicious": ["You're still after {obj}, I hope. Not just taking my hope and walking off with it."],
    "gruff": ["Well? {obj.cap}?", "Any news of {obj}, or are you just passing?"],
    "warm": ["Any sign of {obj}? I've kept a candle in the window.", "Come in - any news of {obj}?"],
    "cheerful": ["There you are! Any luck with {obj}?", "Back already? Tell me you've found {obj}!"],
    "melancholy": ["Any news of {obj}? Don't spare me.", "I don't suppose there's news of {obj}."],
    "shrewd": ["Well? How goes it with {obj}?", "I hear you've been busy. Is any of it about {obj}?"],
    "dreamy": ["I dreamed about {obj} last night. Is that a good sign, do you think?", "Have you found {obj}? I keep thinking I hear them."],
}
# a word about the step you're on
STEP_NUDGE = {
    "ask": ["Did you speak to {far} in {fvillage} yet?", "{far} in {fvillage} is the one to ask. Don't let {fhim} put you off."],
    "deal": ["{far} in {fvillage} will want something for it, mind. {fhe.cap} always does."],
    "bring": ["{far} won't help without what {fhe} asked for. Have you found it?"],
    "search": ["Have you been out to the {lm} yet?", "The {lm}, remember. Look properly."],
    "slay": ["Is that {guard} still on the way? Be careful of it."],
    "deliver": ["Did they take my token at {fvillage}?"],
    "go": ["You'll need to go by {region}. Mind yourself there."],
    "climax": ["It's out there, {dir}. I know it is."],
}
# what they know about the people and places your errands need
PERSON = {
    "suspicious": "{fhe.cap} doesn't trust strangers. Don't take it to heart.", "gruff": "Short with everyone. It's nothing personal.",
    "warm": "Kind soul. You'll be fed before you've asked anything.", "cheerful": "Laughs at everything. You'll like {fhim}.",
    "melancholy": "A sad sort, these days. Go gently.", "shrewd": "Sharp as a tack. Count your coins after.",
    "dreamy": "Head in the clouds, but {fhe} sees more than you'd think.", "nervous": "Jumps at {fhis} own shadow. Speak softly.",
}
NEED_PERSON = ["I hear you're looking for {far}. {fhe.cap}'s the {fjob} in {fvillage}. {manner}",
               "Word gets round: you're after {far}, in {fvillage}? The {fjob}. {manner}",
               "{far}, is it? I know {fhim}. The {fjob} in {fvillage}. {manner}"]
NEED_PLACE = ["They say you're bound for {place}. That's {dir}. {how} {about}", "You're going to {place}? It's {dir}. {how} {about}",
              "If it's {place} you want, it's {dir}. {how} {about}"]
NEED_BEAST = ["I hear you're after that {beast}. It's been seen out in {region}, {dir}. You'll know it by {mark}.",
              "A {beast}, you say? Something like it was seen in {region}, {dir}. Look for {mark}."]


# =============================================================================== more of everything
# (merged into the tables above, so a long game hears the same thing less often)
_MORE_WORK = {
    "land": {
        "spring": ["Three orphan lambs in my kitchen, and every one of them thinks I'm its mother.",
                   "The cuckoo's back. My grandmother said you should turn your money over when you hear it. I've none to turn.",
                   "We drove the beasts up to the high pasture this week. They ran the last mile, they were that glad."],
        "summer": ["I sleep out with the flock on the tops these nights. The stars are company enough.",
                   "Hay's the thing now. Every fine day you're not cutting is a day you'll pay for in February.",
                   "The beasts have found the one gap in the hedge, as they always do, and gone through it."],
        "autumn": ["I counted them off the fell yesterday. Two short. I'll go up again tomorrow.",
                   "The acorns are down, and the pigs are out in the wood eating themselves silly.",
                   "Ploughing for the winter wheat. The gulls follow me up and down all day."],
        "winter": ["Dug three ewes out of a drift this morning, alive, all three. They looked at me as if it were my fault.",
                   "The beasts are in the byre and I'm in with them half the night. It's warmer than my own house.",
                   "Short days. You feed them in the dark, you feed them again in the dark, and in between you mend things."],
    },
    "craft": {
        "spring": ["I've a stack of orders as high as the door, and every one wanted last week.",
                   "New apprentice started this month. Keen as mustard, and clumsy as a calf."],
        "summer": ["The light's good and the days are long. I do my finest work in summer.",
                   "Fair coming up. I'm making a few pieces worth showing, to catch a merchant's eye."],
        "autumn": ["The carts all want mending before the roads go soft. I've two in the yard now.",
                   "Laying in stock for the winter: wood, leather, charcoal, whatever I can afford."],
        "winter": ["Folk come in just to stand by the fire. I let them. I like the talk.",
                   "Quiet work, winter. I make the things there's no time for in summer."],
    },
    "water": {
        "spring": ["Ice went out last week with a noise like a house falling down. Took the jetty with it.",
                   "Elvers coming up the river. You can scoop them out by the bucketful, if you're quick."],
        "summer": ["Swimmers in the river every evening, and every year someone thinks they're cleverer than the current.",
                   "The water's so clear you can count the stones. Fish see you coming."],
        "autumn": ["The river's up and brown with leaves. Everything's on the move under it.",
                   "Storm took a tree into the channel. I've been sawing at it from the boat for two days."],
        "winter": ["Fog off the water every morning. You could lose a boat in it and never know.",
                   "Ice on the oars. Ice in my beard. Ice in my soul, my wife says."],
    },
    "wood": {
        "spring": ["Bluebells under the hazel now. Prettiest time of the year, and the worst for work.",
                   "Barking oak for the tanners. The sap's up and the bark comes off in sheets."],
        "summer": ["The wood's so thick now you can't see ten paces. Good for the deer. Bad for me.",
                   "Thunder in the hills all week. I don't like to be in among the tall trees when it comes."],
        "autumn": ["Leaves everywhere. You can't find a dropped axe for leaves.",
                   "Charcoal's in demand now. Every smith wants a winter's worth."],
        "winter": ["Frost cracks the trunks some nights. Sounds like a bowshot in the dark.",
                   "I can see the shape of the wood again, now the leaves are gone. Old paths, old stumps, old fires."],
    },
    "healer": {
        "spring": ["Every herb wants gathering at once in spring, and every baby wants delivering.",
                   "Bad time for the old chests. I've been brewing horehound by the cauldron."],
        "summer": ["Bee stings and burns and cut feet, all summer long. Folk forget themselves in the sun.",
                   "The meadowsweet's out. I'll dry it for the fevers in the dark months."],
        "autumn": ["Folk eat what they shouldn't at harvest, and come to me groaning.",
                   "Mushroom time. Twice a year somebody eats the wrong one, and I get there too late or just in time."],
        "winter": ["Chilblains, chest-rattles and broken bones from the ice. Winter's a busy season for me.",
                   "I've a house full of dried herbs and not enough of the right ones. There never are."],
    },
    "road": {
        "spring": ["I've a pack full of needles, ribbons and gossip. The gossip sells best.",
                   "Lambs on every hill on the way here. Lovely to look at. Slow to drive round."],
        "summer": ["Long days, long roads. I've slept under hedges for a week and never been happier.",
                   "Every village has a fair or a wake or a wedding. Good for trade, bad for the head."],
        "autumn": ["Apples and cider at every door. A pedlar's road is a merry road, in autumn.",
                   "Weather's turning. I'll winter in one of the towns, I think, and start again in spring."],
        "winter": ["Folk are glad of news in the dark months. I'm the only thing that's happened to them since the leaves fell.",
                   "I've worn through one pair of boots since midwinter and started on the next."],
    },
    "elder": {
        "spring": ["Somebody's goat ate somebody else's beans, and now it's my business. Spring.",
                   "We beat the bounds next week: walk the whole edge of the parish and bump the children on the boundary stones so they'll remember."],
        "summer": ["The young ones want a dance every night and the old ones want quiet. I can't please both.",
                   "A good summer. I'm almost afraid to say so."],
        "autumn": ["The tithe-man comes next month. I'm hiding the good cheese.",
                   "Harvest supper's coming. Somebody will drink too much and somebody will propose, as every year."],
        "winter": ["Three old ones are failing this winter. I sit with each of them in turn.",
                   "We share the fire now, two and three families to a hearth, to save the wood."],
    },
}
for _g, _seasons in _MORE_WORK.items():
    for _s, _lines in _seasons.items():
        WORK[_g][_s] = WORK[_g][_s] + _lines

_MORE_JOB = {
    "smith": {"spring": ["Every plough-share in the valley is in my yard, bent or blunt or both."],
              "summer": ["Too hot to be at the forge past noon. I shoe horses in the morning and sleep in the afternoon."],
              "autumn": ["Sickles and scythes in for sharpening, and everyone wants theirs first."],
              "winter": ["Best place in the village, the forge, come winter. Everyone finds a reason to visit."]},
    "fletcher": {"spring": ["Goose feathers from the moult. I'll fletch a thousand shafts from these."],
                 "summer": ["The lord's men want arrows for the summer muster. I've not seen my bed in days."],
                 "autumn": ["Ash for the shafts, cut now while the sap's down. It'll season over winter."],
                 "winter": ["Arrows sell in winter. Folk hunt when the larder's low."]},
    "weaver": {"spring": ["The new wool's coming in from the shearing. Greasy and smelling of sheep, and I love it."],
               "summer": ["I take the loom out under the eaves on hot days. The whole lane stops to watch."],
               "autumn": ["Everyone wants a new cloak before the cold, and wants it for nothing."],
               "winter": ["The clack of the loom goes on into the night, winter. It's company."]},
    "tanner": {"spring": ["The pits stink worse when it warms. My neighbours remind me, every year."],
               "summer": ["Flies, and the smell. Even I notice it in summer."],
               "autumn": ["The autumn killing brings the hides in. Busy time."],
               "winter": ["Hides freeze stiff in the pits. Slow work, and cold."]},
    "thatcher": {"spring": ["Every roof that leaked all winter wants me now."],
                 "summer": ["Up on the ridge all day, with the whole valley below. Best job there is, in summer."],
                 "autumn": ["New reed's cut. I've a roof a week till the weather stops me."],
                 "winter": ["Gales stripped two roofs last month. I patch and wait for better weather."]},
    "potter": {"spring": ["Clay's soft and the kiln's lit again after the winter. Good to have my hands dirty."],
               "summer": ["The pots dry in a day in this weather. I can barely keep up with them."],
               "autumn": ["Crocks for the pickling and jars for the honey. Everyone's storing something."],
               "winter": ["Frost cracks green pots. I keep them by the kiln and pray."]},
    "cooper": {"spring": ["The brewers want new casks for the spring ale."], "summer": ["Butter churns and milk pails, all summer."],
               "autumn": ["Barrels for the salting and the cider. I hoop them in my sleep."], "winter": ["Mending the casks that split in the frost."]},
    "wheelwright": {"spring": ["The spring mud breaks more wheels than the whole winter did."],
                    "summer": ["Harvest wagons. Every one of them wants new spokes before the corn comes in."],
                    "autumn": ["The carts are working hard. So am I."], "winter": ["Seasoning the timber for next year's wheels. It's slow work, and it can't be hurried."]},
    "shepherd": {"spring": ["Lambing. I'll sleep again in May, maybe."], "summer": ["Up on the tops with the flock. Days go by and I don't speak a word."],
                 "autumn": ["The tups are in. Next year starts now."], "winter": ["Hay up to the fold twice a day. My dog does the hard part."]},
    "ferryman": {"spring": ["The river's too high to cross some days. Folk shout at me from the far bank as if I'd made the rain."],
                 "summer": ["Busy season. Everyone wants to be on the other side of the river in summer."],
                 "autumn": ["Drovers taking their beasts to market. Cattle don't like boats, and they let you know it."],
                 "winter": ["Ice at the edges. I'll cross for anyone, but I charge more."]},
    "woodcutter": {"spring": ["Coppicing the hazel. It'll grow back thicker than ever."],
                   "summer": ["Clearing deadwood before it can catch. Dry summers frighten me."],
                   "autumn": ["The felling. My shoulders know it's autumn before I do."],
                   "winter": ["Everyone wants wood and nobody wants to fetch it. Good for me."]},
    "charcoal-burner": {"spring": ["First burn of the year. The clamp smokes for three days and I watch it for all three."],
                        "summer": ["I live in the wood half the summer. I smell of smoke, and the village lets me know it."],
                        "autumn": ["The smiths want charcoal for the winter. I can't make it fast enough."],
                        "winter": ["Too wet to burn half the time. I cut wood and wait."]},
    "midwife": {"spring": ["Spring babies. Four this month. Their mothers want sleep and I want it more."],
                "summer": ["The summer babies are fat and noisy. That's how I like them."],
                "autumn": ["Three due before the first frost. I've my bag packed by the door."],
                "winter": ["Babies don't wait for the snow to clear. I've waded to a birth up to my waist."]},
    "hedge-witch": {"spring": ["The first green things are the strongest. I'm out gathering before the dew's off."],
                    "summer": ["Midsummer eve's the night for gathering. Some herbs are no use cut any other night."],
                    "autumn": ["Roots and berries. I've jars of things on every shelf, and a few I've forgotten the names of."],
                    "winter": ["Folk come to me in winter for the things the herbs can't do. Love, mostly. Or luck."]},
    "eel-catcher": {"spring": ["The elvers are running. Strange little glass things, thousands of them."],
                    "summer": ["The eels lie low in the heat. I mend traps and wait."],
                    "autumn": ["The dark nights of autumn, that's when they run. I'll be on the water till dawn."],
                    "winter": ["Smoked eel for the winter. My house smells of it. So do I."]},
    "drover": {"spring": ["Taking the young beasts up to summer pasture. Two weeks on the road, with the dogs."],
               "summer": ["Fattening on the hills. I go up and count them and come down again."],
               "autumn": ["Drove to the autumn fair next week. Two hundred head and three dogs, and me."],
               "winter": ["The drove roads are closed till spring. I mend harness and drink too much."]},
    "carter": {"spring": ["The roads are soft. I've been stuck to the axles twice this week."],
               "summer": ["Hay to the farms and stone to the builders. My horse and I don't stop."],
               "autumn": ["Corn to the mill, every day, till the harvest's in."],
               "winter": ["Frost makes the roads hard and fast. Good for carting, if your hands don't freeze to the reins."]},
    "tinker": {"spring": ["Every pot that cracked over the winter wants mending, and I've only two hands."],
               "summer": ["I sleep under the cart and mend kettles by the roadside. It's a life."],
               "autumn": ["Folk want their knives sharp for the killing. I've been grinding all week."],
               "winter": ["Fewer roads open, more pots broken. I go where I can."]},
    "spice-trader": {"spring": ["Ginger and pepper from the south, if the passes are open. This year they barely were."],
                     "summer": ["Saffron for the wedding cakes. Every bride wants it, and none of them can afford it."],
                     "autumn": ["Folk buy spice in autumn for the winter feasts. My busiest season."],
                     "winter": ["Mulled wine needs cinnamon. I'm the only cinnamon for thirty miles."]},
    "horse-coper": {"spring": ["Foals everywhere. I'll buy a few now and sell them as yearlings."],
                    "summer": ["Fair season. Every farmer thinks his nag's a warhorse."],
                    "autumn": ["Selling off what folk won't winter. I'll have a dozen to feed till spring."],
                    "winter": ["Nobody buys a horse in winter. I feed them, and talk to them, and wait."]},
    "chandler": {"spring": ["Fewer candles in spring. Long days. I make soap instead."],
                 "summer": ["Tallow goes soft in the heat. I make candles at night, when it's cool."],
                 "autumn": ["The autumn killing means tallow, and tallow means candles."],
                 "winter": ["Winter's when candles sell. The long nights pay for the year."]},
    "swineherd": {"spring": ["Piglets. Eleven in one litter. The sow's not speaking to me."],
                  "summer": ["The pigs root in the wood and I sit under a tree. Don't tell anyone."],
                  "autumn": ["Pannage. The pigs are fat on acorns and I'm fat on blackberries."],
                  "winter": ["The killing's done. I miss them. You'd not think it, but I do."]},
    "goose-girl": {"spring": ["The goslings follow me everywhere. Even to the privy."],
                   "summer": ["I take the geese down to the common and they take me where they like."],
                   "autumn": ["Fattening them for the autumn fair. They know, I think. They give me looks."],
                   "winter": ["Geese hate the cold more than I do, and they say so, loudly."]},
    "net-mender": {"spring": ["Every net that came through the winter has a hole in it."], "summer": ["I sit on the bank and mend, and the fishermen bring me ale."],
                   "autumn": ["Storm season. Nets come back in rags."], "winter": ["Mending by the fire. My fingers know the knots in the dark."]},
}
_MORE_JOB["goose-boy"] = _MORE_JOB["goose-girl"]
for _j, _seasons in _MORE_JOB.items():
    for _s, _lines in _seasons.items():
        JOB_SEASON.setdefault(_j, {})[_s] = JOB_SEASON.get(_j, {}).get(_s, []) + _lines

NEIGHBOUR += [
    "{other} the {ojob} is courting, they say. {ohe.cap} goes red as a radish if you mention it.",
    "{other} the {ojob} can tell you what the weather'll do three days off. Always right, too. It's unsettling.",
    "{other} the {ojob} keeps a raven that steals spoons. Nobody's brave enough to tell {ohim}.",
    "{other} the {ojob} has a cousin in every village from here to the hills. Ask {ohim}, if you're lost.",
    "{other} the {ojob} lent me a hand when my roof came in. I owe {ohim} for that.",
    "{other} the {ojob} came here as a stranger, years back. Folk still call {ohim} the newcomer.",
    "{other} the {ojob} tells the best stories at the alehouse, and the least true.",
    "{other} the {ojob} hasn't been well. You might stop by, if you've a kind word.",
]
NEIGHBOUR_TEMPER["suspicious"] += ["{other} the {ojob} had money all of a sudden, last spring. Nobody knows where from."]
NEIGHBOUR_TEMPER["gruff"] += ["{other} the {ojob} lets {ohis} beasts in my field. I've told {ohim} twice."]
NEIGHBOUR_TEMPER["shrewd"] += ["{other} the {ojob} is behind on the rent, so you'll get a good price there."]
NEIGHBOUR_TEMPER["warm"] += ["{other} the {ojob} will feed you if you let {ohim}. Let {ohim}."]
NEIGHBOUR_TEMPER["cheerful"] += ["{other} the {ojob} sang at the last wedding. The dogs joined in. Best night of the year."]
NEIGHBOUR_TEMPER["melancholy"] += ["{other} the {ojob} and I were going to be married, once. Long ago now."]
NEIGHBOUR_TEMPER["dreamy"] += ["{other} the {ojob} says {ohe} saw lights on the hill at midsummer. I believe {ohim}."]
NEIGHBOUR_TEMPER["nervous"] += ["{other} the {ojob} says there's something in the old well. I don't go near it now."]

VILLAGE += [
    "{village}'s an old place. Older than the road, the old ones say.",
    "Nothing much happens in {village}. That's how we like it.",
    "There's {economy}, and there's the alehouse, and that's {village} for you.",
    "Folk from {village} don't leave much, and when they do, they come back.",
    "They laugh at us in the next valley for the {economy}. They buy it all the same.",
]
TROUBLE += ["Everyone's on edge, what with {trouble}.", "I'd talk more cheerfully, but there's {trouble}, and it weighs on everyone."]
FESTIVAL += ["There's dancing on the green tonight, for {festival}. You should come.", "Everyone's half drunk already. It's {festival}, and nobody minds."]

# a word about the weather or the hour, when it's worth one (scoped, so it's always the weather there is)
WEATHER_NOW = {
    "rain": ["Rain again. It gets into everything: the bread, the bedding, your bones.", "This rain's set in for the day, I'd say."],
    "drizzle": ["This drizzle's the worst kind of wet. You don't notice it till you're soaked."],
    "storm": ["Listen to it. I'd not be out in this for a king's ransom.", "Storm like this, the old folk stay in and the young folk get into trouble."],
    "fog": ["Can't see the end of the lane in this. Mind how you go.", "Fog like this, you hear the whole village and see none of it."],
    "wind": ["This wind. It'll have the thatch off somebody's roof by nightfall.", "Wind's been at it since dawn. It makes the dogs mad."],
    "snow": ["Snow again. The children are delighted. Nobody else is.", "More snow coming, by the smell of it."],
    "clear": ["Fine day for it, whatever it is.", "Good to see the sky for once."],
}
TIME_NOW = {
    "dawn": ["You're up early. Or late, I suppose."], "dusk": ["Getting dark. You'll want a roof tonight."],
    "evening": ["Most folk are at their suppers by now."], "night": ["It's late to be calling. Still, you're here."],
    "deepnight": ["What are you doing abroad at this hour?"],
}

for _t, _lines in {
    "nervous": ["Sorry. I talk too much when I'm worried.", "Don't mind me. I'll be all right."],
    "suspicious": ["Anyway. I've said enough.", "And that's all you'll get out of me."],
    "gruff": ["Well. Work won't do itself.", "Enough talk."],
    "warm": ["You'll stay for a bite, won't you?", "It's good to have someone to talk to."],
    "cheerful": ["Ha! Listen to me.", "Anyway, mustn't grumble. Well, I must, but I mustn't."],
    "melancholy": ["Still. Nothing lasts.", "I don't know why I'm telling you all this."],
    "shrewd": ["Remember that, if you're buying.", "Worth knowing, that."],
    "dreamy": ["Or so it seems to me, anyway.", "Do you ever feel the days are someone else's dream?"],
}.items():
    TAIL[_t] += _lines

for _t, _lines in {
    "nervous": ["You've not given up? On {obj}? Please say you've not."], "suspicious": ["Well? You said you'd see to {obj}."],
    "gruff": ["{obj.cap}. Anything?"], "warm": ["Sit down, sit down. Is there news of {obj}?"],
    "cheerful": ["Well? Don't keep me waiting - {obj}?"], "melancholy": ["You came back. Is it about {obj}? Tell me straight."],
    "shrewd": ["You've the look of someone with news. {obj.cap}?"], "dreamy": ["I left a light out for {obj}. Did you see it?"],
}.items():
    CHECKIN[_t] += _lines
STEP_NUDGE["ask"] += ["Go and see {far}, in {fvillage}. {fhe.cap} knows more than {fhe} lets on."]
STEP_NUDGE["search"] += ["Look at the {lm} again, if you've been. Things hide in plain sight."]
STEP_NUDGE["deal"] += ["Don't let {far} rob you. Haggle."]
STEP_NUDGE["bring"] += ["Remember what {far} wanted. {fhe.cap} won't budge without it."]
STEP_NUDGE["go"] += ["The way's by {region}. It's not a kind country."]
STEP_NUDGE["climax"] += ["It's {dir}. I'd go myself, if I could."]

# more ways to say what someone's like
PERSON_MORE = {
    "suspicious": ["Won't give you the time of day till {fhe} knows you. Then {fhe}'ll give you the whole day."],
    "gruff": ["Bark's worse than {fhis} bite, mostly."], "warm": ["One of the good ones. You'll see."],
    "cheerful": ["You'll hear {fhim} before you see {fhim}."], "melancholy": ["Lost someone, a while back. It took the light out of {fhim}."],
    "shrewd": ["Never lost a bargain in {fhis} life, to hear {fhim} tell it."], "dreamy": ["Talks to birds. Says they talk back."],
    "nervous": ["Kind, but frightened of everything. Be gentle."],
}
