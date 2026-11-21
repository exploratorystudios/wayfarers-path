"""The Narrator turns world facts into freshly generated prose, every time."""
import math
import random
from collections import deque

from . import coherence as C
from . import lexicon as L
from . import lex_entities as E
from . import lex_more as M
from . import mind
from . import lex_variety as V
from . import lex_landmarks as LM
from . import secrets as SEC
from . import living as LV
from . import story as ST
from .textgen import Grammar, tidy, article, cap, title

PREP_WORDS = ("the ",)


def join_words(words):
    words = list(words)
    if len(words) == 1:
        return words[0]
    return ", ".join(words[:-1]) + " and " + words[-1]


class _Biome:
    """A stand-in tile, so say() knows the biome for its checks."""
    flavour = {}

    def __init__(self, biome):
        self.biome = biome


class Narrator:
    def __init__(self, world, seed=None):
        self.w = world
        self.rng = random.Random(seed)
        self.build_grammar()
        self.last_sky = None
        self.recent = deque(maxlen=80)

    def build_grammar(self):
        """Assemble the rules from the lexicon files (also on load, so saves get current wording)."""
        self.g = Grammar(self.rng)
        for rules in (L.RULES, E.CREATURE_RULES, E.ITEM_RULES, E.SITE_RULES, E.COMBAT_RULES):
            self.g.add(rules)
        npc = dict(E.NPC_RULES)
        for role, opts in npc.pop("doing").items():
            self.g.add({f"{role}:doing": opts})
        self.g.add(npc)
        self.g.add(M.NEW)
        self.g.add(M.MIND)
        from . import lex_classes
        self.g.add(lex_classes.RULES)
        self.g.extend(V.EXTEND)
        self.g.add(V.REPLACE)
        self.g.add(V.INTRO)
        self.g.add(V.ARRIVAL)
        self.g.add(V.DARK)
        self.g.add(LM.rules())
        self.g.extend(M.EXTEND)

    def __getstate__(self):
        state = dict(self.__dict__)
        state.pop("g", None)        # rebuilt from the lexicon on load
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.build_grammar()

    # ------------------------------------------------------------ core
    def scopes(self, biome=None, mood=None):
        w = self.w
        t, wc, s = w.time_of_day, w.weather_class, w.season
        sc = [f"dark_{w.weather}"] if w.is_dark else []
        if biome:
            sc += [f"{biome}:{s}", f"{biome}:{w.weather}", f"{biome}:{t}", biome]
        sc += [f"{t}_{wc}", t, w.weather, s]
        if mood:
            sc.append(mood)
        return sc

    def say(self, template, ctx=None, scopes=None, tile=None):
        if scopes is None:
            scopes = self.scopes()
        base = {"moon_line": self.w.moon_line}
        if tile is not None:
            base.update(tile.flavour)
        w = self.w
        biome = tile.biome if tile is not None else None
        best, best_score = "", None
        for _ in range(8):
            c = dict(base)
            c.update(ctx or {})
            s = tidy(self.g.expand(template, c, scopes))
            # contradicting the moment is worst, then repeating ourselves, then a word used twice
            score = (10 * len(C.context_clashes(s, w.season, w.weather, w.time_of_day, biome))
                     + (3 if s in self.recent else 0) + len(C.repeated_words(s)))
            if best_score is None or score < best_score:
                best, best_score = s, score
            if score == 0:
                break
        self.recent.append(best)
        return best

    def frag(self, template, ctx=None, scopes=None, tile=None):
        """Expand a fragment (no capitalisation or final full stop)."""
        c = {"moon_line": self.w.moon_line}
        if tile is not None:
            c.update(tile.flavour)
        c.update(ctx or {})
        return self.g.expand(template, c, scopes if scopes is not None else self.scopes())

    def pick(self, items, key=None):
        return self.g.pick(items, key)

    def dir_phrase(self, src, dst):
        dx, dy = dst[0] - src[0], dst[1] - src[1]
        dist = abs(dx) + abs(dy)
        if dist == 0:
            return "right here"
        ang = math.degrees(math.atan2(-dy, dx)) % 360
        names = ["east", "north-east", "north", "north-west", "west", "south-west", "south", "south-east"]
        d = names[int((ang + 22.5) // 45) % 8]
        far = ("a short walk to the" if dist <= 3 else "a few hours to the" if dist <= 7
               else "a long way to the" if dist <= 12 else "far, far to the")
        return f"{far} {d}"

    # ------------------------------------------------------------ locations
    def opening(self, pos, came_from=None, direction=None):
        """Arrival transition when the land changes, a travel line within a region,
        or a plain establishing sentence."""
        w = self.w
        t = w.tiles[pos]
        sc = self.scopes(t.biome, t.mood)
        if came_from is not None:
            prev = w.tiles[came_from]
            if prev.biome != t.biome:
                a, b = prev.biome, t.biome
                return self.say("{arrive}", scopes=[f"{a}>{b}", f">{b}", f"{a}>"] + sc + [a], tile=t)
            if prev.region == t.region and self.rng.random() < 0.45:
                return self.say("{onward}", dict(dir=direction, region=w.region_of(pos)["name"]), sc, t)
        return self.say("{opening}", scopes=sc, tile=t)

    def merge_sentences(self, sents):
        """Occasionally fuse two short sentences, for rhythm."""
        out, i = [], 0
        while i < len(sents):
            a = sents[i]
            if (i + 1 < len(sents) and len(a) < 75 and len(sents[i + 1]) < 75 and a.endswith(".")
                    and not sents[i + 1].startswith(("I ", "\"")) and self.rng.random() < 0.3
                    and not set(C.repeated_words(a + " " + sents[i + 1])) - set(C.repeated_words(a)) - set(C.repeated_words(sents[i + 1]))):
                b = sents[i + 1]
                joiner = self.frag("{joiner}")
                out.append(a[:-1] + joiner + b[0].lower() + b[1:])
                i += 2
            else:
                out.append(a)
                i += 1
        return out

    def location(self, pos, brief=False, came_from=None, direction=None):
        w = self.w
        t = w.tiles[pos]
        sc = self.scopes(t.biome, t.mood)
        dark, fog = w.is_dark, w.weather == "fog"
        out = []

        # paragraph 1: the land itself
        first = self.opening(pos, came_from, direction)
        p = []
        visual = ["flora_line", "terrain"] + ([] if dark or fog else ["vista"])
        senses = ["sense_sound", "sense_smell", "smalllife"]
        sky = ["light_line", "weather_line"]
        self.rng.shuffle(visual)
        self.rng.shuffle(senses)
        # the sky only needs describing when it has changed (or now and then, to keep it present)
        sky_key = (w.weather, w.time_of_day)
        fresh = sky_key != getattr(self, "last_sky", None)
        mention_sky = fresh or self.rng.random() < 0.2
        if mention_sky:
            self.last_sky = sky_key
        first_sky = [self.rng.choice(sky)] if mention_sky else []
        if brief:
            beats = first_sky + [(senses if dark else visual)[0]]
            if not mention_sky:
                beats.append(senses[0] if not dark else senses[1])
        else:
            beats = first_sky + visual[: (1 if dark else 2)] + senses[: (2 if dark else 1)]
            if mention_sky and fresh and not dark and self.rng.random() < 0.5:
                beats.insert(1, sky[1] if beats[0] == sky[0] else sky[0])
            extras = (["weather_detail"] if mention_sky else []) + ["time_life", "season_line", "mood_line"]
            self.rng.shuffle(extras)
            beats += extras[: self.rng.choice([1, 1, 2])]
        for b in beats:
            p.append(self.say("{" + b + "}", scopes=sc, tile=t))
        p = self.merge_sentences(p)
        # sometimes lead with the sky rather than the land
        if not brief and came_from is None and self.rng.random() < 0.25:
            p.insert(1, first)
        else:
            p.insert(0, first)
        out.append(" ".join(p))

        # paragraph 2: features and site
        p = []
        feats = t.features if not brief else t.features[:1]
        for f in feats:
            p.append(self.feature_line(f, sc, t.biome))
        for f in t.features:           # something waiting at a landmark shows itself when its moment comes
            h = SEC.hint(self, f)
            if h and self.rng.random() < 0.7:
                p.append(h)
        if t.site:
            p.extend(self.site_lines(t.site, brief))
        if p:
            out.append(" ".join(p))

        # paragraph 3: exits
        out.append(self.exits(pos))

        # paragraph 4: who and what is here
        p = [self.creature_presence(c) for c in t.creatures]
        for n in t.npcs:
            p.append(self.npc_presence(n))
            if n.mem["met"]:
                p.append(self.recognise(n))
        p += [self.item_presence(i) for i in t.items]
        p += ST.marks(w, pos)
        if p:
            out.append(" ".join(p))
        exits = [d for d, n in w.neighbours(pos) if n in w.land]
        out.append(f"[Exits: {', '.join(exits)}]")
        return out

    def header(self, pos):
        t = self.w.tiles[pos]
        name = title(self.w.region_of(pos)["name"])
        if t.site and t.site["kind"] == "village":
            name = f"{t.site['name']}, {name}"
        return name

    def feature_ctx(self, f, biome=None):
        adjphrase = [f.adjs[0], f.adjs[1], f"{f.adjs[1]}, {f.adjs[0]}"]
        return dict(noun=f.noun, adjp=adjphrase, verb=f.verb, where=f.where, d=self.fitting(f.details, biome))

    def fitting(self, details, biome=None):
        """Fixed details that are true right now (no 'not a ripple' in the rain, no rainbow at night)."""
        w = self.w
        scored = [(len(C.context_clashes(d, w.season, w.weather, w.time_of_day, biome)), d) for d in details]
        ok = [d for n, d in scored if n == 0]
        return ok or [min(scored)[1]]

    def moment(self, f, biome=None):
        """How this landmark looks right now: the most striking current condition that has a line."""
        kind = f.archetype
        tag = LM.TAG.get(kind)
        for cond in LM.conditions(self.w):
            key = self.g.lookup(cond, [f"lm:{kind}"]) or (self.g.lookup(cond, [f"lm:{tag}"]) if tag else None)
            if key and key != cond:
                return self.say("{%s}" % key, dict(noun=f.noun), [], None if biome is None else _Biome(biome))
        return ""

    def feature_line(self, f, sc, biome=None):
        frames = ["{adjp.a.cap} {noun} {verb} {where}, {d}.",
                  "{you_notice} {adjp.a} {noun}, which {verb} {where}.",
                  "There is {adjp.a} {noun} here, {d}.",
                  "{adjp.a.cap} {noun} {verb} {where}.",
                  "{adjp.a.cap} {noun} - {d} - {verb} {where}.",
                  "Not far off, {adjp.a} {noun} {verb} {where}.",
                  "The eye goes to {adjp.a} {noun}, {d}.",
                  "{adjp.a.cap} {noun} catches your attention: {d}.",
                  "Off to one side, {adjp.a} {noun} {verb} {where}.",
                  "Here, {adjp.a} {noun} {verb} {where}, {d}.",
                  "One thing stands out: {adjp.a} {noun}, {d}.",
                  "{adjp.a.cap} {noun} {verb} {where} - {d}.",
                  "Close by, {adjp.a} {noun}; {d}."]
        if not f.where.startswith(PREP_WORDS):
            frames += ["{where.cap} {verb} {adjp.a} {noun}.", "{where.cap} {verb} {adjp.a} {noun}, {d}.",
                       "{where.cap}, {adjp.a} {noun} {verb}.", "Just {where}, {adjp.a} {noun} {verb}, {d}."]
        # striking openers ("One thing stands out...") are noticed when they recur: use them sparingly
        loud = ("Not far off", "The eye goes", "catches your attention", "Off to one side", "One thing stands out", "Close by", "Just {where}")
        weighted = [(fr, 0.35 if any(x in fr for x in loud) else 1.0) for fr in frames]
        line = self.say(self.g.choose("featframe", weighted), self.feature_ctx(f, biome), sc)
        if self.rng.random() < 0.4:
            extra = self.moment(f, biome)
            if extra:
                line += " " + extra
        return line

    def feature_full(self, f, biome):
        c = self.feature_ctx(f, biome)
        fit = self.fitting(f.details, biome)
        now = self.moment(f, biome)
        if len(fit) >= 2:
            d1, d2 = fit[:2]
        else:       # a detail is false right now: let the moment take its place
            d1 = fit[0]
            d2 = (now[0].lower() + now[1:].rstrip(".")) if now else self.pick(["little else of note", "nothing more to it than that"])
        c.update(a1=f.adjs[0], a2=f.adjs[1], d1=d1, d2=d2)
        frames = ["The {noun} {verb} {where}. It is {a1} and {a2}. {d1.cap}; {d2}.",
                  "You take a closer look at the {noun}: {a2}, {a1}, {d1}. Looking longer, you notice {d2}.",
                  "Up close, the {a1} {noun} is {a2}. You see {d2}, and {d1}.",
                  "The {noun} rewards attention. {d1.cap}. {d2.cap}. It is unmistakably {a1}."]
        s = self.say(self.pick(frames, "featfull"), c, self.scopes(biome))
        s = s.replace("You see its", "Its").replace("you notice its", "you notice that its")
        return s + (" " + now if now and len(fit) >= 2 else "")

    # ------------------------------------------------------------ sites
    def economy_line(self, site):
        """Show the village's trade - mostly through concrete signs, sometimes by name."""
        signs = site.get("signs") or V.ECONOMY_SIGNS.get(site.get("economy"), [])
        if signs and self.rng.random() < 0.7:
            return self.pick(signs, f"signs{site['name']}")
        trade = self.pick([site.get("economy"), site.get("economy2") or site.get("economy")], f"trade{site['name']}")
        return self.say(self.pick(V.ECONOMY_NAMED, "econnamed"), dict(economy=trade))

    def site_lines(self, site, brief=False):
        k = site["kind"]
        if k == "village":
            c = dict(site)
            out = [self.say("{village_line}", c)]
            if not brief:
                out.append(self.say("{village_centre}", c))
                out.append(self.economy_line(site))
            trouble, fest = LV.trouble_lines(self, site), LV.festival_lines(self, site)
            if fest:
                out += fest
            elif trouble:
                out += trouble
            else:
                out.append(self.say("{night_village}" if self.w.is_dark else "{village_mood_%s}" % site["mood"], c))
            if trouble and fest:
                out += trouble
            return out
        if k == "ruin":
            c = dict(site, a_purpose=article(site["purpose"]))
            out = [self.say("{ruin_line}", c)]
            if not brief:
                out.append(self.say("{ruin_detail}", c))
            if site.get("quest"):
                out.append(self.pick(["Something about this place feels heavier than the rest, as though it is guarding a secret.",
                                      "The air here thrums faintly, like a plucked string.",
                                      "You sense that this is a place of power - and of danger."]))
            return out
        if k == "shrine":
            c = dict(site, a_form=article(site["form"]))
            out = [self.say("{shrine_line}", c), self.say("{shrine_offer}", c)]
            if site.get("used"):
                out.append(self.pick(["The shrine feels quiet now, its blessing spent.", "Whatever power dwelt here has already answered you."]))
            else:
                out.append(self.pick(["You feel you could pray here.", "It seems to invite a prayer.", "A sense of patient welcome hangs about it."]))
            return out
        if k == "camp":
            return [self.say("{camp_line}")]
        return []

    # ------------------------------------------------------------ exits
    def exits(self, pos):
        w, rng = self.w, self.rng
        t = w.tiles[pos]
        groups = {}
        for d, n in w.neighbours(pos):
            nt = w.tiles[n]
            kind = "water" if nt.biome == "lake" else "same" if nt.region == t.region else "diff"
            groups.setdefault((kind, nt.region), []).append((d, nt))
        same = [(reg, ds) for (k, reg), ds in groups.items() if k == "same"]
        diff = [(reg, ds) for (k, reg), ds in groups.items() if k == "diff"]
        water = [(reg, ds) for (k, reg), ds in groups.items() if k == "water"]
        rng.shuffle(diff)
        here_sc = self.scopes(t.biome)
        here_region = w.regions[t.region]["name"]
        lines = []

        def known(reg):
            return any(w.tiles[p].visited and w.tiles[p].region == reg for p in w.land)

        # one sentence for "the same land continues here, but changes there"
        if same and diff and len(same[0][1]) <= 2 and rng.random() < 0.45:
            _, sd = same.pop(0)
            reg, dd = diff.pop(0)
            nt = dd[0][1]
            lines.append(self.say("{exit_pair}", dict(
                sdirs=join_words(d for d, _ in sd), ddirs=join_words(d for d, _ in dd),
                land=self.frag("{land}", None, here_sc, t),
                glimpse=self.frag("{glimpse}", None, self.scopes(nt.biome), nt)), here_sc, t))
        for reg, ds in same:
            nt = ds[0][1]
            if len(ds) >= 3:
                others = [d for d in ("north", "south", "east", "west") if d not in {x for x, _ in ds}]
                but = "" if not others else self.pick([f", except to the {others[0]}", f" - all but the {others[0]}", f", save to the {others[0]}",
                                                       f", the {others[0]} excepted", f", except toward the {others[0]}", f" (bar the {others[0]})"], "but")
                lines.append(self.say("{exit_surround}", dict(but=but, region=here_region), here_sc, t))
            else:
                lines.append(self.say("{exit_same}", dict(dirs=join_words(d for d, _ in ds), region=here_region), self.scopes(nt.biome), nt))
        for reg, ds in diff:
            nt = ds[0][1]
            tmpl = "{exit_diff_named}" if (known(reg) or rng.random() < 0.4) else "{exit_diff}"
            lines.append(self.say(tmpl, dict(dirs=join_words(d for d, _ in ds), region=w.regions[reg]["name"]), self.scopes(nt.biome), nt))
        for reg, ds in water:
            nt = ds[0][1]
            lines.append(self.say("{exit_water}", dict(dirs=join_words(d for d, _ in ds)), self.scopes(nt.biome), nt))
        rng.shuffle(lines)
        return " ".join(lines)

    # ------------------------------------------------------------ creatures
    def creature_np(self, c, definite=False):
        if c.boss:
            return title(c.title) if not definite else title(c.title)
        name_words = set(c.species["name"].replace("-", " ").split())
        adjs = [a for a in (c.trait, c.species["size"], c.species["colour"]) if not set(a.replace("-", " ").split()) & name_words]
        adj = self.pick(adjs or [c.species["size"]], f"cadj{id(c)}")
        np = f"{adj} {c.species['name']}"
        return ("the " + c.species["name"]) if definite else article(np)

    def creature_presence(self, c):
        if c.boss:
            return self.say("{name} is here: {a_big} with {mark}. It {idle}.",
                            dict(name=title(c.title), a_big=article(f"colossal {c.species['name']}"),
                                 mark=c.species["mark"], idle=c.species["habits"]))
        it = mind.intent(c)
        if it != "wander":
            return self.say("{intent_presence}", dict(a_c=self.creature_np(c)), [it])
        idle = list(c.species["habits"]) + list(c.species["arch"]["idle"])[:2]
        return self.say("{presence}", dict(a_creature=self.creature_np(c), idle=idle))

    def mind_line(self, key, c, **extra):
        """Narration for a creature's change of mind or intent-driven action."""
        return self.say("{%s}" % key, dict(the_c=self.creature_np(c, True), a_c=self.creature_np(c), **extra))

    def creature_full(self, c):
        sp, a = c.species, c.species["arch"]
        hp = c.hp / c.maxhp
        health = ("It looks unhurt." if hp > 0.95 else "It carries a few wounds." if hp > 0.6
                  else "It is badly hurt." if hp > 0.25 else "It is close to death, barely standing.")
        mood = self.say("{intent_desc}", {}, [mind.intent(c)])
        ctx = dict(n=sp["name"], size="monstrous" if c.boss else sp["size"], cov=a["covering"], col=sp["colour"], mark=sp["mark"],
                   trait=c.trait, habit=sp["habits"])
        frames = ["The {n} is {size}, its {cov} {col}. Most striking is {mark}. This one is {trait}.",
                  "A {trait}, {size} beast with {col} {cov}. You note {mark}. It {habit}.",
                  "You study the {n}: {col} {cov}, {mark}, and a {size} frame. It is {trait}, even for its kind.",
                  "It is {a_trait} {n}, {size}, with {col} {cov} and {mark}."]
        ctx["a_trait"] = article(c.trait)
        name = (title(c.title) + ". ") if c.boss else ""
        return name + self.say(self.pick(frames, "cfull"), ctx) + " " + health + " " + mood

    def aggro(self, c):
        return self.say("{aggro_line}", dict(the_creature=self.creature_np(c, True)))

    # ------------------------------------------------------------ npcs
    def npc_presence(self, n):
        L_ = n.look
        if not n.known:   # you can see what they do, not what they're called
            desc = [f"{L_['age']} {n.job} with {L_['hair']}", f"{L_['build']} {n.job} in {L_['clothes']}",
                    f"{L_['age']}, {L_['build']} {n.job}"]
            return self.say("{npc_presence_anon}", dict(a_desc=article(self.pick(desc)), job=n.job, **n.pronouns()), self.role_scopes(n))
        desc = [f"{L_['age']}, {L_['build']} {self.pick(['figure', 'soul', 'person', 'local'])}",
                f"{L_['build']} {self.pick(['figure', 'soul', 'person'])} in {L_['clothes']}",
                f"{L_['age']} {n.job} with {L_['hair']}"]
        return self.say("{npc_presence}", dict(name=n.name, a_desc=article(self.pick(desc)), job=n.job, **n.pronouns()), self.role_scopes(n))

    def role_scopes(self, n):
        """What someone is doing depends on their role, and on whether it is night."""
        return ([f"{n.role}_dark"] if self.w.is_dark else []) + [n.role]

    def npc_full(self, n):
        L_ = n.look
        ctx = dict(name=n.name, sur=L_["surname"], age=L_["age"], build=L_["build"], hair=L_["hair"],
                   clothes=L_["clothes"], mark=L_["mark"], dem=n.demeanour, job=n.job)
        ctx.update(n.pronouns())
        frames = ["{name} {sur} is {age} and {build}, with {hair}, dressed in {clothes}. You notice {mark}. {he.cap} seems {dem}.",
                  "The {job} - {name} {sur}, you gather - is {build}, {age}, with {hair}. {clothes.cap} and {mark} complete the picture.",
                  "You take in {name}: {age}, {build}, wearing {clothes}. The detail that stays with you is {mark}. {his.cap} manner is {dem}."]
        if not n.known:
            frames = ["The {job} is {age} and {build}, with {hair}, dressed in {clothes}. You notice {mark}. {he.cap} seems {dem}.",
                      "This {job} is {build} and {age}, with {hair}. {clothes.cap} and {mark} complete the picture. You don't know {his} name.",
                      "You take in the {job}: {age}, {build}, wearing {clothes}. The detail that stays with you is {mark}. {his.cap} manner is {dem}."]
            return self.say(self.pick(frames, "npcfull_anon"), ctx)
        return self.say(self.pick(frames, "npcfull"), ctx)

    def greet(self, n, player):
        """First meeting: a temperament greeting and introductions. Later: a greeting
        coloured by how they feel about you and how long you've been away."""
        m, day = n.mem, self.w.day
        if m["met"] == 0:
            return self.say("{greet}", {}, [n.demeanour]) + " " + self.say("{ask_name}", dict(player=player, **n.pronouns()))
        addr = player if m["knows_name"] else self.pick(["stranger", "traveller", "friend"])
        gap = day - m["last_day"]
        if gap >= 3:
            gap_line = self.say("{mem_long_gap}")
        elif gap == 0:
            gap_line = self.pick(["Back so soon?", "Twice in one day!", "Forgotten something?"])
        else:
            gap_line = self.pick([f"It's been {gap} day{'s' if gap > 1 else ''}.", "Keeping well?", "Still in one piece, I see."])
        line = self.say("{return_greet}", dict(addr=addr, name=n.name, gap=["again", "once more", "back again"], gap_line=gap_line, **n.pronouns()), [n.tier])
        if gap >= 3 and gap_line not in line:
            line += " " + gap_line
        return line

    def recognise(self, n):
        return self.say("{recognise_line}", dict(name=n.name, **n.pronouns()), [n.tier])

    def memory_remark(self, n, deeds, player_has_relic):
        """Pick the most important thing this person remembers but hasn't mentioned."""
        w, m = self.w, n.mem
        if player_has_relic and not any(e["kind"] == "relic_seen" for e in m["events"]):
            n.remember("relic_seen", said=True)
            return self.say("{mem_deed_relic}", dict(thing=w.relic.name, name=n.name))
        # news of deeds: heard if nearby, or once a day has passed for it to travel
        while m["deeds_heard"] < len(deeds):
            d = deeds[m["deeds_heard"]]
            dist = abs(d["pos"][0] - n.home[0]) + abs(d["pos"][1] - n.home[1])
            if d["day"] >= w.day and dist > 4:
                break
            m["deeds_heard"] += 1
            if d["kind"] == "boss":
                n.like(3)
                return self.say("{mem_deed_boss}", dict(thing=d["thing"]))
            if dist <= 5:
                n.like(1)
                return self.say("{mem_deed_kill}", dict(a_thing=article(d["thing"]), where=d["where"]))
        for e in reversed(m["events"]):
            if e["said"]:
                continue
            if e["kind"] == "shrine":
                if w.tiles[e["pos"]].site.get("used"):
                    e["said"] = True
                    return self.say("{mem_shrine}", dict(spirit=e["spirit"]))
                continue
            if e["kind"] in ("bought", "sold", "gift") and e["day"] < w.day:
                e["said"] = True
                return self.say("{mem_%s}" % e["kind"], dict(thing=e["thing"], name=n.name, **n.pronouns()))
        return None

    def rumour_options(self, n, here):
        w, r = self.w, self.rng
        opts = []
        q = w.tiles[w.quest_pos]
        opts.append(("quest", f"the {w.relic.name} lies in a {q.site['state']} {q.site['purpose']} {self.dir_phrase(here, w.quest_pos)}, "
                              f"in {w.region_of(w.quest_pos)['name']}. Something old guards it.", None))
        for sp in w.species:
            homes = [p for p in w.land if any(c.species is sp for c in w.tiles[p].creatures)]
            if homes:
                p = min(homes, key=lambda p: abs(p[0] - here[0]) + abs(p[1] - here[1]))
                opts.append((f"sp:{sp['name']}", f"there's {article(sp['name'])} out in {w.region_of(p)['name']}, {self.dir_phrase(here, p)}. "
                                                 f"{cap(self.pick(['you will know it by', 'look for', 'mind', 'watch out for']))} {sp['mark']}.", None))
        for v in w.villages:
            if v != here:
                s = w.tiles[v].site
                trade = s.get("economy2") if (s.get("economy2") and r.random() < 0.4) else s["economy"]
                tail = self.pick([f"They live by {trade} there, and the trading's fair.", f"Good {trade} country, that.",
                                  f"Ask there if you need anything to do with {trade}.", f"It's a {trade} place - you'll smell it before you see it.",
                                  f"Folk there are mostly in {trade}; decent sorts.", f"My cousin went there for the {trade} and never came back. Happily, I mean."], "vtail")
                opts.append((f"v:{v}", f"{s['name']} lies {self.dir_phrase(here, v)}. {tail}", None))
        for p in w.land:
            s = w.tiles[p].site
            if s and s["kind"] == "shrine" and not s["used"]:
                opts.append((f"shrine:{p}", f"if you're hurt, pray at the shrine of {s['spirit']}, {self.dir_phrase(here, p)}. It has mended many.",
                             dict(kind="shrine", pos=p, spirit=s["spirit"])))
            if s and s["kind"] == "ruin" and not s.get("quest"):
                opts.append((f"ruin:{p}", f"there's an old {s['purpose']} {self.dir_phrase(here, p)}, {s['state']}. Folk say there's still things worth finding in it.", None))
        lore = [f"the weather's turning. My {self.pick(['knee', 'back', 'old scar'])} says so.",
                "the old roads aren't safe after dark. Never were.",
                f"this {w.season} feels wrong somehow. The birds know it.",
                "you should never whistle in a fen. Calls things up.",
                "my grandmother saw the sky burn green, the year the relic went."]
        opts.append((f"lore:{w.day}:{n.name}", self.pick(lore), None))
        r.shuffle(opts)
        fresh = [(k, t[0].lower() + t[1:].rstrip("."), None) for k, t in LV.news(w, here)]   # fresh news first
        return fresh[::-1] + opts

    def rumour(self, n, here):
        """A rumour this person hasn't told you yet, or None if they're out of news."""
        told = n.mem["told"]
        for key, text, event in self.rumour_options(n, here):
            if key not in told:
                told.append(key)
                if event:
                    n.remember(event.pop("kind"), day=self.w.day, **event)
                return self.say("{rumour_frame}", dict(rumour=text))
        return None

    def out_of_news(self, n, player):
        addr = player if n.mem["knows_name"] else "traveller"
        return self.say("{mem_out_of_news}", dict(addr=addr))

    # ------------------------------------------------------------ items
    def item_np(self, it, a=True):
        return article(it.name) if a else it.name

    def item_presence(self, it):
        frames = ["{a_item.cap} lies {where_i}.", "Lying {where_i} is {a_item}.", "{a_item.cap} has been left here.",
                  "You spot {a_item} {where_i}."]
        return self.say(self.pick(frames, "itempres"), dict(
            a_item=self.item_np(it),
            where_i=["half-hidden in the grass", "on the ground", "nearby", "in the mud", "among the stones", "at your feet"]))

    def item_full(self, it):
        f = it.facts
        if it.kind == "weapon":
            heft = "light and quick" if it.dmg <= 2 else "well balanced" if it.dmg <= 5 else "heavy and brutal"
            intro = self.pick([f"You turn the {f['noun']} over in your hands. It feels {heft}.",
                               f"{cap(article(it.name))}, {heft} in the hand.",
                               f"It is {article(it.name)}, and it feels {heft}."])
            body = " ".join(self.rng.sample(f["details"], len(f["details"])))
            return tidy(f"{intro} {body} {f.get('hist', '')}") + f"  (damage {it.dmg}, worth ~{it.value} coins)"
        if it.kind == "armour":
            intro = self.pick([f"{cap(article(it.name))}.", f"You hold up the {it.name} and look it over.", f"It is {article(it.name)}."])
            return tidy(f"{intro} {f['detail']} {f.get('hist', '')}") + f"  (protection {it.df}, worth ~{it.value} coins)"
        if it.kind == "herb":
            return self.say(self.pick(["A {name}, with {look}. It smells green and medicinal.",
                                       "You examine the {name}: {look}. Hedge-wise folk chew it for wounds.",
                                       "The {name} has {look}. It might ease an injury."], "herbfull"),
                            dict(name=it.name, look=f["look"])) + f"  (heals ~{it.heal})"
        if it.kind == "potion":
            return self.say(self.pick(["It comes in {vessel}. The liquid is {colour} and smells of {smell}.",
                                       "Through {vessel} you see a {colour} liquid. Unstoppered, it smells of {smell}.",
                                       "{vessel.cap}, holding a draught that is {colour}, with a whiff of {smell}."], "potfull"),
                            dict(f)) + f"  (heals ~{it.heal})"
        if it.kind == "food":
            return self.pick([f"{cap(article(it.name))}. Your stomach takes an interest.",
                              f"{cap(article(it.name))}, a little travel-worn but edible.",
                              f"Plain food: {article(it.name)}. Better than nothing on the road."]) + f"  (heals ~{it.heal})"
        if it.kind == "trinket":
            return self.pick([f"{cap(article(it.name))} {f['detail']}. Someone once treasured it.",
                              f"You turn the {it.name} over in the light. It is a small thing, {f['detail']}.",
                              f"{cap(article(it.name))}, {f['detail']}. It would fetch a few coins."]) + f"  (worth ~{it.value} coins)"
        if it.kind == "token":
            return self.pick([f"The {it.name}. It isn't yours to keep; someone is waiting for it.",
                              f"You turn the {it.name} over. It carries {f.get('glow', 'a weight beyond its size')}. It belongs somewhere else."])
        if it.kind == "relic":
            return self.pick([f"The {it.name}. Wrought of {f['material']}, it gives off {f['glow']}. It feels important in a way you can't name.",
                              f"You hold the {it.name}: {f['material']}, heavier than it should be, and alive with {f['glow']}."])
        return cap(article(it.name)) + "."

    def use_item(self, it):
        if it.kind == "herb":
            return self.pick([f"You chew the {it.name}. It tastes bitter, then numbing, and the pain recedes.",
                              f"You crush the {it.name} and press it to your hurts. A cool tingling spreads.",
                              f"The {it.name} is foul-tasting, but warmth spreads through your limbs."])
        if it.kind == "potion":
            return self.pick([f"You drink the {it.facts['colour']} draught. It tastes of {it.facts['smell']} and burns pleasantly going down.",
                              f"You knock back the draught. Heat floods your chest, and your wounds itch as they knit.",
                              f"The {it.facts['colour']} liquid slides down your throat. For a moment the world tilts, then steadies, and you feel stronger."])
        return self.pick([f"You eat the {it.name}, slowly, savouring it.", f"You wolf down the {it.name}.",
                          f"You sit a moment and eat the {it.name}. It does you good."])

    # ------------------------------------------------------------ combat
    def player_attack(self, outcome, weapon, c):
        cls = weapon.cls if weapon else "fist"
        wname = f"your {weapon.facts.get('noun', weapon.name)}" if weapon else "your fist"
        ctx = dict(weapon=wname, target=self.creature_np(c, True),
                   part=c.species["arch"]["parts"])
        return self.say("{%s}" % outcome, ctx, [cls])

    def enemy_attack(self, outcome, c, armour):
        ctx = dict(attacker=self.creature_np(c, True), attackverb=c.species["arch"]["attacks"],
                   armour=(armour.name.split()[-1] if armour else "skin"))
        return self.say("{%s}" % outcome, ctx)

    def death(self, c):
        return self.say("{the_c.cap} {death}.", dict(the_c=self.creature_np(c, True), death=c.species["arch"]["death"]))

    def flee(self, ok, c):
        return self.say("{flee_ok}" if ok else "{flee_fail}", dict(attacker=self.creature_np(c, True)))

    # ------------------------------------------------------------ sky
    def sky(self, pos):
        t = self.w.tiles[pos]
        sc = self.scopes(t.biome, t.mood)
        return " ".join(self.say("{%s}" % k, scopes=sc, tile=t) for k in ("light_line", "weather_line", "season_line"))
