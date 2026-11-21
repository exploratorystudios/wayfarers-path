#!/usr/bin/env python3
"""Launch the procedurally generated text RPG.

  python3 play.py                 open the game in your web browser (default)
  python3 play.py --port 9000     ...on a different port
  python3 play.py --no-browser    start the server without opening a browser
  python3 play.py --classic [seed]      play in the terminal instead
  python3 play.py --classic --load X    resume save slot X in the terminal
"""
import sys

from rpg.game import Game


def ask(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)


def classic(args):
    if args[:1] == ["--load"]:
        slot = args[1] if len(args) > 1 else "autosave"
        try:
            return Game.load(slot).run(resumed=True)
        except Exception as e:
            print(f"Couldn't load '{slot}': {e}")
            return
    seed = int(args[0]) if args and args[0].isdigit() else None
    saves = Game.list_saves()
    if saves and seed is None:
        print("Saved games: " + ", ".join(p.stem for p in saves))
        slot = ask("Type a save name to continue it, or press Enter for a new world: ")
        if slot:
            try:
                return Game.load(slot).run(resumed=True)
            except Exception as e:
                print(f"Couldn't load '{slot}': {e}. Starting a new world.")
    name = ask("What is your name, traveller? (Enter for 'Wanderer', ? for a random one) ") or None
    while name == "?":
        import random as _r
        from rpg.names import gen
        cand = gen().generate(_r.Random(), _r.choice(["Archaic", "Westron", "Northish", "Southron"]), _r.choice(["female", "male"]))
        name = ask(f"How about {cand}? (Enter to accept, ? for another, or type your own) ") or cand
    from rpg.classes import CLASSES, ABILITIES
    keys = list(CLASSES)
    print()
    for i, k in enumerate(keys, 1):
        c = CLASSES[k]
        print(f"  {i}. {c['name']:7} ({c['difficulty']}) - {c['blurb']}")
        print(f"     {', '.join(ABILITIES[a]['label'] for a in c['abilities'])}; {c['passive'][0]}: {c['passive'][1]}")
    pick = ask("Choose a class [1-5, Enter for Knight]: ")
    klass = keys[int(pick) - 1] if pick.isdigit() and 1 <= int(pick) <= len(keys) else (pick.lower() if pick.lower() in CLASSES else "knight")
    Game(seed=seed, name=name, klass=klass).run()


def main():
    args = sys.argv[1:]
    if "--classic" in args:
        args.remove("--classic")
        return classic(args)
    from rpg.web import serve
    port = 8765
    if "--port" in args:
        i = args.index("--port")
        port = int(args[i + 1])
    serve(port=port, open_browser="--no-browser" not in args)


if __name__ == "__main__":
    main()
