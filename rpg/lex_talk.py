"""Conversation: first meetings, introductions and speech beats.

A first meeting is told as a small scene: what the person is doing as you come
up (their temperament shows), what they say, the exchange of names, and how they
introduce themselves (their trade shows). Later lines carry a beat - a gesture
or a glance - so it's always clear who is speaking.

ctx: the_npc ("the smith" / a name), name, job, he/him/his/himself, player,
tool (what their hands are busy with), job_self (how they describe their work).
"""

# what someone's hands are busy with, by trade (falls back to their role)
TOOL = {
    "smith": "hammer", "trader": "coins", "pedlar": "pack-straps", "packman": "pack-straps", "huckster": "trinkets", "tinker": "a half-mended pot",
    "chandler": "a bundle of tapers", "cloth-seller": "a bolt of cloth", "spice-trader": "a twist of paper", "horse-coper": "a bridle",
    "fletcher": "an arrow shaft", "weaver": "a shuttle", "tanner": "a scraping knife", "miller": "a sack", "brewer": "a ladle",
    "beekeeper": "a smoking pot", "eel-catcher": "a wicker trap", "shepherd": "a crook", "swineherd": "a switch", "thatcher": "a bundle of reed",
    "midwife": "a basket of linen", "hedge-witch": "a bunch of drying herbs", "wise-woman": "a bunch of drying herbs", "wise-man": "a bunch of drying herbs",
    "potter": "a lump of clay", "cooper": "a stave", "tinsmith": "a pair of snips", "wheelwright": "a spoke", "carter": "the reins",
    "woodcutter": "an axe", "charcoal-burner": "a rake", "ferryman": "a pole", "net-mender": "a net", "drover": "a stick", "ploughman": "a harness strap",
    "gravedigger": "a spade", "rat-catcher": "a sack that moves", "hurdle-maker": "a hazel rod", "goose-girl": "a long switch", "goose-boy": "a long switch",
    "chandler's boy": "a tray of candles", "chandler's girl": "a tray of candles",
}
ROLE_TOOL = {"elder": "staff", "merchant": "wares", "folk": "a basket"}

# how people describe their work (the trade shows in how they introduce themselves)
JOB_SELF = {
    "smith": ["I keep the forge", "I'm the smith - you'll have heard the hammer", "I make the nails, the hinges and the blades round here"],
    "fletcher": ["I make arrows, and the odd bow", "I fletch - arrows, mostly"],
    "trader": ["I buy and sell, mostly sell", "I trade - a bit of this, a bit of that"],
    "pedlar": ["I carry what folk need from one village to the next", "I walk the roads with a pack"],
    "packman": ["I carry a pack between the villages", "I walk the roads with goods"],
    "huckster": ["I sell what I can, to whoever'll buy", "I've a stall, and a quick tongue"],
    "tinker": ["I mend pots and sell odds and ends", "I fix what's broken, mostly"],
    "chandler": ["I make the candles, and sell a few other things", "candles, wax, ink - that's me"],
    "spice-trader": ["I bring spices up from the south", "I sell things that smell better than this village"],
    "horse-coper": ["I deal in horses, when there are horses", "horses, harness, whatever moves"],
    "cloth-seller": ["I sell cloth, and the coats made from it", "I deal in wool and linen"],
    "hedge-witch": ["I know herbs, and a little more", "folk come to me when the herbs won't do"],
    "wise-woman": ["folk bring me their ailments", "I know which leaf does what"],
    "wise-man": ["folk bring me their ailments", "I know which leaf does what"],
    "midwife": ["I bring the babies in", "I see to births, and the sick"],
    "miller": ["I grind the corn", "I run the mill"], "brewer": ["I brew the ale", "I keep the brew-house"],
    "beekeeper": ["I keep the bees", "the hives are mine"], "eel-catcher": ["I trap eels", "I take eels from the water"],
    "shepherd": ["I keep sheep up on the tops", "the flock's mine"], "thatcher": ["I thatch roofs", "I keep the rain off folk"],
    "ferryman": ["I take folk across", "I keep the ferry"], "gravedigger": ["I dig the graves", "I see folk to the ground"],
    "rat-catcher": ["I catch rats", "rats - I'm the reason you don't see many"],
}
GENERIC_SELF = ["I'm the {job}", "I do the {job}'s work round here", "I'm what passes for a {job} in these parts"]

RULES = {
    # ---------------------------------------------------------------- first meeting: what they're doing as you come up
    "nervous:meet_beat": ["{the_npc.cap} starts as you come close, nearly dropping {tool}.", "{the_npc.cap} looks up too quickly, then away.",
                          "{the_npc.cap} goes still, like a hare in the grass, as you approach.", "{the_npc.cap} flinches, then tries to make it look like a stretch.",
                          "{the_npc.cap} clutches {tool} a little tighter as you come over."],
    "suspicious:meet_beat": ["{the_npc.cap} watches you come the whole way, eyes narrowed.", "{the_npc.cap} sets down {tool} and folds {his} arms.",
                             "{the_npc.cap} looks you up and down, lingering on your weapon.", "{the_npc.cap} doesn't stop what {he}'s doing, but {he} doesn't take {his} eyes off you either."],
    "gruff:meet_beat": ["{the_npc.cap} grunts without looking up.", "{the_npc.cap} spares you a glance and goes back to {tool}.",
                        "{the_npc.cap} straightens slowly, as if you've interrupted something important.", "{the_npc.cap} jerks {his} chin at you."],
    "warm:meet_beat": ["{the_npc.cap} breaks into a smile as you come over.", "{the_npc.cap} puts down {tool} and comes to meet you.",
                       "{the_npc.cap} waves you over before you've made up your mind.", "{the_npc.cap} looks up, and {his} face opens."],
    "cheerful:meet_beat": ["{the_npc.cap} is whistling, and doesn't stop until you're right there.", "{the_npc.cap} grins at you over {tool}.",
                           "{the_npc.cap} hails you from a dozen paces off.", "{the_npc.cap} laughs at something - perhaps you - and beckons."],
    "melancholy:meet_beat": ["{the_npc.cap} looks up slowly, as if from a long way off.", "{the_npc.cap} sighs and sets {tool} aside.",
                             "{the_npc.cap} gives you a tired, crooked smile.", "{the_npc.cap} is staring at nothing in particular, and takes a moment to notice you."],
    "shrewd:meet_beat": ["{the_npc.cap} takes your measure in one long look - boots, purse, blade.", "{the_npc.cap} smiles, but {his} eyes are doing sums.",
                         "{the_npc.cap} leans back and watches you approach with interest.", "{the_npc.cap} turns {tool} over in {his} fingers, considering you."],
    "dreamy:meet_beat": ["{the_npc.cap} is humming to {himself} and doesn't notice you at first.", "{the_npc.cap} is watching the sky, and only slowly looks down at you.",
                         "{the_npc.cap} blinks at you as if you'd appeared out of the air.", "{the_npc.cap} has stopped mid-task, {tool} forgotten, lost in thought."],

    # ---------------------------------------------------------------- what they say first
    "warm:greet": ["\"Well met, stranger! Sit, rest your feet.\"", "\"A new face! The road's been kind to bring you.\"", "\"Welcome, welcome. You look like you've walked a long way.\"",
                   "\"Come in out of the weather, if you like.\"", "\"Hello! You'll want something warm in you, I expect.\"", "\"There now. A traveller. Good.\""],
    "suspicious:greet": ["\"What do you want?\"", "\"I don't know you. Say your business.\"", "\"Strangers bring trouble, in my experience.\"",
                         "\"Who sent you?\"", "\"You're not from round here.\"", "\"Keep your hands where I can see them.\""],
    "nervous:greet": ["\"Oh! You gave me a fright.\"", "\"Is - is something wrong?\"", "\"Keep your voice down, if you would.\"",
                      "\"I didn't hear you coming.\"", "\"Sorry - sorry. I'm a bit on edge today.\"", "\"Oh. Hello. Yes?\""],
    "gruff:greet": ["\"Hm.\"", "\"If you're going to talk, talk.\"", "\"Busy. Make it quick.\"", "\"What.\"", "\"Well?\"", "\"Out with it.\""],
    "cheerful:greet": ["\"Hello there! Grand day for it, whatever it is.\"", "\"Ha! Another traveller. Come, have news for me?\"", "\"There's a smile I haven't seen before!\"",
                       "\"A visitor! Things are looking up.\"", "\"Well, hello! Where've you blown in from?\"", "\"Good to see a new face, it really is.\""],
    "melancholy:greet": ["\"Ah. Another day, another face.\"", "\"Welcome, I suppose. Not that there's much here.\"", "\"You should have come in better times.\"",
                         "\"Hello. Don't mind me.\"", "\"Oh. A traveller. We don't get many now.\"", "\"Mm. Good day, if it is one.\""],
    "shrewd:greet": ["\"A traveller. And what might you be worth to me, I wonder?\"", "\"Information has a price, friend. Usually.\"", "\"You've a look about you. Adventurer?\"",
                     "\"New in town, and in no hurry. Interesting.\"", "\"You'll be wanting something. Folk always are.\"", "\"Well now. What have we here?\""],
    "dreamy:greet": ["\"Did you see the clouds this morning? Like whales.\"", "\"Oh - hello. I was somewhere else.\"", "\"The wind told me someone would come.\"",
                     "\"Do you ever hear the stones hum? No? Just me, then.\"", "\"You've come from far off. I can see it on you.\"", "\"Hello. Were you in my dream? No, never mind.\""],

    # ---------------------------------------------------------------- beats before a line, later on, by how they feel about you
    "cold:talk_beat": ["{name} doesn't look up.", "{name} folds {his} arms.", "{name} gives you a flat look.", "{name} sniffs.",
                       "{name} keeps working.", "{name} answers without warmth."],
    "neutral:talk_beat": ["{name} nods.", "{name} glances up.", "{name} pauses in {his} work.", "{name} scratches {his} jaw.",
                          "{name} looks over.", "{name} shrugs a little.", "{name} sets down {tool}."],
    "friendly:talk_beat": ["{name} smiles at you.", "{name} looks up, pleased.", "{name} leans in.", "{name} gives you a nod and a half-smile.",
                           "{name} puts {tool} aside for you.", "{name} brightens."],
    "devoted:talk_beat": ["{name}'s face lights up.", "{name} grips your arm in greeting.", "{name} beams at you.", "{name} drops everything to talk."],
    # before a rumour or a piece of news
    "rumour_beat": ["{name} lowers {his} voice.", "{name} glances about, then leans closer.", "{name} points down the road.",
                    "{name} rubs {his} chin.", "{name} looks thoughtful.", "{name} taps the side of {his} nose.", "{name} frowns, remembering.",
                    "{name} goes back to {tool} as {he} talks.", "{name} gestures vaguely at the hills."],
    # before trade patter
    "trade_beat": ["{name} spreads {his} hands over the goods.", "{name} pats the nearest bundle.", "{name} straightens a row of wares.",
                   "{name} looks you over, then the goods, then you again.", "{name} lifts something up for you to see."],
}


# ---------------------------------------------------------------- the exchange of names, and how they introduce themselves
# Every line is tagged with the temperaments it suits ("*" for any), so a gruff man doesn't ask "not unkindly" and a
# nervous girl doesn't speak "as if that settles a great deal". See toned_rules().
TEMPERS = ["nervous", "suspicious", "gruff", "warm", "cheerful", "melancholy", "shrewd", "dreamy"]
# The name exchange. Each line ends on your turn (your words, or narration), never on theirs, and your reply is
# always tagged, so the introduction that follows reads as theirs. A line that opens with their question is
# folded into their greeting, one speech, by Narrator.greet.
ASK_NAME = [
    ("*", "\"And who might you be?\" You tell {him} your name."),
    ("*", "\"Haven't seen you before. Name?\" \"{player},\" you say. {he.cap} nods slowly."),
    ("*", "\"And you'd be?\" \"{player},\" you answer."),
    ("warm cheerful shrewd dreamy", "\"Got a name, traveller?\" You give it: {player}."),
    ("suspicious gruff shrewd", "{he.cap} squints at you. \"Who are you, then?\" \"{player},\" you tell {him}."),
    ("*", "\"And you are?\" You tell {him}: {player}."),
    ("nervous dreamy warm melancholy", "You give your name before {he} can ask: {player}. {he.cap} tries it out under {his} breath."),
    ("gruff shrewd suspicious", "\"You have a name, I suppose?\" \"{player},\" you say. {he.cap} grunts, as if it will do."),
    ("gruff suspicious shrewd", "{he.cap} waits, eyebrows raised, until you offer your name: {player}."),
    ("gruff suspicious melancholy dreamy nervous", "\"{player},\" you say, when the silence has gone on long enough."),
    ("suspicious nervous melancholy", "\"I'm {player},\" you say, and hold out a hand. After a moment {he} takes it."),
    ("warm cheerful dreamy", "\"I'm {player},\" you say, and hold out a hand. {he.cap} shakes it warmly."),
    ("warm cheerful shrewd dreamy", "\"And what do I call you?\" \"{player} will do,\" you say."),
    ("*", "\"Who's this, then?\" \"{player},\" you tell {him}."),
    ("suspicious shrewd gruff", "\"I don't know your face. What do they call you?\" \"{player},\" you say."),
    ("gruff shrewd cheerful", "\"You'll have a name.\" You admit that you do: {player}."),
    ("*", "\"And you are?\" \"{player},\" you say. {he.cap} turns it over, and nods."),
    ("warm melancholy dreamy shrewd", "\"Name?\" {he} asks, not unkindly. \"{player},\" you say."),
    ("warm cheerful melancholy", "\"Whose child are you, then?\" You settle for giving your own name: {player}."),
    ("shrewd gruff suspicious cheerful", "You tell {him} your name. {he.cap} weighs it like a coin."),
    ("cheerful gruff shrewd", "\"Go on, then - who are you?\" \"{player},\" you say."),
    ("*", "You give your name before {he} can ask: {player}."),
    ("suspicious shrewd gruff", "\"Should I know you?\" \"Not yet. {player},\" you say."),
    ("cheerful shrewd", "\"New face. Got a name to go with it?\" \"{player},\" you say."),
    ("nervous", "\"S-sorry, who -?\" \"{player},\" you say gently. {he.cap} manages a nod."),
    ("nervous", "{he.cap} doesn't ask, so you tell {him}: {player}. {he.cap} looks relieved to have it settled."),
    ("dreamy", "\"You'll have a name. Everyone does. Even the wind.\" \"{player},\" you say. {he.cap} smiles, as if you'd told {him} a secret."),
    ("warm", "\"Now, who do I have the pleasure of?\" \"{player},\" you say, and {he} beams."),
    ("melancholy", "\"I'd ask your name, but folk come and go.\" You give it anyway: {player}."),
]
# Their side of it. It follows your turn, so every one says plainly who's speaking.
NPC_INTRO = [
    ("*", "\"{name},\" {he} {itag}. \"{job_self.cap}.\""),
    ("gruff shrewd cheerful suspicious", "\"Name's {name},\" {he} {itag}. \"{job_self.cap}.\""),
    ("cheerful warm dreamy", "\"{name},\" {he} offers, tapping {his} chest. \"{job_self.cap}.\""),
    ("*", "\"Folk call me {name},\" {he} {itag}."),
    ("*", "{he.cap} wipes {his} hands. \"{name}. {job_self.cap}.\""),
    ("warm cheerful shrewd", "\"I'm {name},\" {he} {itag}. \"Pleased, I'm sure.\""),
    ("gruff suspicious melancholy nervous", "\"{name},\" {he} {itag}. A pause. \"{job_self.cap}, if you're wondering.\""),
    ("warm cheerful dreamy", "\"Well, I'm {name},\" {he} {itag}, \"and {job_self}.\""),
    ("gruff", "{he.cap} jerks a thumb at {his} own chest. \"{name}.\""),
    ("*", "\"They call me {name} round here,\" {he} {itag}. \"{job_self.cap}.\""),
    ("melancholy gruff cheerful", "\"{name},\" {he} {itag}. \"The {job} here, for my sins.\""),
    ("melancholy gruff cheerful", "\"{name},\" {he} {itag}. \"{job_self.cap}, for my sins and theirs.\""),
    ("*", "\"{name}'s my name,\" {he} {itag}, \"and I'm the {job}.\""),
    ("gruff", "{he.cap} jerks {his} chin at {his} work. \"{name}. {job_self.cap}.\""),
    ("shrewd cheerful dreamy", "\"You can call me {name},\" {he} {itag}. \"Most do.\""),
    ("shrewd dreamy", "\"{name},\" {he} says, as if that settles a great deal."),
    ("melancholy nervous", "{he.cap} gives a small shrug. \"I'm {name}, and that's about all there is to me. {job_self.cap}.\""),
    ("gruff shrewd suspicious", "\"{name},\" {he} {itag}. \"And before you ask - {job_self}.\""),
    ("nervous", "\"I'm - {name},\" {he} {itag}, as if confessing it. \"{job_self.cap}.\""),
    ("warm", "\"And I'm {name},\" {he} {itag}. \"{job_self.cap}. Anything you need, you ask.\""),
    ("suspicious", "\"{name},\" {he} {itag}, and gives nothing else away for a moment. \"{job_self.cap}.\""),
    ("dreamy", "\"{name},\" {he} {itag}. \"{job_self.cap}, when I remember to be.\""),
]
# how they take it when you say you'll help
THANKS = [
    ("warm melancholy nervous", "{giver} grips your hand. \"Thank you.\""),
    ("*", "{giver} lets out a breath. \"I'll not forget this.\""),
    ("warm melancholy dreamy nervous", "\"Bless you,\" says {giver}."),
    ("melancholy nervous warm", "{giver} nods, and nods again, as if not trusting words."),
    ("nervous melancholy", "\"You will? Truly?\" {giver} looks close to tears."),
    ("warm cheerful", "{giver} squeezes your arm. \"I knew you had the look of someone who'd help.\""),
    ("*", "\"Then there's hope yet,\" says {giver}."),
    ("melancholy warm", "{giver} is quiet a moment. \"Thank you. Thank you.\""),
    ("gruff", "{giver} grunts. \"Good. Don't make me regret it.\""),
    ("gruff", "\"About time someone did,\" says {giver}, which seems to be thanks."),
    ("suspicious", "\"We'll see,\" says {giver}. A pause. \"But thank you.\""),
    ("suspicious", "{giver} looks at you a long moment, then nods once. \"All right.\""),
    ("shrewd", "\"Good. I rather thought you would,\" says {giver}."),
    ("shrewd", "{giver} smiles. \"Then we understand each other.\""),
    ("cheerful", "\"Ha! I knew it!\" {giver} claps you on the shoulder."),
    ("cheerful", "{giver} beams. \"That's the best news I've had all week.\""),
    ("dreamy", "{giver} smiles, as though {he} had known all along you would."),
]


def toned(lines, temper):
    return [t for tags, t in lines if tags == "*" or temper in tags.split()]


def toned_rules():
    """Grammar rules for the name exchange and introductions, one set per temperament (the scoped lookup
    picks 'gruff:ask_name' for a gruff speaker), plus the full set unscoped for anyone else."""
    out = {"ask_name": [t for _, t in ASK_NAME], "npc_intro": [t for _, t in NPC_INTRO],
           "itag": ["says", "says", "tells you", "answers", "replies"]}
    for d in TEMPERS:
        out[f"{d}:ask_name"] = toned(ASK_NAME, d)
        out[f"{d}:npc_intro"] = toned(NPC_INTRO, d)
    return out


def tool_for(npc):
    """What their hands are busy with, as a phrase: 'her hammer', 'a twist of paper'."""
    t = TOOL.get(npc.job) or ROLE_TOOL.get(npc.role, "a basket")
    if t.split()[0] in ("a", "an", "the"):
        return t
    return f"{npc.pronouns()['his']} {t}"


def self_lines(npc):
    """Ways this person might describe their work."""
    generic = [s.replace("{job}", npc.job) for s in GENERIC_SELF]
    return JOB_SELF.get(npc.job, []) + generic
