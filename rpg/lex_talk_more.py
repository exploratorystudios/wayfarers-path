"""More conversation and village lines, for the ones tools/repeats.py finds in nearly every world.

Appended to the existing lists (lex_talk, lex_more, lex_entities), never replacing them.
"""

EXTEND = {
    "ask_name": [
        "\"Who's this, then?\" \"{player},\" you tell {him}.", "\"I don't know your face. What do they call you?\" \"{player}.\"",
        "\"You'll have a name.\" You admit that you do: {player}.", "\"And you are?\" \"{player}.\" {he.cap} turns it over, and nods.",
        "\"Name?\" {he} asks, not unkindly. \"{player},\" you say.", "\"Whose child are you, then?\" You settle for giving your own name: {player}.",
        "{he.cap} waits, eyebrows up, until you give your name: {player}.", "\"{player}, is it?\" {he} says, when you tell {him}. \"Well.\"",
        "\"Go on, then - who are you?\" \"{player}.\"", "You give your name before {he} can ask: {player}.",
        "\"Should I know you?\" \"Not yet. {player}.\"", "\"New face. Got a name to go with it?\" \"{player}.\"",
    ],
    "npc_intro": [
        "\"{name}. {job_self.cap}, for my sins and theirs.\"", "\"They call me {name} round here. {job_self.cap}.\"",
        "\"{name}'s my name, and I'm the {job}.\"", "{he.cap} jerks {his} chin at {his} work. \"{name}. {job_self.cap}.\"",
        "\"You can call me {name}. Most do.\"", "\"{name},\" {he} says, as if that settles a great deal.",
        "\"I'm {name}, and that's about all there is to me. {job_self.cap}.\"", "\"{name}. And before you ask - {job_self}.\"",
    ],
    "trade_beat": [
        "{name} nudges the best of the stock towards you.", "{name} names a price before you've asked about anything.",
        "{name} sweeps a hand along the goods like a conjuror.", "{name} lifts the cover off a basket to show you.",
        "{name} weighs you up as a customer, and seems to decide in your favour.",
    ],
    "recognise_line": [
        "{name} glances up and knows you.", "{name} sees you coming and waits.", "{name} gives you a look that says 'you again'.",
        "{name} lifts {his} chin at you in greeting.", "{name} remembers you, by the look of it.", "{name} calls your name across the lane.",
    ],
    "village_mood_busy": [
        "Carts and barrows squeeze past each other in the lanes.", "Someone is always shouting for someone else.",
        "Washing hangs from every line, and children run under it.", "You have to step aside twice in as many breaths to let people by.",
        "The smell of baking and smoke and animals hangs over everything.",
    ],
    "village_mood_wary": [
        "A mother calls her children indoors as you pass.", "A man leans in his doorway, arms folded, watching you all the way.",
        "Nobody greets you. Nobody needs to.", "You hear a bolt slide home behind a door.",
        "Dogs are tied short here, and so, it seems, are tempers.",
    ],
    "village_mood_sleepy": [
        "An old man dozes on a bench, hat over his face.", "A cat washes itself in the middle of the lane, quite unbothered.",
        "The loudest thing in the village is a hen, complaining.", "Whatever needs doing here can wait until tomorrow, by the look of it.",
        "Someone is snoring behind an open shutter.", "Time seems to move slower between these houses.",
    ],
    "village_mood_mournful": [
        "Shutters are closed on houses where people are plainly home.", "Somewhere, someone is singing a lament, badly and sincerely.",
        "Fresh flowers lie at a doorstep, already wilting.", "The faces you see are drawn and tired.",
        "Nobody laughs here. You notice it after a while.",
    ],
}

# lines the game builds in code rather than from the grammar
WARES = ["{name} gestures at {his} wares.", "{name} waves a hand over what {he} has for sale.", "{name} nods at the goods laid out beside {him}.",
         "{name} shows you what {he}'s selling, without much ceremony.", "{name} points out the best of {his} stock.",
         "\"Have a look,\" says {name}, stepping back from {his} wares.", "{name} turns a few things on the stall so you can see them."]
WAKE = ["You wake feeling better.", "You wake rested, and stiff in new places.", "Sleep does its work; you wake mended.",
        "You wake, and the aches have mostly gone.", "You come awake slowly, feeling more yourself.", "You rest, and are better for it.",
        "You wake with a clearer head and steadier hands."]
GROWN = ["You work at it, and it shows: you are {word} now.", "Days on the road have changed you. You are {word}.",
         "You feel the difference. You are {word}.", "Something has settled in you: you are {word} now.",
         "You notice it on the next hill: you are {word}.", "Practice pays. You are {word}.", "The road has made you {word}."]
CHALK_WALK = ["You walk the whole outline of the {noun}, as the worn path tells you people have for a thousand years. By the end your legs ache, and your arms feel like iron.",
              "You trace the {noun} on foot, every curve and line of it, the way pilgrims must have done. It takes hours. You finish stronger than you started.",
              "Round the {noun} you go, following the chalk where the turf has worn to white. By the last line you feel you could lift a cart.",
              "You walk the {noun}'s lines from end to end. Somewhere in the second hour the tiredness turns into something else: strength."]

PLOT_THANKS = ["{giver} grips your hand. \"Thank you.\"", "{giver} lets out a breath. \"I'll not forget this.\"", "\"Bless you,\" says {giver}.",
               "{giver} nods, and nods again, as if not trusting words.", "\"You will? Truly?\" {giver} looks close to tears.",
               "{giver} squeezes your arm. \"I knew you had the look of someone who'd help.\"", "\"Then there's hope yet,\" says {giver}.",
               "{giver} is quiet a moment. \"Thank you. Thank you.\""]
SNARE_FREE = ["You work the wire loose. The {beast} stares at you for one long second, then is gone. You feel, absurdly, that you've been thanked.",
              "The snare comes free in your hands. The {beast} doesn't wait to say goodbye, but it looks back once before it goes.",
              "You ease the noose off the {beast}'s leg. It lies still a moment, then bolts - and stops, and looks at you, and is gone.",
              "It takes patience and a nipped finger, but the {beast} is free. It vanishes into cover as if it had never been caught.",
              "With the wire cut, the {beast} limps a few steps, finds its legs, and runs. Something in you is lighter for it."]
TROUBLE_LEAD = ["{name} catches your sleeve.", "{name} steps into your path.", "{name} hurries over to you.", "{name} calls out to you.",
                "{name} hesitates, then speaks up.", "{name} plucks at your arm.", "{name} comes over, plainly worried."]
EXTEND.update({
    "rumour_beat": ["{name} jerks a thumb over {his} shoulder.", "{name} drops {his} voice to a murmur.", "{name} looks round before going on.",
                    "{name} taps the side of {his} nose.", "{name} frowns, remembering."],
    "exit_diff_named": ["{region.cap} isn't far: {dirs} of here, {glimpse}.", "Go {dirs} and you'll soon be in {region}.",
                        "{dirs.cap} lies {region}, where the land turns to {glimpse}.", "You can tell where {region} begins, {dirs} of here: {glimpse}."],
})
