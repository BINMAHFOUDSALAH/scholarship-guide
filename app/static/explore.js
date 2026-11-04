// «جرّب قبل أن تقرر» (decision 069): turns the one long form into steps, one question per screen.
// - Part 1 (what makes the decision hard, the grade), part 2 (one activity per screen), part 3 (progress in
//   subjects, a field the student or their family has in mind), then a review where any answer can be changed.
// - Choosing an answer with a tap or click moves to the next activity; with the keyboard it doesn't (arrow keys
//   change a radio's choice, so moving on is left to «التالي»).
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
  const autoHint = form.querySelector("[data-auto-hint]");
  const progress = document.querySelector("[data-explore-progress]");
  const partText = progress.querySelector("[data-progress-part]");
  const countText = progress.querySelector("[data-progress-count]");
  const bar = progress.querySelector("[data-progress-bar]");
  const PARTS = 3;
  let current = 0;
  let backToReview = false; // came here from «غيّر» on the review: «التالي» goes straight back

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
    next.textContent = backToReview ? t("العودة إلى المراجعة") : t("التالي");
    submitArea.hidden = step !== review;
    autoHint.hidden = part !== "2";
    if (moveFocus) {
      const heading = step.querySelector("[tabindex='-1']");
      if (heading) heading.focus();
    }
  }

  function forward() {
    show(backToReview ? steps.indexOf(review) : current + 1);
  }

  prev.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", forward);

  // A tap or click on an answer moves on; a keyboard choice doesn't (see the top of the file).
  let pointerAt = 0;
  // Only a tap on an answer counts: a tap on «التالي» followed by arrow keys must not skip ahead.
  form.addEventListener("pointerdown", (event) => {
    pointerAt = event.target.closest(".explore-option") ? Date.now() : 0;
  });
  form.addEventListener("keydown", () => { pointerAt = 0; });
  form.addEventListener("change", (event) => {
    const step = steps[current];
    const byPointer = Date.now() - pointerAt < 1000;
    if (event.target.type === "radio" && step.hasAttribute("data-auto") && step.contains(event.target) && byPointer) {
      window.setTimeout(() => { if (steps[current] === step) forward(); }, 250);
    }
  });

  // Enter inside a question goes to the next step; only the review's button shows the result.
  form.addEventListener("submit", (event) => {
    if (steps[current] !== review) {
      event.preventDefault();
      forward();
    }
  });

  show(0, false);
})();
