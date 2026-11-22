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
APP_FILES = {"manifest.webmanifest": "application/manifest+json", "icon.svg": "image/svg+xml",
             "icon-192.png": "image/png", "icon-512.png": "image/png"}
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
        g.save("autosave", quiet=True)          # every character has an autosave from the very start

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
                    runs=Game.list_runs(), classes=CLASS_LIST)
        if g is None:
            return dict(base, game=None)
        w, p = g.world, g.player
        sugs = suggest(g) if getattr(g, "show_hints", True) or g.over else []
        path = next((s.path for s in sugs if s.travel and s.path), [])
        tod = {"deepnight": "deep night"}.get(w.time_of_day, w.time_of_day)
        quest = w.quest.goal(g) if g.has_quest else "Speak with the village elder."
        inv = [dict(name=it.name, kind=it.kind,
                    equipped=(it is p.weapon or it is p.armour),
                    usable=bool(it.heal) or it.kind in ("book", "scroll") or bool(it.facts.get("use")), equippable=it.kind in ("weapon", "armour"))
               for it in p.inv]
        return dict(base, game=dict(
            player=dict(name=p.name, klass=p.class_name, res_name=(K.spec(p) or {}).get("res"), res=getattr(p, "res", 0),
                        res_max=getattr(p, "res_max", 0), guard=getattr(p, "guard", 0), ward=getattr(p, "ward", 0),
                        hidden=getattr(p, "hidden", 0), hp=max(0, p.hp), maxhp=p.maxhp, level=p.level, xp=p.xp, xp_next=p.level * 30,
                        atk=p.atk, df=p.df, gold=p.gold, rations=getattr(p, "rations", 0),
                        weapon=p.weapon.name if p.weapon else None, armour=p.armour.name if p.armour else None),
            place=g.narr.header(g.pos), day=w.day, time=tod, season=w.season, weather=w.weather,
            quest=quest, inventory=inv, combat=g.combat.name if g.combat else None,
            over=g.over, died=g.died, won=g.won, novice=getattr(g, "turns", 0) < 40,
            hints=getattr(g, "show_hints", True),
            choice=dict(text=g.pending["text"], options=[o["label"] for o in g.pending["options"]]) if getattr(g, "pending", None) else None,
            journal=S.journal(g) if hasattr(g, "quests") else dict(entries=[], done=[]), effects=S.effects_line(g) if hasattr(g, "buffs") else "",
            companions=[c["name"] for c in getattr(g, "companions", [])],
            save_slot=getattr(g, "save_slot", None), save_id=g.save_id(), run_id=getattr(g, "run_id", None),
            world=g.world.title,
            unsaved=getattr(g, "turns", 0) > getattr(g, "last_save_turn", 0),
            can_save="" if not (g.combat or g.died) else ("You can't save mid-fight." if g.combat else "The dead can't save."),
            suggestions=[dict(cmd=s.cmd, label=s.label, why=s.why) for s in sugs],
            actions=catalog(g), groups=groups(g),
            map=self.map_state(g, set(path))))

    def map_state(self, g, path):
        w = g.world
        targets = goal_titles(g)
        qmarks = set(map(tuple, w.quest.targets(g))) if g.has_quest else set()
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
                    if getattr(t, "road", ""):
                        cell["rd"] = t.road
                    if t.site and (t.visited or getattr(t, "site_seen", False)):
                        cell["s"] = t.site["kind"]
                        if t.site["kind"] == "village":
                            cell["n"] = t.site["name"]
                if pos in path:
                    cell["p"] = 1
                if pos in targets:
                    cell["t"] = targets[pos]
                if g.has_quest and pos in qmarks:
                    cell["q"] = 1
                if pos == g.pos:
                    cell["me"] = 1
                    dirs = {d: (q in w.land) for d, q in w.neighbours(pos)}
                    cell["exits"] = [d for d, ok in dirs.items() if ok]
                row.append(cell)
            rows.append(row)
        return dict(w=w.W, h=w.H, cells=rows, pos=list(g.pos), seed=g.seed, quest_tip=w.quest.mark(g) if g.has_quest else "")


def goal_titles(g):
    """Journal errands with a place on the map: {(x, y): [titles]}."""
    out = {}
    for q in (S.active(g) if hasattr(g, "quests") else []):
        if q.get("target"):
            out.setdefault(tuple(q["target"]), []).append(q["title"])
    return out


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
                if getattr(t, "road", ""):
                    c["rd"] = t.road
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
    goals = [dict(x=p[0], y=p[1], titles=ts) for p, ts in goal_titles(g).items()]
    trail = [list(p) for p in getattr(g, "trail", [])] or [list(w.start), list(g.pos)]
    return dict(w=w.W, h=w.H, cells=cells, regions=regions, trail=trail, pos=list(g.pos), start=list(w.start),
                home=w.tiles[w.start].site["name"], relic=(list(w.quest.targets(g)[0]) if g.has_quest and w.quest.targets(g) else None),
                relic_name=w.quest.goal(g), relic_found=False, quest_mark=w.quest.mark(g) if g.has_quest else "", goals=goals, seed=g.seed,
                name=g.player.name, day=w.day, season=w.season)


CLASS_LIST = [dict(id=k, name=c["name"], blurb=c["blurb"], difficulty=c["difficulty"], hp=c["hp"], res=c["res"], res_max=c["res_max"],
                   passive=c["passive"], abilities=[dict(id=a, label=K.ABILITIES[a]["label"], desc=K.ABILITIES[a]["desc"]) for a in c["abilities"]])
              for k, c in K.CLASSES.items()]

SESSION = Session()


def _query(query):
    return dict(part.partition("=")[::2] for part in query.split("&") if part)


def dispatch(method, path, query="", data=None):
    """Answer one API request: returns (json-able object, status code).

    Shared by the local HTTP server below and the in-browser build (static/), which runs this
    module under Pyodide and calls dispatch() directly instead of going over the network."""
    data = data or {}
    if method == "GET":
        if path == "/api/name":
            import random as _r
            from . import names as NM
            q = _query(query)
            gender = q.get("gender") if q.get("gender") in ("female", "male", "any") else "any"
            culture = q.get("culture") if q.get("culture") in ("Archaic", "Westron", "Northish", "Southron") else _r.choice(["Archaic", "Westron", "Northish", "Southron"])
            return dict(name=NM.gen().generate(_r.Random(), culture, gender), culture=culture, gender=gender), 200
        if path == "/api/atlas":
            with SESSION.lock:
                if SESSION.game is None:
                    return {"error": "no game running"}, 400
                return atlas(SESSION.game), 200
        if path == "/api/state":
            v = _query(query).get("since", "")
            with SESSION.lock:
                return SESSION.state(int(v) if v.isdigit() else 0), 200
        return {"error": "not found"}, 404
    since = int(data.get("since") or 0)
    with SESSION.lock:
        try:
            if path == "/api/new":
                seed = data.get("seed")
                seed = int(seed) if str(seed or "").strip().isdigit() else None
                SESSION.new(str(data.get("name") or "")[:40].strip(), seed, str(data.get("klass") or ""))
                since = 0
            elif path == "/api/load":
                SESSION.load(str(data.get("slot") or "autosave"))
                since = 0
            elif path == "/api/settings":
                if SESSION.game is None:
                    return {"error": "no game running"}, 400
                if "hints" in data:
                    SESSION.game.show_hints = bool(data["hints"])
            elif path == "/api/saves":
                op, slot = data.get("op"), str(data.get("slot") or "")     # slot: a save id, "folder/name"
                g = SESSION.game
                mine = g.save_id() if g else None
                if op == "delete":
                    path = Game.delete_save(slot)
                    if mine and Game.save_ref(path) == mine:
                        g.save_slot = None
                elif op == "delete_run":
                    Game.delete_run(str(data.get("run") or ""))
                    if g and getattr(g, "run_id", None) == Game.safe_slot(str(data.get("run") or "")):
                        g.save_slot = None
                elif op == "rename":
                    path = Game.find_save(slot)
                    new = Game.rename_save(slot, str(data.get("to") or ""))
                    if mine and path and Game.save_ref(path) == mine:
                        g.save_slot = new
                elif op == "save":
                    if SESSION.game is None:
                        return {"error": "no game running"}, 400
                    if not Game.safe_slot(slot):
                        raise ValueError("a save name needs at least one letter or number")
                    SESSION.command("save " + Game.safe_slot(slot))
                else:
                    return {"error": "unknown save operation"}, 400
            elif path == "/api/cmd":
                if SESSION.game is None:
                    return {"error": "no game running"}, 400
                SESSION.command(str(data.get("cmd") or ""))
            else:
                return {"error": "not found"}, 404
        except FileNotFoundError:
            return {"error": "no such save"}, 400
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}, 500
        return SESSION.state(since), 200


def autosave():
    """Save the running game to 'autosave' if it is worth keeping (on quit / page close)."""
    with SESSION.lock:
        g = SESSION.game
        if g and not g.died and not g.over:
            g.save("autosave", quiet=True)
            return True
    return False


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

    def send_file(self, file, ctype, cache=None):
        data = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if cache:
            self.send_header("Cache-Control", cache)
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
            return self.send_file(STATIC / "index.html", "text/html; charset=utf-8")
        if path.startswith("/fonts/") and path[7:] in FONTS:      # bundled map lettering (SIL Open Font License)
            return self.send_file(STATIC / "fonts" / path[7:], "font/woff2", "max-age=86400")
        if path in ("/atlas.js", "/atlas-worker.js"):
            return self.send_file(STATIC / path[1:], "text/javascript; charset=utf-8")
        if path[1:] in APP_FILES:                                   # home-screen icon and manifest
            return self.send_file(STATIC / path[1:], APP_FILES[path[1:]], "max-age=86400")
        self.send_json(*dispatch("GET", path, query))

    def do_POST(self):
        # same-origin only: refuse cross-site form posts from other pages
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host')}":
            return self.send_json({"error": "bad origin"}, 403)
        try:
            data = self.body()
        except Exception as e:
            return self.send_json({"error": str(e)}, 400)
        self.send_json(*dispatch("POST", self.path, "", data))


def serve(port=8765, open_browser=True):
    import webbrowser
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
        if autosave():
            print("\nProgress saved to 'autosave'.")
        httpd.server_close()
