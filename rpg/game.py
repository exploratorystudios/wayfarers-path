"""Game loop, parser, combat and player state."""
import json
import os
import pickle
import random
import shutil
import sys
import time
from pathlib import Path

from .world import World, DIRS
from .describe import Narrator
from .textgen import wrap, cap, article, title, plural, join_speech, one_voice
from . import travel as TR
from . import mind
from . import classes as K
from . import story as S
from . import secrets as SEC
from . import living as LV
from . import encounters as ENC
from . import arts as ARTS
from . import goods as GOODS
from . import crafts as CR
from . import lex_compose as COMPOSE
from . import ui

ALIASES = {"n": "north", "s": "south", "e": "east", "w": "west", "l": "look", "x": "examine",
           "i": "inventory", "inv": "inventory", "get": "take", "grab": "take",
           "fight": "attack", "kill": "attack", "hit": "attack", "eat": "use", "quaff": "use",
           "chew": "use", "wield": "equip", "wear": "equip", "speak": "talk", "ask": "talk",
           "pray": "pray", "sleep": "rest", "camp": "rest", "run": "flee", "q": "quit",
           "inspect": "examine", "check": "examine", "stats": "status", "char": "status",
           "shop": "trade", "list": "trade", "purchase": "buy", "z": "wait", "m": "map", "h": "help", "?": "help",
           "restore": "load", "erase": "delete", "offer": "give", "hand": "give",
           "dig": "search", "rummage": "search", "explore": "search", "scale": "climb", "gather": "forage", "pick": "forage",
           "ring": "touch", "feel": "touch", "hear": "listen", "j": "journal", "quests": "journal", "log": "journal", "history": "chronicle",
           "bathe": "drink", "swim": "drink", "decipher": "read", "study": "read", "learn": "read",
           "train": "improve", "grow": "improve", "spend": "improve", "skills": "arts", "spells": "arts", "prayers": "arts",
           "feats": "arts", "tricks": "arts", "abilities": "arts", "traits": "arts",
           "spellcraft": "craft", "weave": "craft", "pray-write": "compose", "drill": "hone", "practise": "hone", "practice": "hone",
           "unlearn": "forget", "journey": "travel", "ft": "travel", "voyage": "travel"}
LINGER = {"wait", "take", "drop", "use", "equip", "pray", "search", "climb", "drink", "touch", "forage", "read", "listen"}   # commands that give nearby creatures time to act
STOP = {"the", "a", "an", "at", "to", "with", "on", "up", "my", "some", "of"}

SAVE_DIR = Path(os.environ.get("RPG_SAVE_DIR") or Path(__file__).resolve().parent.parent / "saves")   # tests point this elsewhere
SAVE_VERSION = 2

HELP = """Commands:
  look (l)              describe your surroundings anew
  north/south/east/west (n/s/e/w), or go <dir>
  examine (x) <thing>   look closely at a feature, creature, person, item, or 'sky'/'me'
  take <item> / drop <item> / inventory (i)
  equip <item> / use <item>  (eat, drink)
  attack <creature> / flee
  talk <person> / give <item> to <person> / trade / buy <item> / sell <item>
  pray (at a shrine) / rest / wait / map / status
  travel [place]        fast travel to anywhere you've been; costs rations (buy them from merchants, millers, eel-catchers)
  search / climb / drink / touch / read / listen / forage <landmark>   (landmarks keep secrets)
  give <item> to <landmark>  (an offering) / journal (j) / chronicle / 1, 2, 3... to answer a choice
  arts / improve <stat> / read <book or scroll> / craft / compose / hone / forget
  save [slot] / load [slot] / saves / rename [a] [b] / delete [slot] / hints [on|off] / help / quit (autosaves)"""


class Player:
    def __init__(self, name, klass=None):
        self.name = name
        self.klass = klass if klass in K.CLASSES else None
        s = K.CLASSES.get(self.klass)
        self.hp = self.maxhp = s["hp"] if s else 30
        self.base_atk, self.base_df = (s["atk"], s["df"]) if s else (2, 0)
        self.res = self.res_max = s["res_max"] if s else 0
        self.guard = self.ward = self.hidden = 0      # Knight's guard, Wizard's ward, Rogue's hiding
        self.level, self.xp, self.gold = 1, 0, 15
        self.inv, self.weapon, self.armour = [], None, None
        ARTS.ensure(self)
        if self.res_max:
            self.res = self.res_max = self.res_max + ARTS.bonus(self, "spirit")

    @property
    def class_name(self):
        s = K.spec(self)
        return s["name"] if s else "Wanderer"

    @property
    def atk(self):
        return self.base_atk + (self.weapon.dmg if self.weapon else 1) + getattr(self, "bonus_atk", 0) + ARTS.bonus(self, "might") // 2

    @property
    def df(self):
        armoured = 1 if getattr(self, "klass", None) == "knight" else 0
        return max(0, self.base_df + armoured + (self.armour.df if self.armour else 0) + getattr(self, "bonus_df", 0) + ARTS.bonus(self, "grace") // 2)

    def gain_xp(self, n):
        self.xp += n
        msgs = []
        while self.xp >= self.level * 30:
            self.xp -= self.level * 30
            self.level += 1
            s = K.spec(self) or dict(hp_gain=6, atk_every=1, df_every=2, res_gain=0)
            self.maxhp += s["hp_gain"]
            self.hp = self.maxhp
            if self.level % s["atk_every"] == 0:
                self.base_atk += 1
            if self.level % s["df_every"] == 0:
                self.base_df += 1
            self.res_max = getattr(self, "res_max", 0) + s["res_gain"]
            self.res = self.res_max
            msgs.append(f"** You feel yourself grow harder and surer. You are now a level {self.level} {self.class_name.lower()}. **")
            msgs += ARTS.on_level(self, self.level)
        return msgs


class Game:
    def __init__(self, seed=None, name=None, out=print, klass=None):
        self.seed = seed if seed is not None else random.randrange(10 ** 9)
        self.world = World(self.seed, name or "")
        self.narr = Narrator(self.world)
        self.rng = random.Random(self.seed + 1)
        self.player = Player(name or "Wanderer", klass)
        self.player.rations = TR.START_RATIONS
        self.pos = self.world.start
        self.combat = None
        self.over = False
        self.won = False
        self.has_quest = False
        self.deeds = []          # notable things the player has done; news spreads to NPCs
        self.turns = 0           # commands entered (the advisor eases off as this grows)
        self.examined = set()    # (pos, noun) pairs already looked at
        self.last_save_turn = 0
        self.show_hints = True
        self.run_id, self.started = self.new_run_id(self.player.name), time.time()   # this character's save folder
        self.quests, self.companions, self.pending, self.quest_seq = [], [], None, 0
        self.buffs, self.encounters_seen, self.last_encounter_turn = {}, set(), -99
        self.died = False
        self.out = out
        self.width = min(90, shutil.get_terminal_size((80, 24)).columns - 2)
        p = self.player
        s = K.spec(p)
        wtype = self.rng.choice(s["weapon"]) if s else None
        p.weapon = self.world.make_item(1, "weapon", wtype=wtype)
        while p.weapon.dmg > 4 or p.weapon.dmg < 2:
            p.weapon = self.world.make_item(1, "weapon", wtype=wtype)
        p.inv = [p.weapon, self.world.make_item(1, "food"), self.world.make_item(1, "herb")]
        if s and s["armour"]:
            p.armour = self.world.make_item(1, "armour", akind=s["armour"])
            p.inv.insert(1, p.armour)
        kit = {"wizard": "pot of oak-gall ink", "cleric": "bundle of beeswax candles"}.get(p.klass)
        if kit:              # enough for a first try at your own craft
            p.inv.append(GOODS.make(self.world, kit, 1))
        S.ensure(self)

    # ------------------------------------------------------------ output
    def emit(self, text=""):
        held = self.__dict__.get("_held")
        if held is not None:
            held.append(text)
        else:
            self.out(wrap(text, self.width))

    def one_speaker(self, fn, *args):
        """Run fn, and print what it says as one person speaking: quotes that follow straight on from
        each other, in a paragraph or across two, become a single speech."""
        self._held = held = []
        try:
            result = fn(*args)
        finally:
            self._held = None
        merged = []
        for line in held:
            line = one_voice(line)
            if merged and merged[-1].rstrip().endswith('"') and line.lstrip().startswith('"'):
                merged[-1] = join_speech(merged[-1], line)
            else:
                merged.append(line)
        for line in merged:
            self.emit(line)
        return result

    def status_line(self):
        w, p = self.world, self.player
        tod = {"deepnight": "deep night"}.get(w.time_of_day, w.time_of_day)
        s = K.spec(p)
        res = f" · {s['res'].capitalize()} {p.res}/{p.res_max}" if s else ""
        return f"[Day {w.day}, {tod}, {w.season} · {w.weather} · HP {p.hp}/{p.maxhp}{res}]"

    def show_location(self, brief=False, came_from=None, direction=None):
        t = self.world.tiles[self.pos]
        self.emit("")
        self.emit(f"── {self.narr.header(self.pos)} ──")
        self.emit(self.status_line())
        for para in self.narr.location(self.pos, brief=brief, came_from=came_from, direction=direction):
            self.emit("")
            self.emit(para)
        t.visited = True

    # ------------------------------------------------------------ intro
    def intro(self):
        w, n = self.world, self.narr
        v = w.tiles[w.start].site
        elder = w.tiles[w.start].npcs[0]
        s = K.spec(self.player)
        past = n.pick(s["past"] if s else ["a soldier who walked away from a lost war", "a scribe who read one forbidden page too many",
                                           "a poacher with a price on your head", "a mercenary between contracts"])
        p = self.player
        kit = " and ".join(article(i.name) for i in (p.weapon, p.armour) if i)
        sc = [w.weather, w.time_of_day, w.season]
        arrival = n.frag("{intro_arrival}", dict(village=v["name"]), sc)
        opening = n.say("{intro_frame}", dict(name=p.name, past=past, arrival=arrival), sc)
        extra = [n.frag("{intro_motive}", None, sc), n.frag("{intro_kit}", dict(kit=kit), sc)]
        n.rng.shuffle(extra)
        self.emit(" ".join([opening] + [cap(x) for x in extra if x.strip()]))
        if s:
            abil = ", ".join(f"{K.ABILITIES[a]['label']} ({a})" for a in s["abilities"])
            self.emit(f"({s['name']}: {abil}. {s['passive'][0]}: {s['passive'][1]})")
        self.emit("")
        realm = self.world.title
        realm = "t" + realm[1:] if realm.startswith("The ") else realm
        self.emit(f"(This world is {realm}. Its seed is {self.seed}: the same seed gives the same world, but never the same words.)")
        self.show_location()
        self.emit("")
        pr = elder.pronouns()
        self.emit(self.narr.pick(COMPOSE.ELDER_HINT, "elderhint").format(who=cap(elder.called()), him=pr["him"], he=pr["he"], he_cap=cap(pr["he"])))

    # ------------------------------------------------------------ parsing
    def find(self, words, pools):
        words = [x for w in words for x in w.replace("-", " ").split() if x not in STOP]
        if not words:
            return None
        objs = [o for pool in pools for o in pool]
        typed = " ".join(words)
        for obj in objs:   # an exact full name always wins
            name = getattr(obj, "name", None) or getattr(obj, "noun", "")
            if getattr(obj, "known", True) is False:
                name = obj.job
            if name.lower().replace("-", " ") == typed:
                return obj
        best, score = None, 0
        for obj in objs:
            kw = obj.keywords
            sc = sum(1 for x in words if x in kw or any(k.startswith(x) for k in kw if len(x) >= 3))
            if sc > score:
                best, score = obj, sc
        return best

    def handle(self, line):
        self._handle(line)
        TR.fold(self)

    def _handle(self, line):
        words = line.lower().replace(",", " ").split()
        if not words:
            return
        S.ensure(self)
        self.apply_buffs()
        self.turns = getattr(self, "turns", 0) + 1
        if not hasattr(self, "recent_cmds"):
            self.recent_cmds = []
        self.recent_cmds = (self.recent_cmds + [line.strip().lower()])[-10:]
        if getattr(self.player, "hidden", 0) > 0:
            self.player.hidden -= 1
        verb, rest = ALIASES.get(words[0], words[0]), words[1:]
        if verb == "go" and rest:
            verb, rest = ALIASES.get(rest[0], rest[0]), rest[1:]
        if verb == "cast" and rest:
            verb, rest = rest[0], rest[1:]
            if verb == "at" and rest:
                verb, rest = rest[0], rest[1:]
        if S.intercept(self, verb, words):
            self.apply_buffs()
            return
        if verb.isdigit() or verb == "choose":
            return self.emit("There's nothing to choose right now.")
        if verb in DIRS:
            return self.move(verb)
        if verb in K.ABILITIES:
            K.use(self, verb, [x for x in rest if x not in ("at", "on")])
            return
        fn = getattr(self, "cmd_" + verb, None)
        if fn is None:
            msg = self.narr.say("{sys_unknown}")
            self.emit(msg.replace(" (Type 'help' for commands.).", "").replace(" (Type 'help' for commands.)", "") if ui.web else msg)
            return
        fn(rest)
        if verb in LINGER and not self.combat and not self.over:
            self.creatures_react(arrived=False)

    # ------------------------------------------------------------ time
    def apply_buffs(self):
        """Blessings, curses and luck show up in attack and defence."""
        p, b = self.player, lambda k: S.buff(self, k)
        p.bonus_atk = b("blessed") + b("strong") + b("fae") + b("honed") - b("cursed")
        p.bonus_df = b("warded") + b("fae") - b("soaked")

    def hush(self):
        """While an event is being told, let time pass without interrupting to describe the sky."""
        import contextlib
        g = self

        @contextlib.contextmanager
        def quiet():
            g._hushed = getattr(g, "_hushed", 0) + 1
            try:
                yield
            finally:
                g._hushed -= 1
        return quiet()

    def pass_time(self, minutes):
        before = self.world.time_of_day, self.world.weather
        self.world.advance(minutes, self.rng)
        w = self.world
        if not hasattr(w, "last_tick_day"):
            w.last_tick_day = w.day
        while w.last_tick_day < w.day:
            w.last_tick_day += 1
            LV.new_day(self)
            w.quest.on_new_day(self)
        S.tick_buffs(self)
        self.apply_buffs()
        after = self.world.time_of_day, self.world.weather
        if after != before and not getattr(self, "_hushed", 0):
            t = self.world.tiles[self.pos]
            sc = self.narr.scopes(t.biome, t.mood)
            if after[1] != before[1]:
                self.emit(self.narr.say("{weather_line}", scopes=sc))
            elif after[0] != before[0]:
                self.emit(self.narr.say("{light_line}", scopes=sc))

    # ------------------------------------------------------------ movement
    def move(self, d):
        w = self.world
        dx, dy = DIRS[d]
        dest = (self.pos[0] + dx, self.pos[1] + dy)
        fled, self._fled_from = getattr(self, "_fled_from", None), None
        if self.combat:
            fled = self.combat
            if not self.try_flee():
                return
        if dest not in w.tiles:
            self.emit(self.narr.pick(["The land beyond grows wild and trackless; you would only lose yourself there.",
                                      "There is no path that way that you could follow.", "You can go no further in that direction."]))
            return
        if dest not in w.land:
            sc = self.narr.scopes("lake")
            self.emit(self.narr.say("{glimpse.cap} stops you; there is no way across.", scopes=sc))
            return
        came_from, self.pos = self.pos, dest
        if not hasattr(self, "trail"):
            self.trail = [came_from]
        self.trail.append(dest)          # the road you have walked, for the map
        if len(self.trail) > 2000:
            self.trail = self.trail[-2000:]
        if w.road_between(came_from, dest):          # the road is quicker, whatever the country
            self.pass_time(self.rng.randint(15, 25))
        else:
            rough = w.tiles[dest].biome in ("marsh", "peaks") and self.klass() != "ranger"
            self.pass_time(self.rng.randint(25, 45) + (20 if rough else 0))
        self.regen(1)
        t = w.tiles[dest]
        for c in t.creatures:          # minds update first, so the description shows what they intend
            mind.update(c, self.player, w)
        self.show_location(brief=t.visited, came_from=came_from, direction=d)
        self.creatures_follow(came_from, fled)
        self.creatures_react(arrived=True, updated=True)
        self.check_win()
        if not self.over:
            S.on_arrive(self)
            ENC.maybe(self)

    def klass(self):
        return getattr(self.player, "klass", None)

    def regen(self, n):
        p = self.player
        if K.spec(p):
            p.res = min(p.res_max, p.res + n + (1 if self.klass() == "wizard" else 0))

    # ------------------------------------------------------------ creature minds
    def is_village(self, q):
        s = self.world.tiles[q].site
        return bool(s and s["kind"] == "village")

    def escape_routes(self, pos):
        return [(d, q) for d, q in self.world.neighbours(pos)
                if q in self.world.land and not self.is_village(q) and q != self.world.quest_pos]

    def relocate(self, c, frm, to):
        if c not in self.world.tiles[frm].creatures:      # it has already moved (or been moved by magic)
            frm = next((p for p, t in self.world.tiles.items() if c in t.creatures), None)
            if frm is None:
                return
        self.world.tiles[frm].creatures.remove(c)
        self.world.tiles[to].creatures.append(c)

    def creatures_follow(self, came_from, fled):
        """Stalkers and hunters may follow you; a hunter you fled from may give chase."""
        src = self.world.tiles[came_from]
        for c in list(src.creatures):
            if c.boss:
                continue
            it = mind.intent(c)
            chance = {"stalk": 0.75, "hunt": 0.5}.get(it, 0.0)
            if c is fled:
                chance = {"hunt": 0.4, "stalk": 0.3}.get(it, 0.0)
            if not chance or self.rng.random() >= chance:
                continue
            if self.is_village(self.pos):
                self.emit(self.narr.mind_line("follow_stop_village", c))
                continue
            self.relocate(c, came_from, self.pos)
            if c is fled and it == "hunt" and not self.combat:
                self.emit(self.narr.mind_line("chase", c))
                self.combat = c
                self.enemy_turn(committed=True)
                return
            self.emit(self.narr.mind_line("follow", c))
            same = [o for o in self.world.tiles[self.pos].creatures if o is not c and o.species is c.species]
            if same:
                names = plural(c.species["name"])
                self.emit(f"Now there are two {names}: the one that lives here, and the one that followed you." if len(same) == 1
                          else f"Now there are several {names} here, and one of them followed you.")

    def creatures_react(self, arrived=False, updated=False):
        """Creatures on your tile act on their intents. `arrived`: you just walked in."""
        if self.combat or self.over:
            return
        w, p = self.world, self.player
        t = w.tiles[self.pos]
        wary = 0.5 if self.klass() == "ranger" else 1.0       # Woodwise: hard to ambush
        for c in list(t.creatures):
            if updated:
                new, old = mind.intent(c), mind.intent(c)
            else:
                old, new = mind.update(c, p, w)
            m = c.mind
            if getattr(p, "hidden", 0) > 0 and new in ("hunt", "hold", "stalk") and not c.boss:
                if self.rng.random() < 0.4:
                    self.emit(self.narr.mind_line("ab_hidden_safe", c))
                continue
            if new == "flee":
                routes = self.escape_routes(self.pos)
                if routes and self.rng.random() < 0.8:
                    d, q = self.rng.choice(routes)
                    self.relocate(c, self.pos, q)
                    self.emit(self.narr.mind_line("slip_away", c, dir=d))
                    continue
            elif new == "hunt":
                chance = 0.9 if not arrived else (0.85 if c.boss else (0.75 if w.is_dark else 0.6) * wary)
                if self.rng.random() < chance:
                    self.emit("")
                    self.emit(self.narr.aggro(c))
                    self.combat = c
                    self.enemy_turn()
                    return
            elif new == "hold":
                if not m["warned"]:
                    m["warned"] = True
                    self.emit(self.narr.mind_line("warn", c))
                elif not arrived:
                    self.emit(self.narr.mind_line("warn_ignored", c))
                    self.combat = c
                    self.enemy_turn()
                    return
                continue
            elif new == "stalk":
                weak = p.hp / p.maxhp < 0.5 or w.is_dark
                if not arrived and weak and self.rng.random() < 0.5 * wary:
                    self.emit(self.narr.mind_line("ambush", c))
                    self.combat = c
                    self.enemy_turn(bonus=4, committed=True)
                    return
            if old != new and not arrived:
                self.emit(self.narr.mind_line(f"shift_{new}", c))

    # ------------------------------------------------------------ looking
    def cmd_look(self, rest):
        if rest:
            return self.cmd_examine(rest)
        self.show_location()

    def cmd_examine(self, rest):
        t, n = self.world.tiles[self.pos], self.narr
        if not rest:
            return self.emit("Examine what?")
        if rest[0] in ("sky", "weather", "clouds", "moon", "stars", "sun"):
            return self.emit(n.sky(self.pos))
        if rest[0] in ("me", "self", "myself"):
            return self.cmd_status([])
        m = self.merchant()
        stock = m.stock if m and m.mem.get("wares_seen") else []
        place_words = {"village", "town", "hamlet", "ruin", "ruins", "shrine", "camp", "here", "place"}
        if t.site and len(rest) == 1 and rest[0] in place_words | {t.site.get("name", "").lower()}:
            return self.emit(" ".join(n.site_lines(t.site)))       # "examine village" means the place, not the village elder
        obj = self.find(rest, [t.creatures, t.npcs, t.items, self.player.inv, t.features, stock])
        if obj is None:
            if t.site and any(w in (t.site.get("kind"), t.site.get("purpose"), t.site.get("form"), "village", "ruin", "shrine", "camp") for w in rest):
                return self.emit(" ".join(n.site_lines(t.site)))
            return self.emit(n.say("{sys_see_nothing}"))
        kind = type(obj).__name__
        if kind == "Feature":
            if not hasattr(self, "examined"):
                self.examined = set()
            self.examined.add((self.pos, obj.noun))
        if kind == "Creature":
            self.emit(n.creature_full(obj))
        elif kind == "NPC":
            self.emit(n.npc_full(obj))
        elif kind == "Item":
            self.emit(TR.describe(obj) if obj.kind == "ration" else ARTS.describe(self, obj) if ARTS.readable(obj) else
                      GOODS.describe(obj) if GOODS.describable(obj) else n.item_full(obj))
        else:
            self.emit(n.feature_full(obj, t.biome))

    def cmd_map(self, rest):
        w = self.world
        sym = {"forest": "♣", "marsh": "~", "plains": ".", "hills": "n", "peaks": "^", "lake": "≈"}
        lines = []
        for y in range(w.H):
            row = ""
            for x in range(w.W):
                t = w.tiles[(x, y)]
                seen = t.visited or any(w.tiles.get((x + dx, y + dy)) and w.tiles[(x + dx, y + dy)].visited
                                        for dx, dy in DIRS.values())
                if (x, y) == self.pos:
                    ch = "@"
                elif not seen:
                    ch = " "
                elif t.site and t.visited:
                    ch = {"village": "V", "ruin": "R", "shrine": "+", "camp": "c"}[t.site["kind"]]
                else:
                    ch = sym[t.biome]
                row += ch + " "
            lines.append(row.rstrip())
        self.out("\n".join(lines))
        self.out("@ you  V village  R ruin  + shrine  c camp  ♣ forest  . open land  ~ marsh  n hills  ^ peaks  ≈ water")

    def cmd_status(self, rest):
        p = self.player
        self.emit(f"{p.name}, level {p.level} ({p.xp}/{p.level * 30} xp). Health {p.hp}/{p.maxhp}. "
                  f"Attack {p.atk}, defence {p.df}. {p.gold} coins, {TR.rations(self)} travel rations.")
        self.emit(f"Wielding: {p.weapon.name if p.weapon else 'nothing'}. Wearing: {p.armour.name if p.armour else 'ordinary clothes'}.")
        self.emit(ARTS.describe_stats(self))
        s = K.spec(p)
        if s:
            abil = ", ".join((f"{K.ABILITIES[a]['label']} ({K.ABILITIES[a]['cost']} {s['res']})" if ui.web else f"{K.ABILITIES[a]['label']} ({a}, {K.ABILITIES[a]['cost']})") for a in K.known(p))
            self.emit(f"{s['name']} - {s['res']} {p.res}/{p.res_max}. Arts: {abil}.")
            self.emit("Traits: " + "; ".join(f"{a} ({b})" for a, b in ARTS.traits(p)))
            if p.points:
                self.emit(f"(You have {p.points} point{'s' if p.points > 1 else ''} to spend: " + (f"{ui.ref('improve')}" if ui.web else "'improve' might, grace, wits or spirit.") + ")")
            extra = [f"guarding ({p.guard} blows)" if getattr(p, "guard", 0) else "", f"warded ({p.ward})" if getattr(p, "ward", 0) else "",
                     "hidden" if getattr(p, "hidden", 0) else ""]
            if any(extra):
                self.emit("Currently: " + ", ".join(e for e in extra if e) + ".")
        fx = S.effects_line(self)
        if fx:
            self.emit(f"You are under {fx}.")
        hp = p.hp / p.maxhp
        self.emit(self.narr.pick(["You feel strong and whole.", "You are in fine fettle."] if hp > 0.8 else
                                 ["You ache, but you can manage.", "Bruises and cuts, nothing worse."] if hp > 0.45 else
                                 ["You are badly hurt; every step costs you.", "Blood soaks your clothes. You need rest."]))

    # ------------------------------------------------------------ items
    def cmd_inventory(self, rest):
        p = self.player
        if not p.inv:
            return self.emit(f"You carry nothing but {p.gold} coins.")
        lines = []
        for it in p.inv:
            tag = " (wielded)" if it is p.weapon else " (worn)" if it is p.armour else ""
            lines.append(f"  {article(it.name)}{tag}")
        self.out("You are carrying:\n" + "\n".join(lines) + f"\n  {p.gold} coins")

    def cmd_take(self, rest):
        t = self.world.tiles[self.pos]
        if rest and rest[0] == "all":
            items = list(t.items)
        else:
            it = self.find(rest, [t.items])
            items = [it] if it else []
        if not items:
            return self.emit(self.narr.say("{sys_no_take}"))
        if self.combat:
            return self.emit("Not while something is trying to kill you!")
        for it in items:
            t.items.remove(it)
            self.player.inv.append(it)
            self.emit(self.narr.pick([f"You pick up the {it.name}.", f"You take the {it.name}.", f"The {it.name} goes into your pack."]))
            self.world.quest.on_take(self, it)

    def cmd_drop(self, rest):
        it = self.find(rest, [self.player.inv])
        if not it:
            return self.emit(self.narr.say("{sys_no_have}"))
        p = self.player
        p.inv.remove(it)
        if it is p.weapon:
            p.weapon = None
        if it is p.armour:
            p.armour = None
        self.world.tiles[self.pos].items.append(it)
        self.emit(f"You set down the {it.name}.")

    def cmd_equip(self, rest):
        p = self.player
        it = self.find(rest, [p.inv])
        if not it:
            return self.emit("You don't have that.")
        if it.kind == "weapon":
            p.weapon = it
            self.emit(self.narr.pick([f"You take up the {it.name}, testing its weight.", f"You grip the {it.name}. It will do.",
                                      f"The {it.name} settles into your hand."]))
        elif it.kind == "armour":
            p.armour = it
            self.emit(self.narr.pick([f"You struggle into the {it.name} and buckle it tight.", f"You pull on the {it.name}. It smells of its last owner."]))
        else:
            self.emit("That isn't something you can wield or wear.")

    def cmd_use(self, rest):
        p = self.player
        it = self.find(rest, [p.inv])
        if (not it or it.kind == "ration") and any(x.startswith("ration") for x in rest):
            return TR.eat(self)
        if not it:
            return self.emit("You don't have that.")
        if ARTS.readable(it):
            return ARTS.read(self, it, [])
        if GOODS.usable(it):
            return GOODS.use(self, it, [x for x in rest if x not in it.keywords and x not in ("at", "on")])
        if not it.heal:
            return self.emit(f"You can't think how to use the {it.name}.")
        p.inv.remove(it)
        before = p.hp
        p.hp = min(p.maxhp, p.hp + it.heal)
        self.emit(self.narr.use_item(it) + f" (+{p.hp - before} HP)")
        if self.combat:
            self.enemy_turn()

    # ------------------------------------------------------------ people
    def who_list(self, npcs):
        return ", ".join(n.called() for n in npcs)

    def cmd_talk(self, rest, npc=None, for_trade=False):
        t = self.world.tiles[self.pos]
        elder = next((n for n in t.npcs if n.role == "elder"), None)
        if npc is None:
            npc = self.find(rest, [t.npcs]) if rest else (
                t.npcs[0] if len(t.npcs) == 1 else elder if (elder and not self.has_quest) else None)
        if not npc:
            if not t.npcs:
                return self.emit(self.narr.say("{sys_no_one}"))
            return self.emit(f"Talk to whom? ({self.who_list(t.npcs)})")
        n, w, m, p = self.narr, self.world, npc.mem, self.player
        first = m["met"] == 0
        if first:
            npc.like(1)
            m["knows_name"] = True
        elif w.day > m["last_day"]:
            npc.like(1)
        speak = lambda line: self.emit(n.attrib(npc, line))
        from . import speech as SP
        greeting = n.greet(npc, p.name, SP.react(self, npc, first))
        if first:   # introductions go both ways
            greeting += " " + n.introduce(npc, greeting)
        speak(greeting)
        m["introduced"] = True
        if for_trade:
            m["met"] += 1
            m["last_day"] = w.day
            npc.talked += 1
            return
        remark = n.memory_remark(npc, self.deeds, w.quest.carried(self))
        if remark:
            speak(remark)
        handed = S.on_talk(self, npc)
        LV.festival_gift(self, npc)
        main_talk = False          # one request per conversation: the main quest is plenty on its own
        if npc.role == "elder" and npc.home == w.start and self.one_speaker(w.quest.elder, self, npc):
            main_talk = True
        elif npc.role == "elder" and npc.home == w.start and not self.has_quest:
            self.has_quest = True
            main_talk = True
            self.one_speaker(w.quest.offer, self, npc)
        elif npc.role == "merchant" and first:
            from . import lex_talk_more as TALK2
            pr = npc.pronouns()
            self.emit(n.pick(TALK2.WARES, "wares").format(name=npc.name, he=pr["he"], his=pr["his"], him=pr.get("him", "them")) +
                      f" ({ui.how('trade')} to see what's for sale.)")
            m["wares_pointed"] = True
        elif first and GOODS.sells(npc):
            what = GOODS.WARES_WORDS.get(npc.job, "a few things")
            self.emit(n.attrib(npc, n.pick([f"\"If you need {what}, I've some to spare. For coin, mind.\"",
                                                 f"\"I sell {what}, if you've the coin.\"",
                                                 f"\"You'll want {what} on the road. I can help with that.\""]), "trade_beat") + f" ({ui.how(f'trade {npc.name}', 'trade')} to see.)")
            m["wares_pointed"] = True
        elif not handed:
            from . import talk as TK
            said = TK.topic(self, npc)                 # their errand, yours, fresh news, their own life
            rum = None if said else n.rumour(npc, self.pos)
            if said:
                self.emit(n.attrib(npc, said))
            elif rum:
                self.emit(n.attrib(npc, rum, "rumour_beat"))
            elif not remark:
                self.emit(n.attrib(npc, n.out_of_news(npc, p.name)))
        m["met"] += 1
        m["last_day"] = w.day
        npc.talked += 1
        if npc.tier == "devoted" and not m["gave_gift"]:
            m["gave_gift"] = True
            kind = self.rng.choice(["weapon", "armour", "potion"])
            gift = max((w.make_item(3, kind) for _ in range(5)), key=lambda it: it.value)
            p.inv.append(gift)
            self.emit(n.say("{npc_gives}", dict(name=npc.name, a_thing=article(gift.name))))
        if not self.pending and not self.over and not main_talk:
            if not LV.offer_trouble(self, npc) and not self.pending:
                from . import plots
                plots.offer(self, npc)

    def cmd_give(self, rest):
        t, p = self.world.tiles[self.pos], self.player
        words = [x for x in rest if x != "to"]
        if "to" in rest:          # "give <item> to <whom or where>"
            cut = len(rest) - 1 - rest[::-1].index("to")
            item_words, target_words = rest[:cut], rest[cut + 1:]
        else:
            item_words, target_words = words, words
        feat = self.find(target_words, [t.features]) if t.features else None
        if feat and not self.find(target_words, [t.npcs]):
            it = self.find([x for x in item_words if x not in feat.keywords or "to" in rest], [p.inv])
            if not it:
                return self.emit(self.narr.say("{sys_no_have}"))
            return SEC.offer(self, feat, it)
        if not t.npcs:
            return self.emit(self.narr.say("{sys_no_one}"))
        words = [x for x in rest if x != "to"]
        npc = self.find(words, [t.npcs]) or (t.npcs[0] if len(t.npcs) == 1 else None)
        if not npc:
            return self.emit(f"Give it to whom? ({self.who_list(t.npcs)})")
        it = self.find([x for x in words if x not in npc.keywords], [p.inv])
        if not it:
            return self.emit(self.narr.say("{sys_no_have}"))
        if self.world.quest.holds(it):
            return self.emit(f"{npc.name} backs away. \"That's not mine to hold. Take it home, where it belongs.\"")
        if any(q["kind"] == "bring" and q["giver"] == npc.name and (q["item"] == it.name or (q["data"].get("any_kind") == it.kind))
               for q in S.active(self)):
            S.on_talk(self, npc)
            return
        if it.kind == "token":
            return self.emit(f"{npc.name} shakes {npc.pronouns()['his']} head. \"That's not meant for me.\"")
        p.inv.remove(it)
        if it is p.weapon:
            p.weapon = None
        if it is p.armour:
            p.armour = None
        npc.remember("gift", thing=it.name, day=self.world.day)
        if npc.role == "merchant":
            npc.stock.append(it)
        good = it.value >= 8
        npc.like(min(5, max(1, it.value // 8)) if good else 0)
        addr = p.name if npc.mem["knows_name"] else "stranger"
        self.emit(f"You give the {it.name} to {npc.called()}. " + self.narr.say("{gift_thanks}" if good else "{gift_meh}",
                                                                               dict(addr=addr, thing=it.name, name=cap(npc.called()))))
        if npc.tier == "devoted" and not npc.mem["gave_gift"]:
            self.emit(f"{cap(npc.called())} looks at you differently now. Perhaps you should talk.")

    def price_mult(self, m):
        return {"cold": 1.25, "neutral": 1.0, "friendly": 0.9, "devoted": 0.8}[m.tier]

    def buy_price(self, m, it):
        rogue = 0.85 if self.klass() == "rogue" else 1.0      # Light-fingered
        return max(1, round(it.value * self.price_mult(m) * rogue))

    def sell_price(self, m, it):
        rogue = 1.25 if self.klass() == "rogue" else 1.0
        return max(1, round(it.value / 2 / self.price_mult(m) * rogue))

    def sellers(self):
        """Everyone here you can buy from: merchants, and craftsfolk you've been introduced to."""
        return [n for n in self.world.tiles[self.pos].npcs if n.role == "merchant" or (GOODS.sells(n) and n.mem.get("introduced"))]

    def merchant(self):
        """Whoever you're dealing with: the last seller you traded with here, else the first."""
        here = self.sellers()
        cur = next((n for n in here if n.name == getattr(self, "trading_with", None)), None)
        return cur or next((n for n in here if n.role == "merchant"), None) or (here[0] if here else None)

    def cmd_trade(self, rest):
        here = self.sellers()
        m = (self.find(rest, [here]) if rest else None) or (None if rest else self.merchant())
        if rest and not m:
            stranger = self.find(rest, [self.world.tiles[self.pos].npcs])
            if stranger and GOODS.sells(stranger):
                return self.emit(f"You don't know {cap(stranger.called())} well enough to ask about wares. Talk first.")
            return self.emit(f"No one here by that description has anything to sell." + (f" (Sellers: {self.who_list(here)}.)" if here else ""))
        if not m:
            return self.emit(self.narr.say("{sys_no_trader}"))
        self.trading_with = m.name
        if len(here) > 1 and not rest:
            self.emit(f"(Others here sell too: {self.who_list([n for n in here if n is not m])}." + (" Use People › See wares… to choose whose stall." if ui.web else " 'trade <name>' to see their wares.") + ")")
        if not m.known:      # walking up to the stall means meeting whoever keeps it
            self.emit(f"You step over to {m.called()}'s wares.")
            self.cmd_talk([], npc=m, for_trade=True)
        if not m.mem.get("wares_seen"):
            ARTS.stock_for(self, m)          # something on the stall for the way you think
        m.mem["wares_seen"] = True
        if not m.stock:
            return self.emit(f"{m.name} spreads empty hands. \"Sold out, friend.\"")
        if m.tier in ("friendly", "devoted"):
            self.emit(self.narr.attrib(m, self.narr.say("{discount_line}"), "trade_beat"))
        elif m.tier == "cold":
            self.emit(self.narr.attrib(m, self.narr.say("{markup_line}"), "trade_beat"))
        self.out(f"{m.name} has for sale:")
        for it in m.stock:
            if ui.web:      # a narrow screen: no padded columns, the price follows the name
                self.out(f"• {article(it.name)} — {self.buy_price(m, it)} coins")
            else:
                self.out(f"  {article(it.name):45s} {self.buy_price(m, it):4d} coins")
        self.out(f"You have {self.player.gold} coins." + (f" (People › Buy…, People › Sell…, Look › Examine…)" if ui.web
                                                          else " ('buy <item>', 'sell <item>', 'examine <item>')"))
        if TR.sells_rations(m):
            left = TR.supply(m)
            self.out(f"{m.name} has {left} travel ration{'s' if left != 1 else ''} at {TR.RATION_PRICE} coins each ({ui.ref('buy rations')}). You carry {TR.rations(self)}."
                     if left else f"{m.name} has no travel rations left. You carry {TR.rations(self)}.")

    def cmd_buy(self, rest):
        if any(x.startswith("ration") for x in rest):
            return TR.buy(self, " ".join(rest))
        m = self.merchant()
        if not m:
            return self.emit(self.narr.say("{sys_no_trader}"))
        if not m.mem.get("wares_seen"):
            return self.emit(f"You haven't looked over {m.called()}'s wares yet. ({ui.how('trade')} to see what's for sale.)")
        it = self.find(rest, [m.stock])
        if not it:
            other = next((s for s in self.sellers() if s is not m and s.mem.get("wares_seen") and self.find(rest, [s.stock])), None)
            if not other:
                return self.emit(f"{m.name} doesn't have that.")
            m, it = other, self.find(rest, [other.stock])
            self.trading_with = m.name
        price = self.buy_price(m, it)
        if self.player.gold < price:
            return self.emit(f"{m.name} shakes {m.pronouns()['his']} head. \"That's {price} coins. You've not got it.\"")
        self.player.gold -= price
        m.stock.remove(it)
        self.player.inv.append(it)
        m.remember("bought", thing=it.name, day=self.world.day)
        m.like(1)
        self.emit(self.narr.pick([f"You hand over {price} coins and take the {it.name}.",
                                  f"{m.name} bites one of your coins, nods, and passes you the {it.name}.",
                                  f"Coins change hands, and the {it.name} is yours."]))

    def cmd_sell(self, rest):
        m = self.merchant()
        if not m:
            return self.emit(self.narr.say("{sys_no_trader}"))
        if not m.mem.get("wares_seen"):
            return self.emit(f"You haven't dealt with {m.called()} yet. ({ui.how('trade')} to step over to {m.pronouns()['his']} stall.)")
        p = self.player
        it = self.find(rest, [p.inv])
        if not it:
            return self.emit(self.narr.say("{sys_no_have}"))
        if it.kind in ("relic", "token") or self.world.quest.holds(it):
            return self.emit(f"{m.name}'s eyes widen. \"I'd not touch that for all the coin in the world.\"")
        if it.name in S.quest_items(self):
            return self.emit(f"You promised to deliver the {it.name}. It isn't yours to sell.")
        price = self.sell_price(m, it)
        m.remember("sold", thing=it.name, day=self.world.day)
        if price >= 5:
            m.like(1)
        p.inv.remove(it)
        if it is p.weapon:
            p.weapon = None
        if it is p.armour:
            p.armour = None
        p.gold += price
        m.stock.append(it)
        self.emit(f"{m.name} turns the {it.name} over and pays you {price} coins.")

    # ------------------------------------------------------------ rest & shrines
    def cmd_travel(self, rest):
        TR.travel(self, " ".join(rest))

    def cmd_rest(self, rest):
        if self.combat:
            return self.emit("You can't rest with an enemy at your throat!")
        t = self.world.tiles[self.pos]
        p = self.player
        safe = bool(t.site and t.site["kind"] == "village")
        hours = 8 if safe else 4
        lurkers = [c for c in t.creatures if mind.intent(c) in ("stalk", "hunt", "hold")]
        if lurkers and self.rng.random() < (0.5 if self.klass() == "ranger" else 0.85):
            c = lurkers[0]
            self.emit("You settle down and close your eyes...")
            self.emit(self.narr.mind_line("ambush", c))
            self.combat = c
            return self.enemy_turn(bonus=4, committed=True)
        self.emit(self.narr.pick(["You find a sheltered spot and close your eyes.", "You settle down and let sleep take you.",
                                  "You rest a while, listening to the world."]) if not safe else
                  self.narr.pick(COMPOSE.REST_SAFE, "restsafe"))
        self.pass_time(hours * 60)
        p.hp = min(p.maxhp, p.hp + (p.maxhp if safe else p.maxhp // 3))
        if K.spec(p):
            p.res = p.res_max if safe else min(p.res_max, p.res + p.res_max // 2)
        if not safe and self.rng.random() < (0.15 if self.klass() == "ranger" else 0.3):
            fitting = [s for s in self.world.species if t.biome in s["arch"]["biomes"]]
            if fitting:
                c = self.world.make_creature(self.rng.choice(fitting), max(1, t.danger))
                c.aggressive = True
                t.creatures.append(c)
                self.emit("You wake with a start - something has found you!")
                self.emit(self.narr.creature_presence(c))
                self.combat = c
                return self.enemy_turn()
        res = f", {K.spec(p)['res']} {p.res}/{p.res_max}" if K.spec(p) else ""
        from . import lex_talk_more as TALK2
        self.emit(self.narr.pick(TALK2.WAKE, "wake") + f" (HP {p.hp}/{p.maxhp}{res})")
        self.emit(self.narr.sky(self.pos))

    def cmd_wait(self, rest):
        self.emit(self.narr.pick(["Time passes.", "You wait, watching the world.", "You let an hour slip by."]))
        self.pass_time(60)
        self.regen(2)

    def cmd_pray(self, rest):
        t = self.world.tiles[self.pos]
        if not (t.site and t.site["kind"] == "shrine"):
            return self.emit(self.narr.say("{sys_pray_none}"))
        s, p = t.site, self.player
        answer = self.world.quest.on_pray(self, s) if self.has_quest else ""      # the spirit may have something for the quest
        if s["used"]:
            return self.emit(answer or f"You pray to {s['spirit']}, but feel only a polite silence.")
        s["used"] = True
        bonus = 4 if self.klass() == "cleric" else 2     # Blessed
        p.maxhp += bonus
        p.hp = p.maxhp
        if K.spec(p):
            p.res = p.res_max
        self.emit(self.narr.pick([f"You kneel before the {s['form']} and pray to {s['spirit']}. Warmth floods through you, and your wounds close.",
                                  f"You leave a small offering and speak to {s['spirit']}. The wind drops; something listens. You rise whole, and stronger.",
                                  f"As you pray, the {s['form']} seems to breathe. Your pain lifts away like mist."]) + f" (Fully healed, +{bonus} max HP)")
        if answer:
            self.emit(answer)

    # ------------------------------------------------------------ combat
    def cmd_attack(self, rest):
        t = self.world.tiles[self.pos]
        target = self.combat if (self.combat and not rest) else self.find(rest, [t.creatures]) if rest else (t.creatures[0] if t.creatures else None)
        if not target:
            if self.find(rest, [t.npcs]):
                return self.emit("You think better of it. These folk have done you no harm.")
            return self.emit(self.narr.say("{sys_no_fight}"))
        self.combat = target
        p, n = self.player, self.narr
        p.hidden = 0
        hp_before = target.hp
        roll = self.rng.randint(1, 20) + p.atk - target.df
        crit_at = (18 if getattr(p, "klass", None) == "rogue" else 21) - 3 * S.buff(self, "lucky")
        if roll < 6:
            self.emit(n.player_attack("miss", p.weapon, target))
        else:
            dmg = max(1, p.atk + self.rng.randint(0, 3) - target.df)
            if roll >= crit_at:
                tier, dmg = "crit", dmg * 2
            elif roll >= 10:
                tier = "hit"
            else:
                tier, dmg = "graze", max(1, dmg // 2)
            target.hp -= dmg
            self.emit(n.player_attack(tier, p.weapon, target) + f" ({dmg} damage)")
        if target.hp <= 0:
            return self.finish_off(target)
        took = hp_before - target.hp
        self.enemy_turn()
        if self.combat is target:
            # the creature's governing intent is backed if the exchange went its way
            mind.reinforce(target, going_well=self._enemy_dmg >= took)

    def finish_off(self, target):
        """A creature dies: narration, news of the deed, experience, perhaps coin."""
        t, p, n = self.world.tiles[self.pos], self.player, self.narr
        self.emit(n.death(target))
        if target in t.creatures:
            t.creatures.remove(target)
        self.deeds.append(dict(kind="boss" if target.boss else "kill",
                               thing=title(target.title) if target.boss else target.species["name"],
                               where=self.world.region_of(self.pos)["name"], pos=self.pos, day=self.world.day))
        self.combat = None
        S.add_mark(self, self.pos, n.pick([f"The body of the {target.species['name']} you killed lies here, and the crows have found it.",
                                           f"Flattened grass and dark stains show where you fought the {target.species['name']}."]), days=2)
        S.on_kill(self, target)
        self.world.quest.on_kill(self, target)
        for m in p.gain_xp(target.xp):
            self.emit(m)
        rogue = getattr(p, "klass", None) == "rogue"
        if self.rng.random() < (0.55 if rogue else 0.3):
            coins = self.rng.randint(2, 6) * max(1, t.danger) * (2 if rogue else 1)
            p.gold += coins
            self.emit(n.say("{coin_find}", dict(coins=coins)))

    def mitigate(self, c, dmg):
        """Class defences between a blow and your hide: ward, guard, blessing."""
        p, n = self.player, self.narr
        notes = []
        if getattr(p, "klass", None) == "cleric" and c.species["arch"].get("undead") and dmg > 1:
            dmg = max(1, dmg - 2)
            notes.append(n.say("{undead_soften}", {}))
        if getattr(p, "guard", 0) > 0:
            p.guard -= 1
            dmg = max(0, dmg // 2)
            notes.append(n.say("{ab_guard_absorb}", {}))
        if getattr(p, "ward", 0) > 0:
            soak = min(p.ward, dmg)
            p.ward -= soak
            dmg -= soak
            notes.append(n.say("{ab_ward_absorb}" if p.ward > 0 else "{ab_ward_break}", {}))
        return dmg, " ".join(notes)

    def enemy_turn(self, bonus=0, committed=False):
        c, p, n, w = self.combat, self.player, self.narr, self.world
        self._enemy_dmg = 0
        if ARTS.tick(self, c):           # burning or poisoned to death
            return
        if mind.ensure(c).get("stunned"):
            c.mind["stunned"] = False
            self.emit(n.mind_line("ab_stunned", c))
            return
        if committed:              # an ambush or a chase: it has already decided
            mind.commit(c, "hunt")
            new = "hunt"
        else:
            old, new = mind.update(c, p, w, in_combat=True)
            if new != old and new != "wander":
                self.emit(n.mind_line(f"shift_{new}", c))
        if new == "flee":
            routes = self.escape_routes(self.pos)
            if routes and self.rng.random() < 0.65:
                d, q = self.rng.choice(routes)
                self.relocate(c, self.pos, q)
                self.combat = None
                self.emit(n.mind_line("slip_away", c, dir=d))
            else:
                self.emit(n.mind_line("escape_fail", c))
            return
        if new == "stalk":
            c.mind["feint"] = True
            self.emit(n.mind_line("circle", c))
            return
        if c.mind.get("feint"):
            bonus += 4
            c.mind["feint"] = False
        if new in ("hold", "wander"):
            bonus -= 2
        roll = self.rng.randint(1, 20) + c.atk - p.df + bonus
        if roll < 11:
            self.emit(n.enemy_attack("enemy_miss", c, p.armour))
            return
        dmg = c.atk + self.rng.randint(-2, 1) - p.df
        if dmg <= 0:
            self.emit(n.enemy_attack("enemy_block", c, p.armour))
            return
        hard = roll >= 23
        if hard:
            dmg = int(dmg * 1.5)
        dmg, note = self.mitigate(c, dmg)
        p.hp -= dmg
        self._enemy_dmg = dmg
        self.emit(n.enemy_attack("enemy_hard" if hard else "enemy_hit", c, p.armour) + (f" {note}" if note else "") +
                  f" ({dmg} damage, HP {max(0, p.hp)}/{p.maxhp})")
        if p.hp <= 0:
            self.die(c)

    def try_flee(self):
        c = self.combat
        ok = self.rng.random() < (0.35 if c.boss else 0.65) + 0.03 * ARTS.bonus(self.player, "grace")
        self.emit(self.narr.flee(ok, c))
        if ok:
            self.combat = None
            return True
        self.enemy_turn()
        return False

    def cmd_flee(self, rest):
        if not self.combat:
            return self.emit("You're not fighting anything.")
        c = self.combat
        if self.try_flee():
            opts = [d for d, q in self.world.neighbours(self.pos) if q in self.world.land]
            self._fled_from = c
            self.move(self.rng.choice(opts))

    # ------------------------------------------------------------ endings
    def die(self, c):
        self.emit("")
        self.emit(self.narr.pick(["The world tilts and goes dark.", "Your legs give way. The sky is the last thing you see.",
                                  "You fall, and the ground is very cold."]))
        self.emit(f"*** You have died, slain by {self.narr.creature_np(c)}, on day {self.world.day}. ***")
        self.over = self.died = True

    def check_win(self):
        if not self.over:
            self.world.quest.check(self)

    def cmd_quit(self, rest):
        if not self.died:
            self.save("autosave", quiet=True)
            self.emit("(Progress saved to 'autosave'.)")
        self.emit("You leave the world to its weather.")
        self.over = True

    # ------------------------------------------------------------ save / load
    STORY_KEEP = 1500       # lines of the story kept in a save, so a loaded game can be read back

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("out", None)
        source = state.pop("story_source", None)     # set by the web page: the story it has shown so far
        if source is not None:
            state["story"] = list(source()[-self.STORY_KEEP:])
        else:
            state.pop("story", None)      # played in the terminal since: an older story would no longer lead here
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.out = print

    # ------------------------------------------------------------ saves
    # Each character has a folder, saves/<folder>/<slot>.sav, with a small .json summary beside each
    # save and run.json for the character as a whole. A folder is named for the character plus a short
    # random tag, so two travellers called Wren never share one (or one autosave). A save is named as
    # "folder/slot"; a bare slot means this character's save of that name, or failing that the newest
    # save of that name belonging to anyone.

    @staticmethod
    def safe_slot(slot):
        return "".join(ch for ch in str(slot).strip().lower().replace(" ", "-") if ch.isalnum() or ch in "-_")[:40]

    @staticmethod
    def new_run_id(name):
        return f"{(Game.safe_slot(name) or 'wanderer')[:24]}-{os.urandom(3).hex()}"

    def ensure_run(self):
        """Characters from before folders get one the first time they are saved."""
        if not getattr(self, "run_id", None):
            self.run_id = self.new_run_id(self.player.name)
        if not getattr(self, "started", None):
            self.started = time.time()

    @staticmethod
    def save_ref(path):
        return f"{path.parent.name}/{path.stem}"

    @classmethod
    def migrate_saves(cls):
        """Move saves from before character folders into one folder per character (by name and world)."""
        if not SAVE_DIR.exists():
            return
        import hashlib
        for path in sorted(SAVE_DIR.glob("*.sav"), key=lambda p: p.stat().st_mtime):
            side = path.with_suffix(".json")
            try:
                m = json.loads(side.read_text())
            except (OSError, ValueError):
                try:
                    with open(path, "rb") as f:
                        m = pickle.load(f)["game"].meta()
                except Exception:
                    m = {}
            name, seed = m.get("name") or "unknown", m.get("seed")
            folder = SAVE_DIR / f"{(cls.safe_slot(name) or 'unknown')[:24]}-{hashlib.sha1(f'{name}|{seed}'.encode()).hexdigest()[:6]}"
            folder.mkdir(exist_ok=True)
            dest = folder / path.name
            n = 2
            while dest.exists():
                dest = folder / f"{path.stem}-{n}.sav"
                n += 1
            mtime = path.stat().st_mtime
            os.replace(path, dest)
            if side.exists():
                os.replace(side, dest.with_suffix(".json"))
            run = folder / "run.json"
            try:
                info = json.loads(run.read_text())
            except (OSError, ValueError):
                info = {}
            info.setdefault("name", name)
            info.setdefault("seed", seed)
            info["started"] = min(info.get("started", mtime), mtime)     # the oldest save is our best guess
            run.write_text(json.dumps(info))

    @classmethod
    def run_info(cls, folder):
        try:
            return json.loads((SAVE_DIR / folder / "run.json").read_text())
        except (OSError, ValueError):
            return {}

    @classmethod
    def list_saves(cls, run=None):
        """Save files, newest first: one character's (run=folder) or everyone's."""
        cls.migrate_saves()
        if not SAVE_DIR.exists():
            return []
        def age(p):
            try:
                return -p.stat().st_mtime
            except OSError:          # deleted while we looked
                return 0
        pattern = f"{cls.safe_slot(run)}/*.sav" if run else "*/*.sav"
        return sorted((p for p in SAVE_DIR.glob(pattern) if p.exists()), key=age)

    def meta(self):
        """A small summary written next to each save, so saves can be listed without loading them."""
        w, p = self.world, self.player
        return dict(name=p.name, klass=p.class_name, level=p.level, hp=max(0, p.hp), maxhp=p.maxhp,
                    day=w.day, place=self.narr.header(self.pos), seed=self.seed, world=w.title,
                    started=getattr(self, "started", None),
                    relic=bool(w.quest.carried(self)), quest=w.quest.status(self), won=self.won, died=self.died, turns=getattr(self, "turns", 0))

    @classmethod
    def save_info(cls, path):
        """Details of one save file. Older saves without a summary are opened once and given one."""
        info = dict(saved=path.stat().st_mtime)
        side = path.with_suffix(".json")
        try:
            info.update(json.loads(side.read_text()))
        except (OSError, ValueError):
            try:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                if data.get("version") != SAVE_VERSION:
                    info["broken"] = "from an older version of the game"
                else:
                    m = data["game"].meta()
                    side.write_text(json.dumps(m))
                    os.utime(side, (info["saved"], info["saved"]))
                    info.update(m)
            except Exception:
                info["broken"] = "unreadable"
        if info.get("seed") is not None and not info.get("world"):
            from . import places, names
            info["world"] = places.world_title(info["seed"], names.gen())
        info.update(id=cls.save_ref(path), slot=path.stem, run=path.parent.name, saved=path.stat().st_mtime)
        return info

    @classmethod
    def list_save_info(cls, run=None):
        out = []
        for p in cls.list_saves(run):
            try:
                out.append(cls.save_info(p))
            except OSError:          # deleted while we looked
                pass
        return out

    @classmethod
    def list_runs(cls):
        """Characters with saves, the most recently played first, each with its saves (newest first)."""
        runs = {}
        for s in cls.list_save_info():
            runs.setdefault(s["run"], []).append(s)
        out = []
        for folder, saves in runs.items():
            latest = next((s for s in saves if not s.get("broken")), saves[0])
            info = cls.run_info(folder)
            started = latest.get("started") or info.get("started") or min(s["saved"] for s in saves)
            out.append(dict(run=folder, name=latest.get("name") or info.get("name") or folder, klass=latest.get("klass"),
                            level=latest.get("level"), world=latest.get("world"), seed=latest.get("seed", info.get("seed")),
                            started=started, saved=saves[0]["saved"], died=latest.get("died"), won=latest.get("won"),
                            latest=latest["id"], saves=saves))
        return sorted(out, key=lambda r: -r["saved"])

    @classmethod
    def find_save(cls, ref, run=None):
        """The file a save name points at, or None: 'folder/slot', or a bare slot (this character's first)."""
        ref = str(ref or "").strip()
        if "/" in ref:
            folder, _, slot = ref.partition("/")
            p = SAVE_DIR / cls.safe_slot(folder) / f"{cls.safe_slot(slot)}.sav"
            return p if cls.safe_slot(folder) and p.exists() else None
        slot = cls.safe_slot(ref)
        if not slot:
            return None
        if run:
            p = SAVE_DIR / cls.safe_slot(run) / f"{slot}.sav"
            if p.exists():
                return p
        return next((p for p in cls.list_saves() if p.stem == slot), None)

    @classmethod
    def delete_save(cls, ref, run=None):
        path = cls.find_save(ref, run)
        if path is None:
            raise FileNotFoundError(ref)
        path.unlink()
        path.with_suffix(".json").unlink(missing_ok=True)
        if not any(path.parent.glob("*.sav")):              # the character's last save: tidy the folder away
            shutil.rmtree(path.parent, ignore_errors=True)
        return path

    @classmethod
    def delete_run(cls, run):
        folder = SAVE_DIR / cls.safe_slot(run)
        if not cls.safe_slot(run) or not folder.is_dir():
            raise FileNotFoundError(run)
        shutil.rmtree(folder)

    @classmethod
    def rename_save(cls, ref, new, run=None):
        src, safe = cls.find_save(ref, run), cls.safe_slot(new)
        if src is None:
            raise FileNotFoundError(ref)
        if not safe:
            raise ValueError("a save name needs at least one letter or number")
        dst = src.parent / f"{safe}.sav"
        if dst == src:
            return safe
        if dst.exists():
            raise ValueError(f"this character already has a save called '{safe}'")
        os.replace(src, dst)
        if src.with_suffix(".json").exists():
            os.replace(src.with_suffix(".json"), dst.with_suffix(".json"))
        return safe

    def save(self, slot="quicksave", quiet=False):
        self.ensure_run()
        folder = SAVE_DIR / self.run_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{self.safe_slot(slot) or 'save'}.sav"
        self.narr.flush_phrases(force=not quiet)      # what you've read, for the next run to avoid
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump(dict(version=SAVE_VERSION, game=self), f)
        os.replace(tmp, path)
        path.with_suffix(".json").write_text(json.dumps(self.meta()))
        run = folder / "run.json"
        if not run.exists():
            run.write_text(json.dumps(dict(name=self.player.name, seed=self.seed, world=self.world.title, started=self.started)))
        self.last_save_turn = getattr(self, "turns", 0)
        if not quiet:
            self.save_slot = path.stem
            self.emit(f"Game saved to '{path.stem}'. (Day {self.world.day}, {self.narr.header(self.pos)})")

    @classmethod
    def load(cls, slot, out=print, run=None):
        """Load a save file. Saves are pickles: only load files you created yourself."""
        path = cls.find_save(slot, run)
        if path is None:
            raise FileNotFoundError(slot)
        with open(path, "rb") as f:
            data = pickle.load(f)
        if data.get("version") != SAVE_VERSION:
            raise ValueError(f"save '{slot}' is from an incompatible version of the game")
        g = data["game"]
        g.out = out
        g.width = min(90, shutil.get_terminal_size((80, 24)).columns - 2)
        g.run_id = path.parent.name                     # a save belongs to the character whose folder it is in
        if not getattr(g, "started", None):
            g.started = cls.run_info(g.run_id).get("started") or path.stat().st_mtime
        g.save_slot = path.stem
        g.last_save_turn = getattr(g, "turns", 0)
        return g

    def save_id(self):
        slot = getattr(self, "save_slot", None)
        return f"{self.run_id}/{slot}" if slot and getattr(self, "run_id", None) else None

    def cmd_save(self, rest):
        if self.combat:
            return self.emit("You can't save in the middle of a fight!")
        self.save(rest[0] if rest else getattr(self, "save_slot", None) or "quicksave")

    def cmd_hints(self, rest):
        on = (rest[0] in ("on", "yes")) if rest else not getattr(self, "show_hints", True)
        self.show_hints = on
        self.emit(f"Suggestions {'on' if on else 'off'}." + ("" if ui.web else " (Type 'hints' to toggle.)"))

    @staticmethod
    def describe_save(i):
        if i.get("broken"):
            return f"{i['slot']}: ({i['broken']})"
        when = time.strftime("%d %b %H:%M", time.localtime(i["saved"]))
        state = " - dead" if i.get("died") else " - won" if i.get("won") else f" - {i['quest']}" if i.get("quest") else " - carrying the relic" if i.get("relic") else ""
        return f"{i['slot']}: level {i['level']}, day {i['day']}, {i['place']}{state}  (saved {when})"

    def cmd_saves(self, rest):
        runs = self.list_runs()
        if not runs:
            return self.out(f"No saves yet. {ui.how('save [name]', 'save')} to make one.")
        mine = getattr(self, "run_id", None)
        runs.sort(key=lambda r: r["run"] != mine)                 # this character first
        self.out("Saves, by character:")
        for r in runs:
            began = time.strftime("%d %b %Y %H:%M", time.localtime(r["started"])) if r.get("started") else "?"
            who = f"{r['name']}, level {r['level']} {(r['klass'] or '').lower()}".rstrip()
            self.out(f"  {who}{'  (you)' if r['run'] == mine else ''}")
            self.out(f"    {r['world'] or 'an unnamed world'} · seed {r['seed']} · began {began} · folder {r['run']}")
            for s in r["saves"]:
                self.out("      " + self.describe_save(s))
        self.out("  load [name] · rename [old] [new] · delete [name]   (another character's save: load folder/name)")

    def cmd_delete(self, rest):
        if not rest:
            return self.emit(f"Delete which save? ({ui.how('saves')} to list them.)")
        path = self.find_save(rest[0], getattr(self, "run_id", None))
        if path is None:
            return self.emit(f"No save called '{self.safe_slot(rest[0])}'. ({ui.how('saves')} to list them.)")
        ref = rest[0] if "/" in rest[0] else path.stem if path.parent.name == getattr(self, "run_id", None) else self.save_ref(path)
        if rest[1:2] != ["yes"]:
            return self.emit(f"Deleting '{ref}' can't be undone. " + ("Delete it from the Saves window." if ui.web else f"Type 'delete {ref} yes' to confirm."))
        self.delete_save(self.save_ref(path))
        if self.save_ref(path) == self.save_id():
            self.save_slot = None
        self.emit(f"Deleted the save '{ref}'.")

    def cmd_rename(self, rest):
        if len(rest) < 2:
            return self.emit("Usage: rename [old name] [new name]")
        path = self.find_save(rest[0], getattr(self, "run_id", None))
        try:
            new = self.rename_save(rest[0], rest[1], getattr(self, "run_id", None))
        except FileNotFoundError:
            return self.emit(f"No save called '{self.safe_slot(rest[0])}'.")
        except ValueError as e:
            return self.emit(f"Can't rename: {e}.")
        if path is not None and self.save_ref(path) == self.save_id():
            self.save_slot = new
        self.emit(f"Renamed '{path.stem}' to '{new}'.")

    def cmd_load(self, rest):
        slot = rest[0] if rest else "quicksave"
        try:
            g = Game.load(slot, self.out, getattr(self, "run_id", None))
        except FileNotFoundError:
            self.emit(f"No save called '{slot}'. ({ui.how('saves')} to list them.)")
            return False
        except Exception as e:
            self.emit(f"Couldn't load '{slot}': {e}")
            return False
        self.__dict__.update(g.__dict__)
        self.emit(f"Loaded '{slot}'.")
        self.show_location()
        return True

    # ------------------------------------------------------------ landmarks
    def landmark(self, verb, rest):
        if self.combat:
            return self.emit("Not with something trying to kill you!")
        t = self.world.tiles[self.pos]
        fit = [f for f in t.features if SEC.can(verb, f)]
        f = self.find(rest, [t.features]) if rest else (fit[0] if len(fit) == 1 else None)
        if f is None:
            if not t.features:
                return self.emit("There's no landmark here for that.")
            if rest:
                return self.emit(self.narr.say("{sys_see_nothing}"))
            if not fit:
                return self.emit(f"There's nothing here you can {verb}.")
            return self.emit(f"{verb.capitalize()} what? ({', '.join('the ' + x.noun for x in fit)})")
        SEC.act(self, verb, f)
        self.apply_buffs()

    def cmd_search(self, rest):
        self.landmark("search", rest)

    def cmd_climb(self, rest):
        self.landmark("climb", rest)

    def cmd_touch(self, rest):
        self.landmark("touch", rest)

    def cmd_read(self, rest):
        p = self.player
        books = [i for i in p.inv if ARTS.readable(i)]
        it = self.find(rest, [books]) if rest else (books[0] if len(books) == 1 and not self.world.tiles[self.pos].features else None)
        if it is None and rest and books:       # "read scroll at wolf"
            for cut in range(len(rest) - 1, 0, -1):
                it = self.find(rest[:cut], [books])
                if it:
                    return ARTS.read(self, it, [x for x in rest[cut:] if x not in ("at", "on")])
        if it is not None:
            return ARTS.read(self, it, [])
        if not rest and books and not any(SEC.can("read", f) for f in self.world.tiles[self.pos].features):
            return self.emit(f"Read what? ({', '.join('the ' + b.name for b in books)})")
        self.landmark("read", rest)

    def cmd_improve(self, rest):
        ARTS.improve(self, rest)

    def cmd_craft(self, rest):
        p = self.player
        if not ARTS.literate(p, "arcane") and ARTS.literate(p, "divine"):
            return CR.weave(self, "divine", rest)
        if not ARTS.literate(p, "arcane"):
            return self.emit("Spellcraft needs Arcane Letters." + (f" You could hone your techniques instead ({ui.ref('hone')})." if any(CR.can_hone(k) for k in p.known) else ""))
        CR.weave(self, "arcane", rest)

    def cmd_compose(self, rest):
        CR.weave(self, "divine", rest)

    def cmd_hone(self, rest):
        if rest and rest[0] == "combine":           # "hone combine a b"
            rest = rest[1:]
            if len(rest) == 2:
                rest = [rest[0], "with", rest[1]]
        CR.hone(self, rest)

    def cmd_combine(self, rest):
        """'combine a b' or 'combine a with b': join two techniques."""
        words = [x for x in rest if x not in ("and",)]
        if "with" not in words and len(words) == 2:
            words = [words[0], "with", words[1]]
        CR.hone(self, words)

    def cmd_forget(self, rest):
        CR.forget(self, rest)

    def cmd_arts(self, rest):
        """Everything you can do, by school, and the traits that let you learn more."""
        p = self.player
        res = K.res_name(p)
        by = {}
        for k in K.known(p):
            by.setdefault(ARTS.school_of(k)[0], []).append(k)
        for school, keys in by.items():
            sc = ARTS.SCHOOLS.get(school, {})
            self.emit(f"{sc.get('menu', 'Arts')}: " + "; ".join(
                f"{K.ABILITIES[k]['label']} ({'' if ui.web else repr(k) + ', '}{K.ABILITIES[k]['cost']} {res}) - {K.ABILITIES[k]['desc']}" for k in keys))
        self.emit("Traits: " + "; ".join(f"{a} - {b}" for a, b in ARTS.traits(p)))
        if p.points:
            self.emit(f"(You have {p.points} point{'s' if p.points > 1 else ''} to spend: " + (f"{ui.ref('improve')}" if ui.web else "'improve' might, grace, wits or spirit.") + ")")

    def cmd_forage(self, rest):
        self.landmark("forage", rest)

    def cmd_listen(self, rest):
        t = self.world.tiles[self.pos]
        if not rest and len(t.features) != 1:
            return self.emit(self.narr.say("{sense_sound.cap}.", scopes=self.narr.scopes(t.biome, t.mood), tile=t)
                             if t.features == [] else f"Listen where? ({', '.join('the ' + x.noun for x in t.features)})")
        self.landmark("listen", rest)

    def cmd_drink(self, rest):
        it = self.find(rest, [self.player.inv]) if rest else None
        if it and it.heal:
            return self.cmd_use(rest)
        self.landmark("drink", [x for x in rest if x not in ("from", "in")])

    def cmd_journal(self, rest):
        lines = S.journal_lines(self)
        self.out("Journal")
        for l in lines:
            self.out(l)
        if len(S.journal(self)["entries"]) == 1:
            self.out("   (Nothing else on your mind. Landmarks, villages and the road are full of chances.)")
        fx = S.effects_line(self)
        if fx:
            self.out(f"  You are under {fx}.")
        if self.companions:
            self.out("  With you: " + ", ".join(c["name"] for c in self.companions) + ".")

    def cmd_chronicle(self, rest):
        ch = self.world.chronicle
        if not ch:
            return self.out("Nothing worth remembering has happened yet.")
        self.out("The chronicle of your days:")
        for e in ch[-25:]:
            self.out(f"  Day {e['day']}: {e['text']}")

    def cmd_help(self, rest):
        self.out(HELP)
        s = K.spec(self.player)
        if s:
            self.out(f"  {s['name']} arts: " + ", ".join(f"{a} ({K.ABILITIES[a]['cost']} {s['res']})" for a in K.known(self.player))
                     + "  - e.g. 'firebolt wolf', or 'cast firebolt'")
        self.out("  arts (your skills and traits) / improve <might|grace|wits|spirit> / read <book or scroll> (study it; scrolls are spent)")
        self.out("  craft <parts> (spellcraft) / compose <parts> (prayers) / hone [technique] [refinement] / hone <a> with <b> / forget <crafted art>")

    # ------------------------------------------------------------ run
    def run(self, resumed=False):
        if resumed:
            self.emit(f"You return to the world of seed {self.seed}, on day {self.world.day}.")
            self.show_location()
        else:
            self.intro()
        while True:
            while not self.over:
                try:
                    line = input("\n> ")
                except (EOFError, KeyboardInterrupt):
                    if not self.died:
                        self.save("autosave", quiet=True)
                    self.emit("\nFarewell. (Progress saved to 'autosave'.)")
                    return
                self.handle(line)
            if not self.died or not self.list_saves():
                return
            try:
                ans = input("\nLoad a save? Enter a slot name, or press Enter to quit: ").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if not ans:
                return
            if not self.cmd_load([ans]):
                return
