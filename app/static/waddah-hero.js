// وضّاح beside «بوضوح» on the Arabic homepage (owner, 2026-11-27). The figure is a vector drawing of his own shapes
// (partials/waddah_hero.html) and the poses are CSS (style.css, «wh-» keyframes, about four and a half seconds); this
// decides when he plays and which way he turns:
// - once, when the hero is on screen and the page is in front, unless the student has already started on the form;
// - at most one repeat, 13 seconds after the first ends, only if the hero is still on screen and the form untouched;
// - never with reduced motion (the still thinking pose stays);
// - he faces the real search field («تخصص أو جامعة…»), measured on the page, and his open hand is aimed at it, so the
//   gesture lands on it on a laptop and on a phone alike. His feet stay put: the lean pivots on them.
(function () {
  const root = document.querySelector("[data-waddah-hero]");
  if (!root) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const hero = root.closest(".ask-hero");
  const form = hero && hero.querySelector("form");
  const field = document.getElementById("home-q");
  if (!hero || !form || !field) return;

  const REPEAT_AFTER = 13000;
  // On the 360-wide stage (viewBox from y = -44): his feet, and the shoulder of the arm on the side he faces as drawn.
  const FEET_X = 180, SHOULDER_X = 122, SHOULDER_Y = 208, TOP = -44, VIEW_W = 360;
  let touched = false, onScreen = false, plays = 0, timer = 0, waiting = false;

  for (const type of ["focusin", "pointerdown", "input", "keydown", "change"]) {
    form.addEventListener(type, () => { touched = true; clearTimeout(timer); }, { passive: true });
  }

  function aim() {
    const box = root.getBoundingClientRect();
    if (!box.width) return;
    const s = box.width / VIEW_W;
    const f = field.getBoundingClientRect();
    const target = { x: f.left + f.width / 2, y: f.top + f.height / 2 };
    const face = target.x <= box.left + FEET_X * s ? 1 : -1;     // 1: facing the viewer's left, as drawn
    const x = box.left + (face === 1 ? SHOULDER_X : VIEW_W - SHOULDER_X) * s;
    const y = box.top + (SHOULDER_Y - TOP) * s;
    const down = Math.atan2(target.y - y, Math.max(Math.abs(target.x - x), 1)) * 180 / Math.PI;
    // The body leans 8° toward the field as he opens his hand, so the arm makes up the rest; kept to a gesture.
    const angle = Math.max(4, Math.min(48, down - 8));
    root.style.setProperty("--wh-face", face);
    root.style.setProperty("--wh-aim", angle.toFixed(1) + "deg");
  }

  aim();
  let resizeFrame = 0;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => { if (!root.classList.contains("is-playing")) aim(); });
  }, { passive: true });
  if (!("IntersectionObserver" in window)) return;

  function play() {
    if (reduce.matches || plays >= 2) return;
    plays += 1;
    aim();
    root.classList.remove("is-playing");
    void root.offsetWidth; // restart the keyframes
    root.classList.add("is-playing");
  }

  root.addEventListener("animationend", (event) => {
    if (event.animationName !== "wh-fig") return;
    root.classList.remove("is-playing"); // the resting state is the same thinking pose
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
