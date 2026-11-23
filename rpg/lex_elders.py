"""The elders' opening speeches, as sentence shapes.

Each main quest hands speak() its facts as roles: the beast's name and history, who to ask and the way
there, the gifts and where they lie. Those keep every speech true to its world. The shapes here are how
an elder says each part (who's at fault, what's at stake, what you're to do), so the same quest is told
differently from world to world and elder to elder. The world-specific story parts each quest already
builds (a relic's history, a beast's origin, a blight's cause) come in as roles and are kept whole.

Every beat is a list of shapes for sentences.py; LEX is shared with all other dialogue.
"""
from . import sentences as SN
from . import speech as SP

LEX = {
    "all_heard": ["You'll have heard of", "You'll know the name", "Everyone from here to the hills has heard of", "Folk whisper about",
                  "There's not a soul in the valley who hasn't heard of"],
    "if_not": ["If you haven't, you will.", "If not, you soon will.", "Ask anyone.", "You'll hear more than you want to.", "Say it quietly."],
    "none_here": ["Nobody here can [kill|stand against|face] it.", "There's not a soul in {village} who could face it.",
                  "We've tried. We've buried the ones who tried.", "Our young ones went after it once. Once."],
    "maybe_you": ["Maybe you can.", "You might.", "You look like you could.", "I think you might be the one.", "You've the look of someone who could."],
    "proof": ["bring me something of it, so I know it's done", "bring back proof - a tooth, a claw, anything", "bring me a piece of it, so I can sleep",
              "bring something of it home, so folk will believe it"],
    "home_tell": ["Then come home and tell me", "Then come back and tell me", "And then come home to me and say", "Then come and tell me"],
    "listen": ["Listen.", "Hear me out.", "Sit, and listen.", "I'll tell you plainly.", "There's a thing you should know."],
}

# how the elder sets about it, before the speech: by temperament, and by what's at stake
LEADS = {
    "*": ["{name} studies you a long moment, then speaks.", "{name} lowers {his} voice.", "{name} glances round before speaking.",
          "{name} takes your arm and walks you a little apart from the others.", "{name} is quiet for a while, then makes up {his} mind.",
          "{name} sighs, and seems to decide something.", "{name} looks you up and down, as if measuring you for a task.",
          "{name} sets down what {he} was doing.", "{name} waits until no one else is near.", "{name} rubs {his} eyes, and begins."],
    "gruff": ["{name} spits, and gets on with it.", "{name} doesn't waste words.", "{name} jerks {his} head for you to follow, and talks as {he} walks."],
    "warm": ["{name} sits you down and puts a cup in your hands before {he} says a word.", "{name}'s smile goes, and {he} takes your hand."],
    "melancholy": ["{name} looks older than {he} did a moment ago.", "{name} stares at the ground a while before {he} speaks."],
    "shrewd": ["{name} weighs you up, then seems to decide you'll do.", "{name} leans in, as if striking a bargain."],
    "beast": ["{name} doesn't waste words.", "{name} looks toward the hills, and {his} jaw tightens."],
    "heir": ["{name} has been waiting for someone with legs younger than {his} own.", "{name} grips the edge of the table."],
    "pact": ["{name} speaks low, as if someone might be listening.", "{name} looks up at the hill before {he} answers."],
    "beacons": ["{name} looks older than {he} did a month ago.", "{name} pulls {his} coat tighter, though the fire's lit."],
    "feud": ["{name} is grim.", "{name} shakes {his} head slowly."],
    "bandit": ["{name} spits.", "{name}'s hands curl into fists."],
    "blight": ["{name} takes you to the edge of the village and looks out over the land a long while.", "{name} crumbles a black leaf between {his} fingers."],
    "relic": ["{name} studies you a long moment, then speaks.", "{name} glances round before speaking.", "{name} waits until no one else is near."],
}

BEATS = {
    "beast": [
        ["{all_heard} {title}. {if_not}", "{title_cap}. [You'll have heard the name.|That's what they call it now.|Say it quietly.]",
         "There's a thing out there folk call {title}."],
        ["{origin}"],
        ["{toll}"],
        ["{none_here} {maybe_you}"],
        ["Talk to {wa} in {va}, {dir_a} - {wa_he} fought it once and lived.",
         "{wa}, in {va}, {dir_a}, [fought it once|stood against it once] and [lived|lived to tell it]. [Start there.|Ask {wa_him}.|Talk to {wa_him}.]",
         "[Go first to|Start with] {wa} at {va}, {dir_a}. {wa_he_cap} [has fought it|faced it once] and [walked away|lived]."],
        ["And {wb} at {vb} has seen where it goes.", "{wb}, at {vb}, [knows|has seen] where it [lairs|goes to ground|sleeps].",
         "Then {wb} in {vb}. [{wb_he_cap}'s seen its lair.|{wb_he_cap} knows where it sleeps.]"],
        ["Find it, kill it, and {proof}.", "[Hunt it down|Find where it lies], [kill it|end it], and {proof}."]],
    "heir": [
        ["It's my {relation}, {hname}.", "My {relation}. {hname}. [Gone.|{they_cap}'s gone.]", "[I'll tell you plain.|You'll want to know who.] My {relation}, {hname}."],
        ["{reason}"],
        ["The last anyone saw, {they_s.subj} {~was|were} making for {first}, {dir}.",
         "{they_s.subj.cap} {~was|were} seen [heading for|on the road to|making for] {first}, {dir}. That's the last [anyone knows|word we had]."],
        ["Follow, and find {them}. Bring {them} home if you can. If you can't, bring me word.",
         "Find {them}. [Bring {them} home|Fetch {them} back], or [bring me word|tell me what became of {them}]."],
        ["But be quick: give it more than {days} days and the trail will be cold.", "[Don't dawdle.|Be quick.] In {days} days the trail will be cold.",
         "We've {days} days, maybe, before the trail goes cold."]],
    "pact": [
        ["There was a pact, long ago, between this village and {spirit}.", "[Long ago|In the old days], {village} made a pact with {spirit}.",
         "{village} has an old bargain with {spirit}. Older than any of us."],
        ["Every hundred years we take three gifts up to the spirit's place and say the old words. This is the year.",
         "[Once in a hundred years|Every hundredth year] we carry three gifts up to the spirit's place, [and say the old words|with the old words]. [This is the year.|And the hundredth year is this one.]"],
        ["{why}"],
        ["{wrong}"],
        ["The songs name the places: {spots}.", "[The old songs|The songs] [name|tell of] the places: {spots}."],
        ["Take a gift from each, and carry them to {spirit}'s shrine, {dir}, and go by night. That's when the spirit listens.",
         "[Gather|Bring] a gift from each, and carry them to {spirit}'s shrine, {dir}. [Go by night.|By night, mind.] [That's when the spirit listens.|The spirit only listens in the dark.]"]],
    "beacons": [
        ["{wrong}"],
        ["The old ones would have known what to do: {sleeper} has gone to sleep, and must be woken, and the way to wake a sleeper like that is fire.",
         "{sleeper_cap} [has gone to sleep|sleeps], [and must be woken|and won't wake on its own]. [The old ones knew.|My grandmother knew.] [Fire wakes a sleeper like that.|You wake a sleeper like that with fire.]"],
        ["Three beacons stand on the high places: {spots}.", "There are three beacons, [on the high places|up on the heights]: {spots}."],
        ["Light all three, and go up to where the sleeper lies when it stirs.", "Light [all three|every one], then [go up|climb] to where the sleeper lies [when it stirs|once it stirs]."],
        ["Then come home and tell me the year has turned.", "{home_tell} the year has turned."]],
    "feud": [
        ["{a} and {b} are sharpening scythes for each other.", "{a} and {b} [are at each other's throats|are a word away from blood|have stopped trading, and started sharpening scythes]."],
        ["It started over something at {place}, and it's grown in the telling until nobody remembers what's true.",
         "[It began|It started] over something at {place}. [Now nobody remembers what's true.|It's grown in the telling since.]"],
        ["If it comes to blood, every village from here to the hills will be in it by winter.",
         "[If it comes to blood|If a blow's struck], [every village from here to the hills|half the valley] will be in it [by winter|before the year's out]."],
        ["Somebody has to hear both sides with no stake in it, and go and see for themselves.",
         "We need someone with no stake in it to hear both sides, and [go and see|look] for themselves."],
        ["Start at {a}, {dir_a}, and {b}, {dir_b}. Find out what happened at {place}.",
         "[Go to|Start with] {a}, {dir_a}, and then {b}, {dir_b}. [Find out|Learn] what [really happened|truly happened] at {place}."],
        ["Then do what you think is right, and come and tell me.", "Then [do what's right|judge it fairly], and come and tell me."]],
    "bandit": [
        ["{captain_cap}. Holds {fort}, {dir}, and has made a fort of it, with a crew of cut-throats and a beast on a chain.",
         "{captain_cap} [holds|has taken] {fort}, {dir}, and made a fort of it. [A crew of cut-throats|A pack of cut-throats], and a beast on a chain."],
        ["{deed}"],
        ["No village can stand alone. Together, maybe.", "[Alone, no village can stand against them.|One village alone is nothing to them.] [Together, maybe.|Together, we might.]"],
        ["Go to {allies} and ask them to stand with us.", "[Ride|Go] to {allies}. Ask them to stand with us."],
        ["Then go to the fort. If they see enough of us at the gate, they might not even fight.",
         "Then on to the fort. [Enough of us at the gate, and they might not even fight.|If they see us all, they may just run.]"]],
    "blight": [
        ["It started out there, {dir}.", "[Out there|Look out there], {dir}. That's where it started."],
        ["{cause}"],
        ["{sign}"],
        ["It's coming this way, a little every day. {when}", "[It's coming|It creeps] this way, [a little every day|a field a day]. {when}"],
        ["Something at the heart of it is feeding it. Kill what's there, and bless the ground - a shrine's favour will do it, or holy water.",
         "Something lives at the heart of it, feeding it. [Kill it|Kill what's there], and bless the ground: [a shrine's favour|holy water] will do it."],
        ["Then come home and tell me it's done.", "{home_tell} it's done."]],
    "relic": [
        ["There was a thing kept here once - the {relic}. It was {meant}.", "Have you heard of the {relic}? No - why would you? It was {meant}.",
         "I'll not dress it up. The {relic} is gone.", "You'll hear it from someone, so it may as well be me. The {relic} was {meant}, and we let it go.",
         "[The|Our] {relic}. It was {meant}. [Was.|And now it's gone.]"],
        ["{loss}"],
        ["Since then, {since}.", "[Ever since|And since], {since}.", "Since that day, {since}."],
        ["{offer}"]],
}


def speak(g, npc, kind, roles):
    """The elder's opening speech for this quest: how they set about it, then the speech in their voice."""
    from . import lex_dialogue as DL
    n = g.narr
    lex = dict(DL.LEX, **LEX)
    pr = npc.pronouns()
    w = g.world
    base = dict(name=npc.name, he=pr["he"], his=pr["his"], him=pr["him"], village=w.tiles[w.start].site["name"])
    roles = dict(base, **roles)
    temper = npc.demeanour if npc.demeanour in LEADS else "*"
    lead = SN.say(n, LEADS.get(kind, []) + LEADS[temper] + LEADS["*"], lex, roles, f"elder-lead-{kind}")
    parts = [SN.say(n, shapes, lex, roles, f"elder-{kind}:{i}") for i, shapes in enumerate(BEATS[kind])]
    return lead + ' "' + SP.voice(g, npc, parts, roles, plain=True) + '"'
