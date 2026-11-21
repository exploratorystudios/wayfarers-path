"""Creature temperaments: the same kind of beast need not behave the same way in every world.

Each species in each world gets a temperament from the seed (so a wraith that is eerie in one world
may be brazen in the next). The temperament adds its own lines for how the creature stalks, hunts,
guards and flees, and how it warns, follows and circles you, alongside the general ones.
"""
import random

TEMPERS = ["brazen", "furtive", "eerie", "sullen", "skittish", "cunning"]

LINES = {
    "brazen": {
        "stalk": ["{a_c.cap} walks openly alongside you, as if daring you to do something about it.", "{a_c.cap} follows in plain view, making no effort to hide."],
        "hunt": ["{a_c.cap} comes straight at you, not bothering with cover.", "{a_c.cap} lets you see it coming. It wants you to."],
        "hold": ["{a_c.cap} stands square in your path and does not budge.", "{a_c.cap} puffs itself up and holds its ground, all bluster and threat."],
        "flee": ["{a_c.cap} gives ground, but slowly, with a look that promises it'll be back.", "{a_c.cap} backs off, still making a show of itself."],
        "warn": ["{the_c.cap} charges a few steps and stops short. Next time it won't stop.", "{the_c.cap} makes itself as big and loud as it can."],
        "warn_ignored": ["{the_c.cap} wastes no more time on warnings.", "That was all the warning {the_c} meant to give. It comes at you!"],
        "follow": ["{the_c.cap} trails you openly, not caring that you know.", "{the_c.cap} is still behind you, bold as you like."],
        "circle": ["{the_c.cap} swaggers round you, close enough to touch.", "{the_c.cap} circles, making feints it doesn't bother to finish."],
    },
    "furtive": {
        "stalk": ["Something moves at the edge of your sight - {a_c} - and is still again when you look.", "{a_c.cap} slips from cover to cover, never quite in the open."],
        "hunt": ["{a_c.cap} creeps closer, belly low, using every scrap of cover.", "You only notice {a_c} when it's already far too close."],
        "hold": ["{a_c.cap} watches from hiding, and you only know it's there by the eyes.", "{a_c.cap} keeps low and still, guarding its ground from cover."],
        "flee": ["{a_c.cap} melts back into cover the moment you look at it.", "{a_c.cap} is already slinking away."],
        "warn": ["A low sound from cover: {the_c}, telling you to go.", "{the_c.cap} shows itself for a moment, just long enough to be a warning."],
        "warn_ignored": ["{the_c.cap} bursts from cover!", "You hear {the_c} before you see it - and then it's on you."],
        "follow": ["You think you've lost {the_c}. Then a twig snaps behind you.", "{the_c.cap} is back there somewhere, keeping to cover."],
        "circle": ["{the_c.cap} circles through the undergrowth, out of sight more than in it.", "{the_c.cap} keeps moving round you, low and quiet."],
    },
    "eerie": {
        "stalk": ["{a_c.cap} is simply there each time you look round, no nearer, no further.", "{a_c.cap} keeps its distance without ever seeming to move."],
        "hunt": ["{a_c.cap} comes on slowly, and the slowness is the worst of it.", "{a_c.cap} drifts towards you, silent, unhurried, certain."],
        "hold": ["{a_c.cap} does not move at all. Somehow that is a warning.", "{a_c.cap} stands utterly still and watches you, too still for a living thing."],
        "flee": ["{a_c.cap} withdraws without seeming to turn its back.", "{a_c.cap} is further away each time you look, and you never see it go."],
        "warn": ["{the_c.cap} makes no sound at all. The silence around it says enough.", "{the_c.cap} tilts its head at you, and the air goes cold."],
        "warn_ignored": ["{the_c.cap} is suddenly much closer than it was.", "There's no warning this time. {the_c.cap} is simply upon you."],
        "follow": ["{the_c.cap} is behind you. You didn't hear it come.", "Each time you glance back, {the_c} is the same distance away."],
        "circle": ["{the_c.cap} circles without seeming to walk.", "{the_c.cap} moves round you, and the hairs on your neck move with it."],
    },
    "sullen": {
        "stalk": ["{a_c.cap} trails after you, sulky and resentful, keeping well back.", "{a_c.cap} follows at a grudging distance, glowering."],
        "hunt": ["{a_c.cap} comes at you with a sort of weary hatred.", "{a_c.cap} lumbers towards you, as if this is a chore it means to finish."],
        "hold": ["{a_c.cap} glowers at you from its ground and will not shift.", "{a_c.cap} hunches over its patch, daring you without much interest."],
        "flee": ["{a_c.cap} stomps off, ill-tempered, looking back now and then.", "{a_c.cap} slopes away with bad grace."],
        "warn": ["{the_c.cap} grumbles deep in its chest. It would rather not, but it will.", "{the_c.cap} turns a dull, resentful stare on you."],
        "warn_ignored": ["{the_c.cap} heaves itself at you, out of patience.", "With a sound like a long-held grudge, {the_c} attacks."],
        "follow": ["{the_c.cap} follows, muttering, as if you owe it something.", "{the_c.cap} is still dogging your steps, sullen and slow."],
        "circle": ["{the_c.cap} shuffles round you, grudging every step.", "{the_c.cap} circles heavily, in no hurry."],
    },
    "skittish": {
        "stalk": ["{a_c.cap} follows in fits and starts, darting off at every sound and creeping back.", "{a_c.cap} edges after you, all nerves."],
        "hunt": ["{a_c.cap} rushes at you, stops, rushes again, working up its courage.", "{a_c.cap} comes at you in jittery bursts."],
        "hold": ["{a_c.cap} stamps and shifts, guarding its ground and plainly hating every moment.", "{a_c.cap} jumps at your every move, but won't leave its place."],
        "flee": ["{a_c.cap} starts at the sight of you and nearly falls over itself getting away.", "{a_c.cap} is ready to bolt at the first wrong move."],
        "warn": ["{the_c.cap} makes a high, nervous sound, half threat, half plea.", "{the_c.cap} shies and stamps: go away, go away."],
        "warn_ignored": ["Panicked, {the_c} lashes out!", "{the_c.cap}'s nerve breaks the wrong way - it attacks!"],
        "follow": ["{the_c.cap} follows, darting off and coming back.", "You keep hearing {the_c} behind you, skittering."],
        "circle": ["{the_c.cap} circles in quick, nervous dashes.", "{the_c.cap} darts round you, never still."],
    },
    "cunning": {
        "stalk": ["{a_c.cap} keeps to your blind side, and seems to know where that is.", "{a_c.cap} matches your pace exactly, studying how you move."],
        "hunt": ["{a_c.cap} angles in from where you're weakest.", "{a_c.cap} waits for you to commit to a step, and then moves."],
        "hold": ["{a_c.cap} has chosen its ground well, and knows it.", "{a_c.cap} watches you from a spot where it has every advantage."],
        "flee": ["{a_c.cap} retreats in a way that looks a lot like leading you somewhere.", "{a_c.cap} backs off, but never far, and never carelessly."],
        "warn": ["{the_c.cap} shows you its teeth, and then, pointedly, the way out.", "{the_c.cap} makes sure you see it - and makes sure you see the way you came."],
        "warn_ignored": ["{the_c.cap} has been waiting for exactly this.", "{the_c.cap} lets you take one step too many, and strikes."],
        "follow": ["{the_c.cap} is following, and you have the feeling it's choosing where.", "{the_c.cap} shadows you, keeping to your weak side."],
        "circle": ["{the_c.cap} circles, watching your feet more than your weapon.", "{the_c.cap} moves round you, testing, learning."],
    },
}
PRESENCE = ("stalk", "hunt", "hold", "flee")
ACTIONS = ("warn", "warn_ignored", "follow", "circle")


def temper(world, c):
    """The temperament of this creature's kind in this world."""
    return random.Random(f"{world.seed}-{c.species['name']}-temper").choice(TEMPERS)


def install(g):
    """Each temperament gets scoped copies of the general lines, plus its own."""
    for t, lines in LINES.items():
        for it in PRESENCE:
            base = g.rules.get(f"{it}:intent_presence", [])
            g.rules[f"{it}_{t}:intent_presence"] = list(base) + g._norm(lines[it]) * 2      # its own lines come up more often
        for key in ACTIONS:
            base = g.rules.get(key, [])
            g.rules[f"tm_{t}:{key}"] = list(base) + g._norm(lines[key]) * 2
