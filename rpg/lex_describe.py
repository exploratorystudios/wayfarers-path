"""The framing lines of place descriptions, built from parts instead of picked whole.

The descriptions' content (what a forest is like in autumn rain) was already built from many small
rules. What repeated, run after run, were the frames around it: "You are hemmed in by...", "The eye goes
to...", "the smell is everywhere here". These were short lists, used in every description.

Here each frame is put together from sub-rules (all named 'x_...'), and some words are chosen one at a
time by what they mean (lex_words.py): what's all around you fits the land ('trees crowd close', 'reeds
rise', 'grass runs on'), and what carries a smell or a sound fits the weather and the hour ('the damp
air', 'the night air').

GRAMMAR is added to the narrator's grammar; EXTEND appends these shapes to the older rules, weighted so
the built ones are used most of the time.
"""

GRAMMAR = {
    # ---- all about you
    "x_you_are": ["You are", "You're", "You find yourself", "You stand", "You walk on"],
    "x_amid": ["deep in", "well into", "in the middle of", "surrounded by", "out among", "in the thick of", "in among", "lost in"],
    "x_every_way": ["Every way you turn, there's", "Whichever way you face, it's", "On all sides, nothing but", "There's no end yet to",
                    "As far as you can see, it's", "Look any way you like: it's all", "Nothing but", "No sign of an end to"],
    "x_all_round": ["on every side", "all around you", "as far as you can see", "in every direction", "wherever you look", "all the way to the sky"],
    "x_region_goes": ["goes on", "runs on", "carries on", "keeps on", "stretches on"],
    # ---- smells
    "x_catch": ["You catch", "You get", "You pick up", "You notice", "There's"],
    "x_whiff": ["the scent of", "a whiff of", "a breath of", "the smell of", "a trace of", "a hint of"],
    "x_hang": ["hangs in the air", "lingers here", "drifts past", "hangs over everything", "comes and goes", "is strong here"],
    # ---- sounds
    "x_hear": ["You hear", "You can hear", "Somewhere, you hear", "Listening, you pick out", "Now and then comes", "From somewhere comes"],
    "x_sound_does": ["carries a long way", "comes and goes", "rises and falls", "goes on and on", "stops, and starts again"],
    # ---- how a landmark is noticed
    "x_lead": ["Not far off", "A little way off", "Nearby", "To one side", "Further on", "Within a stone's throw", "Just ahead", "Over to your left",
               "Over to your right", "A short walk away", "Ahead of you", "Down to one side", "Past the nearest rise", "A few dozen paces on"],
    "x_eye": ["Your eye goes to", "Your gaze settles on", "Your eye is drawn to", "You find yourself looking at", "Your eye keeps coming back to",
              "You can't help noticing", "Your attention catches on", "You look twice at"],
    "x_catches": ["catches your eye", "holds your eye", "draws your gaze", "snags your attention", "takes your eye", "pulls at your attention",
                  "stands out"],
    # ---- walking on
    "x_walk": ["You press on", "You carry on", "You go on", "You keep going", "You walk on", "You push on", "You head on", "You make your way"],
    "x_still_in": ["still in", "deeper into", "further into", "on through", "not yet out of", "across more of"],
    # ---- glimpses of the next land
    "x_glimpse_lead": ["Beyond, to the", "Off to the", "Away to the", "Further to the", "Looking"],
}

# Weights: the older fixed lines stay, at weight 1 each, so these built shapes carry most of the load.
EXTEND = {
    # surrounded: by the land itself, chosen to fit it (lex_words: 'cover' nouns and 'surround' verbs)
    "exit_surround": [
        (10, "{@noun:cover,here.subj.cap>cv} {@verb:surround,with=cv.v} {x_all_round}{but}."),
        (6, "{x_you_are} {x_amid} {land}{but}."),
        (6, "{x_every_way} {land}{but}."),
        (3, "{region.cap} {x_region_goes} [in every direction|as far as you can see|all around you|to the sky's edge]{but}."),
    ],
    # the same land carries on beyond you
    "exit_same": [
        (8, "{@noun:cover,here.subj.cap>cv} {@verb:onward,with=cv.v} to the {dirs}."),
        (4, "[To the {dirs}|Away {dirs}|Looking {dirs}], [it's the same country|there's no change|the land doesn't change] [for a long way|as far as you can see|yet]."),
        (4, "[Going|Heading|Walking] {dirs} [would keep you in|won't take you out of] {region}."),
    ],
    "exit_pair": [
        (8, "{@noun:cover,here.subj.cap>cv} {@verb:onward,with=cv.v} to the {sdirs}; [to the {ddirs}|but {ddirs}] [the land gives way to|you can see|the country turns to] {glimpse}."),
        (4, "[To the {sdirs}|{sdirs.cap}] there's more of the same; [to the {ddirs}|{ddirs}, though,] [you can make out|the land changes to|you glimpse] {glimpse}."),
    ],
    "sense_smell": [
        (8, "{@noun:air,sky,hour,now.subj.cap>ai} {@verb:hold,with=ai.v} {smell}."),
        (6, "{@noun:air,moving,sky,hour,now.subj.cap>ai} {@verb:bring,with=ai.v} {smell}."),
        (6, "{x_catch} {x_whiff} {smell}."),
        (5, "{smell.cap} {x_hang}."),
    ],
    "sense_sound": [
        (6, "{x_hear} {sound}."),
        (6, "{@noun:air,moving,sky,hour,now.subj.cap>ai} {@verb:bring,with=ai.v} {sound}."),
    ],
    "onward": [
        (12, "{x_walk} {dir}, {x_still_in} {region}."),
    ],
}

# extra landmark frames for describe.feature_line, built from the lead-ins above
FEATURE_FRAMES = [
    ("{x_lead}, {adjp.a} {noun} {verb} {where}.", 2.0),
    ("{x_lead}, {adjp.a} {noun} {verb} {where}, {d}.", 1.5),
    ("{x_eye} {adjp.a} {noun}, {d}.", 1.2),
    ("{x_eye} {adjp.a} {noun} that {verb} {where}.", 1.0),
    ("{adjp.a.cap} {noun} {x_catches}: {d}.", 1.0),
]
