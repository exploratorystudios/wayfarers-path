#!/usr/bin/env python3
"""Repetition audit: what does a player see too often?

Plays several sessions following the advisor, then reports:
  1. phrases (5-word runs) repeated most within a single session
  2. "hot narrow" grammar symbols: used a lot, but with few options
  3. fixed-text lines (not from the grammar) that repeat

  4. fact variety: across freshly generated worlds, how often each fact value recurs

Usage: python3 tools/variety.py [sessions] [steps] [worlds]
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rpg.game import Game                     # noqa: E402
from rpg.advisor import suggest               # noqa: E402

SKIP = ("[", "──", "> ", "(", "  ", "@ you", "***", "**")


def sentences(lines):
    for line in lines:
        line = line.replace("\n", " ").strip()
        if not line or line.startswith(SKIP):
            continue
        yield from (s for s in re.split(r"(?<=[.!?\"])\s+", line) if len(s) > 12)


def grams(s, n=5):
    w = re.findall(r"[a-z'-]+", s.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def main(sessions=12, steps=300):
    classes = ["knight", "ranger", "wizard", "rogue", "cleric"]
    per_session = collections.Counter()      # phrase -> total within-session repeats
    sessions_with = collections.Counter()
    sent_repeat = collections.Counter()
    usage = collections.Counter()
    total_sents = 0
    for i in range(sessions):
        out = []
        g = Game(seed=1000 + i, name="Tester", out=out.append, klass=classes[i % 5])
        orig = g.narr.g.choose

        def counting(key, options, _orig=orig):
            usage[(key, len(options))] += 1
            return _orig(key, options)
        g.narr.g.choose = counting
        g.intro()
        for _ in range(steps):
            if g.over:
                break
            g.handle(suggest(g)[0].cmd)
        sents = list(sentences(out))
        total_sents += len(sents)
        counts = collections.Counter(gm for s in sents for gm in grams(s))
        for gm, c in counts.items():
            if c > 1:
                per_session[gm] += c - 1
                sessions_with[gm] += 1
        for s, c in collections.Counter(sents).items():
            if c > 1:
                sent_repeat[s] += c - 1
    print(f"{sessions} sessions, {total_sents} sentences\n")
    print("Most-repeated 5-word phrases within a session (avg extra uses per session):")
    for gm, c in per_session.most_common(30):
        print(f"  {c / sessions:6.1f}  {gm}")
    print("\nWhole sentences repeated within a session (avg per session):")
    for s, c in sent_repeat.most_common(15):
        print(f"  {c / sessions:6.1f}  {s[:100]}")
    print("\nHot narrow symbols (uses per session per option; higher = more repetitive):")
    ranked = sorted(((u / sessions / n, k, n, u / sessions) for (k, n), u in usage.items() if not k.startswith(("ctx:", "list:"))), reverse=True)
    for score, k, n, u in ranked[:25]:
        print(f"  {score:6.1f}  {k[:60]:60}  {n:3} options, {u:6.1f} uses/session")


def facts(worlds=150):
    """For each kind of fixed fact, the share taken by its single most common value
    (lower is better) and how many distinct values turned up."""
    from rpg.world import World
    seen = collections.defaultdict(collections.Counter)
    for i in range(worlds):
        w = World(5000 + i)
        for p in w.villages:
            v = w.tiles[p].site
            for k in ("economy", "economy2", "centre", "material", "roof"):
                seen["village " + k][v.get(k)] += 1
            for n in w.tiles[p].npcs:
                seen["npc job"][n.job] += 1
                seen["npc hair"][n.look["hair"]] += 1
                seen["npc mark"][n.look["mark"]] += 1
                seen["npc name"][n.name] += 1
        for t in w.tiles.values():
            if t.site and t.site["kind"] == "ruin":
                seen["ruin purpose"][t.site["purpose"]] += 1
            if t.site and t.site["kind"] == "shrine":
                seen["shrine spirit"][t.site["spirit"]] += 1
        seen["relic"][w.relic.name] += 1
        for r in w.regions:
            seen["region name word"][r["name"].replace("the ", "").split()[0]] += 1
    print(f"\nFact variety across {worlds} worlds (top value's share; lower = less samey):")
    for k, c in sorted(seen.items()):
        total = sum(c.values())
        top, n = c.most_common(1)[0]
        print(f"  {k:18} {100 * n / total:5.1f}%  ({len(c):3} distinct)  most common: {top}")


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:4]]
    main(*a[:2])
    facts(*a[2:3])
