// GitHub Pages build only: the page talks to "api/..." as if a server were there; this answers those
// requests from the Python game running in a worker (py-worker.js) instead.
(() => {
  const worker = new Worker("py-worker.js");
  const waiting = new Map();
  let next = 0;

  const veil = document.createElement("div");
  veil.id = "bootVeil";
  veil.innerHTML = '<div><div class="bv-title">Wayfarer’s Path</div><div class="bv-msg">Starting…</div>' +
    '<div class="bv-note">The first visit downloads about 10 MB; after that it loads from your browser’s cache. ' +
    'Your saves are kept in this browser only.</div></div>';
  const css = document.createElement("style");
  css.textContent = `#bootVeil{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;background:var(--bg,#15130f);
    color:var(--ink,#e8e0cf);font-family:var(--serif,Georgia,serif);text-align:center;padding:16px}
    #bootVeil .bv-title{font-size:2rem;margin-bottom:.6em;color:var(--accent,#d9a648)}
    #bootVeil .bv-msg{font-size:1.1rem;margin-bottom:1.2em}
    #bootVeil .bv-note{font-family:var(--sans,system-ui,sans-serif);font-size:.85rem;color:var(--ink-faint,#857a66);max-width:28em;margin:auto}
    #bootVeil.bv-bad .bv-msg{color:var(--bad,#d46a5a)}`;
  const mount = () => { document.head.appendChild(css); document.body.appendChild(veil); };
  document.body ? mount() : document.addEventListener("DOMContentLoaded", mount);

  worker.onmessage = (e) => {
    const m = e.data;
    if (m.id) { waiting.get(m.id)?.(m); waiting.delete(m.id); return; }
    if (m.status) veil.querySelector(".bv-msg").textContent = m.status;
    if (m.ready) veil.remove();
    if (m.failed) { veil.classList.add("bv-bad"); veil.querySelector(".bv-msg").textContent = "The game couldn't start: " + m.failed; }
  };

  const realFetch = window.fetch.bind(window);
  window.fetch = (url, opts = {}) => {
    if (typeof url !== "string" || !url.startsWith("api/")) return realFetch(url, opts);
    const [path, query = ""] = url.split("?");
    return new Promise((resolve) => {
      const id = ++next;
      waiting.set(id, (m) => resolve(new Response(m.body, {status: m.code, headers: {"Content-Type": "application/json"}})));
      worker.postMessage({id, method: (opts.method || "GET").toUpperCase(), path: "/" + path, query, body: opts.body || ""});
    });
  };
})();
