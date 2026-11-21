# Wayfarer's Path

A text RPG, played in your browser or terminal, where every description is generated: landscapes, weather, light,
creatures, people, items, rumours and combat.

```
python3 play.py                     # opens the game in your browser (http://127.0.0.1:8765)
python3 play.py --port 9000         # ...on another port
python3 play.py --classic [seed]    # plain terminal version
python3 play.py --classic --load X  # resume a save in the terminal
```

### The web page

* **Story log** on the left.
* **Action bar**, always visible: a compass for movement, plus menus for Look,
  Items, People, Fight, Rest & Time, Info and Game. Every command is listed even
  when it doesn't apply, greyed out with the reason. Commands that need details
  open a submenu: `examine` lists everything in view, `buy` shows prices, `give`
  asks for the item and then the person, `save` takes a slot name. Number keys
  pick from an open menu; Esc steps back.
* **Suggestions** (optional): ranked ideas with reasons, picked with 1-6 or a click.
  The **Suggestions** switch in the header (or "hide suggestions") turns them off
  completely; the action bar stays. Each one shows the real command it runs, so
  you learn the syntax as you go, and the input box always accepts anything.
* **Open map** (on the map panel): unfolds a painted, cartographer-style chart of
  everywhere you've explored: watercolour land that fades into blank parchment,
  inked forests, hills and peaks, villages and landmarks, region names, the dashed
  red line of every road you've walked, and an X where the relic lies once you know.
  Scroll or pinch to zoom, drag to pan, and the **Your road** switch shows or hides
  your trail. **Save image** keeps a copy. Drawn by `rpg/web/atlas.js`, seeded, so a world
  always looks the same. The lettering is IM Fell English by Igino Marini, bundled in
  `rpg/web/fonts/` under the SIL Open Font License, so it works offline.
* **Map** (top right): the same painted land in miniature under a light grid,
  revealed as you explore. Click a tile next to you to walk there. Dots show the suggested route, and a purple ? marks the relic once
  you've been told where it is.
* **Status and pack**: health and experience bars, quest progress, and
  one-click use/equip/examine for everything you carry.

The server only listens on 127.0.0.1 and refuses requests from other sites.

### The suggestion engine (`rpg/advisor.py`)

It scores candidate actions from the current state: odds in a fight (it
estimates whether you'll win before you run out of health), healing that actually
outpaces incoming damage, unmet people, better gear in your pack, danger levels
of unexplored land against your level, the route to the relic (or home), and
when to go back and rest. It also avoids recommending the same informational
command twice in a row, and plans routes around creatures you've seen that would
beat you. It also knows about choices, quests (one at a time, so it doesn't zigzag),
troubles and hints at landmarks. As a test, a bot that always takes suggestion #1
wins about 90-100% of worlds depending on class.

In game (either version): `save [slot]` (plain `save` reuses your current slot), `load [slot]`,
`saves` (lists each save's character, level, day, place and time), `rename [old] [new]`,
`delete [slot]` (asks you to confirm). On the web page the **Saves** button opens a manager that
does all of this, warns before replacing a save or loading over unsaved progress, and marks
which save the current game belongs to. Quitting autosaves to `autosave`; after death you can reload. Saves live in `saves/` (Python pickles, so only load
files you made yourself).

No dependencies; Python 3.8+.

## The core idea: fixed facts, fresh words

* **Facts** are decided once from the seed (`rpg/world.py`): the map, named regions,
  which trees grow on a tile, the fallen oak *across the path* with *bracket fungus on
  its flank*, each creature species' colour and markings, each villager's face,
  each sword's maker's mark.
* **Prose** is generated anew every time (`rpg/describe.py`). Look twice and the same
  oak is described in different words, from a different angle, in a different order,
  coloured by the current time of day, weather, season, moon phase, and the mood of the place.

## How the text engine works (`rpg/textgen.py`)

* Tracery-style templates: `{symbol}`, modifiers `{symbol.a.cap}`, captures
  `{symbol>var}`, inline alternatives `[this|that|]`.
* **Scoped lookup**: `{canopy}` on an autumn forest tile tries `forest:autumn:canopy`
  then `forest:canopy` then `canopy`. Any situation can override general phrasing
  (e.g. `marsh:night:sound`, `dusk_bright:light_line`).
* **Anti-repetition memory**: each symbol remembers its recent choices and avoids
  them; the narrator also re-rolls any full sentence it has said recently.
* Post-processing fixes a/an, capitalisation and punctuation after assembly.

## People remember you

Every NPC keeps a memory: whether they know your name, how often and how
recently you've met, what you bought from, sold or gave them, and which rumours
they've already told you. Disposition (cold, neutral, friendly or devoted) shapes
greetings, prices (±20%), and whether they press a gift on you. News of your deeds
reaches nearby villagers at once and everyone else a day later, and they'll
bring it up.

## Places that do something

**Landmarks in the moment** (`rpg/lex_landmarks.py`). Every landmark has a kind
(41 of them: oaks, holy wells, gibbets, stone circles, hot springs, sunken punts...)
and is described as it is *right now*. Rain pocks the pool, frost furs the
hawthorn, the gibbet's cage squeals in the wind, the stone circle seems to hum under
a full moon, the yew is the only green thing in winter. A fixed detail that isn't
true at the moment ("not a single ripple", in a gale) gives way to one that is.

**Things to do** (`rpg/secrets.py`). `search`, `climb`, `drink`, `touch`, `read`,
`listen` and `forage` work on landmarks (also in the **Explore** menu), and
`give <item> to <landmark>` leaves an offering. Climbing shows you the land around.
Foraging depends on the season. About half of all landmarks keep a secret, fixed
when the world is made. Rewards include hidden caches, old blades, healing springs
and robbers' hoards. Magic includes fairy rings that want you to dance, visions at
standing stones, ghosts asking to be laid to rest, will-o'-wisps, a talking raven
with riddles and a mountain hermit. Mishaps include magpies that rob you (and
where they hide it), bees, badgers, bad water and falling in. Some lead to quests:
a keepsake engraved with the name of a real villager, a letter, a pilgrim's bones,
a cursed stone that must go back. Many only stir at night, under a full moon, in
fog or at dawn, and the description hints when something is waiting.

**Road encounters** (`rpg/encounters.py`). Out in the wilds you may meet a
starving deserter, lost pilgrims, a stuck cart, a lost child, the Wild Hunt, a
wedding, bandits, a bridge-troll, a dying traveller and more, each with a choice.
Answer with a number (or from the **Respond** menu).

**Quests and the journal** (`rpg/story.py`). Errands come from landmarks,
encounters and villages: bring something to someone, deliver it somewhere, kill
something, lead someone home, find a place. `journal` lists them, with directions.
The map outlines their goals.

**A living world** (`rpg/living.py`). Days pass and things happen. Villages develop
troubles: a beast at the folds, a fever, someone lost in the wilds, a haunting, a
stolen heirloom, a fouled well. They ask for your help, and troubles *wait for
you*: they never fail or get worse while you're away. When the season turns, every
village keeps its festival (the Mayday garlanding, midsummer fires, harvest home,
midwinter wassail), and villagers press food on you. Creatures drift back into
empty country. News travels as rumour.

**The world remembers.** `chronicle` lists everything notable you've done or seen.
Places keep traces: the body of a wolf you killed, the dug ground where you found a
cache, garlands after a trouble ends, a mound of stones over bones you buried.
People hear about your deeds and bring them up, the good ones ("you saved
Ashwick") and the embarrassing ones ("you got stuck up a tree for half the afternoon").
Blessings, curses, luck and fae favour change how you fight for a while.

## Names (`rpg/names.py`)

People's first names are invented by a model trained on four naming traditions
(Archaic, Westron, Northish, Southron; from `../fantasy_names.txt`). It learns
sound patterns, not pieces of names:

* letters are classed as vowels or consonants by context (`y` is a vowel unless
  it glides before one), and names are split into syllables by the maximal-onset rule
* per culture and gender it learns syllable counts; which consonants may begin a
  word, sit between vowels, or end a word, letter by letter and by position;
  which vowels form nuclei; and how gender is marked on the last syllable
* a name is built one letter at a time. Each letter depends on the one before,
  backed off to that letter's phonological class (stop, fricative, nasal,
  liquid, glide; front, back, low vowel), so new combinations appear
* every candidate must use only legal clusters for its position, sound typical
  for its culture, and be neither a listed name nor one letter away from one
* sound changes between the traditions are learned by aligning names that
  appear in several lists (Westron Adam ~ Southron Adamo; Westron c becomes
  Northish k 62% of the time). `NameGen().evolve(name, culture, gender)` gives
  any name another tradition's form, and `family()` makes a set of cognates

In the world, the north of the map names its people in the Northish way, the
south in the Southron way and the middle in the Westron way, and many elders
carry old Archaic names. The start screen's **Random name** button (or `?` in
the terminal version) invents one for you.

`python3 tools/name_analysis.py` prints the full linguistic analysis of the lists,
retrains the model (`rpg/data/names_model.json`), and checks the output: whether
it copies, and how its vowel share, endings and length compare with the real
names.

## You only know what you've found out

Menus, typed commands and suggestions all follow what your character has
actually learned. Strangers are "the spice-trader" or "the old headman" until
they tell you their name (the first time you talk). A merchant's goods can't be
examined, bought or sold to until you've looked over their wares (`trade`, which
also introduces you if you haven't met). The quest only completes once the elder
has told you about the relic. If you stumble on it first and carry it home, they
recognise it when you talk to them.

## Classes (`rpg/classes.py`)

| Class | Difficulty | Abilities | Passive |
|---|---|---|---|
| Knight | easy | Shield bash (may stun), Guard (halve the next two blows) | Armoured: +1 defence |
| Ranger | medium | Shoot (a ranged opener it can't answer), Track (read neighbouring tiles and intents) | Woodwise: rarely ambushed, rough ground is quicker |
| Wizard | hard | Firebolt (ignores armour), Ward (absorbs damage), Fear (forces a creature to flee) | Attuned: mana returns faster |
| Rogue | tricky | Backstab (triple damage on anything not yet fighting you), Vanish (escape and hide) | Light-fingered: better prices, more coin, wider crits |
| Cleric | easy | Heal, Smite (doubled vs undead), Turn undead | Blessed: better shrines, softer undead blows |

Abilities spend the class's stamina, mana or faith, which returns as you travel,
wait or rest. Type them (`firebolt wolf`, `cast ward`, `bash`) or use the class
menu in the action bar. Each class levels differently. In testing, the advisor
bot wins 72-100% of worlds depending on class. Saves from before classes load
as a classless Wanderer.

## Creatures have minds (`rpg/mind.py`)

Each creature holds five intents (**wander**, **stalk**, **hunt**, **hold**,
**flee**) with a support level that decays and is topped up by evidence: its
health and yours, how a fight would likely go, darkness, and its temperament.
Temperament comes from its body type (wolves are cunning, boars territorial, crows
skittish) and its individual trait (young, old, scarred). The strongest intent
governs, so creatures commit and then visibly change their minds instead of
flickering. Overwhelming evidence (near death, an easy kill) cuts straight
through, and each fight exchange reinforces or demotes the current intent.

What you'll see: guardians warn you before attacking; stalkers follow you
between tiles and strike when you're weak, it's dark, or you lie down to rest;
wounded animals break and run; hunters may chase you when you flee; cunning
ones circle looking for an opening, then hit hard. Changes of mind are narrated,
`examine` tells you what a creature intends, and the suggestions take it into
account. NPCs are deliberately left predictable.

## Measuring repetition

`python3 tools/variety.py [sessions] [steps] [worlds]` plays sessions with the
advisor and reports the phrases a player would see repeated most within one
playthrough, the grammar symbols that are used a lot but have too few options,
and how often each kind of world fact (trades, village centres, ruins, relics,
people's looks...) recurs across fresh worlds. Use it to decide where new
wording will do the most good.

## Keeping it consistent (`rpg/coherence.py`)

Facts are chosen to agree with each other: elders are old, white hair goes with
age, eel-catchers live near water, bronze tarnishes instead of rusting, flint
makes knives and axe-heads but not broadswords, wraiths are never "mangy", font
and bells only turn up in religious ruins. The narrator also re-rolls any
sentence that contradicts the moment: sunlight at night, stars through cloud, far
views in fog, snow in summer (except on high peaks), spring blossom in autumn.
`python3 tools/coherence.py [worlds]` generates text in every season, time and
weather and reports any contradictions it finds. Saves rebuild the grammar on
load, so wording fixes reach old games too.

## Where to add variety

| To add...                          | Edit                                   |
|------------------------------------|----------------------------------------|
| Landscape/weather/light phrasing   | `rpg/lexicon.py` → `RULES`             |
| Extra phrasing, transitions, dialogue memory lines | `rpg/lex_more.py` (`EXTEND` appends to existing symbols) |
| Variety pass: exits, weather, intro, trades, fact pools | `rpg/lex_variety.py` (`REPLACE`, `EXTEND`, `ECONOMY`, `FACT_POOLS`) |
| New landmark types                 | `rpg/lexicon.py` → `FEATURES`          |
| Creatures (body plans)             | `rpg/lex_entities.py` → `ARCHETYPES`   |
| People, dialogue, greetings        | `rpg/lex_entities.py` → `NPC_RULES` etc|
| Weapons, armour, item details      | `rpg/lex_entities.py` → `WEAPONS`, `ITEM_RULES` |
| Menu actions (web)                 | `rpg/actions.py` → `catalog()`         |
| Combat narration                   | `rpg/lex_entities.py` → `COMBAT_RULES` |
| Classes, abilities, balance        | `rpg/classes.py`; narration in `rpg/lex_classes.py` |
| Landmark kinds, how they look in each season/weather/hour | `rpg/lex_landmarks.py` (`NEW_FEATURES`, `TAG`, `_TAGS`, `_KINDS`) |
| Landmark secrets and what the verbs do | `rpg/secrets.py` (`DECK`, `HINTS`, one function per secret) |
| Road encounters                    | `rpg/encounters.py` (`DECK`, a start function and outcomes) |
| Village troubles, festivals        | `rpg/living.py` (`TROUBLES`, `FESTIVALS`) |
| Name traditions (retrain after editing the list) | `../fantasy_names.txt`, then `python3 tools/name_analysis.py` |
| Creature intent narration / temperaments | `rpg/lex_more.py` → `MIND`; `rpg/mind.py` → `TEMPER`, `TRAIT` |

## Goal

Talk to the elder in your starting village, recover the relic from a distant ruin
guarded by something old, and bring it home. Type `help` in game for commands.
