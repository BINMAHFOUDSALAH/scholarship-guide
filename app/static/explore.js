// «جرّب قبل أن تقرر» (decision 069): turns the one long form into steps, one question per screen.
// - Part 1 (what makes the decision hard, the grade), part 2 (one activity per screen), part 3 (progress in
//   subjects, a field the student or their family has in mind), then a review where any answer can be changed.
// - In part 2, tapping an answer moves on to the next activity after a short moment (AUTO_NEXT_MS), so the
//   student sees their choice first (owner, 2026-11-04: pressing «التالي» 30 times is too slow). Only taps do this:
//   with the keyboard, arrow keys change the choice and the student moves on with Enter or «التالي».
//   «تخطَّ» skips a question; «التالي» shows when a question already has an answer (e.g. after «السابق»).
// - A survey must never record an answer nobody chose. The first version of moving on by itself let a second tap
//   answer the next question (owner's iPhone, 2026-11-04). Now a second tap before the move lands on the same
//   question (the last choice wins, one move), and for a moment after the question changes, taps on the questions
//   and buttons are ignored (never key presses).
// - Each visit starts clean (a reload never brings old answers back); Back returns to where the student left off,
//   with the answers: the review when coming back from the result, the same question when they left mid-way.
//   Only the step number is kept, in this page's own history entry; answers are never stored.
// - Nothing is stored or sent until the student presses «اعرض النتيجة». Without JavaScript the whole form shows
//   and works as it is.
(function () {
  const t = (text) => (window.WADIH_I18N && window.WADIH_I18N[text]) || text; // English pages (decision 066)
  const fill = (text, values) => t(text).replace(/\{(\w+)\}/g, (m, key) => (key in values ? String(values[key]) : m));

  // The result page: printing is the only way to keep it (nothing is saved).
  for (const button of document.querySelectorAll("[data-print]")) {
    button.hidden = false;
    button.addEventListener("click", () => window.print());
  }

  const form = document.querySelector("[data-explore]");
  if (!form) return;

  const steps = Array.from(form.querySelectorAll("[data-step]"));
  const review = form.querySelector("[data-review]");
  const activities = steps.filter((s) => s.dataset.part === "2");
  const partTwo = form.querySelector(".explore-part");
  const nav = form.querySelector("[data-explore-nav]");
  const prev = nav.querySelector("[data-prev]");
  const next = nav.querySelector("[data-next]");
  const submitArea = form.querySelector("[data-submit-area]");
  const progress = document.querySelector("[data-explore-progress]");
  const partText = progress.querySelector("[data-progress-part]");
  const countText = progress.querySelector("[data-progress-count]");
  const bar = progress.querySelector("[data-progress-bar]");
  const PARTS = 3;
  let current = 0;
  let backToReview = false; // came here from «غيّر» on the review: «التالي» goes straight back
  const STEP_LOCK_MS = 400;  // the second tap of a double tap: too soon to have read the new question
  const AUTO_NEXT_MS = 300;  // a tap on an answer: long enough to see it chosen, short enough not to wait
  let autoNext = 0;          // the pending move, cancelled by any other move
  let tappedAt = 0;          // when an answer was last tapped (a key press resets it)
  let lockedUntil = 0;

  form.classList.add("is-stepped");
  nav.hidden = false;
  progress.hidden = false;
  review.hidden = false;

  function chosenLabels(group) {
    return Array.from(group.querySelectorAll("input:checked"))
      .map((input) => input.closest("label").querySelector("span").textContent.trim());
  }

  function buildReview() {
    const list = review.querySelector("[data-review-list]");
    list.replaceChildren();
    steps.forEach((step, index) => {
      if (step === review) return;
      const groups = step.matches("fieldset") ? [step] : Array.from(step.querySelectorAll("fieldset"));
      for (const group of groups) {
        const label = group.dataset.label;
        const row = document.createElement("div");
        row.className = "summary-row";
        const dt = document.createElement("dt");
        dt.textContent = label;
        const dd = document.createElement("dd");
        const answer = document.createElement("span");
        const chosen = chosenLabels(group);
        answer.textContent = chosen.length ? chosen.join(t("، ")) : t("لم تُجب");
        const change = document.createElement("button");
        change.type = "button";
        change.className = "btn btn--small btn--secondary explore-change";
        change.textContent = t("غيّر");
        change.setAttribute("aria-label", fill("غيّر إجابتك عن: {label}", { label }));
        change.addEventListener("click", () => {
          backToReview = true;
          show(index);
        });
        dd.append(answer, " ", change);
        row.append(dt, dd);
        list.append(row);
      }
    });
  }

  function show(index, moveFocus = true) {
    window.clearTimeout(autoNext);
    current = Math.max(0, Math.min(index, steps.length - 1));
    const step = steps[current];
    steps.forEach((s, i) => { s.hidden = i !== current; });
    const part = step.dataset.part;
    partTwo.hidden = part !== "2";
    if (step === review) {
      buildReview();
      backToReview = false;
      partText.textContent = t("المراجعة الأخيرة");
      countText.textContent = "";
    } else {
      partText.textContent = fill("الجزء {n} من {total}", { n: part, total: PARTS });
      countText.textContent = part === "2"
        ? fill("النشاط {n} من {total}", { n: activities.indexOf(step) + 1, total: activities.length }) : "";
    }
    countText.hidden = !countText.textContent;
    bar.value = current / (steps.length - 1);
    prev.hidden = current === 0;
    next.hidden = step === review;
    updateNext();
    submitArea.hidden = step !== review;
    // Which step this is, in this page's own history entry (a number, never an answer), so Back returns here.
    try { history.replaceState({ ...(history.state || {}), exploreStep: current }, ""); } catch (e) { /* not needed to work */ }
    if (moveFocus) {
      lockedUntil = Date.now() + STEP_LOCK_MS; // only after the student moved: the first press always counts
      const heading = step.querySelector("[tabindex='-1']");
      if (heading) heading.focus({ preventScroll: true });
      // Bring the progress line and the question into view at once (no smooth scroll: the page must not still be
      // moving under the student's finger), and only when they're out of view.
      const top = progress.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight / 2) window.scrollTo({ top: window.scrollY + top - 8, behavior: "instant" });
    }
  }

  // «التالي» once something is chosen, «تخطَّ» while nothing is: the button says what pressing it does.
  function updateNext() {
    const answered = !!steps[current].querySelector("input:checked");
    next.textContent = backToReview ? t("العودة إلى المراجعة") : answered ? t("التالي") : t("تخطَّ");
  }

  function forward() {
    show(backToReview ? steps.indexOf(review) : current + 1);
  }

  // Captured before anything else sees it: the tap neither chooses an answer nor presses a button. Only taps and
  // clicks (event.detail ≥ 1); a key press (detail 0) is always deliberate, so the keyboard is never held up.
  form.addEventListener("click", (event) => {
    if (event.detail > 0 && Date.now() < lockedUntil && event.target.closest(".explore-option, [data-prev], [data-next]")) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);
  prev.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", forward);
  form.addEventListener("change", updateNext);

  // Tap an activity's answer → move on after AUTO_NEXT_MS. A second tap before then (the same answer, or another:
  // the last one wins) restarts the wait, so there is one move. Tapping the answer already chosen (after «السابق»)
  // moves on too. A key press never moves on by itself.
  form.addEventListener("pointerup", (event) => {
    if (event.target.closest(".explore-option")) tappedAt = Date.now();
  });
  form.addEventListener("keydown", () => { tappedAt = 0; });
  form.addEventListener("click", (event) => {
    const step = steps[current];
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || input.type !== "radio" || step.dataset.part !== "2") return;
    if (!step.contains(input) || Date.now() - tappedAt > 1000) return;
    window.clearTimeout(autoNext);
    autoNext = window.setTimeout(() => { if (steps[current] === step) forward(); }, AUTO_NEXT_MS);
  });

  // Enter inside a question goes to the next step; only the review's button shows the result. Enter is a key
  // press, so it's never held up, but a held-down Enter (key repeat) would race through questions: ignored.
  form.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && event.repeat) event.preventDefault();
  });
  form.addEventListener("submit", (event) => {
    if (steps[current] !== review) {
      event.preventDefault();
      forward();
    }
  });

  // A reload starts clean, and Back from the result opens the review with the answers. Browsers put earlier
  // answers back after the page has loaded, just before "pageshow" (measured in Chromium, 2026-11-04), so the
  // choice is made there. A first visit has nothing to restore and is left alone; a page the browser kept in
  // memory comes back exactly as it was.
  const navigation = (performance.getEntriesByType && performance.getEntriesByType("navigation")[0]) || {};
  const answered = () => !!form.querySelector("input:checked");
  const savedStep = (history.state || {}).exploreStep; // read before show() below writes step 0 over it
  show(0, false);
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) return; // kept in memory by the browser: the page, its step and its answers are as left
    const back = navigation.type === "back_forward";
    if (back && answered()) {
      // Back to where the student left off: the question they were on, or the review if they came from the result.
      show(Number.isInteger(savedStep) ? savedStep : steps.indexOf(review), false);
    } else if (back || navigation.type === "reload") {
      form.reset();
      show(0, false);
    }
  });
})();
