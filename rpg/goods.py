"""Trade goods: what each trade sells, the tools, draughts and charms, and stalls that restock.

Every seller's stock follows their job: a smith sells blades and mail, a
fletcher arrows, a hedge-witch herbs and charms, a pedlar a bit of everything.
Some village folk (smith, fletcher, wise-woman...) keep a small stall too, open
once you've met them. Stalls restock every few days, and what's on them follows
the season.

Goods that do something when used carry facts["use"]; `use()` runs them.
"""
from .textgen import cap, article

# name -> kind, value, use, what it does (shown on examine), how it looks
GOODS = {
    "pot of oak-gall ink": dict(kind="reagent", value=12, use=None,
                                desc="Black ink made from oak galls. A spellcrafter writes a new spell out with it before the spell will hold.",
                                looks=["a stoppered clay pot of black ink", "a little horn pot of ink, sealed with wax"]),
    "bundle of beeswax candles": dict(kind="reagent", value=10, use=None,
                                      desc="Good beeswax, the kind burned at shrines. A prayer is composed by their light, or not at all.",
                                      looks=["six honey-coloured candles tied with string", "a bundle of beeswax candles that smells of summer"]),
    "whetstone": dict(kind="tool", value=8, use="hone", desc="Ten minutes' work puts a fresh edge on your weapon: harder blows for half a day. It wears away with use.",
                      looks=["a grey stone worn hollow in the middle", "a fine-grained stone in a leather sleeve"]),
    "set of lockpicks": dict(kind="tool", value=30, use="picks", uses=3,
                             desc="In a ruin or an abandoned camp, there may be a strongbox worth opening. Clumsy hands snap them.",
                             looks=["thin hooked picks in a roll of oilcloth", "a tinker's picks, each filed to a different shape"]),
    "quiver of fire arrows": dict(kind="tool", value=24, use="arrows", arrows="fire",
                                  desc="Light them and loose: your next three shots set what they hit burning. (You'll need to be someone who shoots.)",
                                  looks=["arrows with pitch-soaked rag wound behind the heads", "black-fletched arrows that smell of tar"]),
    "quiver of bodkin arrows": dict(kind="tool", value=22, use="arrows", arrows="bodkin",
                                    desc="Made for punching through mail: your next three shots ignore armour. (You'll need to be someone who shoots.)",
                                    looks=["narrow square-headed arrows, made for punching through mail", "heavy arrows with needle-like iron heads"]),
    "flask of holy water": dict(kind="tool", value=18, use="holy",
                                desc="Water blessed at a shrine. Thrown in a fight, it scalds, and the dead feel it three times over.",
                                looks=["a small flask stamped with a sun", "a pewter flask, cold to the touch"]),
    "smoke pot": dict(kind="tool", value=16, use="smoke",
                      desc="It bursts into thick smoke. Smash it mid-fight and you're gone before anyone can see where.",
                      looks=["a fist-sized clay pot sealed with wax", "a little crock with a fuse of waxed string"]),
    "draught of strength": dict(kind="potion", value=20, use="buff", buff=("strong", 12, 1),
                                desc="For half a day your blows land harder.", looks=["a brown, bitter-smelling draught in a squat bottle"]),
    "warding draught": dict(kind="potion", value=20, use="buff", buff=("warded", 12, 1),
                            desc="It tastes of iron. For half a day blows find it harder to land on you.", looks=["a grey, iron-smelling draught"]),
    "draught of fortune": dict(kind="potion", value=24, use="buff", buff=("lucky", 24, 1),
                               desc="Fizzes on the tongue. For a day, luck leans your way.", looks=["a pale gold draught that fizzes faintly"]),
    "draught of clarity": dict(kind="potion", value=22, use="clarity",
                               desc="It fills your well of mana, faith or stamina to the brim.", looks=["a draught as clear as snowmelt in a thin glass vial"]),
    "antidote": dict(kind="potion", value=14, use="cleanse",
                     desc="Foul and effective: it purges sickness, poison and bad luck.", looks=["a cloudy green draught that smells of crushed nettles"]),
    "rowan cross": dict(kind="charm", value=14, use="buff", buff=("warded", 48, 1),
                        desc="Carried, it turns ill aside for a couple of days, until the thread frays.",
                        looks=["two rowan twigs bound crosswise with red thread"]),
    "hare's-foot charm": dict(kind="charm", value=16, use="buff", buff=("lucky", 48, 1),
                              desc="Luck for a couple of days, they say.", looks=["a hare's foot on a leather thong, worn smooth"]),
    "witch-stone": dict(kind="charm", value=28, use="buff", buff=("fae", 24, 1),
                        desc="Look through it and the hidden folk notice you, kindly, for a day.",
                        looks=["a pale stone with a hole worn clean through it"]),
}

# food a trade makes: name, heal
TRADE_FOOD = {
    "miller": [("fresh loaf", 5), ("bag of oat flour cakes", 4)], "brewer": [("jug of brown ale", 4), ("flask of strong cider", 4)],
    "beekeeper": [("comb of wild honey", 6), ("pot of honey", 5)], "eel-catcher": [("strip of smoked eel", 4), ("eel pie", 6)],
    "shepherd": [("wedge of ewe's cheese", 5)], "swineherd": [("twist of salted pork", 5)], "spice-trader": [("packet of candied ginger", 4), ("twist of saffron cakes", 5)],
}

# what each trade sells: (maker, weight). makers: weapon[:type], armour[:kind], herb, potion, food, trinket, book, scroll, or a GOODS name
TRADES = {
    # merchants: a full stall
    "pedlar":  [("weapon", 2), ("armour", 1), ("herb", 2), ("potion", 1), ("food", 2), ("trinket", 2), ("book", 0.6), ("scroll", 0.6), ("whetstone", 0.6), ("smoke pot", 0.3),
                ("pot of oak-gall ink", 0.5), ("bundle of beeswax candles", 0.5)],
    "packman": [("weapon", 2), ("armour", 1), ("herb", 2), ("potion", 1), ("food", 2), ("trinket", 2), ("book", 0.6), ("scroll", 0.6), ("whetstone", 0.6), ("rowan cross", 0.4)],
    "trader":  [("weapon", 2), ("armour", 2), ("herb", 1), ("potion", 1), ("food", 2), ("trinket", 2), ("book", 0.5), ("whetstone", 0.6)],
    "huckster": [("trinket", 3), ("food", 2), ("herb", 1), ("potion", 1), ("weapon", 1), ("hare's-foot charm", 0.8), ("smoke pot", 0.5), ("draught of fortune", 0.4)],
    "tinker": [("whetstone", 2), ("set of lockpicks", 1.5), ("trinket", 2), ("weapon:dagger", 1), ("weapon", 1), ("smoke pot", 0.6)],
    "chandler": [("scroll", 2), ("book", 1), ("flask of holy water", 1.2), ("potion", 1), ("pot of oak-gall ink", 1.5), ("bundle of beeswax candles", 1.5)],
    "cloth-seller": [("armour:jerkin", 3), ("trinket", 2), ("rowan cross", 0.8)],
    "spice-trader": [("potion", 2), ("draught of strength", 1), ("draught of clarity", 1), ("draught of fortune", 0.8), ("antidote", 1), ("food", 1.2), ("scroll", 0.6)],
    "horse-coper": [("armour:jerkin", 1), ("food", 2), ("whetstone", 1), ("weapon:spear", 1), ("trinket", 1), ("hare's-foot charm", 0.6)],
    # village folk with a little stall of their own
    "smith": [("weapon:sword", 2), ("weapon:axe", 2), ("weapon:mace", 1.5), ("armour:mail", 2), ("armour:scale", 0.5), ("whetstone", 2)],
    "fletcher": [("quiver of fire arrows", 2), ("quiver of bodkin arrows", 2), ("weapon:spear", 1)],
    "hedge-witch": [("herb", 3), ("potion", 2), ("rowan cross", 1.5), ("witch-stone", 0.8), ("antidote", 1), ("draught of clarity", 0.8), ("bundle of beeswax candles", 0.6)],
    "wise-woman": [("herb", 3), ("potion", 2), ("rowan cross", 1.5), ("hare's-foot charm", 1), ("antidote", 1)],
    "wise-man": [("herb", 3), ("potion", 2), ("rowan cross", 1.5), ("hare's-foot charm", 1), ("antidote", 1)],
    "midwife": [("herb", 3), ("antidote", 2), ("potion", 1)],
    "tanner": [("armour:jerkin", 3)], "weaver": [("armour:jerkin", 2), ("trinket", 1)],
    "miller": [("food", 3)], "brewer": [("food", 3)], "beekeeper": [("food", 3)], "eel-catcher": [("food", 3)],
}
STALL_FOLK = {k for k in TRADES if k not in ("pedlar", "packman", "trader", "huckster", "tinker", "chandler", "cloth-seller", "spice-trader", "horse-coper")}
# a few words for what's on offer, used when you meet them
WARES_WORDS = {
    "smith": "blades and mail", "fletcher": "arrows", "hedge-witch": "herbs, draughts and charms", "wise-woman": "herbs and charms",
    "wise-man": "herbs and charms", "midwife": "herbs and remedies", "tanner": "leather", "weaver": "cloth coats and odds and ends",
    "miller": "bread", "brewer": "ale and cider", "beekeeper": "honey", "eel-catcher": "smoked eel",
}

SEASON_WEIGHT = {   # what the time of year puts on the stalls
    "spring": {"herb": 1.6, "food": 0.8}, "summer": {"herb": 2.0, "food": 1.2},
    "autumn": {"food": 1.6, "herb": 1.0}, "winter": {"herb": 0.4, "armour:jerkin": 1.8, "food": 0.7, "potion": 1.4},
}
RESTOCK_DAYS = 3


# how often each of the goods turns up as loot (lost, stashed or carried by someone who didn't need it any more)
LOOT_WEIGHT = {"whetstone": 3, "set of lockpicks": 1.2, "quiver of fire arrows": 1, "quiver of bodkin arrows": 1, "flask of holy water": 1.5,
               "smoke pot": 1.5, "draught of strength": 1.2, "warding draught": 1.2, "draught of fortune": 1, "draught of clarity": 1.2,
               "antidote": 1.5, "rowan cross": 1.5, "hare's-foot charm": 1.2, "witch-stone": 0.6,
               "pot of oak-gall ink": 1.5, "bundle of beeswax candles": 1.5}


def loot_pick(r):
    names = list(GOODS)
    return r.choices(names, [LOOT_WEIGHT.get(n, 1) for n in names])[0]


def recipe(job):
    return TRADES.get(job) or TRADES["pedlar"]


def sells(npc):
    return npc.role == "merchant" or npc.job in STALL_FOLK


def make(world, maker, danger, season=None, job=""):
    """One item for a stall."""
    from .world import Item
    r = world.rng
    if maker in GOODS:
        gd = GOODS[maker]
        facts = dict(use=gd["use"], desc=gd["desc"], look=r.choice(gd["looks"]))
        if gd["use"] is None:
            facts.pop("use")
        for k in ("buff", "arrows", "uses"):
            if k in gd:
                facts[k] = gd[k]
        return Item(gd["kind"], maker, value=gd["value"], facts=facts)
    if maker == "food" and job in TRADE_FOOD:
        name, heal = r.choice(TRADE_FOOD[job])
        return Item("food", name, value=heal + 1, heal=heal)
    base, _, sub = maker.partition(":")
    if base == "weapon":
        return world.make_item(danger, "weapon", wtype=sub or None)
    if base == "armour":
        return world.make_item(danger, "armour", akind=sub or None)
    return world.make_item(danger, base)


def stock(world, job, n, danger, season=None):
    """A stall's worth of goods for this trade, weighted by the season, with few repeats."""
    r = world.rng
    rec = recipe(job)
    sw = SEASON_WEIGHT.get(season or "", {})
    out, used = [], {}
    for _ in range(n):
        weights = [w * sw.get(m, sw.get(m.split(":")[0], 1.0)) / (1 + 1.5 * used.get(m, 0)) for m, w in rec]
        m = r.choices([m for m, _ in rec], weights)[0]
        used[m] = used.get(m, 0) + 1
        out.append(make(world, m, danger, season, job))
    return out


def stall_size(npc):
    return (4, 6) if npc.role == "merchant" else (2, 3)


def restock(g):
    """Every few days, sellers top their stalls back up with this season's goods."""
    w = g.world
    for v in w.villages:
        for npc in w.tiles[v].npcs:
            if not sells(npc):
                continue
            last = npc.mem.get("restocked", 1)
            if w.day - last < RESTOCK_DAYS:
                continue
            npc.mem["restocked"] = w.day
            from . import travel as TR
            if TR.sells_rations(npc):
                TR.restock(npc, g.rng)
            lo, hi = stall_size(npc)
            keep = [it for it in npc.stock if g.rng.random() < 0.6]       # some things sell to other folk
            want = g.rng.randint(lo, hi) - len(keep)
            npc.stock = keep + (stock(w, npc.job, want, 2 + w.day // 6, w.season) if want > 0 else [])


# ------------------------------------------------------------------ using goods
def usable(it):
    return bool(it.facts.get("use")) and it.kind in ("tool", "potion", "charm")


def describable(it):
    return it.kind in ("tool", "potion", "charm", "reagent") and "desc" in it.facts


def describe(it):
    f = it.facts
    return f"{cap(article(it.name))}: {f['look']}. {f['desc']}  (worth ~{it.value} coins)"


def use(g, it, rest=()):
    """Use a tool, draught or charm. Returns nothing; narrates."""
    from . import story as S
    from . import classes as K
    from . import arts as ARTS
    from . import mind
    p, f, w = g.player, it.facts, g.world
    kind = f["use"]
    spend = lambda: p.inv.remove(it)
    if kind == "buff":
        spend()
        S.add_buff(g, *f["buff"])
        g.emit({"potion": f"You drink the {it.name}. " + {"strong": "Heat runs down your arms.", "warded": "Your skin prickles, then hardens.",
                                                           "lucky": "You feel, absurdly, as if things will go your way."}.get(f["buff"][0], "You feel it take hold."),
                "charm": f"You hang the {it.name} about your neck and feel, for a moment, watched over."}.get(it.kind, f"You use the {it.name}."))
    elif kind == "clarity":
        spend()
        before = p.res
        p.res = p.res_max
        g.emit(f"You drink the {it.name}. The world goes very sharp and clear. (+{p.res - before} {K.res_name(p)})")
    elif kind == "cleanse":
        spend()
        gone = [b for b in ("cursed", "queasy", "soaked") if g.buffs.pop(b, None)]
        g.emit(f"You choke down the {it.name}." + (" " + ", ".join(S.BUFF_NAMES[b] for b in gone).capitalize() + " - gone." if gone else " You feel scoured clean, if nothing else."))
    elif kind == "hone":
        if g.combat:
            return g.emit("No time to sharpen anything now.")
        if not p.weapon:
            return g.emit("You've nothing to sharpen.")
        S.add_buff(g, "honed", 12)
        f["uses"] = f.get("uses", 3) - 1
        if f["uses"] <= 0:
            spend()
        g.emit(g.narr.pick([f"You sit and work the {p.weapon.facts.get('noun', p.weapon.name)} against the {it.name} until the edge sings.",
                            f"Ten patient minutes with the {it.name}, and your {p.weapon.facts.get('noun', p.weapon.name)} has a fresh bite to it."])
               + (" The stone is worn through." if f["uses"] <= 0 else ""))
        with g.hush():
            g.pass_time(10)
    elif kind == "arrows":
        if "shoot" not in K.known(p):
            return g.emit("You'd need a bow, and the knack of using one.")
        p.arrows = dict(kind=f["arrows"], left=3)
        spend()
        g.emit(f"You fill your quiver with {f['arrows']} arrows. (Your next three shots.)")
    elif kind == "holy":
        c = g.combat or (g.find(list(rest), [w.tiles[g.pos].creatures]) if rest else None)
        if c is None:
            return g.emit("Holy water is for throwing at something that deserves it.")
        spend()
        undead = c.species["arch"].get("undead", False)
        dmg = (6 + g.rng.randint(0, 3)) * (3 if undead else 1)
        c.hp -= dmg
        g.emit((f"The holy water hisses on {g.narr.creature_np(c, True)} like water on a forge, and it shrieks." if undead else
                f"You fling the holy water at {g.narr.creature_np(c, True)}. It stings, at least.") + f" ({dmg} damage)")
        K.finish_exchange(g, c, dmg)
    elif kind == "smoke":
        if not g.combat:
            return g.emit("Save it for when you need to disappear.")
        c = g.combat
        spend()
        g.combat = None
        p.hidden = 2
        m = mind.ensure(c)
        m["support"]["wander"] = max(m["support"].values()) + 0.1
        m["intent"] = "wander"
        g.emit(f"You smash the {it.name} at your feet. Thick grey smoke boils up, and by the time it thins you are somewhere else.")
    elif kind == "picks":
        t = w.tiles[g.pos]
        site = t.site
        if not site or site["kind"] not in ("ruin", "camp"):
            return g.emit("There's nothing here to pick. Strongboxes turn up in ruins and abandoned camps.")
        if g.combat:
            return g.emit("Not with something trying to kill you!")
        if site.get("box") == "open":
            return g.emit("You've already emptied whatever strongbox was here.")
        if "box" not in site:
            site["box"] = "locked" if g.rng.random() < 0.7 else "none"
        if site["box"] == "none":
            site["box"] = "open"
            return g.emit("You search for anything with a lock. There's nothing here worth picking.")
        chance = 0.45 + 0.08 * (ARTS.stat(p, "grace") - 4) + (0.3 if p.klass == "rogue" else 0)
        with g.hush():
            g.pass_time(20)
        if g.rng.random() < chance:
            site["box"] = "open"
            gold = g.rng.randint(10, 30) + 4 * t.danger
            loot = w.make_item(t.danger + 1)
            p.gold += gold
            p.inv.append(loot)
            g.emit(g.narr.pick([f"Under fallen stones you find an iron-bound box. A little patient work with the picks, a click, and it's open: {gold} coins and {article(loot.name)}.",
                                f"The lock on the old strongbox is rusted but simple. It gives with a satisfying clunk: {gold} coins and {article(loot.name)}."]))
        else:
            f["uses"] = f.get("uses", 3) - 1
            g.emit("You find a strongbox and work at the lock, but a pick snaps in it." + (" That was your last one." if f["uses"] <= 0 else " You could try again."))
            if f["uses"] <= 0:
                spend()
    if g.combat and kind not in ("holy", "smoke"):
        g.enemy_turn()
