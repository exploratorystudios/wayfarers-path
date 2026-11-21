"""Openings assembled from parts, and wider weather, mood and conversation lines.

Every tile you enter opens with a line from its land type, so even a list of fifteen is cycled through
in every run. Here each land type also gets subjects (all singular, so the verb always agrees) and
things they do, joined into about fifty more openings each. Weather and mood lines, which also come up
in nearly every description, get more lines too. All appended, none replacing.
"""

OP_SUBJ = {
    "forest": ["The wood", "The undergrowth", "The path", "The old forest", "The greenwood", "The tree-cover"],
    "marsh":  ["The fen", "The bog", "The marsh", "The wet ground", "The reed-bed", "The mire"],
    "plains": ["The heath", "The downland", "The grassland", "The open ground", "The common", "The moor"],
    "hills":  ["The hillside", "The slope", "The upland", "The high ground", "The hill country", "The ridge"],
    "peaks":  ["The mountainside", "The rock", "The crag", "The ridge", "The scree slope", "The high pass"],
}
OP_PRED = {
    "forest": ["is thick with holly and bramble", "grows close and dim on either side", "has swallowed the old track almost whole",
               "is criss-crossed by deer paths", "smells of leaf mould and fungus", "is older than any village near it",
               "thins here, then thickens again", "hums with small unseen life"],
    "marsh":  ["stretches flat and sodden in every direction", "is laced with channels of black water", "gives a little under every step",
               "breathes out a smell of rot and peat", "is broken up by tussocks and standing pools", "has swallowed fence-posts and paths alike",
               "is loud with small splashes and rustles", "lies low and brooding"],
    "plains": ["rolls away in long, low swells", "is cropped short by sheep and rabbits", "is crossed by an old drove road",
               "runs on to the edge of sight", "is dotted with gorse and lonely thorns", "lies open on every side",
               "rises so gently you barely notice", "is marked here and there by old boundary stones"],
    "hills":  ["climbs steadily ahead of you", "is scarred by old sheep-tracks", "folds down into a narrow valley",
               "is studded with grey boulders", "is crossed by a tumbledown wall", "gives way to scree near the top",
               "rises in a series of false summits", "drops away steeply to one side"],
    "peaks":  ["is bare and broken", "falls away into a sheer drop on one side", "is cracked by frost into great blocks",
               "rises in steps like a giant's stair", "is streaked with old stains of meltwater", "gives no easy footing anywhere",
               "is silent except for falling stones", "leans out over you, grey and enormous"],
}

EXTEND = {
    "overcast:weather_line": ["Cloud lies over everything like a lid.", "The sky is one even grey, without a seam.",
                              "The light is flat and shadowless under the cloud.", "A grey ceiling of cloud hangs over the land."],
    "cloudy:weather_line": ["Clouds drift over in no hurry.", "Shadows of clouds slide across the land.",
                            "Patches of blue come and go between the clouds.", "The clouds are piled high and white."],
    "clear:weather_line": ["The sky is clean and wide.", "Not a cloud anywhere.", "The air is so clear that far things look near.",
                           "Every edge stands out sharp under the open sky."],
    "rain:weather_line": ["Rain falls steadily, without spite.", "The rain finds its way down your collar.", "Everything drips.",
                          "Rain hisses on the ground around you."],
    "drizzle:weather_line": ["A fine drizzle hangs in the air more than falls.", "Drizzle beads on your sleeves.", "The air is damp enough to drink."],
    "fog:weather_line": ["Fog has rubbed out the distance.", "The world ends a stone's throw away, in white.", "Fog beads on every blade of grass."],
    "wind:weather_line": ["The wind pushes at you, then pulls.", "Gusts come and go, flattening the grass.", "The wind never quite stops."],
    "snow:weather_line": ["Snow falls slowly, each flake taking its time.", "The snow muffles every sound."],
    "storm:weather_line": ["The storm throws rain at you in handfuls.", "Thunder walks about the sky."],
    "dark_clear:weather_line": ["The stars are out, thick as frost.", "The night sky is clear and enormous."],
    "dark_cloudy:weather_line": ["Clouds slide over the stars and away again.", "Here and there a star shows between the clouds."],
    "dark_overcast:weather_line": ["The night is starless and close.", "No stars; the cloud has them all."],
    "dark_rain:weather_line": ["Rain falls in the dark, heard more than seen.", "The night is full of the sound of rain."],
    "dark_drizzle:weather_line": ["Drizzle drifts through the dark.", "The night is damp and soft."],
    "dark_fog:weather_line": ["Fog and darkness together leave you almost blind.", "The night fog swallows even the nearest shapes."],
    "dark_wind:weather_line": ["The wind roams the dark, unseen.", "Something in the night creaks with every gust."],
    "serene:mood_line": ["Nothing here is in a hurry.", "It is a place to sit, if you had the time.", "The quiet here feels kept, like a garden.",
                         "Everything seems to be exactly where it ought to be."],
    "eerie:mood_line": ["The silence here has a texture to it.", "You keep wanting to look behind you.", "Something about this place is listening."],
    "desolate:mood_line": ["Nothing here suggests anyone has ever cared for it.", "The emptiness has a weight of its own.", "It is a long way from anywhere here."],
    "ominous:mood_line": ["The air feels like the moment before a blow.", "Birds avoid this place, you notice.", "Your hand keeps drifting to your weapon."],
    "lush:mood_line": ["Everything here grows as if it has something to prove.", "Green crowds in on every side.", "Life is thick here, almost too thick."],
    "neutral:talk_beat": ["{name} rubs {his} chin.", "{name} tilts {his} head.", "{name} wipes {his} hands.", "{name} squints at you.", "{name} leans on {tool}."],
    "cold:talk_beat": ["{name} lets the silence stretch.", "{name} barely turns.", "{name} looks past you."],
    "friendly:talk_beat": ["{name} laughs.", "{name} makes room for you.", "{name} seems glad of the company."],
}
for _land in OP_SUBJ:
    EXTEND[f"{_land}:op_s"] = OP_SUBJ[_land]
    EXTEND[f"{_land}:op_p"] = OP_PRED[_land]
    EXTEND[f"{_land}:opening"] = ["{op_s} {op_p}."] * 8       # about fifty openings, weighted alongside the written ones

# lines the game builds in code
REST_SAFE = ["You find a bed for the night under a friendly roof.", "Someone lets you sleep by their hearth.",
             "A family makes room for you by the fire.", "You sleep in a loft that smells of hay and apples.",
             "You're given a pallet in a corner, and you sleep like the dead.", "Someone finds you a blanket and a dry corner."]
ELDER_HINT = ["{who} seems to be waiting for someone. Perhaps you should talk to {him}.",
              "{who} keeps glancing your way, as if {he} has something to say.",
              "{who} is watching you, the way people watch someone they mean to speak to.",
              "{who} looks like someone with a favour to ask. It might be worth a word.",
              "{who} catches your eye and holds it a moment. {he_cap} wants a word, plainly."]
RING = ["You strike the stone with your knuckles and it rings, a long pure note that goes out over the land and doesn't seem to stop.",
        "You tap the stone, and it answers with a note like a bell, which hangs in the air far longer than it should.",
        "The stone hums when you knock on it, and the hum spreads out through the ground under your feet.",
        "A knock with your knuckles, and the stone sings - a clear, high note that seems to come from everywhere."]
