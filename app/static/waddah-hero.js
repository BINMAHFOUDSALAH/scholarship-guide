// وضّاح beside «بوضوح» on the Arabic homepage (owner, 2026-11-27). The scene itself is CSS (style.css, «wh-» keyframes,
// about four seconds); this decides when it plays and where he points:
// - once, when the hero is on screen and the page is in front, unless the student has already started on the form;
// - at most one repeat, 13 seconds after the first ends, only if the hero is still on screen and the form untouched;
// - never with reduced motion (the still lean stays);
// - he faces and tilts toward the real search field («تخصص أو جامعة…»), measured on the page, so the point lands on
//   it on a laptop and on a phone alike. His feet stay put: the tilt pivots on them.
(function () {
  const root = document.querySelector("[data-waddah-hero]");
  if (!root) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const hero = root.closest(".ask-hero");
  const form = hero && hero.querySelector("form");
  const field = document.getElementById("home-q");
  if (!hero || !form || !field || !("IntersectionObserver" in window)) return;

  const REPEAT_AFTER = 13000;
  // On the 360-wide stage (viewBox from y = -44): his feet, and the pointing hand of the left-facing pose.
  const FEET_X = 180, HAND_X = 16, HAND_Y = 131, TOP = -44, VIEW_W = 360;
  let touched = false, onScreen = false, plays = 0, timer = 0, waiting = false;

  for (const type of ["focusin", "pointerdown", "input", "keydown", "change"]) {
    form.addEventListener(type, () => { touched = true; clearTimeout(timer); }, { passive: true });
  }

  function aim() {
    const box = root.getBoundingClientRect();
    const s = box.width / VIEW_W;
    const f = field.getBoundingClientRect();
    const target = { x: f.left + f.width / 2, y: f.top + f.height / 2 };
    const face = target.x <= box.left + FEET_X * s ? 1 : -1;     // 1: the left-facing pose as drawn
    const handX = box.left + (face === 1 ? HAND_X : VIEW_W - HAND_X) * s;
    const handY = box.top + (HAND_Y - TOP) * s;
    const down = Math.atan2(target.y - handY, Math.max(Math.abs(target.x - handX), 1)) * 180 / Math.PI;
    const tilt = Math.max(-6, Math.min(22, down));                  // a lean, never a fall
    root.style.setProperty("--wh-face", face);
    root.style.setProperty("--wh-aim", (face === 1 ? -tilt : tilt).toFixed(1) + "deg");
  }

  function play() {
    if (reduce.matches || plays >= 2) return;
    plays += 1;
    aim();
    root.classList.remove("is-playing");
    void root.offsetWidth; // restart the keyframes
    root.classList.add("is-playing");
  }

  root.addEventListener("animationend", (event) => {
    if (event.animationName !== "wh-lean") return;
    root.classList.remove("is-playing"); // the resting state is the same still lean
    if (plays < 2) timer = setTimeout(() => {
      if (onScreen && !touched && document.visibilityState === "visible") play();
    }, REPEAT_AFTER);
  });

  function first() {
    if (plays || waiting || touched || !onScreen || document.visibilityState !== "visible") return;
    waiting = true;
    setTimeout(() => {
      waiting = false;
      if (!plays && !touched && onScreen && document.visibilityState === "visible") play();
    }, 600);
  }

  new IntersectionObserver((entries) => {
    onScreen = entries[entries.length - 1].isIntersecting;
    if (!onScreen) clearTimeout(timer);
    first();
  }, { threshold: 0.6 }).observe(hero);
  document.addEventListener("visibilitychange", first);
  reduce.addEventListener && reduce.addEventListener("change", () => { if (reduce.matches) root.classList.remove("is-playing"); });
})();
