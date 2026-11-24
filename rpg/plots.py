"""Procedural quests: stories assembled from motive, object, obstacles, twist and ending.

A villager wants something (a MOTIVE: grief, debt, love, fear...) about something
(an OBJECT: a lost child, a strayed horse, a beast, a stolen heirloom, a shrine,
word from another village...). Between you and it stand one to three OBSTACLES,
each a story laid over one of a few mechanics the game already has:

    search   hidden at a landmark, sometimes only at night, at dawn, in fog
    slay     something guards the way
    ask      someone elsewhere knows: go and talk to them
    deal     someone wants paying, persuading, or facing down (your stats count)
    bring    someone wants something first: a trader's goods, a herb, a trinket
    deliver  an offering or token must be taken somewhere first
    go       just get there

When you reach the object there may be a TWIST (the beast is guarding young, the
heirloom is cursed, the one who asked lied...), and then you choose an ENDING
(return it, keep it, show mercy, sell it to a rival, tell the truth or a kind lie...).
Endings are remembered: liking, rumour, the chronicle.

Every step becomes an ordinary journal errand, so the map, the advisor and saving
all work. Every piece is filled from the world: real villagers, their jobs and
villages, real landmarks and regions, creatures that live there, the season.

36 motives x 24 objects x 40 obstacles (in chains of one to three) x 32 twists x
20 endings, before any wording varies. Recent pieces are avoided, so stories don't
repeat their shapes.
"""
from . import story as S
from .textgen import cap, article

# ======================================================================= OBJECTS
# kind: person | animal | creature | item | place | word
OBJECTS = {
    # people
    "child": dict(kind="person", lines=["\"{obj_cap} went off {toward} {when} and hasn't come home.\"", "\"{obj_cap}'s missing. Last seen heading off {toward}, {when}.\""],
                  title=["Where is {obj}?", "Bring {obj} home"]),
    "elder": dict(kind="person", lines=["\"{obj_cap} wandered off {when}. {ohe_cap}'s not been right in the head since the winter. {dir_cap}, we think.\"",
                                        "\"{obj_cap} went off {toward} to visit an old grave {when}, and never came back.\""],
                  title=["Old {oname}", "Find {obj}"]),
    "sweetheart": dict(kind="person", lines=["\"{obj_cap} and I had words, and {ohe} walked out {toward} {when}. I need {ohim} back.\"",
                                             "\"{obj_cap} went off {toward} {when} - to make {ohis} fortune, {ohe} said. It's been too long.\""],
                       title=["{giver}'s {oname}", "After {obj}"]),
    "apprentice": dict(kind="person", lines=["\"My apprentice, {obj}, ran off {toward} {when}. Half-trained and owing me a year.\"",
                                             "\"{obj_cap} - my apprentice - went off {toward} {when} to fetch something for the trade and hasn't come back.\""],
                       title=["The runaway apprentice", "{giver}'s apprentice"]),
    "runaway": dict(kind="person", lines=["\"{obj_cap} ran away {when}, after a quarrel at home. Somewhere {dir}.\"",
                                          "\"{obj_cap} took a loaf and a blanket and went off {toward} {when}. We know why. We need {ohim} back anyway.\""],
                    title=["The runaway", "{obj_cap} ran away"]),
    "stranger": dict(kind="person", lines=["\"A traveller came through {when}, sick and feverish, and went on {toward} before anyone could stop {ohim}.\"",
                                           "\"There's a stranger out {dir} - hurt, the shepherd says. We can't just leave {ohim}.\""],
                     title=["The sick traveller", "A stranger in the wild"]),
    # animals
    "flock": dict(kind="animal", lines=["\"The {oname} broke through the hedge {when} and went off {toward}.\"", "\"My {oname} - gone off {toward}, {when}. The wolves will have them if we don't hurry.\""],
                  title=["The strayed {oname}", "After the {oname}"]),
    "dog": dict(kind="animal", lines=["\"My dog, {oname}, went after a hare {when}, off {toward}, and didn't come back.\"", "\"{oname_cap}'s gone. Best sheepdog in the valley. {dir_cap}, {when}.\""],
                title=["{oname_cap}, the lost dog", "Whistle for {oname}"]),
    "horse": dict(kind="animal", lines=["\"The {oname} slipped its tether {when} and bolted off {toward}.\"", "\"Our {oname} - we can't plough without it - ran off {toward} {when}.\""],
                  title=["The bolted {oname}", "Catch the {oname}"]),
    "hawk": dict(kind="animal", lines=["\"My hawk flew off {toward} {when} and didn't come to the lure. She'll be sitting somewhere sulking, in a tall tree.\"",
                                       "\"Lost my falcon, {when}. Flew off {toward} after a heron. There's a silver bell on her jess.\""],
                 title=["The lost hawk", "{giver}'s falcon"]),
    # creatures
    "beast": dict(kind="creature", lines=["\"There's a {oname} out {dir}. It's had two sheep and a dog {when}.\"", "\"A {oname} has made its lair {dir}. Nobody dares go that way now.\""],
                  title=["The {oname} {dir_short}", "A {oname} to kill"]),
    "dead": dict(kind="creature", lines=["\"Something dead walks {dir}. A {oname}, the old folk call it. It came up from the ground {when}.\"",
                                         "\"A {oname} - dead, and walking - has been seen {dir}. It knocked at a door {when}.\""],
                 title=["The {oname}", "Lay the {oname} to rest"]),
    "lurker": dict(kind="creature", lines=["\"Something's got into the {place} {dir}. A {oname}, by the look. Folk used to go there.\"",
                                           "\"We can't get to the {place} {dir} any more. There's a {oname} there.\""],
                   title=["The {oname} at the {place}", "Clear the {place}"]),
    "terror": dict(kind="creature", lines=["\"There's a great {oname} {dir}, bigger than any I've seen. It took a grown man {when}.\"",
                                           "\"The old folk say a {oname} like that comes once in a lifetime. It's out {dir}.\""],
                   title=["The great {oname}", "A {oname} for the songs"]),
    # items
    "heirloom": dict(kind="item", lines=["\"The {oname} is gone - stolen {when}. It's been in the family six generations.\"", "\"Somebody took the {oname} {when}. It's all we had of the old days.\""],
                     title=["The stolen {oname}", "The {oname}"]),
    "tool": dict(kind="item", lines=["\"My {oname} went missing {when}. I can't do a day's work now.\"", "\"Someone made off with my {oname} {when}. My trade's at a standstill.\""],
                 title=["{giver}'s {oname}", "The missing {oname}"]),
    "remedy": dict(kind="item", lines=["\"There's a {oname} that grows {dir}, the old wives say. It's the only thing that'll help.\"",
                                       "\"The cure's a {oname}. Our wise-woman says it grows {dir}, if you know where.\""],
                   title=["The {oname}", "A cure from the wild"]),
    "letter": dict(kind="item", lines=["\"A {oname} was lost on the road {when} - dropped, or taken. It mustn't fall into the wrong hands.\"",
                                       "\"The carrier was robbed {when}, {dir}. The {oname} was in his bag.\""],
                   title=["The lost {oname}", "Recover the {oname}"]),
    "keepsake": dict(kind="item", lines=["\"I lost my {oname} {when}, out {dir}. I know it's foolish. It's all I have of them.\"",
                                         "\"My {oname}. I dropped it {when}, somewhere {dir}. Please.\""],
                     title=["{giver}'s {oname}", "A small lost thing"]),
    "charter": dict(kind="item", lines=["\"The {oname} that proves our claim to the common was taken {when}. Without it, the lord's men will have the land.\"",
                                        "\"Our {oname} - the old parchment - has gone. Taken {dir}, we think. Everything depends on it.\""],
                    title=["The {oname}", "Proof of right"]),
    "charm": dict(kind="item", lines=["\"The {oname} that hung over our gate is gone - taken {when}. Since then, nothing's gone right.\"",
                                      "\"Somebody's had the {oname} off the well-head. The wise-woman says it must come back before the next moon.\""],
                  title=["The {oname}", "Bring back the {oname}"]),
    # places
    "shrine": dict(kind="place", lines=["\"The shrine of {spirit} {dir} was fouled {when}, and nobody's set it right.\"",
                                        "\"Someone must go to the shrine of {spirit}, {dir}, and set it right. The village has felt it.\""],
                   title=["The fouled shrine", "Tend the shrine of {spirit}"]),
    "grave": dict(kind="place", lines=["\"My {kin} lies buried by the {place}, {dir}. Nobody has tended the grave in years.\"",
                                       "\"There's a grave by the {place} {dir} - my {kin}'s. I can't walk that far any more.\""],
                  title=["A grave by the {place}", "{giver}'s {kin}"]),
    # word
    "news": dict(kind="word", lines=["\"I need word from {far} in {fvillage}. I've heard nothing in weeks, and that's not like {far}.\"", "\"Go to {fvillage}, find {far}, and ask whether what they're saying about the family there is true. I have to know.\""],
                 title=["Word from {fvillage}", "Ask {far}"]),
}
PERSON_WHO = {"child": ["little ", "young "], "elder": ["old "], "sweetheart": [""], "apprentice": ["young "], "runaway": ["young ", ""], "stranger": [""]}
ANIMAL_NAMES = {"flock": ["sheep", "goats", "geese", "heifers", "ewes"], "dog": ["Brack", "Nell", "Tam", "Bess", "Rook", "Moss", "Fly", "Gyp"],
                "horse": ["grey mare", "plough-horse", "pony", "old cob", "black gelding"], "hawk": ["hawk"]}
ITEM_NAMES = {
    "heirloom": ["silver-mounted drinking horn", "old sword from over the hearth", "bridal crown of braided straw and silver", "great-grandmother's brooch", "bronze bowl"],
    "tool": ["best chisel", "shuttle", "pruning hook", "awl and needles", "hammer", "spinning wheel's flyer", "set of weights"],
    "remedy": ["moonwort", "feverfew in flower", "white hellebore", "adder's-tongue fern", "eyebright", "lungwort"],
    "letter": ["sealed letter", "bundle of letters", "deed of sale", "will", "letter under the reeve's seal"],
    "keepsake": ["locket", "ring", "carved wooden bird", "lock of hair in a twist of cloth", "comb", "little brass bell"],
    "charter": ["charter", "grant of common", "book of rights", "boundary roll"],
    "charm": ["horse-brass", "rowan cross", "holed stone", "iron horseshoe", "corn dolly from last harvest"],
}
WHEN = ["yesterday", "two days back", "before dawn", "at the last full moon", "three nights ago", "on market day", "after the storm", "last week"]
KIN = ["mother", "father", "first husband", "first wife", "brother", "sister", "son", "daughter", "old master", "grandmother"]

# ======================================================================= MOTIVES
# Why they want it, in their own voice. fits: the object TAGS this motive makes sense for (any one will do).
# Each line may narrow that with its own tags ("" = any the motive fits), and `who` limits the speaker:
# young / old / notold (by age), notelder (not the village head), seller (keeps a stall or trades).
OBJECT_TAGS = {
    "child": "person missing kin young", "elder": "person missing kin old", "sweetheart": "person missing love quarrel",
    "apprentice": "person missing trade young", "runaway": "person missing quarrel kin young", "stranger": "person sick stranger",
    "flock": "animal stray livestock", "dog": "animal stray pet", "horse": "animal stray livestock trade", "hawk": "animal stray pet",
    "beast": "creature danger predator", "dead": "creature danger undead", "lurker": "creature danger haunt", "terror": "creature danger predator",
    "heirloom": "item stolen heirloom", "tool": "item lost trade", "remedy": "item cure", "letter": "item lost stolen",
    "keepsake": "item lost memento", "charter": "item stolen common", "charm": "item stolen luck",
    "shrine": "place holy", "grave": "place grave kin", "news": "word",
}
M = lambda fits, lines, who="": dict(fits=set(fits.split()), lines=[l if isinstance(l, tuple) else ("", l) for l in lines], who=who)
MOTIVES = {
    "loss":      M("missing stray lost stolen memento heirloom", ["I've walked the lane every night since. I know every stone in it now.", "I still set a place for {obj}. Then I clear it away again."]),
    "grief":     M("memento heirloom grave", [("memento heirloom", "It's all I have left of them."), ("grave", "I've not been since the burying. I keep putting my boots on and taking them off again.")]),
    "love":      M("love memento kin", [("love kin", "I'd go myself, but my legs won't have it. I've tried. I got as far as the stile."), "I've a ribbon of {ohis} in my pocket. I keep putting my hand on it."]),
    "debt":      M("trade livestock common", ["There's a man coming from the market at the next moon with a tally-stick. Mine's the long one.", "There's money owing, and this is the only way I pay it back."]),
    "fear":      M("danger undead holy", ["We bar the doors at dusk now. We never used to own a bar.", "The children won't sleep. Neither will I."]),
    "duty":      M("danger holy grave common word", ["It falls to me. It's fallen to me for twenty years. My knees have stopped agreeing.", "I went halfway, last week. Then I came back. I'm not proud of it."]),
    "pride":     M("stolen trade stray", ["They stop talking when I come into the alehouse. Then they start again, louder.", "My father would have had it back by now. Everybody keeps telling me so."]),
    "guilt":     M("missing stray lost quarrel", [("missing stray lost", "I left the gate. I know I left the gate. I keep going back to look at it."), ("quarrel", "I said a thing at supper. I'd give my right hand to have it back in my mouth.")]),
    "rivalry":   M("stolen trade livestock", ["If the folk at {fvillage} hear of this, I'll never live it down.", "{other} would love to see me fail."]),
    "curiosity": M("word holy", ["I lie awake making up answers. None of them are any good.", "It's been at me for weeks, like a stone in a boot."]),
    "revenge":   M("predator stolen", [("predator", "It took my best dog. I found her collar. Only her collar."), "I've a fair idea who. I want to be sure before I knock on their door."]),
    "promise":   M("missing grave word holy memento", ["I gave my word. My word's about the only thing I own outright.", "I swore on my mother's grave I'd see it done."]),
    "hunger":    M("livestock predator", [("livestock", "Without {obj}, we'll go hungry before the year's out."), ("predator", "Every beast it takes is meat off our table."),
                                         "We had nettle soup three nights running. The little ones have stopped asking what's in it."]),
    "illness":   M("cure", ["My {kin} has stopped eating. Just water, and not much of that.", "There's a fever in the house. I hung wet sheets in the doorway, like my mother did. It hasn't helped."]),
    "inheritance": M("heirloom", ["The old man promised it to me with his hand on my head. I was nine. I remember the smell of his pipe.", "Without it, my cousins will have the lot."]),
    "honour":    M("heirloom predator grave", ["My grandfather's name is cut on the moot-stone. I'd like it to stay a name people say kindly.", "We've not got much. We've got our name. People still lend to us on it."]),
    "jealousy":  M("love word", [("love", "I need to know who {ohe} is with."), ("word", "They're all talking. I need to know the truth.")]),
    "homesick":  M("word memento", [("word", "I've not been home in six years. I don't even know if the door's the same colour."), ("memento", "It smells of home. That's all. That's enough.")]),
    "superstition": M("luck holy undead", ["The milk turns in a night. Two calves born dead. The dog won't go past the gate.", "The wise-woman says the village is cursed until it's done."]),
    "faith":     M("holy luck", ["The candles go out in a still room. Every one, all at once.", "My grandmother made me kneel there every spring. It shouldn't be left like that."]),
    "ambition":  M("trade", ["With it, I'd have a stall of my own. I've picked the spot. By the well, out of the wind.", "This is my chance. I'll not get another."], who="notold"),
    "shame":     M("lost stolen quarrel", ["I go to the well before light now, so nobody's there.", "Nobody must know it was me."]),
    "mercy":     M("sick stray", ["You can hear it, some nights, when the wind's right. I lie there and listen.", "Nobody deserves to be left like that."]),
    "justice":   M("stolen", ["Nobody's said a word. Everybody knows. It sits in the village like smoke.", "What was taken should be given back. That's all."]),
    "loneliness": M("kin pet love", ["I talk to the hens now. They're not much for answering.", "There's nobody else. I've asked. I've asked everyone twice."]),
    "nostalgia": M("grave holy heirloom memento", [("grave holy", "I used to go there as a child. I want it the way it was."), ("heirloom memento", "It was my father's. He'd turn it over in his hands by the fire, all evening, saying nothing.")]),
    "protection": M("danger", ["I've got little ones. I've told them it's a story to frighten them. It isn't.", "I sit up with the axe across my knees. I've not slept a whole night in a week."]),
    "wager":     M("predator stray", ["I made a bet in the alehouse. I'd had three. I'd have bet the roof off my house.", "There's money riding on it - mine."], who="notelder"),
    "apprenticeship": M("lost trade", ["My master hasn't said a word about it. That's worse than shouting.", "I'm only learning. I can't afford a mistake like this."], who="young notelder"),
    "betrothal": M("memento heirloom love word", ["I'm to be married at the next moon. My mother's already sewing. She doesn't know yet.", "There's no wedding without it. Not in our family. Not ever."], who="notold notelder"),
    "quarrel":   M("lost stray stolen", ["{other} says it's my fault. I'll prove it isn't.", "It started a quarrel that's split the village."]),
    "omen":      M("danger holy luck undead", ["I've dreamed it three nights running. The same door, the same sound behind it.", "A hare crossed my path backwards. I know what that means."]),
    "vow":       M("holy grave", [("holy grave", "I made a vow at the shrine. I'm too old now to keep it."), "I swore an oath when I was young and foolish. It still binds."], who="old"),
    "rescue":    M("missing stray sick", ["Every hour you stand here is an hour gone.", "The nights are cold. You know what's out there at night."]),
    "reputation": M("stolen trade", ["Folk won't buy from me while this hangs over me.", "My good name's worth more than coin."], who="seller"),
    "kinship":   M("kin word grave", ["Blood is blood.", "Family looks after family. That's all there is to it."]),
}


def speaker_ok(who, npc):
    """Can this person say a line meant for `who`?"""
    from . import goods as GOODS
    band = npc.look.get("age_band", "mid")
    tests = {"young": band == "young", "old": band == "old", "notold": band != "old", "notelder": npc.role != "elder",
             "seller": npc.role == "merchant" or GOODS.sells(npc)}
    return all(tests.get(w, True) for w in who.split())


def motives_for(okey, npc):
    tags = set(OBJECT_TAGS.get(okey, "").split())
    return [k for k, m in MOTIVES.items() if m["fits"] & tags and speaker_ok(m["who"], npc)]


def motive_lines(mkey, okey):
    """The lines of this motive that fit this object."""
    tags = set(OBJECT_TAGS.get(okey, "").split())
    return [t for need, t in MOTIVES[mkey]["lines"] if not need or set(need.split()) & tags] or [t for _, t in MOTIVES[mkey]["lines"]]


# ======================================================================= OBSTACLES
# mechanic, object kinds it fits ("any" for all), intro (what you learn), journal title, plus parameters
OBSTACLES = {
    # search: hidden at a landmark, perhaps only at a certain time
    "tracks":      ("search", "person animal creature", "\"There'll be tracks by the {lm}, {lmdir}. Start there.\"", "Look for tracks at the {lm}", dict(cond=None)),
    "dropped":     ("search", "person animal item", "\"A shepherd saw something dropped by the {lm}, {lmdir}.\"", "Search the {lm}", dict(cond=None)),
    "moonlit":     ("search", "any", "\"There's a mark on the {lm}, {lmdir}, that only shows by moonlight, and it points the way to {obj}. Or so the old tales say.\"", "Search the {lm} by night", dict(cond="dark")),
    "fogbound":    ("search", "person item place", "\"The old ones say the way to {obj} only shows in fog. Look at the {lm}, {lmdir}, when the mist is down.\"", "Search the {lm} in fog or rain", dict(cond="fog_or_rain")),
    "dawnsign":    ("search", "any", "\"Folk say the first light of dawn falls on the {lm}, {lmdir}, and shows the way to {obj}. Be there for it.\"", "Search the {lm} at dawn", dict(cond="dawn")),
    "duskcall":    ("search", "animal person", "\"Go to the {lm}, {lmdir}, at dusk. That's when things come out, and {obj} with them, maybe.\"", "Search the {lm} at dusk", dict(cond="dusk")),
    "cache":       ("search", "item word", "\"Thieves stash things at the {lm}, {lmdir}, before moving them on. Look there first.\"", "Search the thieves' stash at the {lm}", dict(cond=None)),
    "scrawl":      ("search", "any", "\"Somebody's scratched a sign on the {lm}, {lmdir}, and I'd swear it's about {obj}. I couldn't read it. Maybe you can.\"", "Read the sign at the {lm}", dict(cond=None)),
    # slay: something guards the way
    "guarded":     ("slay", "person animal item place", "\"Something lairs on the way {gdir} - a {guard}. You'll not get past it.\"", "Deal with the {guard} on the way", {}),
    "brood":       ("slay", "creature", "\"It isn't alone. There's a {guard} with it, {gdir} - kill that first, or it'll come at your back.\"", "Kill the {guard} first", {}),
    "ambush":      ("slay", "item word person", "\"Whoever took it left a {guard} to watch the road {gdir}.\"", "The {guard} on the road", {}),
    "warden":      ("slay", "place", "\"A {guard} has taken the way {gdir}. Nothing goes by it.\"", "Clear the way of the {guard}", {}),
    # ask: someone elsewhere knows
    "witness":     ("ask", "person animal item", "\"{far} in {fvillage} was there when it happened. Ask {fhim}.\"", "Ask {far} in {fvillage}", {}),
    "gossip":      ("ask", "any", "\"{far}, over in {fvillage}, hears everything. If anyone knows, it's {fhim}.\"", "Hear what {far} knows", {}),
    "kinfolk":     ("ask", "person word", "\"{ohe_cap} has kin in {fvillage} - {far}. {ohe_cap} may have gone there first.\"", "Ask {far}, in {fvillage}", {}),
    "trader":      ("ask", "item animal", "\"A trader called {far} in {fvillage} buys things without asking questions. Ask what came through.\"", "Question {far} in {fvillage}", {}),
    "wisewoman":   ("ask", "item place creature", "\"Go to {far} in {fvillage}. {fhe_cap} knows the old ways, and where things are.\"", "Consult {far} in {fvillage}", {}),
    "drover":      ("ask", "animal person", "\"The drovers came through yesterday. {far} in {fvillage} might have seen.\"", "Ask the drover {far}", {}),
    "shepherds":   ("ask", "any", "\"The shepherds up on the tops see everything. {far}, in {fvillage}, will know who to ask.\"", "Ask {far} what the shepherds saw", {}),
    # deal: someone wants paying, persuading or facing down
    "toll":        ("deal", "any", "\"{far} in {fvillage} keeps the only bridge that way. {fhe_cap}'ll want paying.\"", "Get past {far}'s toll", dict(price=10)),
    "fence":       ("deal", "item", "\"It's been sold on to {far} in {fvillage}. {fhe_cap} won't give it back for nothing.\"", "Get it back from {far}", dict(price=18)),
    "ferryman":    ("deal", "person animal place", "\"The ford's up. {far} in {fvillage} has a boat, but {fhe}'s a hard one to deal with.\"", "Bargain with {far} for the crossing", dict(price=8)),
    "stubborn":    ("deal", "word person", "\"{far} in {fvillage} knows - but {fhe} won't say, not to me.\"", "Get {far} to talk", dict(price=6)),
    "hoarder":     ("deal", "item", "\"{far} in {fvillage} found it and says finders keepers.\"", "Persuade {far} to give it up", dict(price=14)),
    "lordsman":    ("deal", "item word place", "\"The lord's man, {far}, is lodging at {fvillage}. Nothing happens without {fhis} say-so.\"", "Win over the lord's man, {far}", dict(price=20)),
    # bring: someone wants something first
    "smithwork":   ("bring", "item place creature", "\"{far} in {fvillage} could help, but {fhe} wants a whetstone first - {fhis} last one cracked.\"", "Bring {far} a whetstone", dict(item="whetstone")),
    "wiseprice":   ("bring", "any", "\"{far} in {fvillage} will tell you, for a healing herb. {fhe_cap}'s always short.\"", "Bring {far} a healing herb", dict(any_kind="herb")),
    "bribe":       ("bring", "any", "\"{far} in {fvillage} might talk, for something pretty. A pendant, a cloak pin.\"", "Bring {far} a trinket", dict(any_kind="trinket")),
    "candlecost":  ("bring", "place word", "\"{far} in {fvillage} keeps a vigil. Bring candles, and {fhe}'ll help.\"", "Bring {far} beeswax candles", dict(item="bundle of beeswax candles")),
    "holywater":   ("bring", "creature place", "\"{far} in {fvillage} says you'll want holy water for it, and {fhe}'ll bless the way if you bring some.\"", "Bring {far} holy water", dict(item="flask of holy water")),
    "rope":        ("bring", "person animal", "\"{far} in {fvillage} can help, but {fhe}'ll need a draught - {fhe}'s been ill.\"", "Bring {far} a healing draught", dict(any_kind="potion")),
    "food":        ("bring", "any", "\"{far} in {fvillage} hasn't eaten in two days. Feed {fhim}, and {fhe}'ll tell you anything.\"", "Bring {far} something to eat", dict(any_kind="food")),
    "charmprice":  ("bring", "creature place item", "\"{far} in {fvillage} won't go near it without a rowan cross. Find {fhim} one.\"", "Bring {far} a rowan cross", dict(item="rowan cross")),
    # deliver: something must be taken somewhere first
    "offering":    ("deliver", "place creature", "\"Leave an offering at the shrine of {spirit} first, {sdir}, or the spirits won't help.\"", "Leave an offering at the shrine of {spirit}", {}),
    "message":     ("deliver", "person word", "\"Take this token to {fvillage} first, so they'll know you come from me.\"", "Carry {giver}'s token to {fvillage}", {}),
    "permission":  ("deliver", "item place", "\"The way runs through {fvillage}'s land, and they don't like strangers on it. Take this token and show it there, so they'll know you come from me.\"", "Show {giver}'s token at {fvillage}", {}),
    # go: just get there - a long walk, a dangerous place
    "longroad":    ("go", "any", "\"The quickest way is through {region}. Go carefully.\"", "Cross {region}", {}),
    "ruinroad":    ("go", "any", "\"The trail runs past the old {ruin} - pass it, and go on from there.\"", "Pass the old {ruin}", {}),
    "highplace":   ("go", "person animal creature place", "\"From the high ground at {region} you'll see the whole country. Look from there.\"", "Look out from {region}", {}),
    "crossing":    ("go", "any", "\"You'll have to go round by {region}; the direct way's flooded.\"", "Go round by {region}", {}),
}

# ======================================================================= TWISTS
# kinds it fits, what you find out, the endings it opens
TWISTS = {
    "young":       ("creature", "As you raise your weapon you see why it fought so hard: young, mewling, in the hollow behind it.", ["spare", "kill"]),
    "wounded":     ("creature animal", "It's already hurt - a snare-wire bitten deep into one leg. Someone set traps here.", ["spare", "kill", "free"]),
    "old":         ("creature", "Up close it's old, grey-muzzled, half-blind. It can barely stand.", ["spare", "kill"]),
    "bewitched":   ("creature animal", "There's a twist of red thread knotted round its neck - a hex-binding. Someone sent it.", ["kill", "spare", "expose"]),
    "notmissing":  ("person", "{obj_cap} isn't lost at all. {ohe_cap}'s made camp here on purpose, and doesn't want to go back.", ["persuade", "let_go", "return"]),
    "eloped":      ("person", "{obj_cap} isn't alone - there's someone with {ohim}, and they're holding hands.", ["let_go", "persuade", "return"]),
    "hiding":      ("person", "{obj_cap} is terrified - not of the wild, but of going home. There are bruises {ohe} tries to hide.", ["let_go", "true_owner", "return"]),
    "fever":       ("person animal", "{obj_cap} is burning with fever. Moving {ohim} now could kill {ohim}.", ["return", "bargain"]),
    "cursed":      ("item", "The moment you touch it, your fingers go numb. Something is wrong with it - a curse, maybe, or worse.", ["destroy", "shrine", "return"]),
    "notheirs":    ("item", "Scratched on it, plain as day, is another name: {other}. It was never {giver}'s at all.", ["true_owner", "return", "keep"]),
    "thiefchild":  ("item", "There's a child's den here - a blanket, apple cores, and the thing you came for. The thief was a hungry child.", ["forgive", "report", "return"]),
    "rivalwant":   ("item word", "Someone else has been asking after it: {far}, from {fvillage}, and {fhe} offers good coin.", ["sell_rival", "return", "bargain"]),
    "fake":        ("item", "It's a copy - a cheap one. The real one must have been sold long ago. Does {giver} know?", ["tell_truth", "comfort_lie", "keep_secret"]),
    "worthmore":   ("item", "Cleaned off, it's worth far more than anyone said - real silver under the grime.", ["return", "keep", "bargain"]),
    "broken":      ("item", "It's broken - snapped in two. You could still bring it back.", ["return", "tell_truth", "comfort_lie"]),
    "lied":        ("item person animal", "From what you find here, {giver} lied about how it happened. It wasn't lost. {giver} sold it, and the buyer wouldn't take it back.", ["expose", "return", "keep_secret"]),
    "badnews":     ("word person", "The news is bad: {far}'s {kin} died at the turn of the season. Nobody has told {giver}.", ["tell_truth", "comfort_lie"]),
    "goodnews":    ("word", "The news is better than anyone hoped - a birth, a wedding, a fortune made.", ["return", "bargain"]),
    "secretkin":   ("word person", "{far} lets slip something {giver} doesn't know: they're kin. Half-siblings.", ["tell_truth", "keep_secret"]),
    "debtowed":    ("word item", "It turns out {giver} owes {far} money - a lot of it. {far} wants it said.", ["tell_truth", "keep_secret", "bargain"]),
    "fouledby":    ("place", "It wasn't spirits that fouled it. Someone did this on purpose - you find a dropped glove with {other}'s mark on it.", ["expose", "keep_secret", "return"]),
    "spirit":      ("place", "The air goes still and cold, and you feel very strongly that something is grateful you came.", ["shrine", "return"]),
    "emptygrave":  ("place", "The grave has been opened, and it's empty.", ["tell_truth", "comfort_lie", "bury"]),
    "treasure":    ("place", "Under a loose stone you find a little hoard of old coins, green with age.", ["keep", "share", "return"]),
    "flowers":     ("place", "Someone has been here before you, often: fresh flowers, kept up for years.", ["return", "keep_secret", "tell_truth"]),
    "followed":    ("any", "You're not alone - someone has been following you from the village, and ducks out of sight when you turn.", ["return", "expose"]),
    "storm":       ("person animal item place", "A storm comes in fast as you get there, and you have to shelter half the night before you can do anything.", ["return"]),
    "stranger":    ("item person", "An old woman sits by the way, and asks for a share of whatever you came for. She doesn't look like she'd take no kindly.", ["share", "return"]),
    "ghostly":     ("place item creature", "For a moment you see a figure standing where no one is - and then it's gone, and the place feels lighter.", ["shrine", "return", "bury"]),
    "swapped":     ("animal", "It isn't {giver}'s {oname} at all - it's another, wilder one. {giver}'s must be elsewhere. But this one would do.", ["return", "free", "keep"]),
    "rich":        ("person", "{obj_cap} has found something out here - a seam of good stone, a hidden spring - and wants a share of the reward for telling.", ["share", "return"]),
    "too_late":    ("creature", "Near its lair lie the remains of the last person who tried this, their purse still at their belt.", ["kill", "bury", "spare"]),
}

# ======================================================================= ENDINGS
# label (as a choice), and what it does
ENDINGS = {
    "return":      {"person": "Bring {obj} home to {giver}", "animal": "Bring {obj} back to {giver}", "item": "Take it back to {giver}",
                    "place": "Go back and tell {giver} it's done", "word": "Take the news back to {giver}"},
    "kill":        "Finish it - that's what you came for",
    "spare":       "Let it live, and say it fled",
    "free":        "Cut it loose and let it go",
    "expose":      "Tell the village what you found",
    "persuade":    "Talk {ohim} into coming home",
    "let_go":      "Let {ohim} stay, and take word back instead",
    "true_owner":  "Take it to {other} instead",
    "destroy":     "Destroy it, here and now",
    "shrine":      "Leave it on holy ground",
    "keep":        "Keep it for yourself",
    "forgive":     "Leave the child something, and say nothing",
    "report":      "Tell {giver} who took it",
    "sell_rival":  "Sell it to {far} instead",
    "bargain":     "Ask {giver} for more, first",
    "tell_truth":  "Tell {giver} the truth",
    "comfort_lie": "Tell {giver} a kinder story",
    "keep_secret": "Say nothing about it",
    "share":       "Share it, fairly",
    "bury":        "Do right by the dead first",
}
# ======================================================================= THE FOLLOWER
# The 'followed' twist: who has been dogging your steps from the village, why, and what you do about them.
# Settling it is a choice of its own; the errand then ends the usual way (for a beast, still the kill).
# Each option: label, what happens, liking (giver, follower), reward scale, an aftermath line for the end, and a
# note for the chronicle. 'close' options end the errand on the spot.
FOLLOWED = {
    "glory": dict(who="neighbour", reveal=[
        "You double back and catch {shadow} crouched behind a bush, red to the ears. {sh_he_cap} only wanted to be there when it was done - to have a story of {sh_his} own, for once.",
        "It's {shadow}, from {village}, caught in the open and trying to look as if {sh_he} was out for a walk. {sh_he_cap} admits it: {sh_he} wanted a share of the glory."],
        options={
            "f_credit": ("Let {shadow} share the credit", "You wave {shadow} over. From here on it's {sh_his} story as much as yours, and {sh_he} looks ten years younger for it.",
                         (0, 4), 0.8, "{shadow} tells the tale louder than you would, and takes half the thanks. You let {sh_him}.", "and let {shadow} share the credit"),
            "f_send": ("Send {shadow} home", "\"Go home, {shadow}.\" {sh_he_cap} goes, scowling, kicking at the ferns.",
                       (0, -2), 1.0, None, None)}),
    "worry": dict(who="kin", reveal=[
        "It's {shadow}, {giver}'s {sh_kin}. {giver} didn't trust a stranger with this, and sent {sh_him} to keep an eye on you.",
        "You catch {shadow} - {giver}'s {sh_kin} - picking a burr out of {sh_his} sleeve. \"{giver} said to watch you,\" {sh_he} mumbles. \"Just in case.\""],
        options={
            "f_together": ("Let {shadow} walk with you", "You wave {shadow} out of hiding, and the two of you go on together. {sh_he_cap} talks the whole way.",
                           (2, 3), 1.0, "{shadow} vouches for every step of it, and {giver} looks a little ashamed of ever doubting you.", "with {giver}'s {sh_kin} {shadow} for company"),
            "f_words": ("Have words with {giver} about being watched", "You send {shadow} home with a message: you don't work with someone looking over your shoulder.",
                        (-2, 0), 1.3, "\"I had to be sure,\" {giver} mutters, and adds a good deal to what {he} owes you.", "and made {giver} pay for having you watched")}),
    "rival": dict(who="rival", reveal=[
        "It's {far}, from {fvillage}. {fhe_cap} heard what {giver} was offering, and meant to let you do the hard part and then get there first.",
        "You round on your follower: {far}, of {fvillage}, who has no business here at all. {fhe_cap} doesn't bother denying it. \"There's coin in this. Why should it all be yours?\""],
        options={
            "f_chase": ("Run {far} off", "You come at {far}, and {fhe} runs for {fvillage} without looking back.",
                        (1, -3), 1.0, None, "and ran off {far} of {fvillage}, who meant to steal the job"),
            "f_deal": ("Take {far}'s coin and let {fhim} claim it", "{far} counts coins into your hand and goes on ahead, to be the one who did it.",
                       (-4, 3), 0, None, "You took {far}'s coin and let {fhim} claim the credit for {giver}'s errand.", "close")}),
    "guilty": dict(who="neighbour", reveal=[
        "It's {shadow}. {sh_he_cap} goes white when you catch {sh_him}, and it all comes out: {guilt}. {sh_he_cap} followed you to see whether you'd find out.",
        "You catch {shadow} by the collar. {sh_he_cap} doesn't struggle; it's almost a relief to {sh_him}. {guilt_cap}. {sh_he_cap} had to know if you'd find out."],
        options={
            "f_expose": ("Tell the village what {shadow} did", "You'll tell {village} the whole of it. {shadow} doesn't argue.",
                         (1, -4), 1.0, "When you tell it, the village turns to look at {shadow}. {sh_he_cap} doesn't meet anyone's eye.", "and told {village} what {shadow} had done"),
            "f_confess": ("Make {shadow} tell {giver} {sh_him}self", "\"You'll tell {giver},\" you say. \"Not me. You.\" {shadow} swallows, and nods.",
                          (1, 1), 1.0, "{shadow} stammers it all out to {giver}. It's hard to watch, and better than the alternative.", "and saw {shadow} own up to {giver}"),
            "f_secret": ("Keep {shadow}'s secret", "You let {sh_him} go. Some things don't need to be said.",
                         (0, 4), 1.0, None, None)}),
    "child": dict(who="child", reveal=[
        "It's a child - {shadow}, from {village}, no more than ten, with a stick for a sword. {sh_he_cap} wants to do what you do when {sh_he} grows up.",
        "A small face peers out of the bracken: {shadow}, a {village} child, who has walked all this way on {sh_his} own to see a real adventure."],
        options={
            "f_lesson": ("Let {shadow} watch, then walk {sh_him} home", "You make {shadow} promise to stay back, and {sh_he} does - mostly. {sh_his_cap} eyes are enormous.",
                         (2, 0), 1.0, "{shadow} is home before you've finished telling it, already telling it better.", "with a {village} child trailing at your heels"),
            "f_shoo": ("Send {shadow} running home", "\"Home. Now.\" {shadow} runs, and you watch until {sh_he}'s out of sight.",
                       (0, 0), 1.0, None, None)}),
}
# what the follower had done, for 'guilty', by kind of errand
GUILT = {"item": "{sh_he} took it in the first place, and lost it", "animal": "{sh_he} left the gate open",
         "person": "{sh_he} said something cruel the night before {obj} went", "creature": "{sh_he} drew it here, leaving offal out at the edge of the wood",
         "place": "{sh_he} let the place go to ruin, after promising to keep it", "word": "{sh_he} was meant to carry this message months ago, and never did"}
KIN_WORDS = {"female": ["niece", "youngest", "cousin", "sister", "granddaughter"], "male": ["nephew", "youngest", "cousin", "brother", "grandson"]}


def _setup_followed(g, plot, F, home):
    """Choose who is following you, and why, when the twist is chosen."""
    w = g.world
    kind = plot["kind"]
    motives = [m for m in FOLLOWED if not (m == "rival" and plot.get("far_home") == home)]
    m = _choose(g, "follower", motives)
    who = FOLLOWED[m]["who"]
    if who == "neighbour":
        name = F["other"]
        n = S.find_npc(w, name)
        pr = n.pronouns() if n else _pron(g.rng.choice(["female", "male"]))
    elif who == "rival":
        name, pr = F["far"], dict(he=F["fhe"], him=F["fhim"], his=F["fhis"])
    else:
        gender = g.rng.choice(["female", "male"])
        name, pr = w.new_name(w.culture_of(home), gender), _pron(gender)
        F["sh_kin"] = g.rng.choice(KIN_WORDS[gender])
    F.update(shadow=name, sh_he=pr["he"], sh_him=pr["him"], sh_his=pr["his"], sh_he_cap=cap(pr["he"]), sh_his_cap=cap(pr["his"]))
    if m == "guilty":
        F["guilt"] = fill(GUILT[kind], F)
        F["guilt_cap"] = cap(F["guilt"])
    plot["follow"] = m
    plot["follow_real"] = who in ("neighbour", "rival")      # someone whose liking you can change


def _settle_follower(g, plot, key):
    """Carry out the choice about the follower. Returns True if that ends the errand."""
    F = plot["F"]
    label, text, (dg, df), bonus, after, note, *close = FOLLOWED[plot["follow"]]["options"][key]
    g.emit(fill(text, F))
    if dg:
        _like(g, plot["giver"], dg)
    if df and plot.get("follow_real"):
        _like(g, F["shadow"], df)
    plot["bonus"] = plot.get("bonus", 1.0) * bonus if bonus else plot.get("bonus", 1.0)
    plot["follow_after"] = fill(after, F) if after else None
    plot["follow_note"] = fill(note, F) if note else None
    if close:
        gold = g.rng.randint(20, 45)
        g.player.gold += gold
        g.emit(f"({gold} coins.)")
        _close(g, plot, plot["follow_note"], xp=15, story=f"you sold {plot['giver']}'s errand to a rival", like=-2)
        return True
    if key == "f_expose":
        for n in g.world.tiles[plot["home"]].npcs:
            if n.name not in (plot["giver"], F["shadow"]):
                n.like(1)
    return False


# a beast is either dealt with or let go: walking back to the giver with it still alive isn't an ending
KIND_ENDINGS_OK = {"creature": {"kill", "spare", "free", "expose", "bury"}}
KIND_DEFAULT_ENDINGS = {"person": ["return"], "animal": ["return", "free"], "creature": ["kill"], "item": ["return", "keep"],
                        "place": ["return"], "word": ["return"]}


# ======================================================================= the engine
def _pron(g_):
    from .world import PRONOUNS
    return PRONOUNS.get(g_, PRONOUNS["female"])


def fill(text, F):
    from .textgen import fix_articles
    out = text
    for k, v in F.items():
        if isinstance(v, str):
            out = out.replace("{" + k + "}", v)
    return fix_articles(out) if "{" not in out else out      # "a adder's-tongue fern" -> "an adder's-tongue fern", once all is filled


def _weight_recent(g, kind, pool):
    """Prefer pieces not used in recent stories."""
    recent = getattr(g, "plot_recent", {}).get(kind, [])
    return [0.15 if k in recent[-6:] else 0.5 if k in recent else 1.0 for k in pool]


def _remember(g, kind, key):
    if not hasattr(g, "plot_recent"):
        g.plot_recent = {}
    g.plot_recent.setdefault(kind, []).append(key)
    g.plot_recent[kind] = g.plot_recent[kind][-20:]


def _choose(g, kind, pool):
    pool = list(pool)
    return g.rng.choices(pool, _weight_recent(g, kind, pool))[0] if pool else None


def _wild(g, home, lo, hi):
    w = g.world
    c = [p for p in w.land if lo <= abs(p[0] - home[0]) + abs(p[1] - home[1]) <= hi and not w.tiles[p].site]
    return g.rng.choice(c) if c else None


def _landmark(g, home, lo, hi, used):
    w = g.world
    c = [(p, f) for p in w.land for f in w.tiles[p].features if lo <= abs(p[0] - home[0]) + abs(p[1] - home[1]) <= hi
         and not ((f.state or {}).get("secret") or {}).get("key") in ("plot", "heirloom") and (p, f.noun) not in used]
    return g.rng.choice(c) if c else None


def _far_npc(g, home, used):
    w = g.world
    c = [(v, n) for v in w.villages if v != home for n in w.tiles[v].npcs if n.name not in used]
    return g.rng.choice(c) if c else None


def _species(g, place, undead=None, strong=False):
    w = g.world
    b = w.tiles[place].biome
    pool = [s for s in w.species if (undead is None or bool(s["arch"].get("undead")) == undead) and (b in s["arch"]["biomes"] or s["home"] == b)]
    return g.rng.choice(pool or [s for s in w.species if undead is None or bool(s["arch"].get("undead")) == undead] or w.species)


def make(g, npc):
    """Build a story for this villager, or None if the world can't support one right now."""
    w = g.world
    home = npc.home
    vname = w.tiles[home].site["name"]
    pr = npc.pronouns()
    others = [n for n in w.tiles[home].npcs if n is not npc]
    other = g.rng.choice(others).name if others else w.new_name(w.culture_of(home), g.rng.choice(["female", "male"]))
    used_lm, used_npc = set(), {npc.name}
    # object
    feasible = [k for k, o in OBJECTS.items()
                if not (o["kind"] == "word" and len(w.villages) < 2)
                and not (k == "dead" and not any(s["arch"].get("undead") for s in w.species))
                and not (k == "shrine" and not any(w.tiles[p].site and w.tiles[p].site["kind"] == "shrine" for p in w.land))]
    okey = _choose(g, "object", feasible)
    obj = OBJECTS[okey]
    kind = obj["kind"]
    F = dict(giver=npc.name, gjob=npc.job, village=vname, he=pr["he"], him=pr["him"], his=pr["his"], he_cap=cap(pr["he"]), his_cap=cap(pr["his"]),
             other=other, when=g.rng.choice(WHEN), kin=g.rng.choice(KIN))
    plot = dict(id=getattr(g, "plot_seq", 0) + 1, giver=npc.name, home=home, village=vname, okey=okey, kind=kind, steps=[], i=0, status="offered")
    g.plot_seq = plot["id"]
    # the object, placed in the world
    if kind in ("person", "animal"):
        where = _wild(g, home, 2, 5)
        if not where:
            return None
        plot["target"] = where
        if kind == "person":
            gg = g.rng.choice(["female", "male"])
            nm = w.new_name(w.culture_of(home), gg)
            op = _pron(gg)
            F.update(oname=nm, obj=g.rng.choice(PERSON_WHO[okey]) + nm, ohe=op["he"], ohim=op["him"], ohis=op["his"], ohe_cap=cap(op["he"]))
        else:
            nm = g.rng.choice(ANIMAL_NAMES[okey])
            F.update(oname=nm, oname_cap=cap(nm), obj=nm if okey == "dog" else f"the {nm}", ohe="it", ohim="it", ohis="its", ohe_cap="It")
    elif kind == "creature":
        where = None
        if okey == "lurker":
            lm = _landmark(g, home, 2, 5, used_lm)
            if not lm:
                return None
            where = lm[0]
            used_lm.add((lm[0], lm[1].noun))
            F["place"] = lm[1].noun
        else:
            where = _wild(g, home, 2, 5)
        if not where:
            return None
        sp = _species(g, where, undead=(okey == "dead") if okey == "dead" else False, strong=okey == "terror")
        c = w.make_creature(sp, (w.tiles[where].danger or 2) + (2 if okey == "terror" else 0), boss=False)
        c.aggressive = False          # it waits: you decide what happens when you find it
        plot["creature_spec"] = (sp["key"] if "key" in sp else None)
        plot["target"] = where
        plot["_creature"] = c
        F.update(oname=sp["name"], obj=f"the {sp['name']}", ohe="it", ohim="it", ohis="its", ohe_cap="It")
    elif kind == "item":
        lm = _landmark(g, home, 2, 6, used_lm)
        if not lm:
            return None
        used_lm.add((lm[0], lm[1].noun))
        nm = g.rng.choice(ITEM_NAMES[okey])
        plot["target"], plot["hide_noun"] = lm[0], lm[1].noun
        F.update(oname=nm, obj=f"the {nm}", ohe="it", ohim="it", ohis="its", ohe_cap="It", place=lm[1].noun)
    elif kind == "place":
        if okey == "shrine":
            shrines = sorted((p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "shrine"),
                             key=lambda p: abs(p[0] - home[0]) + abs(p[1] - home[1]))
            plot["target"] = shrines[0]
            F.update(spirit=w.tiles[shrines[0]].site.get("spirit", "the old spirit"), obj="the shrine", place="shrine")
        else:
            lm = _landmark(g, home, 2, 6, used_lm)
            if not lm:
                return None
            used_lm.add((lm[0], lm[1].noun))
            plot["target"] = lm[0]
            F.update(place=lm[1].noun, obj=f"the grave by the {lm[1].noun}")
        F.update(ohe="it", ohim="it", ohis="its", ohe_cap="It", oname=F.get("obj", "the place"))
    else:  # word
        fn = _far_npc(g, home, used_npc)
        if not fn:
            return None
        fv, far = fn
        used_npc.add(far.name)
        plot["word_npc"], plot["word_home"] = far.name, fv
        F.update(obj=f"word from {far.name}", oname="news", ohe="it", ohim="it", ohis="its", ohe_cap="It")
        F.update(far=far.name, fvillage=w.tiles[fv].site["name"])
    tgt = plot["target"] if "target" in plot else plot["word_home"]
    F.update(dir=g.narr.dir_phrase(home, tgt), dir_cap=cap(g.narr.dir_phrase(home, tgt)), dir_short=_dir_word(home, tgt),
             toward=f"toward the {_dir_word(home, tgt)}" if _dir_word(home, tgt) != "nearby" else "not far off",
             obj_cap=cap(F["obj"]), region=w.region_of(tgt)["name"])
    if "far" not in F:          # someone elsewhere, for obstacles and twists
        fn = _far_npc(g, home, used_npc)
        if fn:
            fv, far = fn
            F.update(far=far.name, fvillage=w.tiles[fv].site["name"])
            plot["far_npc"], plot["far_home"] = far.name, fv
        else:
            F.update(far=other, fvillage=vname)
            plot["far_npc"], plot["far_home"] = other, home
    else:
        plot["far_npc"], plot["far_home"] = plot.get("word_npc"), plot.get("word_home")
    farn = S.find_npc(w, plot["far_npc"]) if plot.get("far_npc") else None
    fp = farn.pronouns() if farn else _pron("female")
    F.update(fhe=fp["he"], fhim=fp["him"], fhis=fp["his"], fhe_cap=cap(fp["he"]))
    # motive
    mkey = _choose(g, "motive", motives_for(okey, npc) or ["duty"])
    plot["motive"] = mkey
    # obstacles: one to three, each fitting the object, none repeated
    n_obs = g.rng.choices([1, 2, 3], [4, 4, 2])[0]
    obs_keys = []
    for _ in range(n_obs):
        pool = [k for k, o in OBSTACLES.items() if (o[1] == "any" or kind in o[1].split()) and k not in obs_keys]
        k = _choose(g, "obstacle", pool)
        step = _obstacle_step(g, plot, k, F, used_lm, used_npc)
        if step:
            obs_keys.append(k)
            plot["steps"].append(step)
    plot["obstacles"] = obs_keys
    # twist (often, not always)
    plot["twist"] = None
    if g.rng.random() < 0.55:
        tw = [k for k, t in TWISTS.items() if t[0] == "any" or kind in t[0].split()]
        plot["twist"] = _choose(g, "twist", tw)
        if plot["twist"] == "followed":
            _setup_followed(g, plot, F, home)
    # the climax step
    plot["steps"].append(_climax_step(g, plot, F))
    plot["F"] = F
    plot["title"] = fill(g.rng.choice(obj["title"]), F)
    for kk, vv in (("object", okey), ("motive", mkey), ("twist", plot["twist"])):
        if vv:
            _remember(g, kk, vv)
    for k in obs_keys:
        _remember(g, "obstacle", k)
    return plot


def _dir_word(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    ns = "north" if dy < 0 else "south" if dy > 0 else ""
    ew = "east" if dx > 0 else "west" if dx < 0 else ""
    return (ns + ("-" if ns and ew else "") + ew) or "nearby"


def _obstacle_step(g, plot, k, F, used_lm, used_npc):
    w = g.world
    mech, _kinds, intro, title, par = OBSTACLES[k]
    home = plot["home"]
    tgt = plot.get("target") or plot.get("word_home")
    step = dict(mech=mech, key=k, intro=intro, title=title, **par)
    if mech == "search":
        lm = _landmark(g, home, 1, 5, used_lm)
        if not lm:
            return None
        used_lm.add((lm[0], lm[1].noun))
        step.update(pos=lm[0], noun=lm[1].noun, lm=lm[1].noun, lmdir=g.narr.dir_phrase(home, lm[0]))
    elif mech == "slay":
        spot = _wild(g, home, 1, 4)
        if not spot:
            return None
        sp = _species(g, spot, undead=False)
        step.update(pos=spot, species=sp["name"], guard=sp["name"], gdir=g.narr.dir_phrase(home, spot))
        step["_sp"] = sp
    elif mech in ("ask", "deal", "bring"):
        fn = _far_npc(g, home, used_npc)          # someone in another village, not already in this story
        if not fn:
            return None
        v, n = fn
        used_npc.add(n.name)
        p_ = n.pronouns()
        step.update(npc=n.name, npc_home=v, far=n.name, fvillage=w.tiles[v].site["name"], fhe=p_["he"], fhim=p_["him"], fhis=p_["his"], fhe_cap=cap(p_["he"]))
    elif mech == "deliver":
        if k == "offering":
            shrines = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "shrine"]
            if not shrines:
                return None
            sp = min(shrines, key=lambda p: abs(p[0] - home[0]) + abs(p[1] - home[1]))
            step.update(pos=sp, spirit=w.tiles[sp].site.get("spirit", "the old spirit"), sdir=g.narr.dir_phrase(home, sp))
        else:
            others = [v for v in w.villages if v != home]
            if not others:
                return None
            v = g.rng.choice(others)
            step.update(pos=v, fvillage=w.tiles[v].site["name"])
    elif mech == "go":
        if k == "ruinroad":
            ruins = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "ruin" and not w.tiles[p].site.get("quest")]
            if not ruins:
                return None
            rp = min(ruins, key=lambda p: abs(p[0] - home[0]) + abs(p[1] - home[1]))
            step.update(pos=rp, ruin=w.tiles[rp].site.get("purpose", "ruin"))
        else:
            spot = _wild(g, home, 2, 5)
            if not spot:
                return None
            step.update(pos=spot, region=w.region_of(spot)["name"])
    return step


def _climax_step(g, plot, F):
    kind, home = plot["kind"], plot["home"]
    if kind in ("person", "animal"):
        return dict(mech="go", key="climax", climax=True, pos=plot["target"], title=f"Find {F['obj']}", intro="")
    if kind == "creature":       # you find it first; whether it dies is one of the endings
        return dict(mech="go", key="climax", climax=True, pos=plot["target"], title=f"Track down {F['obj']}", intro="")
    if kind == "item":
        return dict(mech="search", key="climax", climax=True, pos=plot["target"], noun=plot["hide_noun"], cond=None,
                    title=f"Find {F['obj']} at the {plot['hide_noun']}", intro="")
    if kind == "place":
        return dict(mech="go", key="climax", climax=True, pos=plot["target"], title=f"Go to {F['obj']}", intro="")
    return dict(mech="ask", key="climax", climax=True, npc=plot["word_npc"], npc_home=plot["word_home"], title=f"Ask {F['far']} for news", intro="")


# ----------------------------------------------------------------------- offering and running a story
def offer(g, npc):
    """A villager with a need may ask for help (at most a few stories at once, not too often)."""
    w = g.world
    if npc.role == "merchant" and g.rng.random() < 0.7:
        return False
    plots = getattr(g, "plots", [])
    if sum(1 for p in plots if p["status"] == "active") >= 3:
        return False
    if any(p["giver"] == npc.name and p["status"] == "active" for p in plots):
        return False
    if npc.mem.get("plot_day", -9) > w.day - 3:
        return False
    npc.mem["plot_day"] = w.day
    if g.rng.random() > 0.55:
        return False
    plot = make(g, npc)
    if not plot:
        return False
    g._plot_offer = plot
    S.ask(g, offer_text(g, plot, npc),
          [("Say you'll help", "plot_yes", dict(id=plot["id"])), ("Not now", "plot_no", dict(id=plot["id"]))], leave=1)
    return True


# how each temperament leads into asking, and how it closes the asking
ASK_LEAD = {
    "nervous": ["{name} wrings {his} hands.", "{name} glances round, then speaks low and fast.", "{name} hesitates, then blurts it out.",
                "{name} [twists|fidgets with] {his} [sleeve|apron|cap].", "{name} opens {his} mouth, shuts it, and tries again."],
    "suspicious": ["{name} looks you over once more before deciding.", "{name} lowers {his} voice, though there's no one near.",
                   "{name} [glances|looks] [up and down the lane|over {his} shoulder] first.", "{name} [seems to make up {his} mind|comes to a decision]."],
    "gruff": ["{name} sets down {tool} with a thump.", "{name} doesn't waste words.", "{name} [jerks {his} head|nods] toward [the lane|the hills|you]."],
    "warm": ["{name} touches your arm.", "{name}'s smile fades.", "{name} [takes your hand|pats your arm] [for a moment|gently]."],
    "cheerful": ["The grin slips from {name}'s face for a moment.", "{name} tries to make light of it, and can't quite.",
                 "{name} [laughs, but it comes out wrong|stops smiling]."],
    "melancholy": ["{name} sighs.", "{name} looks away down the lane.", "{name} [rubs {his} eyes|stares at the ground] [a while|before speaking]."],
    "shrewd": ["{name} leans closer.", "{name} weighs you up, then seems to decide.", "{name} [taps {his} nose|lowers {his} voice] [as if striking a bargain|and leans in]."],
    "dreamy": ["{name}'s gaze drifts, then comes back to you.", "{name} speaks as if half to someone else.", "{name} [looks at the sky|watches a bird] [a moment|a while] first."],
}
ASK_CLOSE = {
    "nervous": ["Please.", "I wouldn't ask if there were anyone else.", "Will you? Please?", "[I'm sorry to ask.|I hate to ask.] [Will you?|Could you?]"],
    "suspicious": ["I can't pay much. But I'd owe you.", "I don't ask for help often.", "[I'll make it worth your while.|There'll be something for you.] If you're straight with me."],
    "gruff": ["Well? Will you or won't you?", "That's all. Will you go?", "[Yes or no?|Well?] [I've work to do.|I'll not ask twice.]"],
    "warm": ["Will you help?", "I'd be grateful past saying.", "[Would you?|Could you, do you think?] [I'd not forget it.|I'd bless you for it.]"],
    "cheerful": ["What do you say?", "Go on - you look like you could use an adventure.", "[Fancy it?|How about it?] [It'll be a story to tell!|You'd be a hero.]"],
    "melancholy": ["I don't suppose you would...", "But why would you?", "[It's too much to ask, I know.|I know it's a lot.] [Still.|But.]"],
    "shrewd": ["There'd be something in it for you.", "Well? Interested?", "[Name your price.|We can talk terms.] [Within reason.|I'm not made of coin.]"],
    "dreamy": ["I think you were meant to come.", "The wind said someone would help.", "[I dreamed of someone like you.|The crows said you'd come.] [Was I right?|Will you?]"],
}


def _unquote(line):
    line = line.strip()
    return line[1:-1] if len(line) > 1 and line[0] == line[-1] == '"' else line


def offer_text(g, plot, npc):
    """The asking, as one speech in one voice: what's wrong, why it matters to them, where to start, and a
    closing in their own temperament."""
    from . import lex_talk as TALK
    F, n = plot["F"], g.narr
    what = fill(n.pick(OBJECTS[plot["okey"]]["lines"], f"plotobj-{plot['okey']}"), F)
    why = fill(n.pick(motive_lines(plot["motive"], plot["okey"]), f"plotwhy-{plot['motive']}"), F)
    first = plot["steps"][0]
    hint = fill(fill(first["intro"], first), F) if not first.get("climax") and first.get("intro") else ""
    temper = npc.demeanour if npc.demeanour in ASK_CLOSE else "warm"
    close = n.pick(ASK_CLOSE[temper], f"askclose-{temper}")
    from . import sentences as SN, lex_dialogue as DL
    what, why, close = (SN.expand(n, x, DL.LEX, key="offer") for x in (what, why, close))
    plot["pitch"] = f"\"{_unquote(what)} {_unquote(why)}\""            # for the journal, in their own words
    speech = " ".join(x for x in (_unquote(what), _unquote(why), _unquote(hint), close) if x)
    pr = npc.pronouns()
    lead = SN.expand(n, n.pick(ASK_LEAD[temper], f"asklead-{temper}").format(name=npc.name, his=pr["his"], tool=TALK.tool_for(npc)), DL.LEX, key="lead")
    return f"{lead} \"{speech}\""


@S.choice_handler("plot_yes")
def _plot_yes(g, d):
    plot = getattr(g, "_plot_offer", None)
    if not plot or plot["id"] != d["id"]:
        return
    g._plot_offer = None
    if not hasattr(g, "plots"):
        g.plots = []
    plot["status"] = "active"
    g.plots.append(plot)
    giver = S.find_npc(g.world, plot["giver"])
    c = plot.pop("_creature", None)
    if c is not None:
        g.world.tiles[plot["target"]].creatures.append(c)
        plot["creature"] = c
    from . import lex_talk as TALK
    temper = giver.demeanour if giver else "warm"
    he = giver.pronouns()["he"] if giver else "they"
    g.emit(g.narr.pick(TALK.toned(TALK.THANKS, temper), f"plotthanks-{temper}").format(giver=plot["giver"], he=he) + f" (Journal: {plot['title']}" + ("" if plot["title"].endswith(("?", "!")) else ".") + ")")
    S.record(g, f"{plot['giver']} of {plot['village']} asked for your help: {plot['title'].lower()}.", "quest", pos=plot["home"])
    _start_step(g, plot, 0)


@S.choice_handler("plot_no")
def _plot_no(g, d):
    g._plot_offer = None
    g.emit("You shake your head. Perhaps another time.")


def _plot(g, pid):
    return next((p for p in getattr(g, "plots", []) if p["id"] == pid), None)


def _start_step(g, plot, i):
    """Turn a story step into an ordinary journal errand."""
    w = g.world
    plot["i"] = i
    st = plot["steps"][i]
    F = dict(plot["F"])
    F.update({k: v for k, v in st.items() if isinstance(v, str)})
    title = cap(fill(st["title"], F))
    data = dict(plot=plot["id"], step=i)
    reward = dict(xp=8)
    mech = st["mech"]
    if i > 0 and st.get("intro"):        # the asker told you more before you set out
        g.emit(g.narr.pick([f"You remember {plot['giver']}'s words: ", f"{plot['giver']} had said more: ", f"Next, as {plot['giver']} told you: "]) + fill(fill(st["intro"], st), F))
    if mech == "search":
        f = next((f for f in w.tiles[st["pos"]].features if f.noun == st["noun"]), None)
        if f is None:
            return _advance(g, plot)
        f.state = f.state or {}
        f.state["secret"] = dict(key="plot", verbs=["search"], cond=st.get("cond"), found=False, planted=True, plot=plot["id"], step=i)
        data.update(search=True, noun=st["noun"])
        S.new_quest(g, "find", title, f"{title} ({plot['title']})", reward, target=st["pos"], source="plot", on_done="plot", data=data)
    elif mech == "slay":
        if st.get("climax"):
            c = plot.get("creature")
            if c is None or not any(c in t.creatures for t in w.tiles.values()):
                c = w.make_creature(_species(g, st["pos"], undead=plot["okey"] == "dead"), w.tiles[st["pos"]].danger or 2)
                w.tiles[st["pos"]].creatures.append(c)
                plot["creature"] = c
        else:
            sp = st.pop("_sp", None) or _species(g, st["pos"], undead=False)
            c = w.make_creature(sp, max(1, w.tiles[st["pos"]].danger or 1))
            w.tiles[st["pos"]].creatures.append(c)
        S.new_quest(g, "slay", title, f"{title} ({plot['title']})", reward, target=st["pos"], creature=c, source="plot", on_done="plot", data=data)
    elif mech in ("ask", "deal"):
        n = S.find_npc(w, st["npc"])
        if n is None:
            return _advance(g, plot)
        data["message"] = True
        S.new_quest(g, "bring", title, f"{title} ({plot['title']})", reward, giver=n, source="plot", on_done="plot", data=data)
    elif mech == "bring":
        n = S.find_npc(w, st["npc"])
        if n is None:
            return _advance(g, plot)
        if st.get("any_kind"):
            data["any_kind"] = st["any_kind"]
        q = S.new_quest(g, "bring", title, f"{title} ({plot['title']})", reward, giver=n, item=st.get("item"), source="plot", on_done="plot", data=data)
        q["data"]["done_text"] = f"{n.name} takes the {{thing}} and nods. \"Right. Now, what you wanted to know...\""
    elif mech == "deliver":
        from .world import Item
        token = f"{plot['giver']}'s token" if st["key"] != "offering" else "small offering"
        g.player.inv.append(Item("token", token, value=0, facts=dict(material="a twist of cloth", glow="a promise")))
        S.new_quest(g, "deliver", title, f"{title} ({plot['title']})", reward, target=st["pos"], item=token, source="plot", on_done="plot", data=data)
    else:  # go
        S.new_quest(g, "find", title, f"{title} ({plot['title']})", reward, target=st["pos"], source="plot", on_done="plot", data=data)


def step_done(g, q):
    """A story errand was finished: the next step, a deal to strike, or the climax."""
    plot = _plot(g, q["data"].get("plot"))
    if not plot or plot["status"] != "active":
        return
    st = plot["steps"][q["data"]["step"]] if q["data"].get("step") is not None and q["data"]["step"] < len(plot["steps"]) else None
    if q["data"].get("final"):
        return _complete(g, plot)
    if q["data"].get("final_kill"):
        return _final_return(g, plot)
    if st is None:
        return
    if st.get("climax"):
        return _climax(g, plot)
    if st["mech"] == "deal":
        return _deal(g, plot, st)
    _advance(g, plot)


def _advance(g, plot):
    if plot["i"] + 1 < len(plot["steps"]):
        _start_step(g, plot, plot["i"] + 1)


def arrived(g, q):
    """Reaching a 'go' step's place."""
    plot = _plot(g, q["data"].get("plot"))
    if not plot:
        return S.finish(g, q)
    st = plot["steps"][q["data"]["step"]]
    if st.get("climax"):
        return S.finish(g, q, None)
    S.finish(g, q, g.narr.pick(["You've come far enough. You can see where to go next.", "From here the way is clearer.",
                                 "You stop to get your bearings. Yes - onward."]))


def searched(g, f, sec):
    """Searching a landmark that holds the next clue (or the thing itself)."""
    sec["found"] = True
    plot = _plot(g, sec.get("plot"))
    q = next((q for q in S.active(g) if q["data"].get("plot") == sec.get("plot") and q["data"].get("step") == sec.get("step")), None)
    if not plot or not q:
        return g.emit(f"You search the {f.noun}, but whatever was here is gone.")
    st = plot["steps"][sec["step"]]
    if st.get("climax"):
        g.emit(fill(g.narr.pick([f"There, tucked out of sight at the {f.noun}: {{obj}}.", f"You find {{obj}} at last, wedged under the {f.noun}."]), plot["F"]))
        return S.finish(g, q)
    clues = {"tracks": "The tracks are plain once you look: they lead on.", "dropped": "You find what was dropped - and it tells you where to go next.",
             "moonlit": "By moonlight, a mark you'd never have seen by day: an arrow, scratched deep.",
             "fogbound": "In the fog, the path shows - a line of stones you'd never see in clear weather.",
             "dawnsign": "The first light falls just so, and picks out a sign carved into the stone.",
             "duskcall": "At dusk, you hear it - a call, faint, from further on.", "cache": "The stash is here, half-emptied. A scrap of cloth tells you where the rest went.",
             "scrawl": "The sign is old, but you make it out: a direction, and a warning."}
    S.finish(g, q, clues.get(st["key"], "You find a sign, and it points onward."))


def _deal(g, plot, st):
    from . import arts as ARTS
    F = dict(plot["F"], **{k: v for k, v in st.items() if isinstance(v, str)})
    price = st.get("price", 10) + 2 * len(plot["steps"])
    p = g.player
    opts = []
    if p.gold >= price:
        opts.append((f"Pay {price} coins", "plot_deal", dict(id=plot["id"], how="pay", price=price)))
    opts.append((f"Talk {F['fhim']} round ({'you have a way with words' if ARTS.stat(p, 'wits') >= 6 or ARTS.stat(p, 'spirit') >= 6 else 'it may not work'})",
                 "plot_deal", dict(id=plot["id"], how="talk", price=price)))
    opts.append((f"Lean on {F['fhim']} ({'you look like you mean it' if ARTS.stat(p, 'might') >= 6 else 'you may not convince'})",
                 "plot_deal", dict(id=plot["id"], how="lean", price=price)))
    opts.append(("Come back later", "plot_deal", dict(id=plot["id"], how="later", price=price)))
    S.ask(g, fill(g.narr.pick([f"{{far}} folds {{fhis}} arms. \"It'll cost you. {price} coins.\"", f"{{far}} looks you up and down. \"Nothing's free, friend. {price} coins, or nothing.\""]), F),
          opts, leave=len(opts) - 1)


@S.choice_handler("plot_deal")
def _plot_deal(g, d):
    from . import arts as ARTS
    plot = _plot(g, d["id"])
    if not plot:
        return
    st = plot["steps"][plot["i"]]
    F = dict(plot["F"], **{k: v for k, v in st.items() if isinstance(v, str)})
    p, how = g.player, d["how"]
    n = S.find_npc(g.world, st.get("npc"))
    ok = False
    if how == "pay" and p.gold >= d["price"]:
        p.gold -= d["price"]
        ok = True
        g.emit(fill("You count the coins into {far}'s hand. \"Pleasure,\" {fhe} says.", F))
    elif how == "talk":
        ok = g.rng.random() < 0.25 + 0.1 * (max(ARTS.stat(p, "wits"), ARTS.stat(p, "spirit")) - 4)
        g.emit(fill("You talk, and {far} listens, and in the end {fhe} shrugs and gives way." if ok else
                    "You talk. {far} hears you out, then shakes {fhis} head. \"Coin, or nothing.\"", F))
        if n and ok:
            n.like(1)
    elif how == "lean":
        ok = g.rng.random() < 0.2 + 0.12 * (ARTS.stat(p, "might") - 4)
        g.emit(fill("You step close and say it quietly. {far} goes pale and gives way." if ok else
                    "You lean on {far}. {fhe_cap} leans back. \"Get out,\" {fhe} says. It'll have to be coin, or charm, another time.", F))
        if n:
            n.like(-2 if ok else -1)
    if ok:
        return _advance(g, plot)
    # not yet: the same person waits for you to come back
    _start_step(g, plot, plot["i"])
    if how == "later":
        g.emit(fill("\"You know where I am,\" says {far}.", F))


def _climax(g, plot):
    F = plot["F"]
    tw = plot.get("twist")
    endings = list(KIND_DEFAULT_ENDINGS[plot["kind"]])
    if tw == "followed" and plot.get("follow"):
        fo = FOLLOWED[plot["follow"]]
        g.emit(fill(TWISTS[tw][1], F) + " " + fill(g.narr.pick(fo["reveal"]), F))
        opts = [(fill(o[0], F), "plot_end", dict(id=plot["id"], ending=k)) for k, o in fo["options"].items()]
        return S.ask(g, "What about " + F["shadow"] + "?", opts, leave=0)
    if tw:
        g.emit(fill(TWISTS[tw][1], F))
        for e in TWISTS[tw][2]:
            if e not in endings:
                endings.append(e)
        if plot["kind"] == "creature" and "kill" in endings and "spare" in endings and plot.get("creature") is not None:
            pass
    else:
        g.emit(fill(g.narr.pick({"person": ["There's {obj} at last, cold and tired and very glad to see you.", "You find {obj}, footsore and frightened, but alive."],
                                 "animal": ["There's {obj}, not far off, looking as if nothing happened.", "You find {obj}, muddy but unhurt."],
                                 "creature": ["It's done. {obj_cap} lies still.", "{obj_cap} is dead."],
                                 "item": ["It's {obj}, sure enough.", "There it is: {obj}."],
                                 "place": ["You reach {obj}. It's quiet here.", "{obj_cap}, at last."],
                                 "word": ["{far} tells you everything.", "{far} gives you the news, slowly."]}[plot["kind"]]), F))
    ok = KIND_ENDINGS_OK.get(plot["kind"])
    endings = [e for e in endings if ok is None or e in ok][:4]
    if len(endings) == 1:          # nothing to decide
        return _plot_end(g, dict(id=plot["id"], ending=endings[0]))
    label = lambda e: ENDINGS[e][plot["kind"]] if isinstance(ENDINGS[e], dict) else ENDINGS[e]
    opts = [(fill(label(e), F), "plot_end", dict(id=plot["id"], ending=e)) for e in endings]
    S.ask(g, "What now?", opts, leave=0)


def _like(g, name, n):
    npc = S.find_npc(g.world, name)
    if npc:
        npc.like(n)


@S.choice_handler("plot_end")
def _plot_end(g, d):
    from . import arts as ARTS
    from .world import Item
    plot = _plot(g, d["id"])
    if not plot or plot["status"] != "active":
        return
    e, F, w, p = d["ending"], plot["F"], g.world, g.player
    kind = plot["kind"]
    if e.startswith("f_") and plot.get("follow"):
        if _settle_follower(g, plot, e):
            return
        e = KIND_DEFAULT_ENDINGS[kind][0]           # then the errand ends the ordinary way
    if e not in KIND_ENDINGS_OK.get(kind, (e,)):      # a choice saved before beasts lost the endings that skipped the fight
        e = "kill"
    plot["ending"] = e
    if e == "persuade":
        if g.rng.random() < 0.3 + 0.1 * (max(ARTS.stat(p, "spirit"), ARTS.stat(p, "wits")) - 4):
            g.emit(fill("You sit with {obj} a long time, and talk, and at last {ohe} sighs and gets up. \"All right. Home.\"", F))
            return _final_return(g, plot)
        g.emit(fill("{obj_cap} won't be moved. You'll have to take word back instead.", F))
        e = plot["ending"] = "let_go"
    if e == "bargain":
        if g.rng.random() < 0.35 + 0.1 * (ARTS.stat(p, "wits") - 4):
            plot["bonus"] = 1.6
            g.emit("You make it clear the job was harder than anyone said. It'll be worth more.")
        else:
            plot["bonus"] = 0.8
            g.emit("You try to drive the price up. It doesn't make you any friends.")
        return _final_return(g, plot)
    if kind == "creature" and e in ("bury", "expose"):     # these come before the beast is dealt with, not instead of it
        if e == "bury":
            from . import story as ST
            ST.add_buff(g, "blessed", 24)
            g.emit("You do what's right by the dead first: a few stones, a few words. It feels like enough. (You feel blessed.) "
                   "The beast is still out there.")
        else:
            g.emit("The village will want to hear what you found - but the beast comes first.")
    if kind == "creature" and e in ("kill", "bury", "expose"):
        c = plot.get("creature")
        if c is None or not any(c in t.creatures for t in w.tiles.values()):
            c = w.make_creature(_species(g, plot["target"], undead=plot["okey"] == "dead"), w.tiles[plot["target"]].danger or 2)
            w.tiles[plot["target"]].creatures.append(c)
            plot["creature"] = c
        c.aggressive = True
        S.new_quest(g, "slay", f"Kill {F['obj']}", f"Kill {F['obj']} ({plot['title']})", dict(xp=5), target=plot["target"], creature=c,
                    source="plot", on_done="plot", data=dict(plot=plot["id"], final_kill=True))
        return
    if e in ("return", "kill", "report", "tell_truth", "comfort_lie", "keep_secret", "expose"):
        return _final_return(g, plot)
    if e == "spare":
        c = plot.get("creature")
        for t in w.tiles.values():
            if c in t.creatures:
                t.creatures.remove(c)
        g.combat = None
        g.emit("You lower your weapon and step back. After a long moment it slips away, and doesn't look back.")
        return _final_return(g, plot)
    if e == "free":
        g.emit("You cut it loose. It bolts for the trees and is gone.")
        _like(g, plot["giver"], -1)
        return _close(g, plot, f"You set {F['obj']} free instead of bringing it home to {plot['giver']}.", xp=15)
    if e == "let_go":
        return _final_return(g, plot)
    if e == "true_owner":
        n = S.find_npc(w, F["other"])
        if n:
            g.player.inv.append(Item("token", F.get("oname", "it"), value=0, facts=dict(material="old", glow="someone's rightful property")))
            q = S.new_quest(g, "bring", f"Give it to {F['other']}", f"Take {F['obj']} to {F['other']}, its true owner", dict(xp=20, gold=g.rng.randint(5, 15), like=4),
                            giver=n, item=F.get("oname", "it"), source="plot", on_done="plot", data=dict(plot=plot["id"], final=True))
            q["data"]["done_text"] = f"{F['other']} stares at it, then at you. \"I thought I'd never see it again.\""
            _like(g, plot["giver"], -2)
            return
        return _final_return(g, plot)
    if e in ("destroy", "shrine", "bury"):
        from . import story as ST
        ST.add_buff(g, "blessed", 24)
        txt = {"destroy": "You smash it on a stone. Something cold goes out of the air.", "shrine": "You leave it on holy ground, and feel a weight lift from you.",
               "bury": "You do what's right by the dead: a few stones, a few words. It feels like enough."}[e]
        g.emit(txt + " (You feel blessed.)")
        if kind in ("item",) and e != "bury":
            _like(g, plot["giver"], -1)
            return _close(g, plot, f"You {e == 'destroy' and 'destroyed' or 'gave to holy ground'} {F['obj']} rather than return it.", xp=20)
        return _final_return(g, plot)
    if e == "keep":
        p.inv.append(Item("trinket", F.get("oname", "keepsake"), value=g.rng.randint(25, 60), facts=dict(detail="the thing someone sent you to find")))
        _like(g, plot["giver"], -4)
        g.emit(fill("You keep {obj}. Nobody need know. Probably.", F))
        return _close(g, plot, f"You kept {F['obj']} for yourself.", xp=10, story=f"you kept what {plot['giver']} sent you for", like=-2)
    if e == "forgive":
        food = next((i for i in p.inv if i.kind == "food"), None)
        if food:
            p.inv.remove(food)
        g.emit("You leave " + (f"your {food.name}" if food else "a few coins") + " on the child's blanket, and take only what you came for.")
        if not food:
            p.gold = max(0, p.gold - 3)
        return _final_return(g, plot)
    if e == "sell_rival":
        gold = g.rng.randint(30, 60)
        p.gold += gold
        _like(g, plot["giver"], -5)
        _like(g, F.get("far", ""), 3)
        g.emit(f"{F.get('far', 'The rival')} pays well. ({gold} coins.) {plot['giver']} will hear of it.")
        return _close(g, plot, f"You sold {F['obj']} to {F.get('far', 'a rival')} instead.", xp=15, story=f"you sold what {plot['giver']} sent you for", like=-3)
    if e == "share":
        gold = g.rng.randint(8, 20)
        p.gold += gold
        g.emit(f"You split it fairly. ({gold} coins your share.)")
        return _final_return(g, plot)
    return _final_return(g, plot)


def _final_return(g, plot):
    """The last errand: back to whoever asked."""
    w = g.world
    F, e, kind = plot["F"], plot.get("ending", "return"), plot["kind"]
    giver = S.find_npc(w, plot["giver"])
    if giver is None:
        return _complete(g, plot)
    data = dict(plot=plot["id"], final=True)
    if kind in ("person", "animal") and e not in ("let_go",):
        comp = dict(name=F["obj"])
        g.companions.append(comp)
        q = S.new_quest(g, "escort", f"Bring {F['obj']} home", f"Lead {F['obj']} back to {plot['village']}", dict(xp=5), target=plot["home"],
                        companion=comp, source="plot", on_done="plot", data=data)
        g.emit(fill("(Journal: {obj_cap} will follow you home.)", F))
        return
    if kind == "item":
        from .world import Item
        if not any(i.name == F["oname"] for i in g.player.inv):
            g.player.inv.append(Item("token", F["oname"], value=0, facts=dict(material="old", glow="someone else's"), ))
        q = S.new_quest(g, "bring", f"Return {F['obj']}", f"Take {F['obj']} back to {plot['giver']} in {plot['village']}", dict(xp=5), giver=giver,
                        item=F["oname"], source="plot", on_done="plot", data=data)
        return
    S.new_quest(g, "bring", f"Back to {plot['giver']}", f"Tell {plot['giver']} in {plot['village']} how it went", dict(xp=5), giver=giver,
                source="plot", on_done="plot", data=dict(data, message=True))


ENDING_TEXT = {
    "return": ["{giver} takes it all in, and has to sit down. \"Thank you. I mean it.\"", "{giver}'s face does something complicated, and settles on relief."],
    "kill": ["{giver} listens to the tale of the fight, and grips your arm. \"Then it's over.\""],
    "spare": ["\"It fled?\" {giver} looks at you a long moment. \"Well. So long as it's gone.\""],
    "let_go": ["You tell {giver} that {obj} is safe, and won't be coming back. {he_cap} is quiet for a long time. \"Safe. That's something.\""],
    "report": ["You tell {giver} who took it. {he_cap} goes very still, then nods. \"I'll deal with it.\""],
    "tell_truth": ["You tell {giver} the truth, all of it. {he_cap} doesn't thank you, not yet. But {he} will."],
    "comfort_lie": ["You tell {giver} a kinder story than the true one. {he_cap} believes it, and smiles. You hope you were right."],
    "keep_secret": ["You hand it over and say nothing of what else you found. Some things are better left."],
    "expose": ["You tell the village what you found. There's an uproar, and {giver} won't meet anyone's eye - but folk thank you for it."],
    "persuade": ["{obj_cap} comes home, and the village comes out to see."],
    "share": ["{giver} takes the rest gladly. \"Fair's fair.\""],
    "forgive": ["{giver} gets it back and asks no questions. You don't offer any answers."],
    "bury": ["You tell {giver} what you did for the dead out there. {he_cap} nods slowly. \"That was well done.\""],
    "bargain": ["{giver} pays what you asked. {he_cap} doesn't look happy about it, but {he} pays."],
}


# what you did, for the chronicle, the journal and gossip (said of you: "You brought ... home")
OUTCOME = {
    "return": {"person": "You brought {obj} home to {giver}.", "animal": "You brought {obj} back to {giver}.",
               "creature": "You dealt with {obj} for {giver}.", "item": "You found {obj} and gave it back to {giver}.",
               "place": "You set {obj} right, for {giver}.", "word": "You brought {giver} word from {far}."},
    "kill": "You killed {obj}, as {giver} asked.", "persuade": "You talked {obj} into coming home.",
    "tell_truth": "You told {giver} the truth, hard as it was.", "comfort_lie": "You told {giver} a kind lie, and let it stand.",
    "expose": "You told {village} what really happened.", "bargain": "You drove a hard bargain with {giver} over {obj}.",
    "spare": "You let {obj} live, and told {giver} it had fled.", "let_go": "You let {obj} go their own way, and took word back to {giver}.",
    "report": "You told {giver} who the thief was.", "keep_secret": "You brought {obj} back, and kept what else you found to yourself.",
    "share": "You shared what you found with {giver}.", "forgive": "You let the thief go, and brought {obj} back to {giver}.",
    "bury": "You buried the dead you found, and told {giver}.",
}


def outcome(plot):
    o = OUTCOME.get(plot.get("ending", "return"), OUTCOME["return"])
    if isinstance(o, dict):
        o = o.get(plot["kind"], o["item"])
    return fill(o, dict(plot["F"], village=plot["village"]))


def _complete(g, plot):
    """The story's end: rewards, liking, and what the village remembers."""
    F, e = plot["F"], plot.get("ending", "return")
    n_steps = len(plot["steps"])
    gold = int((10 + 8 * n_steps) * plot.get("bonus", 1.0))
    xp = 15 + 10 * n_steps
    like = {"return": 4, "kill": 4, "persuade": 5, "tell_truth": 3, "comfort_lie": 4, "expose": -2, "bargain": 1, "spare": 2, "let_go": 2,
            "report": 3, "keep_secret": 4, "share": 3, "forgive": 3, "bury": 4}.get(e, 3)
    g.emit(fill(g.narr.pick(ENDING_TEXT.get(e, ENDING_TEXT["return"])), F))
    if plot.get("follow_after"):
        g.emit(plot["follow_after"])
    if e == "expose":
        for n in g.world.tiles[plot["home"]].npcs:
            if n.name != plot["giver"]:
                n.like(2)
    done = outcome(plot)
    if plot.get("follow_note"):
        done = done.rstrip(".") + ", " + plot["follow_note"] + "."
    _close(g, plot, done, xp=xp, gold=gold, like=like, story="you" + done[3:].rstrip("."), item_chance=0.25)


def _close(g, plot, chronicle, xp=10, gold=0, like=0, story=None, item_chance=0.0):
    p = g.player
    plot["status"] = "done"
    plot["outcome"], plot["day_done"] = chronicle, g.world.day
    bits = []
    if gold:
        p.gold += gold
        bits.append(f"{gold} coins")
    if xp:
        for m in p.gain_xp(xp):
            g.emit(m)
        bits.append(f"{xp} experience")
    if item_chance and g.rng.random() < item_chance:
        it = g.world.make_item(3, g.rng.choice(["book", "scroll", "potion", "armour", "weapon", "trinket", "goods"]))
        p.inv.append(it)
        bits.append(article(it.name))
    if like:
        _like(g, plot["giver"], like)
    if bits:
        g.emit("(Reward: " + ", ".join(bits) + ".)")
    for c in list(g.companions):
        if c.get("name") == plot["F"].get("obj"):
            g.companions.remove(c)
    S.record(g, chronicle, "quest", pos=g.pos, story=story, like=1 if like >= 0 else -1)
    if getattr(g, "_last_journal", None) != plot["title"]:
        g.emit(f"(Journal: {plot['title']} - done.)")
