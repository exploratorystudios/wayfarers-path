"""The elder's tale of the lost relic, built per world instead of one speech with the names swapped.

Layers: what the relic was to the village, how it was lost (eight different shapes of story, some with
a named person in them), when, what has gone wrong since, what the village offers, and how the elder
tells it (five shapes of speech, plus how they set about saying it). The choice comes from the world's
seed with its own dice, so the story is the same however often you ask, and older saves get one too.
"""
import random

from . import names as NAMES
from .textgen import article

MEANT = [
    "the heart of the harvest rites", "what the founders swore their oath on", "the luck of this village",
    "carried at every wedding and every burying", "set over the hall door each midwinter",
    "what the old lords gave us when they freed the land", "our ward against whatever walks {region} at night",
    "the thing the first families brought with them when they came here", "the pledge that kept the peace with our neighbours",
    "what the wise-women read the year's turn by",
]

# how it was lost: (story, what it suggests about the place it went). {who} is a person's name where wanted.
LOSS = {
    "stolen":  ["It was stolen {when} - by a guest we fed and sheltered, if you can believe it - and carried off to {place}.",
                "Raiders took it {when}. They didn't get far: it ended up at {place}, and there it stayed."],
    "debt":    ["In a hungry year, {when}, we pawned it to pay what we owed. The debt's long paid. Nobody ever brought it back from {place}.",
                "{who} put it up against a debt {when}, meaning to redeem it. The man who held it took it to {place}, and that was that."],
    "keeper":  ["{who} was its keeper. {when_c}, there was trouble, and {who} carried it off to keep it safe - to {place}. {who} never came back.",
                "We gave it into {who}'s care {when}. For safekeeping, {who} took it to {place}, and neither of them was seen again."],
    "pledge":  ["We gave it as a pledge {when}, to seal a peace. The peace broke long ago, and the pledge still lies at {place}.",
                "It went to {place} {when}, as surety for a promise. The promise is dust; the thing itself never came home."],
    "buried":  ["We buried it {when} with {who}, at {place}, because it seemed right to. It seems less right now.",
                "{who} was laid to rest at {place} {when}, and it went into the ground with them. We need it back, and I don't say that lightly."],
    "cursed":  ["Folk thought it cursed, {when}, and sent it away to {place}. They were wrong. Everything that's gone wrong since says so.",
                "{when_c}, a bad run of luck was laid at its door, and it was carried out to {place}, and left there. A mistake, I think now."],
    "raid":    ["When the old hall burned, {when}, it was carried off in the confusion. It turned up at {place}, they say, and no one has dared fetch it.",
                "It was lost in the burning of the old hall {when}. Whoever saved it from the fire took it to {place}, and there it went cold."],
    "sold":    ["A headman sold it {when}, to a travelling collector, for less than a cow is worth. The collector got as far as {place}.",
                "{who} sold it {when}, may they be forgiven, and it passed from hand to hand until it came to rest at {place}."],
}
WHEN = ["generations back", "in my grandmother's time", "before I was born", "in the winter of the long frost", "forty years ago",
        "when the old hall still stood", "in my father's day", "longer ago than anyone can rightly say", "the year the river changed its course"]
SINCE = ["the seasons have soured", "the wells have tasted of iron", "the harvests have failed one year in three",
         "the dead haven't rested easy", "nothing has quite gone right", "the river floods every spring", "the bees left, and never came back",
         "we've quarrelled among ourselves", "children have been born sickly", "{region} has crept closer every year",
         "the old songs have stopped making sense"]
OFFER = ["Bring it home and {village} will not forget you.", "Bring it back, and you'll never pay for a bed here again.",
         "Fetch it home, and you'll have a place at our hearths for as long as you live.",
         "Whoever brings it home will have their name in our songs.", "I can't pay what it's worth. But {village} will remember.",
         "Do this, and ask anything of us that we can give.", "Bring it home. I'd like to see it here once before I die.",
         "Bring it back to {village}, and we'll owe you more than we can say."]
# how the elder sets about it (before the speech)
DELIVERY = ["{name} studies you a long moment, then speaks.", "{name} lowers {his} voice.", "{name} glances round before speaking.",
            "{name} takes your arm and walks you a little apart from the others.", "{name} is quiet for a while, then makes up {his} mind.",
            "{name} sighs, and seems to decide something.", "{name} looks you up and down, as if measuring you for a task.",
            "{name} sets down what {he} was doing.", "{name} waits until no one else is near.", "{name} rubs {his} eyes, and begins."]


def tale(world):
    """The world's relic story (cached on the world; worked out from the seed alone)."""
    t = world.__dict__.get("_relic_tale")
    if t:
        return t
    r = random.Random(f"{world.seed}-relic-tale")
    kind = r.choice(sorted(LOSS))
    try:
        who = NAMES.gen().generate(r, r.choice(["Archaic", "Westron", "Northish", "Southron"]), r.choice(["female", "male"]))
    except Exception:
        who = r.choice(["Old Aske", "Hild", "Tobin", "Mother Wenna"])
    t = world._relic_tale = dict(kind=kind, loss=r.choice(LOSS[kind]), meant=r.choice(MEANT), when=r.choice(WHEN),
                                 since=r.choice(SINCE), offer=r.choice(OFFER), shape=r.randrange(5), who=who)
    return t


def speech(g, npc):
    """What the elder says when they give you the quest: the delivery, then the tale in one of five shapes."""
    w, n = g.world, g.narr
    t = tale(w)
    q = w.tiles[w.quest_pos]
    region = w.region_of(w.quest_pos)["name"]
    village = w.tiles[w.start].site["name"]
    relic = w.relic.name
    place = f"{article(q.site['purpose'])} {n.dir_phrase(g.pos, w.quest_pos)}, in {region}"
    when = t["when"]
    fill = dict(when=when, when_c=when[0].upper() + when[1:], place=place, who=t["who"], region=region, village=village)
    loss = t["loss"].format(**fill)
    meant = t["meant"].format(**fill)
    since = t["since"].format(**fill)
    since = since[0].lower() + since[1:] if since.startswith("The ") else since
    offer = t["offer"].format(**fill)
    pr = npc.pronouns()
    lead = n.pick(DELIVERY, "relic-delivery").format(name=npc.name, he=pr["he"], his=pr["his"])
    shape = t["shape"]
    if shape == 0:      # what it was, how it went, what came after
        body = f"There was a thing kept here once - the {relic}. It was {meant}. {loss} Since then, {since}. {offer}"
    elif shape == 1:    # the trouble first, then the cause
        body = f"Ever since the {relic} left us, {since}. It was {meant}, you understand. {loss} {offer}"
    elif shape == 2:    # a question to the stranger
        body = f"Have you heard of the {relic}? No - why would you? It was {meant}. {loss} And since, {since}. {offer}"
    elif shape == 3:    # blunt
        body = f"I'll not dress it up. The {relic} is gone, and {since} ever since. {loss} {offer}"
    else:               # a confession
        body = f"You'll hear it from someone, so it may as well be me. The {relic} was {meant}, and we let it go. {loss} Since then, {since}. {offer}"
    return f"{lead} \"{body}\""
