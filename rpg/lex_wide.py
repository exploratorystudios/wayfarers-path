"""Widening the lines every location uses, measured as the most repeated across worlds (tools/repeats.py).

Terrain changes: each land type has ways of being left and ways of being entered, joined in several
ways, so a change from wood to fen is one of dozens of passages instead of one of two. The lines about
what surrounds you, what lies onward and how the ground goes get lines of their own for each land
type, added to the general ones rather than replacing them.

Lines make no claims about weather, light or season (those come from elsewhere and are checked).
"""

LAND = ["forest", "marsh", "plains", "hills", "peaks"]

# leaving a land type: sentence-starting clauses without a full stop
LEAVE = {
    "forest": ["the trees thin, then fall behind you", "the last trunks drop away", "you push out through a fringe of hazel and bramble",
               "the wood lets you go", "the shade breaks up into scattered trees and then into none",
               "you come out from under the branches", "the canopy opens and does not close again"],
    "marsh":  ["the mud gives up its grip on your boots", "the reeds fall away behind you", "you climb out of the wet ground",
               "the last pools are behind you", "the squelch underfoot turns to something firmer",
               "you leave the fen and its sour smell behind", "the ground stops moving when you stand on it"],
    "plains": ["the open country is behind you", "the grass gives way", "you leave the wide land at your back",
               "the level ground comes to an end", "the long views close up behind you", "the turf runs out"],
    "hills":  ["you come down off the slopes", "the high ground falls away behind you", "the hills shrug you off",
               "the last ridge drops behind you", "your knees stop arguing with the gradient", "the ground levels out at last"],
    "peaks":  ["you come down out of the crags", "the bare rock is behind you", "the mountain lets go of you",
               "the scree gives way to the first thin grass", "you leave the high stone and its cold behind",
               "the thin air thickens as you descend"],
}
# entering a land type: clauses that can follow "and" or a semicolon
ENTER = {
    "forest": ["trees close in around you", "you walk into green shade", "trunks rise on every side",
               "the wood takes you in", "branches knit together overhead", "leaf litter softens every step",
               "you are among the trees"],
    "marsh":  ["the ground turns soft and wet", "reeds rise around you", "each step sucks at your boots",
               "water stands in every hollow", "you are in fen country", "the air smells of wet earth and rot",
               "the path becomes a guess between pools"],
    "plains": ["the land opens out wide around you", "you are out in open country", "the horizon steps back",
               "grass runs away on every side", "nothing rises higher than you for a long way", "the sky takes up most of the view"],
    "hills":  ["the ground begins to climb", "the land folds itself into hills", "slopes rise on either hand",
               "you start to feel the climb in your legs", "the path finds its way between rounded hills", "ridges lift ahead of you"],
    "peaks":  ["there is only rock", "the crags rise up ahead", "the climb grows hard and steep",
               "stone walls rise on either side", "the mountains stand over you", "loose scree shifts under your boots"],
}
ARRIVE_FORMS = ["{tleave.cap}, and {tenter}.", "{tleave.cap}; {tenter}.", "{tleave.cap}. Soon {tenter}.",
                "{tleave.cap} - and {tenter}.", "{tleave.cap}, and before long {tenter}."]

# what surrounds you, per land type ({but} is ", except to the north" and the like)
SURROUND = {
    "forest": ["Trunks crowd in on every side{but}.", "Whichever way you turn there are trees{but}.", "There's no seeing out of the wood from here{but}.",
               "Green shade wraps round you on all sides{but}.", "The wood goes on in every direction{but}.", "Trees, and more trees, all around{but}."],
    "marsh":  ["Reeds and water stretch away on every side{but}.", "There is no firm edge to the fen in any direction{but}.",
               "Pools and tussocks run on all around you{but}.", "The marsh spreads out on every hand{but}.", "Wet ground, in every direction{but}."],
    "plains": ["Open land runs away in every direction{but}.", "The grass goes on to every horizon{but}.", "There's nothing to stop the eye in any direction{but}.",
               "Wide country lies on every side{but}.", "Wherever you turn, it's open ground{but}."],
    "hills":  ["Slopes rise and fall on every side{but}.", "Hill after hill rolls away around you{but}.", "Wherever you look the land folds into hills{but}.",
               "Ridges ring you round{but}.", "There's high ground on every side{but}."],
    "peaks":  ["Rock walls you in on every side{but}.", "Crags stand round you like a ring of giants{but}.", "Stone, in every direction{but}.",
               "There is no way out of the mountains that doesn't climb{but}.", "Peaks crowd the sky all around{but}."],
}
# more of the same land onward, per land type ({dirs} "north and east", {region})
SAME = {
    "forest": ["The trees go on {dirs}.", "{dirs.cap}, the wood thickens.", "More woodland lies {dirs} of here.", "Head {dirs} and you stay under the trees."],
    "marsh":  ["The fen goes on {dirs}.", "{dirs.cap}, more reeds and standing water.", "Head {dirs} and it's marsh all the way.", "The wet ground continues {dirs}."],
    "plains": ["The open country goes on {dirs}.", "{dirs.cap}, more grassland, flat and wide.", "Head {dirs} and the land stays open.", "The wide land continues {dirs}."],
    "hills":  ["The hills go on {dirs}.", "{dirs.cap}, ridge follows ridge.", "Head {dirs} and you'll keep climbing and dropping.", "More slopes lie {dirs} of here."],
    "peaks":  ["The crags go on {dirs}.", "{dirs.cap}, more rock and more height.", "Head {dirs} and the mountains go with you.", "Bare stone continues {dirs}."],
}
# walking on within one region ({dir}, {region})
ONWARD = ["You go on {dir} through {region}.", "{region.cap} carries on as you head {dir}.", "You make your way {dir}, {region} all around.",
          "The going stays the same as you head {dir} through {region}.", "{dir.cap}, and still {region}.", "You cover more ground {dir}ward, in {region} yet.",
          "Your way runs {dir}, through more of {region}.", "You follow the lie of the land {dir} across {region}."]
TERRAIN = ["Underfoot it's {ground}.", "{ground.cap}, mostly.", "You make your way over {ground}.", "The way is {ground}.",
           "Your path crosses {ground}.", "It's {ground} for a while.", "{ground.cap} slows you a little."]
OPENING = {
    "forest": ["Moss softens the roots of every tree.", "Somewhere above, branches creak against each other.", "The wood is full of small noises you can't place.",
               "Old leaves have drifted deep between the roots.", "A track of sorts winds between the trunks."],
    "marsh":  ["Bubbles rise where you step and break with a small sour smell.", "The ground quakes a little under your weight.", "A heron lifts from the reeds ahead, slow and offended.",
               "Black water lies between the tussocks.", "Every path here might be a path, or might be a trap."],
    "plains": ["The grass is long and full of small movement.", "A track runs across the open ground, pale and straight.", "A hare bolts from almost under your feet.",
               "There is a lot of sky here, and not much else.", "The land rolls gently, and you roll with it."],
    "hills":  ["The path climbs, drops, and climbs again.", "Sheep watch you pass from a slope above.", "A dry-stone wall follows the hill's curve, then gives up.",
               "Each rise shows you another rise behind it.", "Streams have cut deep little valleys into the hillside."],
    "peaks":  ["Every step up costs something.", "Loose stones skitter away down the slope behind you.", "The rock is cracked and split by frost.",
               "Ravens tumble along the ridge, calling.", "Old stone cairns mark the way, where there is a way."],
}


def install(g):
    """Add all of the above to a grammar that already holds the base lexicon."""
    ext = {}
    for a, leaves in LEAVE.items():
        ext[f"{a}>:tleave"] = list(leaves)
    for b, enters in ENTER.items():
        ext[f">{b}:tenter"] = list(enters)
    for a in LAND:
        for b in LAND:
            if a != b:
                ext[f"{a}>{b}:arrive"] = list(ARRIVE_FORMS)
    for land in LAND:                       # scoped copies keep the general lines and add the land's own
        base = g.rules.get("exit_surround", [])
        g.rules[f"{land}:exit_surround"] = list(base) + g._norm(SURROUND[land])
        base = g.rules.get("exit_same", [])
        g.rules[f"{land}:exit_same"] = list(base) + g._norm(SAME[land])
        ext[f"{land}:opening"] = OPENING[land]
    ext["onward"] = ONWARD
    ext["terrain"] = TERRAIN
    g.extend(ext)
