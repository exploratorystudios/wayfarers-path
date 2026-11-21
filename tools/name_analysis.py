#!/usr/bin/env python3
"""Analyse the fantasy name lists, train the name model, and test what it makes.

Usage: python3 tools/name_analysis.py [--samples N]
Writes rpg/data/names_model.json.
"""
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from name_corpus import parse_strict          # noqa: E402
from rpg import names as N                     # noqa: E402


def pct(c, total):
    return f"{100 * c / total:4.1f}%"


def top(counter, k=10, total=None):
    total = total or sum(counter.values())
    return ", ".join(f"{a} {pct(b, total)}" for a, b in counter.most_common(k))


def main(samples=12):
    first, _ = parse_strict()
    cultures = list(first)
    every = [(c, g, n) for c in first for g in first[c] for n in first[c][g]]
    print(f"Corpus: {len(every)} first names, {len(cultures)} cultures x 2 genders\n")

    # ---------------------------------------------------------------- letters
    print("== Letter frequency (all names)")
    letters = Counter(ch for _, _, n in every for ch in n.lower())
    print("  " + top(letters, 26))
    print("\n== Letters most characteristic of each culture (log-odds against the others)")
    for c in cultures:
        mine = Counter(ch for cc, _, n in every if cc == c for ch in n.lower())
        rest = Counter(ch for cc, _, n in every if cc != c for ch in n.lower())
        tm, tr = sum(mine.values()), sum(rest.values())
        lo = {ch: math.log((mine[ch] + 1) / tm) - math.log((rest[ch] + 1) / tr) for ch in letters}
        hi = sorted(lo, key=lambda x: -lo[x])[:5]
        lo_ = sorted(lo, key=lambda x: lo[x])[:3]
        print(f"  {c:9s} more: {' '.join(f'{x}(x{math.exp(lo[x]):.1f})' for x in hi)}   fewer: {' '.join(f'{x}(x{math.exp(lo[x]):.2f})' for x in lo_)}")

    # ---------------------------------------------------------------- vowels & consonants
    print("\n== Vowels and consonants  (y counts as a vowel unless it glides before one)")
    for c in cultures:
        for g in ("female", "male"):
            ns = first[c][g]
            sks = [N.skeleton(n) for n in ns]
            v = sum(s.count("V") for s in sks) / sum(len(s) for s in sks)
            sv = sum(s[0] == "V" for s in sks) / len(sks)
            ev = sum(s[-1] == "V" for s in sks) / len(sks)
            cc = sum("CC" in s for s in sks) / len(sks)
            vv = sum("VV" in s for s in sks) / len(sks)
            print(f"  {c:9s} {g:6s}  vowels {v:.0%} of letters | start with a vowel {sv:.0%} | end with a vowel {ev:.0%} | "
                  f"has a CC cluster {cc:.0%} | has a vowel pair {vv:.0%}")
    print("\n== Commonest consonant/vowel shapes")
    for g in ("female", "male"):
        sk = Counter(N.skeleton(n) for c, gg, n in every if gg == g)
        print(f"  {g:6s}: " + top(sk, 8))

    # ---------------------------------------------------------------- syllables
    onsets = set()
    for _, _, n in every:
        lead = []
        for u, k in N.units(n):
            if k == "V":
                break
            lead.append(u)
        if lead:
            onsets.add("".join(lead))
    print("\n== Syllables per name, and length in letters")
    for c in cultures:
        for g in ("female", "male"):
            ns = first[c][g]
            sy = Counter(len(N.syllables(n, onsets)) for n in ns)
            ln = sum(len(n) for n in ns) / len(ns)
            print(f"  {c:9s} {g:6s}  " + "  ".join(f"{k} syl {pct(sy[k], len(ns))}" for k in sorted(sy)) + f"   avg {ln:.1f} letters")
    print("\n== Example syllabifications (maximal onset)")
    for n in ["Aelisabeth", "Christophyr", "Gioseppos", "Asljena", "Brokalina", "Naethynel"]:
        print("  " + n + " -> " + ".".join("".join(o + nu + co) for o, nu, co in N.syllables(n, onsets)))

    # ---------------------------------------------------------------- clusters and nuclei
    lead, bridge, coda, nuc = Counter(), Counter(), Counter(), Counter()
    for _, _, n in every:
        ss = N.syllables(n, onsets)
        lead["".join(ss[0][0]) or "(none)"] += 1
        for i in range(1, len(ss)):
            bridge["".join(ss[i - 1][2] + ss[i][0])] += 1
        coda["".join(ss[-1][2]) or "(none)"] += 1
        for s in ss:
            nuc["".join(s[1])] += 1
    print("\n== Word-initial consonants:   " + top(lead, 14))
    print("== Between vowels:            " + top(bridge, 14))
    print("== Word-final consonants:     " + top(coda, 10))
    print("== Syllable nuclei (vowels):  " + top(nuc, 14))

    # ---------------------------------------------------------------- gender marking
    print("\n== How gender is marked: the final letter")
    for c in cultures:
        for g in ("female", "male"):
            ends = Counter(n[-1] for n in first[c][g])
            print(f"  {c:9s} {g:6s}  " + top(ends, 6))
    print("\n== ...and the final syllable's rhyme")
    for g in ("female", "male"):
        r = Counter()
        for _, gg, n in every:
            if gg == g:
                o, nu, co = N.syllables(n, onsets)[-1]
                r["-" + "".join(nu + co)] += 1
        print(f"  {g:6s}: " + top(r, 10))

    # ---------------------------------------------------------------- the model
    model = N.train(first)
    N.MODEL_PATH.parent.mkdir(exist_ok=True)
    N.MODEL_PATH.write_text(json.dumps(model))
    gen = N.NameGen(model)
    print(f"\n== Sound changes learned from cognates (Westron -> other cultures)")
    for c, ch in model["changes"].items():
        subs = ", ".join(f"{r['src']}->{r['dst'] or '0'} ({r['rate']:.0%})" for r in ch["subs"][:8])
        print(f"  {c:9s} letters: {subs}")
        for key in sorted(ch["endings"]):
            opts = ch["endings"][key]
            shown = ", ".join(("no change" if o["strip"] == 0 and not o["add"] else (f"drop {o['strip']}" if o["strip"] else "") +
                               (" + " if o["strip"] and o["add"] else "") + (f"add -{o['add']}" if o["add"] else "")) + f" {o['p']:.0%}" for o in opts[:4])
            print(f"            {key:16s} {shown}")

    # ---------------------------------------------------------------- what it makes
    rng = random.Random(7)
    print("\n== Generated names (none in the lists, none one letter from a listed name)")
    for c in cultures:
        for g in ("female", "male"):
            print(f"  {c:9s} {g:6s}  " + ", ".join(gen.generate(rng, c, g) for _ in range(samples)))
    print("\n== One invented name, evolved into each culture")
    for g in ("female", "male", "female", "male"):
        fam = gen.family(rng, g)
        print("  " + "   ".join(f"{c}: {n}" for c, n in fam.items()))

    # ---------------------------------------------------------------- does it copy?
    print("\n== Novelty and fidelity (500 names per culture/gender)")
    for c in cultures:
        for g in ("female", "male"):
            made = [gen.generate(random.Random(i * 7919 + len(c)), c, g).lower() for i in range(500)]
            real = [n.lower() for n in first[c][g]]
            copies = sum(m in gen.known for m in made)
            uniq = len(set(made))
            ev_real = sum(N.skeleton(n)[-1] == "V" for n in real) / len(real)
            ev_made = sum(N.skeleton(n)[-1] == "V" for n in made) / len(made)
            v_real = sum(N.skeleton(n).count("V") for n in real) / sum(len(N.skeleton(n)) for n in real)
            v_made = sum(N.skeleton(n).count("V") for n in made) / sum(len(N.skeleton(n)) for n in made)
            l_real = sum(len(n) for n in real) / len(real)
            l_made = sum(len(n) for n in made) / len(made)
            lr = Counter(n[-1] for n in real)
            lm = Counter(n[-1] for n in made)
            # how far the final-letter distributions are apart (total variation distance)
            tv = 0.5 * sum(abs(lr[k] / len(real) - lm[k] / len(made)) for k in set(lr) | set(lm))
            print(f"  {c:9s} {g:6s}  copies {copies}/500, distinct {uniq}/500 | vowel share {v_real:.0%} real vs {v_made:.0%} made | "
                  f"ends in vowel {ev_real:.0%} vs {ev_made:.0%} | length {l_real:.1f} vs {l_made:.1f} | ending-letter gap {tv:.2f}")
    print(f"\nModel written to {N.MODEL_PATH.relative_to(Path.cwd()) if N.MODEL_PATH.is_relative_to(Path.cwd()) else N.MODEL_PATH}")


if __name__ == "__main__":
    n = 12
    if "--samples" in sys.argv:
        n = int(sys.argv[sys.argv.index("--samples") + 1])
    main(n)
