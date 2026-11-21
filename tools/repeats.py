#!/usr/bin/env python3
"""Measure how much text repeats *across* worlds: what a player who starts a second run will notice.

Each world is played for a while by the suggestion engine (talking, questing, fighting, travelling),
and everything the game prints is collected. Then:

  overlap   - for pairs of runs, the share of one run's sentences that also appear in the other
  sentences - sentences found in many worlds, with names masked (so "Bring it home and Oakby will
              not forget you" and "... Stanbeck will not forget you" count as the same line)
  phrases   - 5-word runs of words found in many worlds, even inside different sentences

  python3 tools/repeats.py [worlds] [turns] [memory]   (defaults: 30 worlds, 150 turns each)
"""
import os
import random
import re
import sys
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path

os.environ["RPG_SAVE_DIR"] = tempfile.mkdtemp(prefix="variety-")          # a fresh phrasebook every time
MEMORY = "memory" in sys.argv[1:]
os.environ["RPG_PHRASEBOOK"] = "1" if MEMORY else "0"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rpg.game import Game            # noqa: E402
from rpg.advisor import suggest      # noqa: E402

SKIP = re.compile(r"^\s*(\(|\[|>|──|\*\*|Exits|Saves|  \d\.|\d\. )")
UI = re.compile(r"^[('\[]|Type '|for sale:|^You have \d+ coins|'buy |\(Luck|^Wherever you can|^This world is|never the same words")   # interface, not prose
STOP = set("a an the of and to in on at it is was you your his her its their with for from by as that this but or".split())


def play(seed, turns, klass):
    out = []
    g = Game(seed=seed, name="Tester", out=out.append, klass=klass)
    g.intro()
    rng = random.Random(seed)
    for _ in range(turns):
        if g.over:
            break
        g.player.hp = max(g.player.hp, g.player.maxhp // 2)       # keep the run going; we want words, not deaths
        sugs = [s for s in suggest(g) if not s.cmd.startswith(("save", "load", "quit"))]
        cmd = (sugs[0] if rng.random() < 0.75 or len(sugs) < 2 else rng.choice(sugs[:4])).cmd if sugs else "look"
        g.handle(cmd)
    g.narr.flush_phrases(force=True)          # (only kept when the phrasebook is on)
    names = {g.player.name}
    w = g.world
    names |= {r["name"] for r in w.regions}
    names |= {t.site["name"] for t in w.tiles.values() if t.site and t.site.get("name")}
    names |= {n.name for t in w.tiles.values() for n in t.npcs}
    names |= {w.relic.name, w.title}
    return out, names


def sentences(lines, names):
    for line in lines:
        for part in str(line).split("\n"):
            if not part.strip() or SKIP.match(part):
                continue
            text = part
            for n in sorted(names, key=len, reverse=True):          # mask names so templates line up
                if n and len(n) > 2:
                    text = text.replace(n, "#")
            for s in re.split(r"(?<=[.!?\"])\s+", text):
                s = s.strip()
                if len(s.split()) >= 4 and not UI.search(s):
                    yield s


def shingles(s, n=5):
    words = re.findall(r"[a-z'#-]+", s.lower())
    for i in range(len(words) - n + 1):
        sh = words[i:i + n]
        if sum(w not in STOP and w != "#" for w in sh) >= 2:
            yield " ".join(sh)


def opening(s, n=3):
    return " ".join(re.findall(r"[A-Za-z'#-]+", s)[:n]).lower()


def landmarks(seeds=range(9300, 9310)):
    """Examine (twice), climb and search every landmark in a few worlds; count sentence openings per verb."""
    stats = {}
    for seed in seeds:
        out = []
        g = Game(seed=seed, name="Tester", out=out.append, klass="ranger")
        w = g.world
        for p in [p for p in w.land if w.tiles[p].features][:6]:
            g.pos, g.combat = p, None
            w.tiles[p].creatures = []
            for f in w.tiles[p].features:
                for verb in ("examine", "examine", "climb", "search"):
                    out.clear()
                    g.handle(f"{verb} {f.noun.split()[-1]}")
                    g.combat, g.pending = None, None
                    text = " ".join(x for x in out if x and not SKIP.match(x)).replace("\n", " ")
                    for s in re.split(r"(?<=[.!?])\s+", text):
                        if s.strip():
                            stats.setdefault(verb, Counter())[opening(s)] += 1
    return {v: (sum(c.values()), c.most_common(3)) for v, c in stats.items()}


def main(worlds=30, turns=150):
    classes = ["knight", "ranger", "wizard", "rogue", "cleric"]
    per_world, phrase_world = [], []
    for i in range(worlds):
        lines, names = play(9000 + i, turns, classes[i % 5])
        ss = list(sentences(lines, names))
        per_world.append(ss)
        phrase_world.append({sh for s in ss for sh in shingles(s)})
        print(f"\rplayed {i + 1}/{worlds}", end="", file=sys.stderr)
    print(file=sys.stderr)

    sets = [set(s) for s in per_world]
    pairs = list(combinations(range(worlds), 2))
    shared = [len(sets[a] & sets[b]) / max(1, len(sets[a])) for a, b in pairs]
    seen = [sum(1 for s in per_world[a] if s in sets[b]) / max(1, len(per_world[a])) for a, b in pairs]
    sent_worlds = Counter(s for st in sets for s in st)
    phr_worlds = Counter(p for st in phrase_world for p in st)
    total = sum(len(s) for s in per_world)

    print(f"{worlds} worlds x {turns} turns: {total} sentences shown, {len(sent_worlds)} distinct (names masked)"
          f"{'  [phrase memory ON]' if MEMORY else ''}")
    before, seen_so_far = [], set()
    for k, ss in enumerate(per_world):
        if k:
            before.append(sum(1 for x in ss if x in seen_so_far) / max(1, len(ss)))
        seen_so_far |= set(ss)
    print(f"returning player: runs 2-3 showed {100 * sum(before[:2]) / 2:.1f}% already-seen sentences; "
          f"runs {worlds - 9}-{worlds}, {100 * sum(before[-10:]) / max(1, len(before[-10:])):.1f}%")
    print(f"run-to-run overlap: {100 * sum(shared) / len(shared):.1f}% of one run's distinct sentences also occur in another run;")
    print(f"                    {100 * sum(seen) / len(seen):.1f}% of the sentences a player reads were also in the other run")
    for k in (0.5, 0.25, 0.1):
        n = sum(1 for c in sent_worlds.values() if c >= k * worlds)
        print(f"sentences in >= {int(k * 100)}% of worlds: {n}")
    # frames inside one run: how much of the text opens the same few ways
    tops = []
    for ss in per_world:
        op = Counter(opening(x) for x in ss)
        tops.append(sum(c for _, c in op.most_common(10)) / max(1, len(ss)))
    print(f"within a run, the 10 commonest sentence openings start {100 * sum(tops) / len(tops):.1f}% of sentences")
    lm = landmarks()
    for verb, (n, top) in lm.items():
        print(f"landmark {verb}: {n} sentences; commonest opening '{top[0][0]}' is {100 * top[0][1] / max(1, n):.1f}%")
    print("\nmost widespread sentences (worlds):")
    for s, c in sent_worlds.most_common(30):
        print(f"  {c:3}  {s[:150]}")
    print("\nmost widespread 5-word phrases (worlds):")
    for p, c in phr_worlds.most_common(40):
        print(f"  {c:3}  {p}")


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:3] if x.isdigit()]
    main(*a)
