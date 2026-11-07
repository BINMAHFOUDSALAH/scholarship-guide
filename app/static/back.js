// Back keeps your place (decision 085). Safari on iPhone sometimes restores a page's scroll before the page has its
// full height, and lands at the top. So each page remembers where you were when you leave it, and on Back puts you
// there if the browser didn't. Pages that restore their own place (the explorer's results) are left alone.
// sessionStorage: this tab only, cleared when it closes; only a path and a number.
(function () {
  "use strict";
  const KEY = "wadih:place:" + location.pathname + location.search;
  const remember = () => {
    try { sessionStorage.setItem(KEY, String(Math.round(window.scrollY))); } catch (e) { /* storage blocked */ }
  };
  window.addEventListener("pagehide", remember);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") remember(); });

  function restore() {
    // The explorer's results restore their own place (universities.js).
    if (history.scrollRestoration === "manual" || document.getElementById("results")) return;
    let y = 0;
    try { y = Number(sessionStorage.getItem(KEY)) || 0; } catch (e) { return; }
    if (y < 40 || window.scrollY > 40 || location.hash) return; // nothing to restore, or the browser already did
    const go = () => { if (window.scrollY < 40) window.scrollTo(0, y); };
    go();
    // Again once images and fonts have given the page its full height.
    window.addEventListener("load", go, { once: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(go);
  }
  const nav = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
  if (nav && nav.type === "back_forward") restore();
  // A page brought back whole from the browser's cache: only if it came back at the top.
  window.addEventListener("pageshow", (event) => { if (event.persisted) restore(); });
})();
