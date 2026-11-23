"""Words that know what they mean, for word-level choices inside sentence shapes.

A slot like {@verb:hurt,with=part} asks for a verb tagged 'hurt' that can take the bound 'part' as its
subject: knees ache, stiffen or creak; a back aches but doesn't creak. {@noun:weather,bad,now} asks for
foul weather that can happen in the current season (no snow coming in summer). sentences.py does the
choosing; this file is only the words.

NOUNS   text: tags. The text is the whole noun phrase as it would be said ('a storm', 'rain', 'the east
        wind'). 'pl' makes it plural for agreement; 'season:a/b' limits it to those seasons.
VERBS   lemma: (tags, subject tags). The verb fits a subject that has any of the subject tags.
ADJS    word: (tags, tags of what it can describe).
"""

NOUNS = {
    # ---- the body (bare: shapes say 'my {part}')
    "knee": "body joint leg", "knees": "body joint leg pl", "hip": "body joint", "wrist": "body joint arm", "shoulder": "body joint arm",
    "back": "body trunk", "hands": "body arm pl hand", "ankle": "body joint leg", "elbow": "body joint arm", "fingers": "body arm pl hand",
    "neck": "body trunk", "old break in my arm": "body arm wound",
    # ---- weather on the way
    "a storm": "weather bad wet wind storm", "rain": "weather bad wet falling", "a frost": "weather bad cold frosty season:autumn/winter/spring",
    "snow": "weather bad cold falling season:winter", "the east wind": "weather bad wind cold", "a gale": "weather bad wind storm",
    "thunder": "weather bad storm season:spring/summer/autumn", "sleet": "weather bad cold wet falling season:autumn/winter/spring",
    "a wet spell": "weather bad wet", "fog": "weather bad still", "a hard frost": "weather bad cold frosty season:winter",
    "a cold snap": "weather bad cold season:autumn/winter/spring", "hail": "weather bad cold storm falling season:spring/summer/autumn",
    "a thaw": "weather mild season:winter/spring", "a dry spell": "weather fair season:spring/summer/autumn", "a warm spell": "weather fair mild season:spring/summer/autumn",
}

# ---- for descriptions: what's all around you, by terrain; what the air is like, by weather and hour
NOUNS.update({
    "trees": "cover pl tall biome:forest", "trunks": "cover pl tall biome:forest", "the trees": "cover pl tall biome:forest",
    "oaks and birches": "cover pl tall biome:forest", "undergrowth": "cover low biome:forest", "the wood": "cover wide biome:forest",
    "reeds": "cover pl tall biome:marsh", "pools and tussocks": "cover pl low wet biome:marsh", "bog": "cover low wet biome:marsh",
    "sedge": "cover low biome:marsh", "black water": "cover low wet biome:marsh/lake",
    "grass": "cover low wide biome:plains", "open grassland": "cover low wide biome:plains", "the downs": "cover pl wide biome:plains/hills",
    "the long grass": "cover low biome:plains", "fields": "cover pl wide biome:plains",
    "slopes": "cover pl wide biome:hills", "the hills": "cover pl wide tall biome:hills", "heather": "cover low wide biome:hills",
    "bracken": "cover low biome:hills/forest", "the fells": "cover pl wide tall biome:hills/peaks",
    "crags": "cover pl tall biome:peaks", "scree": "cover low biome:peaks", "bare rock": "cover low wide biome:peaks", "the peaks": "cover pl tall biome:peaks",
    "water": "cover wide wet biome:lake", "the shore": "cover low biome:lake", "the lake": "cover wide wet biome:lake",
    # the air
    "the breeze": "air moving weather:clear/cloudy/overcast/drizzle", "the wind": "air moving weather:wind/storm/rain/snow/cloudy",
    "the still air": "air still weather:clear/fog/overcast/cloudy", "the damp air": "air damp weather:fog/drizzle/rain/overcast",
    "the cold air": "air cold season:winter/autumn", "the warm air": "air warm season:summer/spring weather:clear/cloudy",
    "the night air": "air time:night/deepnight/evening", "the morning air": "air fresh time:dawn/morning", "the evening air": "air time:dusk/evening",
    "every breath": "air", "the air": "air", "a faint stir of air": "air moving", "a light air": "air moving", "the faintest breeze": "air moving", "a breath of wind": "air moving",
    "the moving air": "air moving", "each gust": "air moving weather:wind/storm",
    "the fog": "air damp still weather:fog",
})
VERBS = {
    # ---- what a bad joint does
    "ache": ("hurt", "body"), "throb": ("hurt", "body"), "stiffen": ("hurt", "joint hand"), "creak": ("hurt", "joint"), "swell": ("hurt", "joint hand"),
    "lock": ("hurt", "joint"), "burn": ("hurt", "body"), "grumble": ("hurt", "body"), "play up": ("hurt", "body"), "twinge": ("hurt", "body"),
    "complain": ("hurt", "body"), "nag at me": ("hurt", "body"), "give me gyp": ("hurt", "body"), "go stiff": ("hurt", "joint trunk hand"),
    "seize up": ("hurt", "joint trunk"), "tingle": ("hurt", "hand arm wound"), "pull": ("hurt", "wound trunk"), "pinch": ("hurt", "trunk joint"),
    # ---- knowing the weather before it comes
    "know": ("sense", "body"), "feel": ("sense", "body"), "smell": ("sense", "body"), "tell": ("sense", "body"), "sense": ("sense", "body"),
    # ---- what someone sick does through the night (subject: a person)
    "cough": ("sicknight", "person"), "wheeze": ("sicknight", "person"), "toss and turn": ("sicknight", "person"), "mutter": ("sicknight", "person"),
    "moan": ("sicknight", "person"), "shiver": ("sicknight", "person"), "burn up": ("sicknight", "person"), "fight for breath": ("sicknight", "person"),
    "call out": ("sicknight", "person"), "sweat through the sheets": ("sicknight", "person"), "rattle": ("sicknight", "person"),
    # ---- weather arriving
    "come": ("approach", "weather"), "come in": ("approach", "weather"), "blow up": ("approach", "wind storm"), "set in": ("approach", "wet cold still"),
    "roll in": ("approach", "wet still storm"), "gather": ("approach", "storm"), "brew": ("approach", "storm wind wet"), "creep in": ("approach", "cold still frosty"),
    "work up": ("approach", "storm wind"), "draw in": ("approach", "weather"), "close in": ("approach", "still cold wet"), "settle in": ("approach", "cold wet still frosty mild fair"),
    "build": ("approach", "storm"),
    # ---- what's around you does this, on every side
    "crowd close": ("surround", "tall"), "press in": ("surround", "tall"), "stand": ("surround", "tall"), "rise": ("surround", "tall"),
    "close in": ("surround", "tall wet"), "loom": ("surround", "tall"), "hem you in": ("surround", "tall"),
    "stretch away": ("surround", "wide low"), "spread": ("surround", "wide low wet"), "roll away": ("surround", "wide"),
    "lie": ("surround", "wide low wet"), "fill the view": ("surround", "wide tall"),
    # ---- what the same land does beyond you, onward in a direction
    "go on": ("onward", "wide low tall"), "run on": ("onward", "wide low"), "carry on": ("onward", "wide low tall"),
    "stretch on": ("onward", "wide low"), "march on": ("onward", "tall"), "roll on": ("onward", "wide"), "keep on": ("onward", "wide low tall"),
    # ---- what the air does with a smell or a sound
    "carry": ("bring", "moving"), "bring": ("bring", "moving"), "bear": ("bring", "moving"), "smell of": ("hold", "air"), "be thick with": ("hold", "still damp warm"),
    "hold": ("hold", "still damp cold"), "taste of": ("hold", "air"), "be full of": ("hold", "air"), "hang heavy with": ("hold", "still damp warm"),
    "be sharp with": ("hold", "cold fresh"), "come down": ("approach", "falling"), "turn up": ("approach", "wind"),
}

ADJS = {
    "bad": ("plain", "body"), "old": ("plain", "body"), "stiff": ("plain", "joint hand trunk"), "useless": ("grumble", "body"), "wretched": ("grumble", "body"),
    "creaking": ("plain", "joint"), "crooked": ("plain", "hand arm joint"), "ruined": ("grumble", "joint"), "cursed": ("grumble", "body"),
    "dodgy": ("plain", "body"), "gammy": ("plain", "leg joint"), "worn-out": ("plain", "body"), "trick": ("plain", "joint"),
}


def _split(tags):
    """'weather bad season:winter/spring biome:marsh' -> ({'weather', 'bad'}, {'season': {'winter', 'spring'}, 'biome': {'marsh'}})."""
    plain, limits = set(), {}
    for x in tags.split():
        if ":" in x:
            k, v = x.split(":", 1)
            limits.setdefault(k, set()).update(v.split("/"))
        else:
            plain.add(x)
    return plain, limits


def table():
    """The dictionary as {pos: [(text, tags, partner tags, limits)]}. Partner tags are what a verb's subject
    or an adjective's noun must have; limits are season/weather/time/biome a word is restricted to."""
    out = {"noun": [], "verb": [], "adj": []}
    for text, tags in NOUNS.items():
        plain, limits = _split(tags)
        out["noun"].append((text, plain, set(), limits))
    for lemma, (tags, subj) in VERBS.items():
        plain, limits = _split(tags)
        out["verb"].append((lemma, plain, set(subj.split()), limits))
    for word, (tags, desc) in ADJS.items():
        plain, limits = _split(tags)
        out["adj"].append((word, plain, set(desc.split()), limits))
    return out
