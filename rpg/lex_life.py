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
                   "The tups are in with the ewes. Next spring's lambs, if all goes well."],
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
    "miller": {"spring": ["The millpond's full with the melt. Good water, and nothing to grind till harvest."],
               "summer": ["The wheel wants new paddles before the harvest comes in. Always something."],
               "autumn": ["Harvest's in, and every soul for miles wants their grain ground yesterday."],
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
                    "winter": ["The rats come indoors for the warmth. So do I."]},
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
