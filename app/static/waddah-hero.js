// وضّاح beside «بوضوح» on the Arabic homepage (owner, 2026-11-27). He is his own renders (partials/waddah_hero.html):
// one pose shows at a time, and this decides which, and when. style.css moves him between poses (a squash, a hop, a
// lean toward the field) and keeps him breathing while he rests.
//
// - The scene, once the hero is on screen and the page is in front: «hmm…» (unsure), «got it!» (a hop, cheering), a
//   lean pointing at the search field, a wave, then back to resting with a hand at his chin (about five seconds).
// - Small moments after that, every 9 to 15 seconds while the hero is on screen: a wave, a look in a book, a cheer…
//   at most MAX_MOMENTS of them, and never while the student is in the search field.
// - He answers the student: the search field focused → his magnifier; the pointer on him → a wave; a tap → a cheer.
// - He points at the real search field, measured on the page, so on a laptop and a phone alike.
// - Reduced motion (on many Windows laptops, where «Animation effects» is off): no hops, leans or breathing. The poses
//   only fade from one to the next, the scene plays once and he still answers the field and the pointer.
(function () {
  const root = document.querySelector("[data-waddah-hero]");
  if (!root) return;
  const hero = root.closest(".ask-hero");
  const form = hero && hero.querySelector("form");
  const field = document.getElementById("home-q");
  if (!hero || !form || !field) return;
  const body = root.querySelector(".wh-body");
  const imgs = {};
  for (const img of root.querySelectorAll("[data-pose-img]")) imgs[img.dataset.poseImg] = img;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  const REST = "logo";
  const SCENE = [["unsure", 950, "pop"], ["cheer", 900, "hop"], ["point", 1500, "lean"], ["wave", 1100, "pop"]];
  const MOMENTS = [["wave", 1300, "pop"], ["read", 1900, "pop"], ["cheer", 900, "hop"], ["unsure", 1200, "pop"],
                   ["point", 1500, "lean"], ["search", 1600, "pop"]];
  const MAX_MOMENTS = 8;
  let pose = REST, busy = false, onScreen = false, played = false, moments = 0, timer = 0, run = 0, inField = false, touched = false;

  // The other poses load once the page is idle, so the first paint only waits for the resting one.
  function preload() {
    for (const img of Object.values(imgs)) if (img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; }
  }
  if ("requestIdleCallback" in window) requestIdleCallback(preload, { timeout: 1500 }); else setTimeout(preload, 600);

  // Which way the field is from him: the point pose (drawn pointing to the viewer's right) turns to face it.
  function aim() {
    const me = root.getBoundingClientRect(), f = field.getBoundingClientRect();
    const left = f.left + f.width / 2 < me.left + me.width / 2;
    root.dataset.face = left ? "left" : "right";
  }

  async function show(next, move) {
    const img = imgs[next];
    if (!img) return;
    if (img.dataset.src) preload();
    try { await img.decode(); } catch (e) { if (!img.complete) return; }
    if (next === "point") aim();
    for (const [name, el] of Object.entries(imgs)) el.classList.toggle("is-on", name === next);
    root.dataset.pose = pose = next;
    body.classList.remove("wh-pop", "wh-hop", "wh-lean");
    if (move && !reduce.matches) {
      void body.offsetWidth; // restart the movement
      body.classList.add("wh-" + move);
    }
  }

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));

  // A run of poses, then back to resting (or to the magnifier, if the student is in the field by then). A newer run,
  // or the student entering the field, ends it.
  async function play(steps) {
    const id = ++run;
    busy = true;
    for (const [p, ms, move] of steps) {
      if (id !== run || inField) break;
      await show(p, move);
      await wait(ms);
    }
    if (id !== run) return;
    busy = false;
    await show(inField ? "search" : REST, "pop");
    schedule();
  }

  function schedule() {
    clearTimeout(timer);
    if (reduce.matches || moments >= MAX_MOMENTS) return;
    timer = setTimeout(() => {
      if (busy || inField || !onScreen || document.visibilityState !== "visible") return schedule();
      // Once the student has used the form, he no longer points them to it.
      const choices = MOMENTS.filter(([p]) => !(touched && p === "point") && p !== pose);
      moments += 1;
      play([choices[Math.floor(Math.random() * choices.length)]]);
    }, 9000 + Math.random() * 6000);
  }

  function first() {
    if (played || !onScreen || document.visibilityState !== "visible") return;
    played = true;
    setTimeout(() => { if (!inField) play(SCENE); else schedule(); }, 600);
  }

  field.addEventListener("focus", () => { inField = true; touched = true; run++; busy = false; show("search", "pop"); });
  field.addEventListener("blur", () => { inField = false; if (!busy) show(REST, "pop"); schedule(); });
  form.addEventListener("input", () => { touched = true; }, { passive: true });

  // The pointer on him: a wave. A tap or a click: a cheer. Neither interrupts the student's search.
  root.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse" && !busy && !inField) play([["wave", 1300, "pop"]]); });
  root.addEventListener("click", () => { if (!inField) play([["cheer", 900, "hop"]]); });

  window.addEventListener("resize", () => { if (pose === "point") aim(); }, { passive: true });
  if (!("IntersectionObserver" in window)) return;
  new IntersectionObserver((entries) => {
    onScreen = entries[entries.length - 1].isIntersecting;
    first();
  }, { threshold: 0.4 }).observe(hero);
  document.addEventListener("visibilitychange", first);
})();
