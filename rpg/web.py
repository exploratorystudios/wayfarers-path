"""Local web front-end. Runs the game in-process and serves a single page.

Binds to 127.0.0.1 only. Endpoints:
  GET  /                  the page
  GET  /api/state?since=N game state plus log lines after index N
  GET  /api/name          a freshly generated name (?gender=female|male|any&culture=...)
  POST /api/new           {"name": str, "seed": int|null}
  POST /api/load          {"slot": str}
  POST /api/cmd           {"cmd": str}
  POST /api/settings      {"hints": bool}   (no log output)
  POST /api/saves         {"op": "save"|"delete"|"rename", "slot": str, "to": str}
"""
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .actions import catalog, groups
from .advisor import suggest
from . import classes as K
from . import story as S
from .game import Game
from .world import DIRS

STATIC = Path(__file__).resolve().parent / "web"
FONTS = {"IMFellEnglish-Regular.woff2", "IMFellEnglish-Italic.woff2", "IMFellEnglishSC-Regular.woff2"}
MAX_LOG = 3000
MAX_BODY = 4096
NO_WRAP = 10 ** 6
DEAD_OK = {"load", "restore", "saves", "help", "h", "?"}


class Session:
    def __init__(self):
        self.game = None
        self.log = []
        self.offset = 0      # lines trimmed from the front of the log
        self.epoch = 0       # bumps when a new game/load replaces the log
        self.lock = threading.Lock()

    # -- output capture ------------------------------------------------------
    def out(self, text):
        self.log.extend(str(text).split("\n"))
        if len(self.log) > MAX_LOG:
            cut = len(self.log) - MAX_LOG
            del self.log[:cut]
            self.offset += cut

    def reset_log(self):
        self.log, self.offset = [], 0
        self.epoch += 1

    def attach(self, g):
        g.out = self.out
        g.width = NO_WRAP      # the browser wraps text
        self.game = g

    # -- actions -------------------------------------------------------------
    def new(self, name, seed, klass=""):
        self.reset_log()
        g = Game(seed=seed, name=name or None, out=self.out, klass=klass if klass in K.CLASSES else "knight")
        self.attach(g)
        g.intro()

    def load(self, slot):
        g = Game.load(slot, self.out)
        self.reset_log()
        self.attach(g)
        g.emit(f"You return to the world of seed {g.seed}, on day {g.world.day}.")
        g.show_location()

    def command(self, cmd):
        g = self.game
        cmd = cmd.strip()[:200]
        if not cmd:
            return
        self.out("> " + cmd)
        verb = cmd.split()[0].lower()
        if g.died and verb not in DEAD_OK:
            self.out("You are dead. Load a save, or start a new game.")
            return
        g.handle(cmd)
        self.attach(self.game)   # 'load' may have swapped state in; keep capture + no-wrap

    # -- state for the page --------------------------------------------------
    def state(self, since):
        g = self.game
        total = self.offset + len(self.log)
        start = max(0, since - self.offset) if since >= self.offset else 0
        base = dict(epoch=self.epoch, total=total, lines=self.log[start:],
                    saves=Game.list_save_info(), classes=CLASS_LIST)
        if g is None:
            return dict(base, game=None)
        w, p = g.world, g.player
        sugs = suggest(g) if getattr(g, "show_hints", True) or g.over else []
        path = next((s.path for s in sugs if s.travel and s.path), [])
        tod = {"deepnight": "deep night"}.get(w.time_of_day, w.time_of_day)
        if not g.has_quest:
            quest = "Speak with the village elder."
        elif w.relic in p.inv:
            quest = f"Bring the {w.relic.name} home to {w.tiles[w.start].site['name']}."
        else:
            quest = f"Recover the {w.relic.name} from {w.region_of(w.quest_pos)['name']}."
        inv = [dict(name=it.name, kind=it.kind,
                    equipped=(it is p.weapon or it is p.armour),
                    usable=bool(it.heal), equippable=it.kind in ("weapon", "armour"))
               for it in p.inv]
        return dict(base, game=dict(
            player=dict(name=p.name, klass=p.class_name, res_name=(K.spec(p) or {}).get("res"), res=getattr(p, "res", 0),
                        res_max=getattr(p, "res_max", 0), guard=getattr(p, "guard", 0), ward=getattr(p, "ward", 0),
                        hidden=getattr(p, "hidden", 0), hp=max(0, p.hp), maxhp=p.maxhp, level=p.level, xp=p.xp, xp_next=p.level * 30,
                        atk=p.atk, df=p.df, gold=p.gold,
                        weapon=p.weapon.name if p.weapon else None, armour=p.armour.name if p.armour else None),
            place=g.narr.header(g.pos), day=w.day, time=tod, season=w.season, weather=w.weather,
            quest=quest, inventory=inv, combat=g.combat.name if g.combat else None,
            over=g.over, died=g.died, won=g.won, novice=getattr(g, "turns", 0) < 40,
            hints=getattr(g, "show_hints", True),
            choice=dict(text=g.pending["text"], options=[o["label"] for o in g.pending["options"]]) if getattr(g, "pending", None) else None,
            journal=S.journal_lines(g) if hasattr(g, "quests") else [], effects=S.effects_line(g) if hasattr(g, "buffs") else "",
            companions=[c["name"] for c in getattr(g, "companions", [])],
            save_slot=getattr(g, "save_slot", None),
            unsaved=getattr(g, "turns", 0) > getattr(g, "last_save_turn", 0),
            can_save="" if not (g.combat or g.died) else ("You can't save mid-fight." if g.combat else "The dead can't save."),
            suggestions=[dict(cmd=s.cmd, label=s.label, why=s.why) for s in sugs],
            actions=catalog(g), groups=groups(g),
            map=self.map_state(g, set(path))))

    def map_state(self, g, path):
        w = g.world
        targets = {tuple(q["target"]) for q in S.active(g) if q.get("target")} if hasattr(g, "quests") else set()
        seen = lambda x, y: w.tiles[(x, y)].visited or getattr(w.tiles[(x, y)], "glimpsed", False) or any(
            (x + dx, y + dy) in w.tiles and w.tiles[(x + dx, y + dy)].visited for dx, dy in DIRS.values())
        rows = []
        for y in range(w.H):
            row = []
            for x in range(w.W):
                t = w.tiles[(x, y)]
                pos = (x, y)
                cell = dict(b=None)
                if seen(x, y):
                    cell = dict(b=t.biome, r=w.regions[t.region]["name"], v=t.visited)
                    if t.site and (t.visited or getattr(t, "site_seen", False)):
                        cell["s"] = t.site["kind"]
                        if t.site["kind"] == "village":
                            cell["n"] = t.site["name"]
                if pos in path:
                    cell["p"] = 1
                if pos in targets:
                    cell["t"] = 1
                if g.has_quest and pos == w.quest_pos:
                    cell["q"] = 1
                if pos == g.pos:
                    cell["me"] = 1
                    dirs = {d: (q in w.land) for d, q in w.neighbours(pos)}
                    cell["exits"] = [d for d, ok in dirs.items() if ok]
                row.append(cell)
            rows.append(row)
        return dict(w=w.W, h=w.H, cells=rows, pos=list(g.pos))


def atlas(g):
    """Everything the player has discovered, for the painted map."""
    w = g.world
    visited = {p for p, t in w.tiles.items() if t.visited}
    near = {q for p in visited for _, q in w.neighbours(p)}
    cells = []
    for y in range(w.H):
        row = []
        for x in range(w.W):
            p, t = (x, y), w.tiles[(x, y)]
            k = 2 if t.visited else 1 if (p in near or getattr(t, "glimpsed", False)) else 0
            c = dict(k=k)
            if k:
                c.update(b=t.biome, g=t.region)
                if t.site and (t.visited or getattr(t, "site_seen", False)):
                    c["s"] = t.site["kind"]
                    if t.site["kind"] == "village":
                        c["n"] = t.site["name"]
                if t.visited:
                    c["f"] = [f.archetype for f in t.features]
            row.append(c)
        cells.append(row)
    known_regions = {w.tiles[p].region for p in visited}
    regions = [dict(id=i, name=r["name"], biome=r["biome"]) for i, r in enumerate(w.regions) if i in known_regions]
    goals = [list(q["target"]) for q in S.active(g) if q.get("target")] if hasattr(g, "quests") else []
    trail = [list(p) for p in getattr(g, "trail", [])] or [list(w.start), list(g.pos)]
    return dict(w=w.W, h=w.H, cells=cells, regions=regions, trail=trail, pos=list(g.pos), start=list(w.start),
                home=w.tiles[w.start].site["name"], relic=list(w.quest_pos) if g.has_quest else None,
                relic_name=w.relic.name, relic_found=w.relic in g.player.inv, goals=goals, seed=g.seed,
                name=g.player.name, day=w.day, season=w.season)


CLASS_LIST = [dict(id=k, name=c["name"], blurb=c["blurb"], difficulty=c["difficulty"], hp=c["hp"], res=c["res"], res_max=c["res_max"],
                   passive=c["passive"], abilities=[dict(id=a, label=K.ABILITIES[a]["label"], desc=K.ABILITIES[a]["desc"]) for a in c["abilities"]])
              for k, c in K.CLASSES.items()]

SESSION = Session()


class Handler(BaseHTTPRequestHandler):
    server_version = "WayfarersPath/1.0"

    def log_message(self, fmt, *args):   # keep the terminal quiet
        pass

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path in ("/", "/index.html"):
            data = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/name":
            import random as _r
            from . import names as NM
            q = dict(part.partition("=")[::2] for part in query.split("&") if part)
            gender = q.get("gender") if q.get("gender") in ("female", "male", "any") else "any"
            culture = q.get("culture") if q.get("culture") in ("Archaic", "Westron", "Northish", "Southron") else _r.choice(["Archaic", "Westron", "Northish", "Southron"])
            return self.send_json(dict(name=NM.gen().generate(_r.Random(), culture, gender), culture=culture, gender=gender))
        if path.startswith("/fonts/") and path[7:] in FONTS:      # bundled map lettering (SIL Open Font License)
            data = (STATIC / "fonts" / path[7:]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "font/woff2")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/atlas.js":
            data = (STATIC / "atlas.js").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/atlas":
            with SESSION.lock:
                if SESSION.game is None:
                    return self.send_json({"error": "no game running"}, 400)
                return self.send_json(atlas(SESSION.game))
        if path == "/api/state":
            since = 0
            for part in query.split("&"):
                k, _, v = part.partition("=")
                if k == "since" and v.isdigit():
                    since = int(v)
            with SESSION.lock:
                return self.send_json(SESSION.state(since))
        self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        # same-origin only: refuse cross-site form posts from other pages
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host')}":
            return self.send_json({"error": "bad origin"}, 403)
        try:
            data = self.body()
        except Exception as e:
            return self.send_json({"error": str(e)}, 400)
        since = int(data.get("since") or 0)
        with SESSION.lock:
            try:
                if self.path == "/api/new":
                    seed = data.get("seed")
                    seed = int(seed) if str(seed or "").strip().isdigit() else None
                    SESSION.new(str(data.get("name") or "")[:40].strip(), seed, str(data.get("klass") or ""))
                    since = 0
                elif self.path == "/api/load":
                    SESSION.load(str(data.get("slot") or "autosave"))
                    since = 0
                elif self.path == "/api/settings":
                    if SESSION.game is None:
                        return self.send_json({"error": "no game running"}, 400)
                    if "hints" in data:
                        SESSION.game.show_hints = bool(data["hints"])
                elif self.path == "/api/saves":
                    op, slot = data.get("op"), str(data.get("slot") or "")
                    if op == "delete":
                        Game.delete_save(slot)
                        if SESSION.game and getattr(SESSION.game, "save_slot", None) == Game.safe_slot(slot):
                            SESSION.game.save_slot = None
                    elif op == "rename":
                        new = Game.rename_save(slot, str(data.get("to") or ""))
                        if SESSION.game and getattr(SESSION.game, "save_slot", None) == Game.safe_slot(slot):
                            SESSION.game.save_slot = new
                    elif op == "save":
                        if SESSION.game is None:
                            return self.send_json({"error": "no game running"}, 400)
                        if not Game.safe_slot(slot):
                            raise ValueError("a save name needs at least one letter or number")
                        SESSION.command("save " + Game.safe_slot(slot))
                    else:
                        return self.send_json({"error": "unknown save operation"}, 400)
                elif self.path == "/api/cmd":
                    if SESSION.game is None:
                        return self.send_json({"error": "no game running"}, 400)
                    SESSION.command(str(data.get("cmd") or ""))
                else:
                    return self.send_json({"error": "not found"}, 404)
            except FileNotFoundError:
                return self.send_json({"error": "no such save"}, 400)
            except ValueError as e:
                return self.send_json({"error": str(e)}, 400)
            except Exception as e:
                return self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)
            return self.send_json(SESSION.state(since))


def serve(port=8765, open_browser=True):
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"Wayfarer's Path is running at {url}  (Ctrl-C to stop; your progress autosaves)")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with SESSION.lock:
            g = SESSION.game
            if g and not g.died and not g.over:
                g.save("autosave", quiet=True)
                print("\nProgress saved to 'autosave'.")
        httpd.server_close()
