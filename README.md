# Wayfarer's Path

A text RPG, played in your browser or terminal, where every description is generated: landscapes, weather, light,
creatures, people, items, rumours and combat.

```
python3 play.py                     # opens the game in your browser (http://127.0.0.1:8765)
python3 play.py --port 9000         # ...on another port
python3 play.py --classic [seed]    # plain terminal version
python3 play.py --classic --load X  # resume a save in the terminal
```

### On a phone

Narrower than 760px, the page switches to a phone layout:
- **Tabs:** a bar along the bottom switches between Story, Map, Traveller, Journal and Pack. A dot
  marks a tab with something new (story text, a journal entry, an item), and red means trouble (a
  fight, or low health).
- **Status strip:** a strip under the place name always shows health, your class resource, coins
  and the time; tap it for the full Traveller page.
- **Menus:** action menus and the ☰ menu open as sheets from the bottom of the screen. The phone's
  Back button closes a sheet, or steps up one submenu, instead of leaving the game.
- **Suggestions:** ideas scroll sideways, and a pending choice is listed in full.
- **Map:** tap a neighbouring tile to walk there, or any tile to name it. On the painted map, pinch
  and drag, and tap a marker to see which errand it belongs to.
- **Reading:** "hide actions" tucks the controls away to leave more room for the story, and the ☰
  menu has a text-size setting. Both are remembered.
- **Keyboard:** it only opens when you tap the command box.
- **Home screen:** the page can be added to a home screen as an app (it has a web manifest and
  icon).

### Playing on GitHub Pages

The same game also runs with no server at all. `tools/build_static.py` copies the page into `site/`,
zips the `rpg/` package into `rpg.zip` and adds `static/py-worker.js`, which runs the Python game in
the browser with [Pyodide](https://pyodide.org) in a background worker. A small bridge
(`static/bridge.js`) answers the page's `api/...` requests from that worker instead of the network,
so the page itself is identical to the local one. Saves are written to an IndexedDB-backed folder,
so they stay in that browser on that device; `autosave` is refreshed after every turn outside a
fight, since closing the tab is how you quit. The first visit downloads about 10 MB of runtime, and
later visits load it from the browser cache.

`.github/workflows/pages.yml` builds and deploys this on every push to `main`. To turn it on, set
the repository's **Settings → Pages → Source** to **GitHub Actions**. To try the build locally:

```
python3 tools/build_static.py && python3 -m http.server -d site 8000   # then open http://127.0.0.1:8000
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
  always looks the same. It is repainted in the background (a worker,
  `rpg/web/atlas-worker.js`) whenever what you know changes, so it opens instantly
  and keeps up live if you leave it open while you play. The lettering is IM Fell English by Igino Marini, bundled in
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
which save the current game belongs to.

Saves are kept per character: `saves/<character>/<slot>.sav`, where the folder is the character's
name plus a short random tag, so two characters with the same name never share saves. The
start screen has a **Continue** card for each character, showing their name, their world's name,
level and class, and the date and time they began (handy for telling two Wrens apart). The Saves
manager groups saves the same way and can delete a whole character. Every character has their own
`autosave`, written as soon as the game begins and again when you quit (after every turn on the
GitHub Pages build). After death you can reload. Save names only need to be unique within one
character. A bare name in `load`/`rename`/`delete` means this character's save. To reach
another character's save, use `folder/name`; `saves` lists the folder names. Saves from before
folders are sorted into one folder per character automatically. They live in `saves/` (in the
browser's storage on the GitHub Pages build). They are Python pickles, so only load files you
made yourself.

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

**Everyone has a temperament** (nervous, suspicious, gruff, warm, cheerful, melancholy,
shrewd or dreamy), and a whole conversation keeps to it: how they look up as you come,
what they say first, how they ask your name and give theirs, how they ask for help and
how they thank you. A gruff man never asks "not unkindly".

**What they talk about** (`rpg/talk.py`, `rpg/lex_life.py`), in order of what matters
to them:
1. The errand they gave you. They ask after it ("Any sign of the plough-horse?") and
   nudge you about the step you're on ("Did you speak to Kaisesos in Uniobridge yet?").
2. Your errands. They tell you what they know of the people, places and beasts you
   need: who someone is and what they're like, how far a village is and whether a
   road goes there, where a beast was last seen.
3. Fresh news from elsewhere.
4. Their own life, put together from parts the way the descriptions are: their work
   this season (by trade: lambing, a frozen mill-race, the autumn eel run), then a word
   about a neighbour, the village's trouble or a festival, and a closing remark in
   their own temperament.
5. The old rumours: a beast seen somewhere, a ruin, a shrine.

Each topic is told once (their own life once a day), so going back brings something
new. One request per conversation: an elder giving you the main quest won't also ask a
favour in the same breath.

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
something, lead someone home, find a place. `journal` groups them by story. The
main quest comes first, then each story you've taken on, with who asked you, their
words, the steps you've done and the one you're on, with directions. Loose errands
follow, then what you've finished and how it ended ("You brought young Lisindra home
to Oryia."). The map outlines their goals.

**A living world** (`rpg/living.py`). Days pass and things happen. Villages develop
troubles, thirteen kinds of them (`rpg/troubles.py`): a beast at the folds, a fever,
someone lost in the wilds, a haunting, a stolen heirloom, a fouled well, strayed
livestock, a letter or parcel to carry to another village, supplies only a trader
sells, a wedding that wants a gift, a blight on the fields, a feud between neighbours
(take a side, or try to make peace, which takes a steady spirit), and work that needs
hands (harvest, lambing, haymaking or storm repairs, by season). Each is told with
several titles, openings, requests and endings. The next one leans away from the
kinds you've seen lately and toward ones you haven't. They ask for your help, and
troubles *wait for you*: they never fail or get worse while you're away. The season turns every 7 days
(you'll notice the morning it does), and every village keeps its festival (the Mayday garlanding, midsummer fires, harvest home,
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

### Place names (`rpg/places.py`)

Villages, towns and regions are named the way real places got their names: a
founder's name worn down plus an element meaning farm, stream or clearing (a
fresh name from the model, clipped: "Asa" becomes *Asby*), or a feature plus an
element (*Oakley*, *Stanbeck*). Some get a prefix or suffix (*Long Wendham*,
*Sloeworth-under-Edge*); market towns can be *Chipping* or *Market* something.
Endings follow the local tradition: -by, -thwaite, -garth in the north, -ton,
-ham, -ley in the middle, -combe, -leigh, -port in the south. Regions pair a
biome word (Weald, Moss, Fells, Hanger, Levels, Brae...) with a root, an
adjective (*the Gloaming Copse*), a place (*the Frith of Swinholm*) or a
possessive (*Yala's Fells*). Within a world no root, ending or adjective is used
twice. Across 40 test worlds, 1,504 of 1,523 names were distinct.

Each world also has a name of its own, worked out from the seed with separate dice, so it never
changes and older saves get one too. A clipped name takes a grand ending (*-oria*, *-mere*,
*-garde*, *-enmark*). It then stands alone, takes an epithet (*Valdoria, Land of Long Winters*,
*Datador, the Hollow Crown*), or sits in a title (*The Sundered Marches of Ostmere*). Across 2,000
seeds, 1,997 world names were distinct. It appears in the opening lines and on the save screens.

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

## Procedural stories (`rpg/plots.py`)

Besides the village troubles, almost anyone you talk to may ask for help with a
story the game assembles on the spot from five layers. The asking is one speech in
one voice: what's wrong, why it matters to them, where to start, and a closing in
their own temperament. Motives are matched to the kind of trouble (grief to a
keepsake or a grave, justice only to a theft) and to the speaker (only the young
fear their master, only the old are too old to keep a vow, the village head never
asks for the village head's leave).

| Layer | Count | Examples |
|-------|-------|----------|
| Motive | 36 | grief, debt, love, guilt, rivalry, a vow, an omen, a wager, a betrothal |
| Object | 24 | a lost child or runaway apprentice, a bolted horse or lost hawk, a beast or something dead, a stolen charter or keepsake, a fouled shrine, a neglected grave, news from another village |
| Obstacles (one to three) | 40 | tracks at a landmark, a sign that only shows by moonlight or in fog, a guardian beast, a witness in another village, a toll-keeper or fence to pay, persuade or lean on, someone who wants a whetstone or a herb first, an offering at a shrine |
| Twist (about half the time) | 32 | the beast is guarding young; the runaway doesn't want to come back; the heirloom is cursed, or a fake, or was never theirs; the asker lied; the news is bad and nobody has told them |
| Ending (your choice) | 20 | return it, spare it, let them stay, take it to its true owner, destroy it, keep it, sell it to a rival, tell the truth or a kinder story, expose what you found |

Every layer is filled from the world: real villagers in real villages, landmarks
and regions near the asker, creatures that live there, the season. The 40
obstacles are stories laid over a few things the game already does (search a
landmark, fight, talk to someone, pay or persuade them using your stats, bring
something, deliver something, go somewhere), and each step becomes an ordinary
journal errand, so the map, the advisor and saving all work. Recently used pieces
are avoided. In testing, 413 generated stories all ran to their end, and no two
had the same shape.

## Stats, schools and books (`rpg/arts.py`)

You have four stats, **might**, **grace**, **wits** and **spirit**. The game
keeps them as small numbers but only ever shows them in words ("powerful",
"light on your feet", "sensible, nearly quick-witted"). Every level brings a
point to spend (`improve wits`, or the Improve menu), and every third level
your calling raises its own stat. A stat above the ordinary starts to tell:
harder blows, a better dodge, stronger spells and prayers, a deeper well of
mana or faith.

There are five schools of learning, each with a stat, a home class and a named
trait that lets you read its books:

| School  | Stat   | Home   | Trait            | Books |
|---------|--------|--------|------------------|-------|
| Arcane  | wits   | Wizard | Arcane Letters   | spellbooks, grimoires, codices; scrolls |
| Divine  | spirit | Cleric | The Kindled Word | litanies, breviaries, psalters; prayer-rolls |
| Martial | might  | Knight | Drill-Learned    | war-manuals, treatises of arms, drill-books |
| Wild    | wits   | Ranger | Trailwise        | field almanacs, hunters' daybooks, herbals |
| Cant    | grace  | Rogue  | Cant-Reader      | cant-books, cutpurses' primers |

You start with your own school's trait. Raise another school's stat far enough
and you earn its trait too, so you can dual-class if you like. Your own school
goes to the fifth circle; anyone else's to the second. Each circle needs a
little more of the school's stat. Two classes lean towards a second school: a
Cleric can learn first-circle arcane spells from the start, and a Ranger needs
one point less grace than anyone else to read thieves' cant (and can go a
circle further in it).

`read` a book to study it. It takes a few hours, and teaches one art, settled
the first time someone who can read it looks inside. A book you can't read
says nothing useful about itself. Scrolls hold one spell or prayer, spent when
you read it aloud. Reading one beyond your circle may go wrong (frogs, blue
hair, a personal snowstorm). Books and scrolls turn up in ruins, on stalls
(often in a school you can read), and as rewards. `arts` lists everything you
know and every trait you have.

There are 35 arts, 7 per school, from first to fifth circle. The original class
abilities are the first rungs; the rest, like Frost Dart, Thunderclap, Sanctuary,
Miracle, Cleave, Bulwark, Snare, Beast-Speech, Envenom and Deathblow, are
data: a list of effects (damage, stun, weaken, expose, burning, flee, heal,
ward, guard, escape, buffs, cleansing, far sight, finishing blows) that one
function runs.

## Crafting your own arts (`rpg/crafts.py`)

Each craft works only within its own school; nothing mixes across schools.

- **Spellcraft** (`craft`, arcane): every spell you know teaches its parts.
  Firebolt gives *fire* and *bolt*, Ward gives *ward*, Fear gives *shadow*,
  Thunderclap *storm* and *burst*, Searing Lance *lance* and *lingering*, and so
  on. You combine an element (fire, frost, storm, stone, shadow) with a shape
  (bolt, burst, lance, ward, veil), and can add a twist (lingering, twin, quiet,
  great). The result is a new named spell, like "Lingering Frost Burst". It
  costs a pot of oak-gall ink and three hours. `craft` on its own lists
  everything you could make.
- **Prayer composing** (`compose`, divine): the same idea with a virtue (mercy,
  wrath, vigil, light, peace) and a form (word, litany, blessing), and can add a
  twist (lasting, humble, or twinned with a second virtue). It makes things like
  "Litany of Twinned Wrath and Light" or "Blessing of Lasting Vigil", and costs
  beeswax candles and two hours.
- **Technique honing** (`hone`, martial, wild and cant): using a technique in
  earnest counts as practice. After five uses you can hone it into one of two
  refinements, for example Shield Bash into *Ringing Bash* or *Shield Rush*,
  Backstab into *Assassin's Cut* or *Bleeding Cut*, or Shoot into *Long Shot*
  or *Pinning Shot*. With the school's stat high enough you can join two of its
  techniques into a combination (`combine feint deathblow`, giving "Feint into
  Deathblow").

Wizards start with a pot of ink and Clerics with candles. Chandlers, pedlars and
hedge-witches sell more. Crafted arts get a one-word command, live in your save,
and can be let go with `forget` (a honed technique goes back to plain).

## The size of the world, roads and travel (`rpg/world.py`, `rpg/travel.py`)

A world is a 24 by 24 map with about 500 squares of land. Home sits off-centre, so one
side of the world is a long way off: danger rises a step every six squares from home,
and the relic lies 20 to 25 steps away. (Worlds saved before the map grew keep their
16 by 16 size.)

**Roads.** Tracks join every village to the rest, with a short cut or two so the
network has loops. A road square says which way the road runs and where it goes
("A drove road runs through here, north to Kirkby and west toward Oswell"), and a
village says where its roads lead. Walking along a road takes about half the time
of open country, and fewer beasts lair beside one. Roads are drawn on both maps.

**Rations and fast travel.** Travel rations cost 5 coins each, up to 10 in your pack
(you start with 2). Only those with food to spare sell them: travelling merchants (pedlar,
trader, huckster and the like) and a miller or eel-catcher with a stall. Each has only a
few, restocked every few days, and your home village always has one such seller. Rations
also turn up as loot, in caches, strongboxes and abandoned camps.
`travel` lists the places you can go back to,
and `travel <place>` takes you to anywhere you have walked: a village, a ruin, a
shrine, a camp, or a landmark ("travel standing stone"). The way follows roads where
it can and country you know where it must. It costs a ration for each half-day of
walking, and the days really pass (nights are spent camping, and heal a little).
The road can still surprise you: a night's stop may bring a road encounter, and
something hunting the country you cross may stop you where it waits. You can't set
off with something stalking you, and if something waits at the place you named, you
stop a square short. Rations can be eaten in a pinch (`eat ration`).

## The main quest (`rpg/mainquest.py`, `rpg/mq_*.py`)

Each world rolls one kind of main quest from its seed. The elder tells it; the
journal, the status panel, the map markers, the suggestions, visions, wise strangers
and village gossip all follow whichever it is. (`RPG_QUEST=beast` forces a kind, for
testing.)

- **The relic** (`relic_tale.py`): recover what the village lost from a guarded ruin,
  and carry it home.
- **The beast** (`mq_beast.py`): something huge is killing. The elder names two people
  who have met it: one knows how to hurt it, one has seen where it lairs. It raids by
  night (the news reaches the villages, and the ground where it fed is marked), and
  near its lair its tracks point the way. Knowing its weakness makes the fight far
  easier (some weaknesses only hold by day). Bring something of it home as proof.
- **The blight** (`mq_blight.py`): a rot spreads from one place a little further every
  day, and the descriptions show it, always thickest toward its heart. Kill what feeds
  it, bless the ground (pray at any shrine for a blessing, or carry holy water), and go
  home.
- **The missing heir** (`mq_heir.py`): the elder's grandchild, ward or apprentice has
  gone. A trail of four places wanders across the map, and each one tells you the next.
  At the end they are held by something that must be killed, or living a life of their
  own, and you choose whether to plead, let them be, or insist.
- **The broken pact** (`mq_pact.py`): an old oath with the spirit of a high place has
  lapsed. Gather three gifts the songs name (water from a spring, a stone from a circle or
  cairn, a sprig of a great tree; one of them guarded), and bring them to the spirit's
  shrine by night. Renew the pact as it was, or bargain for better.
- **The beacons** (`mq_beacons.py`): the year has stuck. Light three beacons on three far
  hills (burn two rations' fat to get the old timber going, or spend hours gathering fuel
  and see what the fire draws), and go to where the sleeper wakes. It's winter, and stays
  winter however long you take, until the sleeper wakes and the spring comes in at once.
- **The feud** (`mq_feud.py`): two villages are heading for war. Hear each side, go to
  where it started and find out what really happened (sometimes it's still there, and
  hungry), then tell them the hard truth or a kinder story.
- **The bandit lord** (`mq_bandit.py`): a robber captain holds a fort on the roads. Win
  over three villages (one wants coin for spears, one wants proof you can fight, one just
  wants asking). The more who come with you, the weaker the captain's chained beast; with
  all three at the gate, the captain yields without a fight.

Quests with a clock (the blight, the heir) say how long you have, and warn you when it
runs short. Running late doesn't lose the game: the blight reaches home and its people
flee, or the heir's trail goes cold and you find only a letter, and the ending, when it
comes, is a sadder one. Each kind has several origins, tellings and endings.

A new kind is a class with `@register` (see the docstring in `mainquest.py` for the
methods it can fill in); the rest of the game asks the quest rather than assuming a
relic. Saves from before quest kinds load as relic quests.

## Villages, traders and goods (`rpg/goods.py`)

Each world has about a dozen settlements: your home village, two **market towns**
(three traders and a few craftsfolk each), and a mix of villages and **hamlets**.
No two people in a settlement share a job.

Traders sell what their trade suggests. A smith has blades, mail and whetstones;
a fletcher fire and bodkin arrows; a hedge-witch or wise-woman herbs, draughts
and charms; a chandler scrolls, books and holy water; a spice-trader draughts
and antidotes; a tinker lockpicks and whetstones; a pedlar or packman a bit of
everything. Craftsfolk keep a small stall once you've been introduced
(`trade <name>`). With several sellers in one place, `trade` names them all, and
`buy` finds the item on any stall you've already looked at. Stalls restock every
few days, and the season shows: herbs in summer, padded coats and draughts in
winter.

None of it is only for sale. Anything a stall sells can also be found: a whetstone in a
hidden cache, a witch-stone in a smuggler's hole, candles and ink in a ruin, a spellbook
in a strongbox.

Things you can use (`use <item>`):

| Item | What it does |
|------|--------------|
| whetstone | a fresh edge: harder blows for half a day (three uses) |
| set of lockpicks | open a strongbox in a ruin or abandoned camp; picks snap in clumsy hands |
| quiver of fire / bodkin arrows | your next three shots burn, or go through armour |
| flask of holy water | thrown in a fight; three times as harsh on the dead |
| smoke pot | vanish from a fight |
| draughts of strength, warding, fortune, clarity; antidote | half a day of harder blows or better guard, a day of luck, a full well of power, a cure |
| rowan cross, hare's-foot charm, witch-stone | a couple of days of warding or luck, or a day of fae favour |

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

`python3 tools/repeats.py [worlds] [turns] [memory]` measures repetition *across* worlds, which is what a
player starting a second run notices. It plays each world with the advisor and reports:
- **Overlap between runs:** the share of one run's sentences that also appear in another, with names masked so
  templates line up.
- **Widespread lines:** sentences and 5-word phrases found in many worlds.
- **Frames:** how much of a run opens the same few ways, and the most common opening when examining, climbing
  and searching landmarks.
- **Returning player** (with `memory`): how much of each later run had already appeared in earlier runs.

The first measurement found 76 sentences in half or more of all worlds, and the elder's relic speech in 27 of
30. After the work described below, 6 sentences reach half the worlds, and runs share 5% of their sentences
instead of 8%.

### Looking at landmarks (`rpg/lex_looks.py`)

Examining, climbing and searching used to give every landmark the same few frames: four for examining, all with
the same three beats; one view from the top; a few ways to search. Now:
- **Examining:** each family of landmark (stone, tree, water, earthwork, building...) has its own textures, and
  each kind (a menhir, a gibbet, a barrow, a chalk figure...) its own things to notice. Twenty frames vary in
  length, order and what leads: a detail, a texture, the weather, or your own movement. A second look moves on
  to something not yet said.
- **Climbing:** how you get up depends on what it is. What you see depends on the weather, the hour, the
  height, and what is really on the map:
  - fog hides the view, but you might hear a village;
  - at night a village shows as lamplit windows;
  - tall landmarks show further;
  - an errand's destination, if in sight, is pointed out.
- **Searching:** finds are put together from small lists and told in ten shapes. Hidden caches have their own.

### The elder's tale (`rpg/relic_tale.py`)

The relic quest is a story built per world, not one speech with the names swapped. It is assembled from what
the relic meant, how it was lost (stolen, pawned for a debt, carried off by a keeper who vanished, given as a
pledge, buried with the dead, sent away as cursed, lost in a burning, sold), when, what has gone wrong since,
and what the village offers. The elder tells it in one of five shapes. 300 worlds give 300 different speeches.

### Wider lines, temperaments and phrase memory

- **Terrain changes** (`rpg/lex_wide.py`) join a way of leaving one land type to a way of entering the next,
  about fifty combinations per pair.
- **Location lines:** surroundings, onward travel and openings have lines for each land type. Openings are also
  assembled from parts (`rpg/lex_compose.py`).
- **Weather, mood, conversation and village lines** are wider too (`rpg/lex_talk_more.py`).
- **Creature temperaments** (`rpg/lex_temper.py`): every species in every world is brazen, furtive, eerie,
  sullen, skittish or cunning. A wraith that drifts eerily in one world may swagger in the next.
- **Phrase memory** (`rpg/phrasebook.py`): the narrator also remembers, across all your runs, the phrases you've
  read, stored as about 400 KB of hashes beside your saves. Candidate sentences that echo an earlier run score
  slightly worse. It changes only how things are told. Set `RPG_PHRASEBOOK=0` to turn it off.

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
| Stats, schools, learnable arts, books and scrolls | `rpg/arts.py` (`SCHOOLS`, `ARTS`, `STAT_WORDS`) |
| What traders sell, tools, draughts and charms | `rpg/goods.py` (`TRADES`, `GOODS`, `SEASON_WEIGHT`) |
| Spellcraft parts, prayer parts, technique refinements | `rpg/crafts.py` (`WEAVES`, `HONES`) |
| Landmark kinds, how they look in each season/weather/hour | `rpg/lex_landmarks.py` (`NEW_FEATURES`, `TAG`, `_TAGS`, `_KINDS`) |
| Landmark secrets and what the verbs do | `rpg/secrets.py` (`DECK`, `HINTS`, one function per secret) |
| Road encounters                    | `rpg/encounters.py` (`DECK`, a start function and outcomes) |
| Village troubles                   | `rpg/troubles.py` (`KINDS`, `TITLES`, `ASKS`, variant lists) |
| Procedural stories                 | `rpg/plots.py` (`MOTIVES`, `OBJECT_TAGS`, `OBJECTS`, `OBSTACLES`, `TWISTS`, `ENDINGS`, `OUTCOME`) |
| What people talk about             | `rpg/lex_life.py` (`WORK`, `JOB_SEASON`, `NEIGHBOUR`, `TAIL`, `CHECKIN`, `STEP_NUDGE`), `rpg/talk.py` |
| Names and introductions by temperament | `rpg/lex_talk.py` (`ASK_NAME`, `NPC_INTRO`, `THANKS`) |
| Festivals                          | `rpg/living.py` (`FESTIVALS`) |
| How many of each landmark secret a world holds; the dead travellers | `rpg/secrets.py` (`CAP`, `TRAVELLERS`) |
| Name traditions (retrain after editing the list) | `../fantasy_names.txt`, then `python3 tools/name_analysis.py` |
| Creature intent narration / temperaments | `rpg/lex_more.py` → `MIND`; `rpg/mind.py` → `TEMPER`, `TRAIT` |

## Goal

Talk to the elder in your starting village, recover the relic from a distant ruin
guarded by something old, and bring it home. Type `help` in game for commands.
