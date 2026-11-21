"""Narration for class abilities. ctx: the_c (creature), part (its body parts)."""

RULES = {
    # ---------------------------------------------------------------- refusals
    "ab_unknown": ["That isn't something a {klass} knows how to do.", "You have no training in {ability}.", "{ability.cap} is beyond you; it isn't your art."],
    "ab_need_fight": ["{ability} is for the heat of a fight.", "There's nothing to use {ability} against right now."],
    "ab_need_peace": ["Not now - you're fighting for your life.", "There's no time for that mid-fight."],
    "ab_spent": ["You're out of {res}. Rest, or let it return as you travel.", "Your {res} is spent.", "You reach for it and find nothing left: no {res}."],
    "ab_no_target": ["There's nothing here to use {ability} on.", "No target presents itself."],
    "ab_which": ["Use {ability} on what?"],

    # ---------------------------------------------------------------- knight
    "ab_bash_hit": ["You drive your shield into {the_c}'s {part} with a crunch.", "Your shield rim catches {the_c} hard across the {part}.", "You slam forward, shield-first, and {the_c} reels."],
    "ab_bash_stun": ["Your shield takes {the_c} full in the {part}, and it staggers, stunned.", "A brutal bash: {the_c} reels, dazed and blinking.", "The blow rings out like a bell, and {the_c} sways, senseless for a moment."],
    "ab_bash_miss": ["You lunge with your shield, but {the_c} slips aside.", "Your bash meets only air as {the_c} twists clear."],
    "ab_stunned": ["{the_c.cap} shakes its head, too dazed to strike.", "{the_c.cap} lurches, still stunned, and does nothing.", "Dazed, {the_c} stumbles and gathers itself."],
    "ab_guard": ["You set your feet and raise your shield.", "You hunker behind your shield, ready to take whatever comes.", "Shield up, chin down: you brace."],
    "ab_guard_absorb": ["Your shield takes most of it.", "The blow lands on your raised shield and half its force is lost."],

    # ---------------------------------------------------------------- ranger
    "ab_shoot_open": ["You nock, draw and loose before {the_c} knows you're there - the arrow takes it in the {part}.",
                      "From a distance, your arrow flies true into {the_c}'s {part}. It is still closing on you.",
                      "Your first arrow is the best one: it thuds into {the_c}'s {part} as it charges."],
    "ab_shoot_hit": ["You loose at close range; the arrow punches into {the_c}'s {part}.", "You snap off a shot that bites into {the_c}'s {part}."],
    "ab_shoot_miss": ["Your arrow hisses past {the_c}.", "The shot goes wide and skips away into the undergrowth.", "{the_c.cap} moves just as you loose; the arrow misses."],
    "ab_track_start": ["You crouch and read the ground: prints, broken stems, droppings, the way the birds sit.",
                       "You go quiet and let the land speak: tracks, scents, disturbed earth."],
    "ab_track_sign": ["To the {dir}, the signs say {a_c}. {intent.cap}", "{dir.cap}ward, fresh sign of {a_c}: {intent}", "There's {a_c} to the {dir}. {intent.cap}"],
    "ab_track_none": ["Nothing large has passed nearby recently.", "The signs are old and cold; the neighbouring land is quiet."],

    # ---------------------------------------------------------------- wizard
    "ab_firebolt": ["Fire gathers in your palm and leaps at {the_c}, bursting across its {part}.", "You speak the hard word and a bolt of flame slams into {the_c}.",
                    "Heat roars from your hands; {the_c}'s {part} blackens and smokes."],
    "ab_firebolt_crit": ["The fire comes out of you whiter than you meant it to - {the_c} is engulfed.", "A great gout of flame swallows {the_c}'s {part} whole."],
    "ab_ward": ["You trace a circle in the air; it hardens into a shimmering skin around you.", "A ward settles over you, faintly humming.", "Pale light knits itself around you into a shield."],
    "ab_ward_absorb": ["Your ward flares and swallows the blow.", "The ward shudders under the impact, but holds."],
    "ab_ward_break": ["Your ward shatters like thin ice.", "The ward gives way with a sound like a snapped string."],
    "ab_fear_ok": ["You fill {the_c}'s mind with something it cannot bear. Its eyes roll white.", "You reach into {the_c}'s thoughts and plant terror there. It recoils.",
                   "A shadow of dread falls on {the_c}. It no longer wants anything but to be gone."],
    "ab_fear_resist": ["{the_c.cap} shakes off the dread you send at it.", "Your spell slides off {the_c}'s stubborn mind.", "{the_c.cap} flinches - then comes on anyway."],
    "ab_fear_boss": ["{the_c.cap} is older than fear. Your magic breaks against it.", "Nothing you can summon frightens {the_c}."],

    # ---------------------------------------------------------------- rogue
    "ab_backstab": ["You're behind {the_c} before it knows it, and your blade finds the soft place in its {part}.",
                    "One quick step from nowhere: your blade sinks deep into {the_c}'s {part}.",
                    "{the_c.cap} never sees you. Your strike to its {part} is precise and terrible."],
    "ab_backstab_seen": ["{the_c.cap} is watching you too closely for tricks; you settle for an ordinary cut.", "No opening - {the_c} sees you coming. Your strike lands, but plainly."],
    "ab_vanish": ["You twist away, drop low, and are simply gone. {the_c.cap} casts about, baffled.", "A feint, a shadow, a step sideways - and {the_c} has lost you.",
                  "You melt into the cover. {the_c.cap} snuffles at empty air."],
    "ab_vanish_fail": ["You try to slip away, but {the_c} keeps you pinned with its gaze.", "{the_c.cap} is not fooled; there's nowhere to hide."],
    "ab_hidden_safe": ["Hidden, you watch {the_c} pass without seeing you.", "{the_c.cap} looks right past your hiding place."],

    # ---------------------------------------------------------------- cleric
    "ab_heal": ["You pray, and warmth runs through you; cuts close and bruises fade.", "Light gathers under your hands and sinks into your wounds.", "You whisper the old words, and the pain eases like a tide going out."],
    "ab_smite": ["Holy force cracks down on {the_c} like a hammer of light.", "You call down judgement, and {the_c} is struck across the {part}.", "Light lances from your raised hand into {the_c}."],
    "ab_smite_undead": ["The light sears {the_c} - it was never meant to bear it.", "Holy fire tears through {the_c}'s unlife; it howls."],
    "ab_turn_ok": ["You raise your symbol and speak with the authority of the living. {the_c.cap} recoils from it.", "\"Begone,\" you command - and {the_c} obeys, shrinking away."],
    "ab_turn_beast": ["{the_c.cap} is flesh and blood; your command means nothing to it.", "Turning works on the dead. {the_c.cap} is very much alive."],
    "undead_soften": ["Your blessing blunts the cold of its touch."],
}
