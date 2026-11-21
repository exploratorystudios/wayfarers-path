// Paints the full map in the background, so it's ready the moment you open it.
// The page posts {key, data, scale}; this paints the map and your road onto
// offscreen canvases and hands back finished bitmaps.
importScripts("/atlas.js");

let fontsReady = null;
function loadFonts() {
  if (fontsReady) return fontsReady;
  const faces = [
    ["IM Fell English", "/fonts/IMFellEnglish-Regular.woff2", {}],
    ["IM Fell English", "/fonts/IMFellEnglish-Italic.woff2", { style: "italic" }],
    ["IM Fell English SC", "/fonts/IMFellEnglishSC-Regular.woff2", {}],
  ];
  fontsReady = Promise.all(faces.map(([family, url, desc]) => {
    try {
      const f = new FontFace(family, `url(${url})`, desc);
      return f.load().then(ff => { self.fonts.add(ff); }).catch(() => {});
    } catch (e) { return Promise.resolve(); }      // no fonts in workers here: fallback lettering
  }));
  return fontsReady;
}

self.onmessage = async (e) => {
  const { key, data, scale } = e.data;
  try {
    await loadFonts();
    const map = new OffscreenCanvas(1, 1), road = new OffscreenCanvas(1, 1);
    self.drawAtlas(map, data, { scale, trail: road });
    const a = map.transferToImageBitmap(), b = road.transferToImageBitmap();
    self.postMessage({ key, map: a, road: b }, [a, b]);
  } catch (err) {
    self.postMessage({ key, error: String(err) });
  }
};
