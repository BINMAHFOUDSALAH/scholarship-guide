// «جرّب قبل أن تقرر» (decision 069): turns the one long form into steps, one question per screen.
// - Part 1 (what makes the decision hard, the grade), part 2 (one activity per screen), part 3 (progress in
//   subjects, a field the student or their family has in mind), then a review where any answer can be changed.
// - Choosing an answer only selects it: the student moves on with «التالي» (or «تخطَّ» while nothing is chosen).
//   It used to move on by itself after a tap, and a second tap then answered the next question for the student
//   (owner's iPhone, 2026-11-04). A survey must never record an answer nobody chose.
// - For a moment after the question changes, taps on the questions and buttons are ignored (never key presses):
//   a quick second tap would otherwise land on one of the new question's answers, or move two steps.
// - Each visit starts clean (a reload never brings old answers back); coming back from the result with the
//   browser's Back opens the review with the answers, to change them.
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

  // Enter inside a question goes to the next step; only the review's button shows the result.
  form.addEventListener("submit", (event) => {
    if (steps[current] !== review) {
      event.preventDefault();
      if (Date.now() >= lockedUntil) forward();
    }
  });

  // A reload starts clean, and Back from the result opens the review with the answers. Browsers put earlier
  // answers back after the page has loaded, just before "pageshow" (measured in Chromium, 2026-11-04), so the
  // choice is made there. A first visit has nothing to restore and is left alone.
  const navigation = (performance.getEntriesByType && performance.getEntriesByType("navigation")[0]) || {};
  const answered = () => !!form.querySelector("input:checked");
  show(0, false);
  window.addEventListener("pageshow", (event) => {
    const back = event.persisted || navigation.type === "back_forward";
    if (back && answered()) {
      show(steps.indexOf(review), false);
    } else if (back || navigation.type === "reload") {
      form.reset();
      show(0, false);
    }
  });
})();
