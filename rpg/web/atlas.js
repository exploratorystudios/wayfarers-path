// The painted map: a cartographer's chart of everywhere the player has explored.
// drawAtlas(canvas, data, opts) renders /api/atlas data. Everything is seeded, so the same
// world always looks the same; only what you have explored changes.
//   opts.scale  pixels per design unit (2 = crisp when zoomed in)
//   opts.mini   just the land, for the map panel: no lettering, frame or decoration,
//               fewer and bolder symbols (the panel's own grid and markers sit on top)
//   opts.trail  a second canvas: the road you have walked is drawn there, on its own,
//               so it can be shown or hidden without repainting the map
(function () {
  "use strict";
  const W = 1400, H = 1460, X0 = 90, Y0 = 150;          // canvas size and where the map area starts
  const INK = "59,42,26";                                // sepia
  const PAPER = [233, 218, 186];
  const BIOME = {                                          // watercolour washes
    forest: [118, 140, 86], plains: [205, 194, 138], hills: [176, 158, 108],
    marsh: [130, 150, 118], peaks: [186, 178, 166], lake: [128, 166, 178],
  };

  // ---------------------------------------------------------------- seeded noise
  function hash(x, y, s) {
    let h = Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263) ^ Math.imul(s | 0, 982451653);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }
  function vnoise(x, y, s) {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    const a = hash(xi, yi, s), b = hash(xi + 1, yi, s), c = hash(xi, yi + 1, s), d = hash(xi + 1, yi + 1, s);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  function fbm(x, y, s, oct) {
    let t = 0, amp = 0.5, f = 1, norm = 0;
    for (let i = 0; i < (oct || 4); i++) { t += amp * vnoise(x * f, y * f, s + i * 17); norm += amp; amp *= 0.5; f *= 2.03; }
    return t / norm;
  }
  function mulberry(a) {
    return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const smooth = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  const mix = (a, b, t) => a + (b - a) * t;

  // ---------------------------------------------------------------- the painting
  function drawAtlas(canvas, A, opts) {
    opts = opts || {};
    const S = opts.scale || 1, MINI = !!opts.mini;
    const ctx = canvas.getContext("2d");
    const N = A.w, T = (W - 2 * X0) / N;                 // tile size in design units
    const seed = (A.seed % 100000) | 0;
    const cell = (x, y) => (x >= 0 && y >= 0 && x < N && y < A.h) ? A.cells[y][x] : { k: 0 };
    const kv = (x, y) => { const k = cell(x, y).k; return k === 2 ? 1 : k === 1 ? 0.62 : 0; };
    // what part of the design is shown: the whole sheet, or (mini) just the land
    const VX = MINI ? X0 : 0, VY = MINI ? Y0 : 0, VW = MINI ? W - 2 * X0 : W, VH = MINI ? A.h * T : H;
    canvas.width = Math.round(VW * S); canvas.height = Math.round(VH * S);
    const design = () => ctx.setTransform(S, 0, 0, S, -VX * S, -VY * S);
    const RES = Math.min(S, 1);                           // textures are computed at most at design resolution

    // ---- paper
    {
      const pw = Math.ceil(VW * RES), ph = Math.ceil(VH * RES);
      const off = document.createElement("canvas"); off.width = pw; off.height = ph;
      const octx = off.getContext("2d"), paper = octx.createImageData(pw, ph);
      for (let y = 0; y < ph; y++) for (let x = 0; x < pw; x++) {
        const dx = VX + x / RES, dy = VY + y / RES;
        const n = fbm(dx / 160, dy / 160, seed + 3, 4) - 0.5, fine = hash(dx | 0, dy | 0, seed) - 0.5;
        const i = (y * pw + x) * 4;
        paper.data[i] = PAPER[0] + n * 26 + fine * 7; paper.data[i + 1] = PAPER[1] + n * 24 + fine * 7;
        paper.data[i + 2] = PAPER[2] + n * 22 + fine * 6; paper.data[i + 3] = 255;
      }
      octx.putImageData(paper, 0, 0);
      design(); ctx.imageSmoothingEnabled = true; ctx.drawImage(off, VX, VY, VW, VH);
    }

    // ---- land and water, painted at half resolution then scaled (watercolour is soft anyway)
    const R = 1 / RES, MW = Math.ceil((W - 2 * X0) / R), MH = Math.ceil(A.h * T / R);
    const biomeAt = new Int8Array(MW * MH), known = new Float32Array(MW * MH), seenOnly = new Float32Array(MW * MH);
    const names = Object.keys(BIOME);
    const sampleB = (mx, my) => { const c = cell(Math.floor(mx), Math.floor(my)); return c.k ? names.indexOf(c.b) : -1; };
    // borders wander at two scales: broad bends, and a finer ragged edge, so nothing follows the tile grid
    const warp = (mx, my) => [mx + (fbm(mx * 0.85, my * 0.85, seed + 11, 3) - 0.5) * 1.05 + (vnoise(mx * 3.1, my * 3.1, seed + 13) - 0.5) * 0.32,
                              my + (fbm(mx * 0.85, my * 0.85, seed + 29, 3) - 0.5) * 1.05 + (vnoise(mx * 3.1, my * 3.1, seed + 31) - 0.5) * 0.32];
    for (let py = 0; py < MH; py++) for (let px = 0; px < MW; px++) {
      const mx = px * R / T, my = py * R / T, [wx, wy] = warp(mx, my);
      const j = py * MW + px;
      biomeAt[j] = sampleB(wx, wy);
      // how well charted this spot is: bilinear over tiles, roughened at the edges
      const gx = wx - 0.5, gy = wy - 0.5, x0 = Math.floor(gx), y0 = Math.floor(gy), fx = gx - x0, fy = gy - y0;
      const k = mix(mix(kv(x0, y0), kv(x0 + 1, y0), fx), mix(kv(x0, y0 + 1), kv(x0 + 1, y0 + 1), fx), fy);
      known[j] = k + (fbm(mx * 2.2, my * 2.2, seed + 41, 3) - 0.5) * 0.35;
      seenOnly[j] = smooth(0.6, 0.95, k);
    }
    // distance to the shore, both ways (two-pass chamfer), for coastlines and ripples
    const INF = 1e9, dW = new Float32Array(MW * MH), dL = new Float32Array(MW * MH);
    const LAKE = names.indexOf("lake");
    for (let j = 0; j < MW * MH; j++) { const water = biomeAt[j] === LAKE; dW[j] = water ? INF : 0; dL[j] = water ? 0 : INF; }
    for (const d of [dW, dL]) {
      for (let y = 0; y < MH; y++) for (let x = 0; x < MW; x++) {
        const j = y * MW + x; if (!d[j]) continue;
        if (x > 0) d[j] = Math.min(d[j], d[j - 1] + 1);
        if (y > 0) d[j] = Math.min(d[j], d[j - MW] + 1);
        if (x > 0 && y > 0) d[j] = Math.min(d[j], d[j - MW - 1] + 1.414);
        if (x < MW - 1 && y > 0) d[j] = Math.min(d[j], d[j - MW + 1] + 1.414);
      }
      for (let y = MH - 1; y >= 0; y--) for (let x = MW - 1; x >= 0; x--) {
        const j = y * MW + x; if (!d[j]) continue;
        if (x < MW - 1) d[j] = Math.min(d[j], d[j + 1] + 1);
        if (y < MH - 1) d[j] = Math.min(d[j], d[j + MW] + 1);
        if (x < MW - 1 && y < MH - 1) d[j] = Math.min(d[j], d[j + MW + 1] + 1.414);
        if (x > 0 && y < MH - 1) d[j] = Math.min(d[j], d[j + MW - 1] + 1.414);
      }
    }
    const off = document.createElement("canvas"); off.width = MW; off.height = MH;
    const octx = off.getContext("2d"), land = octx.createImageData(MW, MH);
    for (let py = 0; py < MH; py++) for (let px = 0; px < MW; px++) {
      const j = py * MW + px, b = biomeAt[j];
      const P = PAPER;
      let a = smooth(0.28, 0.72, known[j]);
      if (b < 0) a = 0;
      let C = b >= 0 ? BIOME[names[b]].slice() : P;
      const mx = px * R / T, my = py * R / T;
      // pigment varies, and pools darker along the edges of each wash
      const wv = (fbm(mx * 1.6, my * 1.6, seed + 61, 3) - 0.5) * 0.22;
      C = C.map(c => c * (1 + wv));
      if (b >= 0) {
        const [wx, wy] = warp(mx, my);
        const e1 = sampleB(wx + 0.07, wy), e2 = sampleB(wx, wy + 0.07);
        if ((e1 >= 0 && e1 !== b) || (e2 >= 0 && e2 !== b)) C = C.map(c => c * 0.86);
      }
      if (names[b] === "peaks" && fbm(mx * 3, my * 3, seed + 71, 3) > 0.58) C = C.map(c => mix(c, 246, 0.6));   // snow
      if (b === LAKE) {
        const d = dW[j] * R;                                     // ripple lines parallel to the shore
        if (d < 44 && (d % 9) < 1.6) C = C.map((c, i) => c * (0.72 + 0.28 * d / 44));
        C = C.map((c, i) => c * (1 - 0.18 * smooth(10, 0, d)));
      } else if (b >= 0 && dL[j] * R < 2.4 && dL[j] > 0) {
        C = [INK.split(",")[0] * 1.2, INK.split(",")[1] * 1.2, INK.split(",")[2] * 1.2];   // inked shoreline
        a = Math.max(a, 0.9 * smooth(0.2, 0.6, known[j]));
      }
      const strength = a * (0.5 + 0.5 * seenOnly[j]) * 0.82;
      const k = j * 4;                                  // a wash laid over the paper: colour, and how much of it
      land.data[k] = C[0]; land.data[k + 1] = C[1]; land.data[k + 2] = C[2]; land.data[k + 3] = Math.round(255 * strength);
    }
    octx.putImageData(land, 0, 0);
    ctx.save(); design(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
    try { ctx.filter = `blur(${(MINI ? 0.4 : 0.9) * S}px)`; } catch (e) { /* no filter support: crisper edges */ }
    ctx.drawImage(off, X0, Y0, MW * R, MH * R); ctx.restore();
    design();

    // ---- ink
    const ink = (a) => `rgba(${INK},${a})`;
    const jitter = (r, n) => (r() - 0.5) * n;
    function stroke(a, w) { ctx.strokeStyle = ink(a); ctx.lineWidth = Math.max(w, 0.75 / S); ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.stroke(); }
    const SYM = MINI ? 1.6 : 1;                           // symbols are drawn bigger (and fewer) on the mini map
    function line(r, x1, y1, x2, y2) {     // a slightly wavering pen line
      const mx = (x1 + x2) / 2 + jitter(r, 2), my = (y1 + y2) / 2 + jitter(r, 2);
      ctx.moveTo(x1, y1); ctx.quadraticCurveTo(mx, my, x2, y2);
    }
    function tree(r, x, y, s, a, conifer) {
      ctx.beginPath();
      if (conifer) {
        ctx.moveTo(x, y - s * 1.25); ctx.lineTo(x - s * 0.62, y + s * 0.2); ctx.lineTo(x + s * 0.62, y + s * 0.2); ctx.closePath();
      } else {
        const pts = 7;
        for (let i = 0; i <= pts; i++) {
          const t = i / pts * Math.PI * 2, rr = s * (0.62 + r() * 0.2);
          const px = x + Math.cos(t) * rr, py = y - s * 0.45 + Math.sin(t) * rr * 0.85;
          i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
        }
        ctx.closePath();
      }
      ctx.fillStyle = `rgba(78,98,58,${0.38 * a})`; ctx.fill(); stroke(0.8 * a, 1.1);
      ctx.beginPath(); line(r, x, y + s * 0.15, x + jitter(r, 1), y + s * 0.7); stroke(0.85 * a, 1.2);
      ctx.beginPath(); ctx.arc(x + s * 0.18, y - s * 0.4, s * 0.42, -0.2, 1.4); stroke(0.35 * a, 1);          // shade
    }
    function hill(r, x, y, s, a) {
      ctx.beginPath(); ctx.moveTo(x - s, y); ctx.quadraticCurveTo(x - s * 0.15, y - s * 1.15, x + s, y); stroke(0.8 * a, 1.4);
      ctx.beginPath();
      for (let i = 0; i < 5; i++) { const t = 0.15 + i * 0.16; const hx = x + s * t, hy = y - s * (1 - t) * 0.85 + 2; line(r, hx, hy, hx + s * 0.18, hy + s * 0.28); }
      stroke(0.45 * a, 0.9);
    }
    function peak(r, x, y, s, a) {
      const h = s * (1.25 + r() * 0.35), sx = x + s * 0.35;
      ctx.beginPath(); ctx.moveTo(x - s, y); ctx.lineTo(x - s * 0.15, y - h); ctx.lineTo(x + s * 0.12, y - h * 0.72); ctx.lineTo(sx, y - h * 0.86); ctx.lineTo(x + s, y);
      ctx.fillStyle = `rgba(244,238,226,${0.55 * a})`; ctx.fill(); stroke(0.85 * a, 1.4);
      ctx.beginPath();
      for (let i = 0; i < 6; i++) { const t = i / 6; const hx = mix(x - s * 0.15, x + s, t) - 2, hy = mix(y - h, y, t); line(r, hx, hy + 3, hx - s * 0.12, hy + s * 0.45); }
      stroke(0.4 * a, 0.9);
      ctx.beginPath(); ctx.moveTo(x - s * 0.15, y - h); ctx.lineTo(x - s * 0.42, y - h * 0.62); ctx.lineTo(x - s * 0.22, y - h * 0.7); ctx.lineTo(x - s * 0.05, y - h * 0.58); ctx.closePath();
      ctx.fillStyle = `rgba(255,255,255,${0.75 * a})`; ctx.fill();
    }
    function tuft(r, x, y, s, a) {
      ctx.beginPath(); line(r, x, y, x - s * 0.45, y - s); line(r, x, y, x, y - s * 1.2); line(r, x, y, x + s * 0.45, y - s); stroke(0.7 * a, 1);
      ctx.beginPath(); line(r, x - s * 1.4, y + 3, x - s * 0.5, y + 3); line(r, x + s * 0.5, y + 4, x + s * 1.3, y + 4);
      ctx.strokeStyle = `rgba(60,90,110,${0.55 * a})`; ctx.lineWidth = 1; ctx.stroke();
    }
    function grass(r, x, y, s, a) { ctx.beginPath(); line(r, x - s * 0.4, y - s * 0.6, x, y); line(r, x, y, x + s * 0.5, y - s * 0.8); stroke(0.5 * a, 1); }
    function house(x, y, s, a) {
      ctx.beginPath(); ctx.rect(x - s * 0.5, y - s * 0.55, s, s * 0.55);
      ctx.moveTo(x - s * 0.62, y - s * 0.5); ctx.lineTo(x, y - s * 1.05); ctx.lineTo(x + s * 0.62, y - s * 0.5);
      ctx.fillStyle = `rgba(214,170,120,${0.75 * a})`; ctx.fill(); stroke(0.9 * a, 1.3);
      ctx.beginPath(); ctx.moveTo(x - s * 0.62, y - s * 0.5); ctx.lineTo(x, y - s * 1.05); ctx.lineTo(x + s * 0.62, y - s * 0.5); ctx.closePath();
      ctx.fillStyle = `rgba(150,70,48,${0.65 * a})`; ctx.fill(); stroke(0.9 * a, 1.2);
    }
    function ruin(r, x, y, s, a) {
      ctx.beginPath(); ctx.moveTo(x - s * 0.45, y); ctx.lineTo(x - s * 0.45, y - s * 1.3); ctx.lineTo(x - s * 0.2, y - s * 1.15); ctx.lineTo(x, y - s * 1.4);
      ctx.lineTo(x + s * 0.18, y - s * 0.9); ctx.lineTo(x + s * 0.45, y - s); ctx.lineTo(x + s * 0.45, y); ctx.closePath();
      ctx.fillStyle = `rgba(200,190,170,${0.7 * a})`; ctx.fill(); stroke(0.9 * a, 1.3);
      ctx.beginPath(); ctx.rect(x - s * 0.12, y - s * 0.6, s * 0.2, s * 0.32); stroke(0.8 * a, 1);
      ctx.beginPath(); for (let i = 0; i < 4; i++) { const rx = x + s * 0.7 + i * 4, ry = y - 2 + jitter(r, 3); ctx.moveTo(rx, ry); ctx.arc(rx, ry, 1.3, 0, 7); } stroke(0.6 * a, 1);
    }
    function shrine(x, y, s, a) {
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - s * 1.2); ctx.moveTo(x - s * 0.38, y - s * 0.85); ctx.lineTo(x + s * 0.38, y - s * 0.85); stroke(0.9 * a, 2);
      ctx.beginPath(); ctx.arc(x, y - s * 1.32, s * 0.16, 0, 7); ctx.fillStyle = `rgba(190,150,60,${0.9 * a})`; ctx.fill();
    }
    function tent(x, y, s, a) {
      ctx.beginPath(); ctx.moveTo(x - s * 0.6, y); ctx.lineTo(x, y - s); ctx.lineTo(x + s * 0.6, y); ctx.closePath();
      ctx.fillStyle = `rgba(190,160,110,${0.7 * a})`; ctx.fill(); stroke(0.9 * a, 1.2);
      ctx.beginPath(); ctx.moveTo(x, y - s); ctx.lineTo(x, y); stroke(0.7 * a, 1);
    }
    const LANDMARK = {                               // small marks for notable landmarks on tiles you've visited
      "standing stone": (r, x, y, a) => { ctx.beginPath(); ctx.ellipse(x, y - 7, 2.6, 7, 0.08, 0, 7); ctx.fillStyle = ink(0.55 * a); ctx.fill(); },
      "stone circle": (r, x, y, a) => { ctx.beginPath(); for (let i = 0; i < 8; i++) { const t = i / 8 * 6.283; ctx.moveTo(x + Math.cos(t) * 8 + 1.6, y + Math.sin(t) * 5); ctx.arc(x + Math.cos(t) * 8, y + Math.sin(t) * 5, 1.6, 0, 7); } ctx.fillStyle = ink(0.7 * a); ctx.fill(); },
      "cairn": (r, x, y, a) => { ctx.beginPath(); [[0, 0], [-3, 0], [3, 0], [-1.5, -3], [1.5, -3], [0, -6]].forEach(([dx, dy]) => { ctx.moveTo(x + dx + 1.6, y + dy); ctx.arc(x + dx, y + dy, 1.6, 0, 7); }); ctx.fillStyle = ink(0.6 * a); ctx.fill(); },
      "gibbet": (r, x, y, a) => { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - 14); ctx.lineTo(x + 7, y - 14); ctx.lineTo(x + 7, y - 10); stroke(0.8 * a, 1.4); },
      "holy well": (r, x, y, a) => { ctx.beginPath(); ctx.arc(x, y - 3, 4, 0, 7); stroke(0.8 * a, 1.2); ctx.beginPath(); ctx.arc(x, y - 3, 2, 0, 7); ctx.fillStyle = "rgba(80,120,150,.8)"; ctx.fill(); },
      "hot spring": (r, x, y, a) => { ctx.beginPath(); ctx.arc(x, y - 3, 4, 0, 7); ctx.fillStyle = "rgba(120,160,170,.7)"; ctx.fill(); ctx.beginPath(); line(r, x - 2, y - 8, x - 3, y - 15); line(r, x + 2, y - 8, x + 3, y - 15); stroke(0.4 * a, 1); },
      "waterfall": (r, x, y, a) => { ctx.beginPath(); for (let i = -1; i <= 1; i++) line(r, x + i * 3, y - 14, x + i * 3 + 1, y); ctx.strokeStyle = "rgba(60,100,130,.75)"; ctx.lineWidth = 1.2; ctx.stroke(); },
      "barrow": (r, x, y, a) => { ctx.beginPath(); ctx.ellipse(x, y, 9, 5, 0, Math.PI, 0); stroke(0.75 * a, 1.3); },
      "hill fort": (r, x, y, a) => { ctx.beginPath(); ctx.ellipse(x, y - 2, 11, 6, 0, 0, 7); ctx.ellipse(x, y - 2, 7, 3.6, 0, 0, 7); stroke(0.6 * a, 1.1); },
      "chalk figure": (r, x, y, a) => { ctx.beginPath(); ctx.moveTo(x - 8, y - 4); ctx.quadraticCurveTo(x, y - 9, x + 8, y - 5); ctx.moveTo(x - 5, y - 5); ctx.lineTo(x - 7, y); ctx.moveTo(x + 5, y - 5); ctx.lineTo(x + 6, y); ctx.strokeStyle = "rgba(255,255,255,.9)"; ctx.lineWidth = 2; ctx.stroke(); },
      "oak": (r, x, y, a) => tree(r, x, y, 13, a), "yew": (r, x, y, a) => tree(r, x, y, 12, a, true),
      "hermit's cell": (r, x, y, a) => house(x, y, 9, a), "dovecote": (r, x, y, a) => { ctx.beginPath(); ctx.rect(x - 4, y - 9, 8, 9); stroke(0.75 * a, 1.1); },
    };

    // terrain symbols, tile by tile, denser on ground you have walked
    for (let y = 0; y < A.h; y++) for (let x = 0; x < N; x++) {
      const c = cell(x, y); if (!c.k || !c.b) continue;
      const r = mulberry(seed * 7919 + x * 131 + y * 7);
      const a = c.k === 2 ? 0.95 : 0.42, cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T;
      const busy = c.s ? 0.32 : 0;                          // keep the middle clear for a village or ruin
      const spot = (spread) => { for (let i = 0; i < 6; i++) { const px = cx + jitter(r, T * spread), py = cy + jitter(r, T * spread); if (!busy || Math.hypot(px - cx, py - cy) > T * busy) return [px, py]; } return null; };
      const few = (n) => MINI ? Math.max(1, Math.round(n * 0.4)) : n;
      if (c.b === "forest") {
        const n = few(c.k === 2 ? 9 : 5), list = [];
        for (let i = 0; i < n; i++) { const p = spot(MINI ? 0.8 : 1.05); if (p) list.push(p); }
        list.sort((p, q) => p[1] - q[1]).forEach(([px, py]) => tree(r, px, py, (8 + r() * 4) * SYM, a, r() < 0.25));
      } else if (c.b === "hills") {
        for (let i = 0; i < few(c.k === 2 ? 3 : 2); i++) { const p = spot(0.8); if (p) hill(r, p[0], p[1], (13 + r() * 6) * SYM, a); }
      } else if (c.b === "peaks") {
        const list = []; for (let i = 0; i < few(c.k === 2 ? 3 : 2); i++) { const p = spot(0.75); if (p) list.push(p); }
        list.sort((p, q) => p[1] - q[1]).forEach(([px, py]) => peak(r, px, py, (15 + r() * 7) * SYM, a));
      } else if (c.b === "marsh") {
        for (let i = 0; i < few(c.k === 2 ? 5 : 3); i++) { const p = spot(0.9); if (p) tuft(r, p[0], p[1], (5 + r() * 2) * SYM, a); }
      } else if (c.b === "plains" && !MINI) {
        for (let i = 0; i < (c.k === 2 ? 5 : 3); i++) { const p = spot(0.95); if (p) grass(r, p[0], p[1], 5 + r() * 2, a); }
        if (r() < 0.22) { const p = spot(0.8); if (p) tree(r, p[0], p[1], 7, a); }
      }
      if (c.f && !MINI) c.f.forEach((kind, i) => {
        const draw = LANDMARK[kind]; if (!draw) return;
        const px = cx + (i ? -1 : 1) * T * 0.3 + jitter(r, 6), py = cy + T * 0.3 + jitter(r, 4);
        draw(r, px, py, a);
      });
    }

    if (MINI) {                                           // the panel shows sites as small icons, and nothing else
      for (let y = 0; y < A.h; y++) for (let x = 0; x < N; x++) {
        const c = cell(x, y); if (!c.s) continue;
        const r = mulberry(seed + x * 31 + y * 1013), cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T, a = c.k === 2 ? 1 : 0.6;
        if (c.s === "village") { [[-14, 6], [13, 8], [0, -10]].forEach(([dx, dy]) => house(cx + dx, cy + dy, 22, a)); }
        else if (c.s === "ruin") ruin(r, cx, cy + 16, 30, a);
        else if (c.s === "shrine") shrine(cx, cy + 16, 26, a);
        else if (c.s === "camp") tent(cx, cy + 16, 30, a);
      }
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      return;
    }

    // the road you have walked, on its own layer (so it can be toggled)
    if (opts.trail) {
      const tc = opts.trail, tctx = tc.getContext("2d");
      tc.width = canvas.width; tc.height = canvas.height;
      tctx.setTransform(S, 0, 0, S, -VX * S, -VY * S);
      const tr = [];
      A.trail.forEach((p) => { const last = tr[tr.length - 1]; if (!last || last.x !== p[0] || last.y !== p[1]) tr.push({ x: p[0], y: p[1] }); });
      if (tr.length > 1) {
        tctx.setLineDash([7, 6]); tctx.beginPath();
        const pt = (q) => { const r = mulberry(seed + q.x * 977 + q.y * 61 + 3); return [X0 + (q.x + 0.5 + jitter(r, 0.32)) * T, Y0 + (q.y + 0.5 + jitter(r, 0.32)) * T]; };
        let [px, py] = pt(tr[0]); tctx.moveTo(px, py);
        for (let i = 1; i < tr.length; i++) { const [nx, ny] = pt(tr[i]); tctx.quadraticCurveTo(px, py, (px + nx) / 2, (py + ny) / 2); px = nx; py = ny; }
        tctx.lineTo(px, py);
        tctx.lineCap = "round"; tctx.strokeStyle = `rgba(${PAPER.join(",")},.6)`; tctx.lineWidth = 4.5; tctx.stroke();   // a pale halo keeps it readable over ink
        tctx.strokeStyle = "rgba(142,42,30,.8)"; tctx.lineWidth = 2.3; tctx.stroke();
        const [sx, sy] = pt(tr[0]);                        // where the road began
        tctx.setLineDash([]); tctx.beginPath(); tctx.arc(sx, sy, 5, 0, 7); tctx.fillStyle = "rgba(142,42,30,.85)"; tctx.fill();
      }
    }

    // sites and their names
    const serif = '"IM Fell English", "Iowan Old Style", Palatino, Georgia, serif';
    const placed = [];                                    // boxes already taken by labels and marks
    const MAPBOX = [X0 + 4, Y0 + 4, W - X0 - 4, Y0 + A.h * T - 4];
    function box(text, x, y, size, opts) {
      ctx.save();
      ctx.font = `${opts.italic ? "italic " : ""}${size}px ${opts.sc ? '"IM Fell English SC", ' : ""}${serif}`;
      const w = ctx.measureText(text).width + (opts.spacing || 0) * text.length, h = size * 1.05;
      ctx.restore();
      const a = opts.angle || 0, cw = Math.abs(Math.cos(a)) * w + Math.abs(Math.sin(a)) * h, chh = Math.abs(Math.sin(a)) * w + Math.abs(Math.cos(a)) * h;
      return [x - cw / 2 - 3, y - chh / 2 - 2, x + cw / 2 + 3, y + chh / 2 + 2];
    }
    const hits = (b) => placed.some(p => b[0] < p[2] && b[2] > p[0] && b[1] < p[3] && b[3] > p[1]);
    const inside = (b) => b[0] >= MAPBOX[0] && b[1] >= MAPBOX[1] && b[2] <= MAPBOX[2] && b[3] <= MAPBOX[3];
    function place(text, cands, opts) {
      // try each (x, y, size) in turn; keep the first that fits on the map without covering anything
      for (const [x, y, size] of cands) {
        const b = box(text, x, y, size, opts);
        if (inside(b) && !hits(b)) { placed.push(b); label(text, x, y, size, opts); return true; }
      }
      return false;
    }
    function reserve(x, y, w, h) { placed.push([x - w / 2, y - h / 2, x + w / 2, y + h / 2]); }
    function label(text, x, y, size, opts) {
      opts = opts || {};
      ctx.save(); ctx.translate(x, y); if (opts.angle) ctx.rotate(opts.angle);
      ctx.font = `${opts.italic ? "italic " : ""}${size}px ${opts.sc ? '"IM Fell English SC", ' : ""}${serif}`;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      if (opts.spacing) { try { ctx.letterSpacing = opts.spacing + "px"; } catch (e) { /* older browsers */ } }
      ctx.lineWidth = opts.halo === undefined ? 4 : opts.halo; ctx.strokeStyle = `rgba(${PAPER.join(",")},.85)`; ctx.lineJoin = "round";
      if (ctx.lineWidth) ctx.strokeText(text, 0, 0);
      ctx.fillStyle = opts.color || ink(opts.alpha || 0.9); ctx.fillText(text, 0, 0); ctx.restore();
    }
    {   // the pin and its label come first: nothing may cover where you are
      const [x, y] = A.pos, cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T - 4;
      reserve(cx, cy - 4, 34, 40);
      place("you are here", [[cx, cy - 32, 14], [cx, cy + 28, 14], [cx + 52, cy - 6, 14], [cx - 52, cy - 6, 14]], { italic: true, color: "rgba(140,30,25,1)" });
    }
    for (let y = 0; y < A.h; y++) for (let x = 0; x < N; x++) {
      const c = cell(x, y); if (c.s) reserve(X0 + (x + 0.5) * T, Y0 + (y + 0.5) * T + 2, c.s === "village" ? 44 : 30, c.s === "village" ? 34 : 28);
    }
    if (A.relic && !A.relic_found) reserve(X0 + (A.relic[0] + 0.5) * T, Y0 + (A.relic[1] + 0.5) * T, 30, 30);
    A.goals.forEach(([x, y]) => reserve(X0 + (x + 0.5) * T, Y0 + (y + 0.5) * T, 30, 30));
    for (let y = 0; y < A.h; y++) for (let x = 0; x < N; x++) {
      const c = cell(x, y); if (!c.s) continue;
      const r = mulberry(seed + x * 31 + y * 1013), cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T, a = c.k === 2 ? 1 : 0.6;
      if (c.s === "village") {
        [[-9, 2], [8, 4], [0, -6], [-2, 12], [11, -6]].slice(0, 4 + (r() < 0.5)).sort((p, q) => p[1] - q[1]).forEach(([dx, dy]) => house(cx + dx, cy + dy, 11, a));
        place(c.n, [[cx, cy + T * 0.42, 19], [cx, cy - T * 0.48, 19], [cx + T * 0.75, cy, 18], [cx - T * 0.75, cy, 18], [cx, cy + T * 0.42, 15]], { sc: true, spacing: 1.5 });
      } else if (c.s === "ruin") { ruin(r, cx, cy + 8, 15, a); place("ruin", [[cx, cy + T * 0.36, 13], [cx, cy - T * 0.36, 13]], { italic: true, alpha: 0.75 }); }
      else if (c.s === "shrine") { shrine(cx, cy + 8, 13, a); place("shrine", [[cx, cy + T * 0.36, 13], [cx, cy - T * 0.36, 13]], { italic: true, alpha: 0.75 }); }
      else if (c.s === "camp") { tent(cx, cy + 8, 15, a); }
    }

    // region names, along the lie of the land
    const regs = A.regions.map((reg) => {
      const pts = [];
      for (let y = 0; y < A.h; y++) for (let x = 0; x < N; x++) { const c = cell(x, y); if (c.k && c.g === reg.id && c.b !== "lake") pts.push([x + 0.5, y + 0.5]); }
      return { reg, pts };
    }).filter(o => o.pts.length >= 2).sort((a, b) => b.pts.length - a.pts.length);     // big regions get first pick
    regs.forEach(({ reg, pts }) => {
      const mx = pts.reduce((s, p) => s + p[0], 0) / pts.length, my = pts.reduce((s, p) => s + p[1], 0) / pts.length;
      let sxx = 0, sxy = 0, syy = 0; pts.forEach(([x, y]) => { sxx += (x - mx) ** 2; sxy += (x - mx) * (y - my); syy += (y - my) ** 2; });
      let ang = 0.5 * Math.atan2(2 * sxy, sxx - syy); ang = Math.max(-0.4, Math.min(0.4, ang));
      const size = Math.min(26, 13 + Math.sqrt(pts.length) * 2.6);
      const name = reg.name.replace(/^the /i, "").toUpperCase();
      const cx = X0 + mx * T, cy = Y0 + my * T;
      const cands = [];
      for (const s of [size, size * 0.82, size * 0.68]) for (const [dx, dy] of [[0, 0], [0, -0.45], [0, 0.45], [0.4, 0], [-0.4, 0], [0, -0.9], [0, 0.9]]) cands.push([cx + dx * T, cy + dy * T, s]);
      for (const angle of [ang, 0]) {
        if (place(name, cands.map(([x, y, s]) => [x, y, s]), { italic: true, spacing: size * 0.22, alpha: 0.62, halo: 3, angle })) break;
      }
    });

    // here be nothing yet: the largest blank stretch is marked unknown
    let best = null;
    for (let y = 1; y < A.h - 1; y++) for (let x = 1; x < N - 1; x++) {
      if (cell(x, y).k) continue;
      let d = 9; for (let yy = 0; yy < A.h; yy++) for (let xx = 0; xx < N; xx++) if (cell(xx, yy).k) d = Math.min(d, Math.max(Math.abs(xx - x), Math.abs(yy - y)));
      if (!best || d > best.d) best = { x, y, d };
    }
    if (best && best.d >= 3) {
      const bx = X0 + (best.x + 0.5) * T, by = Y0 + (best.y + 0.5) * T;
      place("Terra incognita", [[bx, by, 26], [bx, by + T, 26], [bx, by - T, 26], [bx + T, by, 26], [bx - T, by, 26], [bx, by + 2 * T, 22]], { italic: true, alpha: 0.32, halo: 0, angle: -0.12 });
    }

    // the relic, your goals, and you
    if (A.relic && !A.relic_found) {
      const [x, y] = A.relic, cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T;
      ctx.save(); ctx.beginPath(); ctx.moveTo(cx - 11, cy - 11); ctx.lineTo(cx + 11, cy + 11); ctx.moveTo(cx + 11, cy - 11); ctx.lineTo(cx - 11, cy + 11);
      ctx.strokeStyle = "rgba(150,30,25,.9)"; ctx.lineWidth = 4; ctx.lineCap = "round"; ctx.stroke();
      if (!cell(x, y).k) { ctx.setLineDash([3, 5]); ctx.beginPath(); ctx.arc(cx, cy, T * 0.9, 0, 7); ctx.lineWidth = 1.5; ctx.stroke(); }
      ctx.restore();
      place(`the ${A.relic_name} lies hereabouts`, [[cx, cy + T * 0.55, 15], [cx, cy - T * 0.55, 15], [cx, cy + T * 0.55, 12]], { italic: true, color: "rgba(140,30,25,.95)" });
    }
    A.goals.forEach(([x, y]) => {
      const cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T;
      ctx.beginPath(); ctx.arc(cx, cy, 13, 0, 7); ctx.strokeStyle = "rgba(150,30,25,.75)"; ctx.lineWidth = 2; ctx.setLineDash([4, 3]); ctx.stroke(); ctx.setLineDash([]);
    });
    {
      const [x, y] = A.pos, cx = X0 + (x + 0.5) * T, cy = Y0 + (y + 0.5) * T - 4;
      ctx.beginPath(); ctx.moveTo(cx, cy + 14); ctx.bezierCurveTo(cx - 15, cy - 4, cx - 8, cy - 20, cx, cy - 20); ctx.bezierCurveTo(cx + 8, cy - 20, cx + 15, cy - 4, cx, cy + 14);
      ctx.fillStyle = "rgba(170,35,28,.92)"; ctx.fill(); ctx.strokeStyle = ink(0.95); ctx.lineWidth = 1.4; ctx.stroke();
      ctx.beginPath(); ctx.arc(cx, cy - 8, 4.2, 0, 7); ctx.fillStyle = `rgb(${PAPER.join(",")})`; ctx.fill();
    }

    // ---- decoration: frame, cartouche, compass, scale
    ctx.save();
    ctx.strokeStyle = ink(0.85); ctx.lineWidth = 3; ctx.strokeRect(40, 40, W - 80, H - 80);
    ctx.lineWidth = 1; ctx.strokeRect(50, 50, W - 100, H - 100);
    ctx.strokeRect(X0 - 8, Y0 - 8, W - 2 * X0 + 16, A.h * T + 16);
    for (let i = X0; i < W - X0; i += T / 2) {                   // tick marks along the border, like old degree scales
      const k = Math.round((i - X0) / (T / 2)) % 2;
      ctx.fillStyle = ink(k ? 0.8 : 0.15); ctx.fillRect(i, Y0 - 8, T / 2, 4); ctx.fillRect(i, Y0 + A.h * T + 4, T / 2, 4);
    }
    for (let i = Y0; i < Y0 + A.h * T; i += T / 2) {
      const k = Math.round((i - Y0) / (T / 2)) % 2;
      ctx.fillStyle = ink(k ? 0.8 : 0.15); ctx.fillRect(X0 - 8, i, 4, T / 2); ctx.fillRect(W - X0 + 4, i, 4, T / 2);
    }
    [[45, 45], [W - 45, 45], [45, H - 45], [W - 45, H - 45]].forEach(([x, y]) => {
      ctx.beginPath(); ctx.moveTo(x, y - 12); ctx.lineTo(x + 12, y); ctx.lineTo(x, y + 12); ctx.lineTo(x - 12, y); ctx.closePath();
      ctx.fillStyle = `rgb(${PAPER.join(",")})`; ctx.fill(); ctx.lineWidth = 1.4; ctx.stroke();
      ctx.beginPath(); ctx.arc(x, y, 3, 0, 7); ctx.fillStyle = ink(0.8); ctx.fill();
    });
    // title cartouche
    const cw = 640, ch = 78, cx0 = W / 2 - cw / 2, cy0 = 62;
    ctx.beginPath(); ctx.moveTo(cx0 + 20, cy0); ctx.lineTo(cx0 + cw - 20, cy0); ctx.quadraticCurveTo(cx0 + cw, cy0, cx0 + cw, cy0 + 20);
    ctx.lineTo(cx0 + cw, cy0 + ch - 20); ctx.quadraticCurveTo(cx0 + cw, cy0 + ch, cx0 + cw - 20, cy0 + ch); ctx.lineTo(cx0 + 20, cy0 + ch);
    ctx.quadraticCurveTo(cx0, cy0 + ch, cx0, cy0 + ch - 20); ctx.lineTo(cx0, cy0 + 20); ctx.quadraticCurveTo(cx0, cy0, cx0 + 20, cy0);
    ctx.fillStyle = `rgba(${PAPER.join(",")},.92)`; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = ink(0.85); ctx.stroke();
    [[cx0 - 4, cy0 + ch / 2, -1], [cx0 + cw + 4, cy0 + ch / 2, 1]].forEach(([x, y, d]) => {   // scroll curls
      ctx.beginPath(); ctx.arc(x + d * 10, y, 12, 0, 7); ctx.lineWidth = 1.6; ctx.stroke();
      ctx.beginPath(); ctx.arc(x + d * 10, y, 5, 0, 7); ctx.stroke();
    });
    ctx.restore();
    label(`The Lands about ${A.home}`, W / 2, cy0 + 30, 32, { halo: 0, alpha: 0.92 });
    label(`as charted by ${A.name}, day ${A.day}, in ${A.season}`, W / 2, cy0 + 58, 16, { italic: true, halo: 0, alpha: 0.75 });

    // compass rose
    {
      const x = W - X0 - 70, y = Y0 + A.h * T - 80, R1 = 52, R2 = 14;
      ctx.save(); ctx.translate(x, y);
      ctx.beginPath(); ctx.arc(0, 0, R1 + 8, 0, 7); ctx.fillStyle = `rgba(${PAPER.join(",")},.75)`; ctx.fill(); ctx.strokeStyle = ink(0.7); ctx.lineWidth = 1; ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, R1 - 6, 0, 7); ctx.stroke();
      for (let i = 0; i < 8; i++) {
        const t = i * Math.PI / 4 - Math.PI / 2, long = i % 2 === 0, L = long ? R1 : R1 * 0.62;
        for (const side of [-1, 1]) {
          ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(t) * L, Math.sin(t) * L);
          ctx.lineTo(Math.cos(t + side * 0.5) * R2 * (long ? 1 : 0.75), Math.sin(t + side * 0.5) * R2 * (long ? 1 : 0.75)); ctx.closePath();
          ctx.fillStyle = side > 0 ? ink(0.85) : `rgba(${PAPER.join(",")},1)`; ctx.fill(); ctx.strokeStyle = ink(0.85); ctx.lineWidth = 1; ctx.stroke();
        }
      }
      ctx.restore();
      label("N", x, y - R1 - 20, 20, { halo: 0 });
    }
    // scale bar: three tiles is about a morning's walk
    {
      const x = X0 + 30, y = Y0 + A.h * T - 40;
      for (let i = 0; i < 3; i++) { ctx.fillStyle = i % 2 ? `rgb(${PAPER.join(",")})` : ink(0.8); ctx.fillRect(x + i * T, y, T, 7); }
      ctx.strokeStyle = ink(0.85); ctx.lineWidth = 1; ctx.strokeRect(x, y, T * 3, 7);
      label("a morning's walk", x + T * 1.5, y - 14, 15, { italic: true });
    }

    // ---- age: stains, folds and a darkened edge
    ctx.save();
    const sr = mulberry(seed + 99);
    for (let i = 0; i < 3; i++) {
      const x = sr() * W, y = sr() * H, rad = 60 + sr() * 140;
      const g = ctx.createRadialGradient(x, y, rad * 0.2, x, y, rad);
      g.addColorStop(0, "rgba(120,80,30,0)"); g.addColorStop(0.85, "rgba(120,80,30,.045)"); g.addColorStop(1, "rgba(120,80,30,0)");
      ctx.fillStyle = g; ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    for (const [x1, y1, x2, y2] of [[W / 2, 0, W / 2, H], [0, H / 2, W, H / 2]]) {
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.strokeStyle = "rgba(255,250,235,.35)"; ctx.lineWidth = 3; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x1 + (x1 === x2 ? 2 : 0), y1 + (y1 === y2 ? 2 : 0)); ctx.lineTo(x2 + (x1 === x2 ? 2 : 0), y2 + (y1 === y2 ? 2 : 0));
      ctx.strokeStyle = "rgba(90,60,30,.12)"; ctx.lineWidth = 1.5; ctx.stroke();
    }
    const vg = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.42, W / 2, H / 2, Math.max(W, H) * 0.72);
    vg.addColorStop(0, "rgba(80,50,20,0)"); vg.addColorStop(1, "rgba(80,50,20,.38)");
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }

  window.drawAtlas = drawAtlas;
})();
