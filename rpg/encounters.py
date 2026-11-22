"""Meetings on the road.

When you walk into wild country there is a small chance of an encounter: a
person, a creature or something stranger, with a choice to make. Some can only
happen once; some only at night, or in certain country. What you choose is
remembered - in the chronicle, and in what people say about you.
"""
from . import story as S
from .textgen import article

CHANCE = 0.11


def possible(g):
    w = g.world
    t = w.tiles[g.pos]
    b, dark = t.biome, w.is_dark
    seen = g.encounters_seen
    out = []
    for key, (once, biomes, when, weight) in DECK.items():
        if once and key in seen:
            continue
        if biomes and b not in biomes:
            continue
        if when == "night" and not dark or when == "day" and dark:
            continue
        if when == "fog" and w.weather != "fog":
            continue
        if when == "rain" and w.weather not in ("rain", "drizzle", "storm"):
            continue
        out.append((key, weight))
    return out


def maybe(g):
    """Called after arriving somewhere. Starts at most one encounter."""
    w = g.world
    t = w.tiles[g.pos]
    if g.combat or g.pending or t.site or t.creatures or g.over:
        return
    turns = getattr(g, "turns", 0)
    if turns - g.last_encounter_turn < 6 or g.rng.random() > CHANCE:
        return
    opts = possible(g)
    if not opts:
        return
    key = g.rng.choices([k for k, _ in opts], [wt for _, wt in opts])[0]
    g.encounters_seen.add(key)
    g.last_encounter_turn = turns
    g.emit("")
    START[key](g)


# ------------------------------------------------------------------ the encounters
def deserter(g):
    S.ask(g, "A man in a torn soldier's coat sits by the track with his head in his hands. He starts up when he sees you, then sags. \"I'm not going back,\" he says. \"I'd rather starve.\"",
          [("Share your food with him", "enc", dict(k="deserter_feed")), ("Tell him the way to the nearest village", "enc", dict(k="deserter_way")),
           ("Threaten to turn him in unless he pays", "enc", dict(k="deserter_rob")), ("Walk on", "enc", dict(k="walk"))], leave=3)


def pilgrims(g):
    w = g.world
    shrines = [p for p in w.land if w.tiles[p].site and w.tiles[p].site["kind"] == "shrine"]
    if not shrines:
        return wanderer(g)
    s = min(shrines, key=lambda p: abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]))
    S.ask(g, f"Three pilgrims in grey, staffs in hand, are arguing over the way. \"The shrine of {w.tiles[s].site['spirit']},\" the eldest tells you. \"Do you know the road? These hills are no place for old feet alone.\"",
          [("Offer to lead them there", "enc", dict(k="pilgrims_lead", shrine=s)), ("Point the way and wish them luck", "enc", dict(k="pilgrims_point")),
           ("Walk on", "enc", dict(k="walk"))], leave=2)


def cart(g):
    S.ask(g, "A carter's wagon is stuck to the axles in mud, the horse straining, the carter red-faced and swearing at everything.",
          [("Put your shoulder to the wheel", "enc", dict(k="cart_push")), ("Offer advice from a safe distance", "enc", dict(k="cart_advise")),
           ("Walk on", "enc", dict(k="walk"))], leave=2)


def child(g):
    w = g.world
    v = min(w.villages, key=lambda p: abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]))
    from .world import PRONOUNS
    gender = g.rng.choice(["female", "male"])
    pr = PRONOUNS[gender]
    S.ask(g, f"A small {'girl' if gender == 'female' else 'boy'} is sitting on a stone, very determinedly not crying. \"I followed a hare,\" {pr['he']} explains, \"and then it was gone and I don't know where {w.tiles[v].site['name']} is.\"",
          [(f"Take {pr['him']} home", "enc", dict(k="child_home", village=v, gender=gender)), ("Point the way", "enc", dict(k="child_point", village=v, gender=gender))], leave=1)


def pedlar(g):
    S.ask(g, "A pedlar with a tray of charms round his neck falls into step with you. \"Lucky charms, love-knots, wolf-teeth against the evil eye! Two coins, and fortune smiles!\"",
          [("Buy a charm (2 coins)", "enc", dict(k="charm_buy")), ("Haggle", "enc", dict(k="charm_haggle")), ("Send him on his way", "enc", dict(k="walk"))], leave=2)


def wild_hunt(g):
    S.ask(g, "Hoofbeats, though there's no road. Horns, very far off and getting nearer. Across the sky - or just above the trees - comes a hunt of pale riders and hounds with red ears.",
          [("Throw yourself flat and hide", "enc", dict(k="hunt_hide")), ("Stand and watch them pass", "enc", dict(k="hunt_watch")),
           ("Call out to them", "enc", dict(k="hunt_call"))], leave=0)


def wedding(g):
    S.ask(g, "A wedding party comes along the track with pipes and a drum, the bride and groom in borrowed finery, everyone a little drunk already. \"Join us, stranger! It's bad luck to pass a wedding!\"",
          [("Join the dancing", "enc", dict(k="wedding_join")), ("Give the couple a gift", "enc", dict(k="wedding_gift")),
           ("Wish them well and pass by", "enc", dict(k="wedding_pass"))], leave=2)


def thief(g):
    S.ask(g, "A lad comes pelting down the track with a goose under his arm and a furious woman far behind him, shouting \"Thief! Stop him!\"",
          [("Trip him", "enc", dict(k="thief_trip")), ("Step aside and let him go", "enc", dict(k="thief_let"))], leave=1)


def hermit_fire(g):
    S.ask(g, "A small fire burns in a hollow, and an old woman beside it waves you over. \"Sit, sit. Nobody should walk alone at night. I've a story, if you've an ear.\"",
          [("Sit by the fire and listen", "enc", dict(k="fire_sit")), ("Thank her and go on", "enc", dict(k="walk"))], leave=1)


def bandits(g):
    S.ask(g, "Two figures step out from behind a rock, cudgels in hand, scarves over their faces. \"Toll road,\" says one. \"Ten coins, or we take it out of your hide.\"",
          [("Pay them", "enc", dict(k="bandit_pay")), ("Fight", "enc", dict(k="bandit_fight")), ("Talk your way out", "enc", dict(k="bandit_talk"))], leave=None)


def hound(g):
    S.ask(g, "A big shaggy hound limps out of the undergrowth, a thorn deep in one paw. It looks at you, and whines.",
          [("Pull out the thorn", "enc", dict(k="hound_help")), ("Back away carefully", "enc", dict(k="walk"))], leave=1)


def dying(g):
    w = g.world
    npcs = [n for v in w.villages for n in w.tiles[v].npcs]
    if not npcs:
        return wanderer(g)
    kin = g.rng.choice(npcs)
    tg = g.rng.choice(["female", "male"])
    S.ask(g, f"A {'woman' if tg == 'female' else 'man'} lies by the path, pale, a wound under {'her' if tg == 'female' else 'his'} cloak that won't stop bleeding. \"Please,\" {'she' if tg == 'female' else 'he'} whispers. \"My kin - {kin.name}, in {w.tiles[kin.home].site['name']}. Tell them… tell them I was coming home.\"",
          [("Promise to carry the message", "enc", dict(k="dying_yes", kin=kin.name, tg=tg)), ("Try to tend the wound", "enc", dict(k="dying_tend", kin=kin.name, tg=tg))], leave=0)


def shepherd(g):
    S.ask(g, "A shepherd, staff in hand, is scanning the slopes with a worried frown. \"Lost a ewe in the night. Best of the flock. Seen her? White, with a black ear?\"",
          [("Help look for her", "enc", dict(k="ewe_look")), ("Shake your head and go on", "enc", dict(k="walk"))], leave=1)


def ghost_march(g):
    S.ask(g, "Out of the dark comes a column of marching men, armour rusted through, making no sound at all. They pass close enough to touch. None of them looks at you.",
          [("Stand still and let them pass", "enc", dict(k="march_still")), ("Fall in behind them", "enc", dict(k="march_follow"))], leave=0)


def troll_bridge(g):
    S.ask(g, "Where the path crosses a stream on two planks, something big and grey and mossy sits on the far bank, chewing. \"Bridge is mine,\" it rumbles. \"Pay, or answer.\"",
          [("Pay with food", "enc", dict(k="troll_food")), ("Answer its riddle", "enc", dict(k="troll_riddle")), ("Wade across further down", "enc", dict(k="troll_wade"))], leave=2)


def wanderer(g):
    S.ask(g, "Another traveller is coming the other way, a pack on their back, humming. They nod. \"Fair road?\"",
          [("Swap news", "enc", dict(k="news")), ("Nod and pass", "enc", dict(k="walk"))], leave=1)


def mushroom_woman(g):
    S.ask(g, "An old woman with a basket of fungi straightens up from the leaf litter. \"Want to know which are safe? A copper and I'll tell you everything.\"",
          [("Pay a coin and learn", "enc", dict(k="fungi_learn")), ("Decline politely", "enc", dict(k="walk"))], leave=1)


def storm_shelter(g):
    S.ask(g, "Rain hammers down. Under a rock overhang a tinker and his donkey are sheltering, and he shifts over to make room. \"Plenty of dry for two. Three, counting Blossom.\"",
          [("Shelter with them until it eases", "enc", dict(k="shelter_wait")), ("Press on through the rain", "enc", dict(k="walk"))], leave=1)


# key: (only once?, biomes (None = any), when, weight)
DECK = {
    "deserter": (True, None, "day", 2), "pilgrims": (True, ("plains", "hills", "forest"), "day", 2), "cart": (False, ("plains", "marsh", "forest"), "day", 2),
    "child": (True, ("plains", "forest", "hills"), "day", 2), "pedlar": (False, None, "day", 1), "wild_hunt": (True, ("forest", "hills", "plains"), "night", 2),
    "wedding": (True, ("plains", "forest"), "day", 1), "thief": (False, ("plains", "forest"), "day", 1), "hermit_fire": (False, None, "night", 2),
    "bandits": (False, ("forest", "hills", "plains"), None, 2), "hound": (True, ("forest", "hills"), None, 1), "dying": (True, None, None, 1),
    "shepherd": (True, ("hills", "plains"), "day", 2), "ghost_march": (True, ("marsh", "plains", "hills"), "night", 1),
    "troll_bridge": (True, ("forest", "hills", "marsh"), None, 1), "wanderer": (False, None, None, 2), "mushroom_woman": (True, ("forest",), "day", 1),
    "storm_shelter": (False, ("hills", "peaks", "plains"), "rain", 3),
}
START = {"deserter": deserter, "pilgrims": pilgrims, "cart": cart, "child": child, "pedlar": pedlar, "wild_hunt": wild_hunt, "wedding": wedding,
         "thief": thief, "hermit_fire": hermit_fire, "bandits": bandits, "hound": hound, "dying": dying, "shepherd": shepherd,
         "ghost_march": ghost_march, "troll_bridge": troll_bridge, "wanderer": wanderer, "mushroom_woman": mushroom_woman, "storm_shelter": storm_shelter}


# ------------------------------------------------------------------ outcomes
@S.choice_handler("enc")
def outcome(g, d):
    OUT[d["k"]](g, d)


def _walk(g, d):
    g.emit(g.narr.pick(["You walk on.", "You leave them behind.", "You go on your way."]))


def _deserter_feed(g, d):
    food = next((i for i in g.player.inv if i.kind == "food"), None)
    if food:
        g.player.inv.remove(food)
        fname = food.name
    elif getattr(g.player, "rations", 0) > 0:          # a travel ration will do
        g.player.rations -= 1
        fname = "travel ration"
    else:
        g.emit("You have no food to give. He laughs, not unkindly. \"Nor me. Good luck to you.\"")
        return
    g.emit(f"You give him your {fname}. He eats it in four bites. \"I won't forget,\" he says, and from the look of him, he means it.")
    g.deserter_helped = True
    S.record(g, "You fed a starving deserter on the road.", "deed", story="you fed a starving deserter on the road, and asked nothing", like=1)
    if g.rng.random() < 0.6:
        it = g.world.make_item(2, "weapon")
        g.player.inv.append(it)
        g.emit(f"Before you go he presses his old {it.facts.get('noun', 'blade')} on you. \"Better in your hands. I'm done with it.\" ({article(it.name)})")


def _deserter_way(g, d):
    g.emit("You point him toward the nearest village and tell him who might give a man work. He listens hard, nods, and is off.")
    S.record(g, "You set a deserter on the road to a new life.", "deed")


def _deserter_rob(g, d):
    gold = g.rng.randint(2, 6)
    g.player.gold += gold
    g.emit(f"He empties his pockets: {gold} coins and some lint. He doesn't look at you as you go.")
    S.record(g, "You shook down a starving deserter.", "deed", story="you robbed a starving man on the road", like=-2)


def _pilgrims_lead(g, d):
    S.new_quest(g, "escort", "The pilgrims", "Lead the three pilgrims to their shrine", dict(xp=20, buff=("blessed", 48), chronicle="You led three pilgrims safely to their shrine.",
                                                                                            story="you guided three old pilgrims all the way to their shrine", story_like=2),
                target=tuple(d["shrine"]), companion=dict(name="the pilgrims"), source="pilgrims",
                data=dict(done_text="The pilgrims kneel at the shrine, weeping and laughing. The eldest blesses you with a hand that shakes."))


def _pilgrims_point(g, d):
    g.emit("You point the way. The eldest thanks you and blesses you briskly, as if blessings were cheap where she comes from.")
    S.add_buff(g, "blessed", 6)


def _cart_push(g, d):
    g.pass_time(40)
    gold = g.rng.randint(3, 8)
    g.player.gold += gold
    g.emit(f"You heave, the horse heaves, the carter swears creatively, and with a great sucking sound the wagon comes free - spraying you with mud. The carter gives you {gold} coins and a turnip.")
    from .world import Item
    g.player.inv.append(Item("food", "turnip", value=2, heal=2))
    S.record(g, "You helped a carter out of the mud.", "deed", story="you put your shoulder to a stuck cart and got a bath of mud for your trouble", like=1)


def _cart_advise(g, d):
    g.emit("You suggest putting branches under the wheels. The carter's reply is not fit to repeat. You leave him to it.")


def _child_home(g, d):
    v = tuple(d["village"])
    site = g.world.tiles[v].site
    S.new_quest(g, "escort", "The lost child", f"Take the child home to {site['name']}", dict(gold=6, xp=15, village_like=2,
                                                                                          chronicle=f"You brought a lost child home to {site['name']}.",
                                                                                          story=f"you brought a lost child home to {site['name']}", story_like=3),
                target=v, companion=dict(name="the child"), source="child",
                data=dict(done_text="The child's mother comes running, scolds {0}, hugs {0}, scolds {0} again, and presses coins on you.".format(
                    "her" if d.get("gender") == "female" else "him")))


def _child_point(g, d):
    g.emit(f"You point the way and the child sets off, chin up. You watch until {'she' if d.get('gender') == 'female' else 'he'}'s out of sight, and hope.")


def _charm_buy(g, d):
    if g.player.gold < 2:
        return g.emit("You haven't two coins to rub together. The pedlar loses interest at once.")
    g.player.gold -= 2
    if g.rng.random() < 0.5:
        S.add_buff(g, "lucky", 48)
        g.emit("You buy a wolf-tooth on a string. Strangely, you do feel luckier. (Luck for two days.)")
    else:
        g.emit("You buy a love-knot. It falls apart in an hour. You have been had.")
        S.record(g, "A pedlar sold you a useless charm.", "mishap", story="you paid good coin for a pedlar's rubbish charm", like=0)


def _charm_haggle(g, d):
    if g.rng.random() < 0.5:
        S.add_buff(g, "lucky", 24)
        g.emit("You haggle him down to nothing. He throws up his hands and gives you a charm for free, just to be rid of you. (Luck for a day.)")
    else:
        g.emit("You haggle. He haggles better. You leave with nothing and an obscure feeling of defeat.")


def _hunt_hide(g, d):
    g.emit("You throw yourself into the heather. The hunt passes over, a gale of cold and hoofbeats and baying. When you dare to look up, it's gone, and frost has formed on your back.")


def _hunt_watch(g, d):
    if g.rng.random() < 0.5:
        S.add_buff(g, "fae", 24)
        g.emit("You stand your ground and watch. The leader - antlered, beautiful, terrible - looks down at you as they pass, and nods, as one hunter to another. (Fae favour for a day.)")
    else:
        dmg = g.rng.randint(2, 5)
        g.player.hp = max(1, g.player.hp - dmg)
        g.emit(f"You watch, and a red-eared hound breaks from the pack to snap at you in passing. It's gone before you can lift a hand. ({dmg} damage)")
    S.record(g, "You saw the Wild Hunt ride.", "magic", story="you saw the Wild Hunt ride and lived", like=1, reach=10)


def _hunt_call(g, d):
    w = g.world
    far = [p for p in w.land if 4 <= abs(p[0] - g.pos[0]) + abs(p[1] - g.pos[1]) <= 7 and not (w.tiles[p].site and w.tiles[p].site.get("quest"))]
    if far:
        g.pos, g.combat = g.rng.choice(far), None
    g.pass_time(180)
    g.emit("You call out. The hunt turns. A cold hand catches you up, and for a while you ride the wind with the hounds - and then you are dropped, gasping, in country you don't recognise.")
    S.record(g, "You rode with the Wild Hunt.", "magic", story="you rode with the Wild Hunt, and they let you go", like=1, reach=12)
    g.show_location()


def _wedding_join(g, d):
    g.pass_time(90)
    g.player.hp = g.player.maxhp
    g.emit("You dance until you're dizzy, eat until you're stuffed, and are kissed by at least one aunt. (Fully healed.)")
    S.record(g, "You danced at a wedding on the road.", "deed", story="you danced at a road wedding like one of the family", like=1)


def _wedding_gift(g, d):
    gift = next((i for i in g.player.inv if i.kind in ("trinket", "food", "herb")), None)
    if not gift:
        return g.emit("You have nothing to give but your good wishes. They take those gladly.")
    g.player.inv.remove(gift)
    S.add_buff(g, "lucky", 48)
    g.emit(f"You give the couple your {gift.name}. The bride kisses your cheek; the groom shakes your hand till it aches. (Luck for two days.)")
    S.record(g, "You gave a wedding gift to strangers.", "deed", story="you gave a wedding gift to two strangers on the road", like=2)


def _wedding_pass(g, d):
    g.emit("You wish them joy. The piper plays you a little tune as you go.")


def _thief_trip(g, d):
    gold = g.rng.randint(3, 7)
    g.player.gold += gold
    g.emit(f"You stick out a foot. Lad, goose and dignity go flying. The woman arrives, retrieves her goose, boxes the lad's ears and gives you {gold} coins.")
    S.record(g, "You caught a goose thief.", "deed", story="you tripped a goose thief and returned the goose", like=1)


def _thief_let(g, d):
    g.emit("You step aside. The lad flashes you a grin as he passes. The woman, arriving, gives you a look that could curdle milk.")
    g.goose_thief_owes = True


def _fire_sit(g, d):
    w, n = g.world, g.narr
    g.pass_time(60)
    g.player.hp = min(g.player.maxhp, g.player.hp + 6)
    if g.has_quest:
        tale = f"She tells you what she knows. {w.quest.lore(g)}"
    else:
        tale = "She tells you a long story about a king under a hill, and a relic stolen from a village, and an old one still waiting for someone to bring it home."
    g.emit(f"You sit by the fire. It's warm, and her voice is warm. {tale} When you wake it is later, the fire is ash, and she is gone. (+6 HP)")


def _bandit_pay(g, d):
    paid = min(10, g.player.gold)
    g.player.gold -= paid
    g.emit(f"You hand over {paid} coins. They melt back behind the rock, laughing.")


def _bandit_fight(g, d):
    p = g.player
    odds = 0.35 + 0.06 * (p.atk + p.df) + 0.04 * p.level
    if g.rng.random() < odds:
        dmg = g.rng.randint(1, 5)
        gold = g.rng.randint(8, 20)
        p.hp = max(1, p.hp - dmg)
        p.gold += gold
        g.emit(f"It's short and ugly. One runs, the other limps after him, and they leave a purse behind: {gold} coins. ({dmg} damage)")
        S.record(g, "You fought off two highwaymen.", "deed", story="you fought off two highwaymen single-handed", like=2)
        for m in p.gain_xp(12):
            g.emit(m)
    else:
        dmg = g.rng.randint(5, 10)
        p.hp = max(1, p.hp - dmg)
        lost = min(p.gold, 10)
        p.gold -= lost
        g.emit(f"They're better at this than you hoped. You end up face-down in the dirt, {lost} coins lighter. ({dmg} damage)")


def _bandit_talk(g, d):
    if g.klass() in ("rogue", "cleric") or g.rng.random() < 0.4:
        g.emit("You talk. You mention mutual friends, a magistrate's cousin, and a curse on anyone who robs a traveller. By the end they're apologising.")
    else:
        g.emit("You try. They aren't listening.")
        _bandit_fight(g, d)


def _hound_help(g, d):
    g.emit("You ease the thorn out. The hound licks your hand, then trots ahead of you a little way and stops, looking back, as if to say: this way.")
    from .secrets import plant_cache
    target = plant_cache(g, 1, 3)
    if target:
        tp, tf = target
        S.new_quest(g, "find", "Follow the hound", f"The hound led you toward the {tf.noun}. Search it", dict(gold=0), target=tp, source="hound",
                    data=dict(noun=tf.noun, search=True))
    S.record(g, "You helped a lame hound.", "deed")


def _dying_yes(g, d):
    kin = S.find_npc(g.world, d["kin"])
    g.emit(f"You promise. The traveller smiles, and {'her' if d.get('tg') == 'female' else 'his'} eyes go still, looking at something past you.")
    if kin:
        S.new_quest(g, "bring", "A last message", f"Tell {kin.name} in {g.world.tiles[kin.home].site['name']} that {kin.pronouns()['his']} {'kinswoman' if d.get('tg') == 'female' else 'kinsman'} was coming home",
                    dict(like=6, xp=15, chronicle=f"You carried a dying traveller's last words to {kin.name}.",
                         story=f"you carried a dying stranger's last words all the way to {kin.name}", story_like=2),
                    giver=kin, source="dying", data=dict(message=True, done_text=f"{kin.name} hears you out in silence, then sits down very slowly. \"Thank you for telling me. Thank you.\""))
    S.record(g, "A traveller died by the road in your arms.", "event", mark="A low mound of stones by the path marks where a traveller died.")


def _dying_tend(g, d):
    herb = next((i for i in g.player.inv if i.heal), None)
    if herb and g.rng.random() < 0.6:
        g.player.inv.remove(herb)
        g.emit(f"You press your {herb.name} into the wound and bind it tight. Slowly the bleeding stops. The traveller lives - and limps off toward home, blessing you at every step.")
        S.record(g, "You saved a dying traveller.", "deed", story="you saved a traveller who was bleeding to death by the road", like=3)
    else:
        g.emit("You do what you can. It isn't enough.")
        _dying_yes(g, d)


def _ewe_look(g, d):
    g.pass_time(60)
    if g.rng.random() < 0.65:
        g.emit("You find her wedged in a gully, bleating crossly. The shepherd is so grateful he gives you his lunch.")
        from .world import Item
        g.player.inv.append(Item("food", "wedge of ewe's cheese", value=5, heal=5))
        S.record(g, "You found a shepherd's lost ewe.", "deed", story="you found a shepherd's lost ewe in a gully", like=1)
    else:
        g.emit("You search for an hour and find nothing but sheep that aren't her. The shepherd thanks you anyway.")


def _march_still(g, d):
    g.emit("You stand absolutely still. The column passes, rank after rank, until the last of them fades into the dark. Your breath is smoking. Your hands are shaking.")
    S.record(g, "You watched the dead march past.", "magic", story="you saw the dead march past at night", like=0, reach=10)


def _march_follow(g, d):
    S.add_buff(g, "cursed", 6)
    g.pass_time(120)
    g.emit("You fall in behind them. For a while it seems like the most natural thing in the world. Then you are alone, in the cold, and you've lost two hours and some warmth you won't get back soon. (Cursed for a while.)")


def _troll_food(g, d):
    food = next((i for i in g.player.inv if i.kind == "food"), None)
    if not food:
        g.emit("You have no food. The troll looks disappointed in you, personally, and you wade across downstream.")
        return _troll_wade(g, d)
    g.player.inv.remove(food)
    g.emit(f"You toss it your {food.name}. It catches it, sniffs, eats it. \"Good,\" it rumbles, and moves aside.")


def _troll_riddle(g, d):
    if g.rng.random() < 0.55:
        gold = g.rng.randint(5, 15)
        g.player.gold += gold
        g.emit(f"\"What has a bed but never sleeps, a mouth but never eats?\" You think. \"A river.\" The troll sighs and throws you {gold} coins, its own toll money. \"Clever. Go on.\"")
        S.record(g, "You beat a troll at riddles.", "deed", story="you beat a bridge-troll at riddles", like=1, reach=10)
    else:
        dmg = g.rng.randint(3, 6)
        g.player.hp = max(1, g.player.hp - dmg)
        g.emit(f"You get it wrong. The troll, delighted, throws you in the stream. ({dmg} damage)")


def _troll_wade(g, d):
    g.pass_time(30)
    S.add_buff(g, "soaked", 3)
    g.emit("You wade across further down, up to your waist in cold water. The troll watches you the whole way, chewing.")


def _news(g, d):
    from . import living
    items = living.news(g.world, g.pos)
    if items:
        text = g.rng.choice(items)[1]
        g.emit(f"\"Did you hear? {text}\" they say, and you tell them what you've seen in turn.")
    else:
        g.emit("You swap news. Theirs is mostly about the weather. So is yours.")


def _fungi_learn(g, d):
    if g.player.gold < 1:
        return g.emit("You have no copper. She tells you one thing for free: \"If in doubt, don't.\"")
    g.player.gold -= 1
    g.knows_fungi = True
    g.emit("For a copper she tells you everything: ceps and chanterelles, death-caps and destroying angels. You'll never eat a bad mushroom again.")


def _shelter_wait(g, d):
    g.pass_time(120)
    g.player.hp = min(g.player.maxhp, g.player.hp + 5)
    g.emit("You wait out the rain with the tinker and his donkey, who leans on you companionably. The tinker tells terrible jokes. (+5 HP)")


OUT = {"walk": _walk, "deserter_feed": _deserter_feed, "deserter_way": _deserter_way, "deserter_rob": _deserter_rob,
       "pilgrims_lead": _pilgrims_lead, "pilgrims_point": _pilgrims_point, "cart_push": _cart_push, "cart_advise": _cart_advise,
       "child_home": _child_home, "child_point": _child_point, "charm_buy": _charm_buy, "charm_haggle": _charm_haggle,
       "hunt_hide": _hunt_hide, "hunt_watch": _hunt_watch, "hunt_call": _hunt_call, "wedding_join": _wedding_join,
       "wedding_gift": _wedding_gift, "wedding_pass": _wedding_pass, "thief_trip": _thief_trip, "thief_let": _thief_let,
       "fire_sit": _fire_sit, "bandit_pay": _bandit_pay, "bandit_fight": _bandit_fight, "bandit_talk": _bandit_talk,
       "hound_help": _hound_help, "dying_yes": _dying_yes, "dying_tend": _dying_tend, "ewe_look": _ewe_look,
       "march_still": _march_still, "march_follow": _march_follow, "troll_food": _troll_food, "troll_riddle": _troll_riddle,
       "troll_wade": _troll_wade, "news": _news, "fungi_learn": _fungi_learn, "shelter_wait": _shelter_wait}
