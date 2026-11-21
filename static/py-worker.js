// Runs the whole game (the Python package in rpg/) inside the browser with Pyodide.
// Saves are pickles written to /saves, an IndexedDB-backed folder, so they stay in this browser.
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/";
importScripts(PYODIDE + "pyodide.js");

const status = (text) => postMessage({status: text});
let py, handle, syncing = Promise.resolve();

// Write /saves back to IndexedDB at once (one sync at a time, in order). Waiting even a moment
// lost the newest save whenever the page was refreshed or closed inside that moment.
function persist() {
  syncing = syncing.then(() => new Promise((res) => py.FS.syncfs(false, (e) => { if (e) console.error("save sync failed", e); res(); })));
  return syncing;
}
// requests that make a save you asked for: answer only once it is safely stored
const SAVING = (path, body) => path === "/api/saves" || path === "/api/new" ||
  (path === "/api/cmd" && /^\s*(save|quit|exit|q)\b/i.test((JSON.parse(body || "{}").cmd || "")));

const ready = (async () => {
  status("Fetching the Python runtime…");
  py = await loadPyodide({indexURL: PYODIDE});
  status("Unpacking the world…");
  const zip = await (await fetch("rpg.zip", {cache: "no-cache"})).arrayBuffer();
  py.unpackArchive(zip, "zip", {extractDir: "/app"});
  py.FS.mkdirTree("/saves");
  py.FS.mount(py.FS.filesystems.IDBFS, {}, "/saves");
  await new Promise((res, rej) => py.FS.syncfs(true, (e) => (e ? rej(e) : res())));
  status("Waking the narrator…");
  py.runPython(`
import os, sys, json
os.environ["RPG_SAVE_DIR"] = "/saves"
sys.path.insert(0, "/app")
from rpg import web

def handle(method, path, query, body):
    obj, code = web.dispatch(method, path, query, json.loads(body or "{}"))
    g = web.SESSION.game
    # closing the tab is how you quit here, so keep 'autosave' current after every turn
    if method == "POST" and path == "/api/cmd" and g and not (g.combat or g.died or g.over):
        last = getattr(g, "last_save_turn", 0)
        g.save("autosave", quiet=True)
        g.last_save_turn = last        # a named save is still 'unsaved' until you make one
    return json.dumps([code, obj])
`);
  handle = py.globals.get("handle");
})();

ready.then(() => postMessage({ready: true}), (e) => postMessage({failed: String(e && e.message || e)}));

onmessage = async (e) => {
  const {id, method, path, query, body} = e.data;
  try {
    await ready;
    const reply = handle(method, path, query || "", body || "");
    if (method === "POST") {
      const stored = persist();
      if (SAVING(path, body)) await stored;
    }
    const [code, obj] = JSON.parse(reply);
    postMessage({id, code, body: JSON.stringify(obj)});
  } catch (err) {
    postMessage({id, code: 500, body: JSON.stringify({error: String(err && err.message || err)})});
  }
};
