// «سؤالك» (redesign v3, 2026-11): the question «أريد دراسة [تخصص] في [دولة]» as a sentence the student edits.
// - Each slot grows with its words, so the sentence reads as a sentence.
// - On the homepage the answer under the question follows every edit (GET /answer, the same answer as the Finder's).
// - A whole question typed into the first slot («علوم الحاسب في بريطانيا») comes back read: the server returns the
//   major and the country it understood, and the slots take them once the student leaves the box (never under their
//   cursor while they type).
// - «خطوتك التالية» opens on the grade this browser keeps («هذا صفّي», mylist.js).
// Without JavaScript the question is a plain form: /universities draws the same answer.
(function () {
  const t = (text) => (window.WADIH_I18N && window.WADIH_I18N[text]) || text;
  const BASE = document.documentElement.dataset.base || "";

  // ---------- slots that fit their words ----------

  function fit(slot) {
    const field = slot.querySelector("input, select");
    const measure = slot.querySelector("[data-ask-measure]") || slot.appendChild(Object.assign(document.createElement("span"), { className: "ask-measure" }));
    let text = field.tagName === "SELECT" ? (field.selectedOptions[0] || {}).text || "" : field.value || field.placeholder || "";
    measure.textContent = text;
    const extra = field.tagName === "SELECT" ? 1.05 : 0.3; // the chevron, the caret
    const em = parseFloat(getComputedStyle(field).fontSize) || 16;
    const max = slot.closest("[data-ask-sentence]").clientWidth;
    field.style.width = Math.min(max, Math.ceil(measure.offsetWidth + extra * em)) + "px";
  }

  function fitAll(root) {
    for (const slot of root.querySelectorAll(".ask-slot")) fit(slot);
  }

  const sentences = [...document.querySelectorAll("[data-ask-sentence]")];
  if (!sentences.length) return;
  for (const s of sentences) {
    fitAll(s);
    s.addEventListener("input", (e) => { const slot = e.target.closest(".ask-slot"); if (slot) fit(slot); });
    s.addEventListener("change", (e) => { const slot = e.target.closest(".ask-slot"); if (slot) fit(slot); });
  }
  // The display face arrives after first paint: measure again once it's here, and on rotation.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => sentences.forEach(fitAll));
  window.addEventListener("resize", () => sentences.forEach(fitAll));

  // ---------- the question read back into its slots ----------

  // The server says what it read (data-parsed-q / data-parsed-country on the answer). Fill the slots with it once the
  // student isn't typing in the first one, so «علوم الحاسب في بريطانيا» becomes [علوم الحاسب] في [بريطانيا].
  function applyParsed(root, form) {
    const meta = root.querySelector("[data-parsed]");
    if (!meta || !form) return false;
    const q = form.elements.q;
    const country = form.elements.country;
    const fill = () => {
      q.value = meta.dataset.parsedQ || "";
      if (country && meta.dataset.parsedCountry !== undefined) country.value = meta.dataset.parsedCountry;
      fitAll(form);
    };
    if (document.activeElement === q) {
      q.addEventListener("blur", fill, { once: true });
    } else {
      fill();
    }
    return true;
  }

  // The Finder (universities.js) announces each new result; read the question back there too.
  const finder = document.querySelector("form[data-explorer]");
  document.addEventListener("wadih:results", (event) => {
    if (finder && applyParsed(event.detail.root, finder)) {
      const params = new URLSearchParams(new FormData(finder));
      for (const [key, value] of [...params]) if (!value) params.delete(key);
      const meta = event.detail.root.querySelector("[data-parsed]");
      params.set("q", meta.dataset.parsedQ || "");
      if (meta.dataset.parsedCountry) params.set("country", meta.dataset.parsedCountry);
      for (const [key, value] of [...params]) if (!value) params.delete(key);
      history.replaceState(null, "", params.toString() ? "?" + params : location.pathname);
    }
    setupNext(event.detail.root);
    stagger(event.detail.root);
  });

  // The Finder's country chips set «في» in the live form instead of reloading the page.
  if (finder) {
    document.addEventListener("click", (event) => {
      const chip = event.target.closest("a[data-set-country]");
      const results = document.getElementById("results");
      if (!chip || !results || !results.contains(chip)) return;
      event.preventDefault();
      finder.elements.country.value = chip.dataset.setCountry;
      fitAll(finder);
      finder.elements.country.dispatchEvent(new Event("change", { bubbles: true }));
      results.focus();
    });
  }

  // ---------- the homepage: the answer follows the question ----------

  const live = document.querySelector("form[data-ask-live]");
  const target = document.querySelector("[data-answer-target]");
  const status = document.querySelector("[data-answer-status]");
  if (live && target) {
    const q = live.elements.q;
    let timer = null;
    let latest = 0;
    let last = new URLSearchParams(new FormData(live)).toString();

    async function update(force) {
      const params = new URLSearchParams(new FormData(live));
      const query = params.toString();
      if (query === last && !force) return;
      last = query;
      const ticket = ++latest;
      target.setAttribute("aria-busy", "true");
      try {
        const response = await fetch(live.dataset.answerUrl + "?" + query);
        if (!response.ok) throw new Error("answer " + response.status);
        const html = await response.text();
        if (ticket !== latest) return;
        target.innerHTML = html;
        applyParsed(target, live);
        // The same event as the Finder's: save and compare buttons in the new answer wake up (mylist.js, compare.js).
        document.dispatchEvent(new CustomEvent("wadih:results", { detail: { root: target } }));
        const head = target.querySelector(".answer-title");
        if (status) status.textContent = head ? head.textContent.replace(/\s+/g, " ").trim() : "";
      } catch (error) {
        if (ticket !== latest) return;
        target.innerHTML = "";
        const box = document.createElement("div");
        box.className = "notice notice--warn";
        box.setAttribute("role", "alert");
        const text = document.createElement("p");
        text.textContent = t("تعذّر تحديث الإجابة. تحقق من اتصالك، ثم حاول مرة أخرى.");
        const retry = document.createElement("button");
        retry.type = "button";
        retry.className = "btn btn--secondary btn--small";
        retry.textContent = t("حاول مرة أخرى");
        retry.addEventListener("click", () => update(true));
        box.append(text, retry);
        target.append(box);
      } finally {
        if (ticket === latest) target.removeAttribute("aria-busy");
      }
    }

    // A major picked from the suggestions fills the slot; a university opens its page.
    if (window.WadihCombobox) {
      const combobox = window.WadihCombobox(q,
        (u) => { location.href = BASE + "/universities/" + encodeURIComponent(u.id); },
        (m) => { q.value = m.name_ar; combobox.close(); fitAll(live); update(); });
    }
    q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(update, 350); });
    live.addEventListener("change", (event) => { if (event.target !== q) update(); });
    live.addEventListener("submit", (event) => {
      // «اعرض الجامعات» opens the full answer in the Finder (the form's own action); Enter in the box just refreshes.
      if (event.submitter) return;
      event.preventDefault();
      update(true);
    });
    // An example under the question fills both slots.
    live.addEventListener("click", (event) => {
      const ex = event.target.closest("a[data-ask-example]");
      if (!ex) return;
      event.preventDefault();
      q.value = ex.dataset.q || "";
      live.elements.country.value = ex.dataset.country || "";
      fitAll(live);
      update();
    });
    // The answer's country chips refill «في» on the homepage too.
    target.addEventListener("click", (event) => {
      const chip = event.target.closest("a[data-set-country]");
      if (!chip) return;
      event.preventDefault();
      live.elements.country.value = chip.dataset.setCountry;
      fitAll(live);
      // Focus moves to the new answer's title, not to «في»: focusing a <select> opens the native picker on iOS,
      // which then covered the answer the student had just asked for.
      update().then(() => {
        const head = target.querySelector(".answer-title");
        if (!head) return;
        head.setAttribute("tabindex", "-1");
        head.focus();
      });
    });
  }

  // ---------- small touches ----------

  // When the answer holds different universities, its cards arrive one after the other (CSS, short; nothing with
  // reduced motion). The same universities redrawn (a keystroke that changes nothing) stay still, so a frequent
  // action stays immediate and the facts don't move while the student reads them.
  let lastCards = null;
  function stagger(root) {
    const host = root.closest(".answer-live") || root.querySelector(".answer-live") || root;
    const cards = [...host.querySelectorAll(".acard")];
    const ids = cards.map((c) => c.dataset.acard).join(",");
    host.classList.remove("is-new");
    if (ids === lastCards) return;
    lastCards = ids;
    cards.forEach((card, i) => card.style.setProperty("--i", Math.min(i, 5)));
    void host.offsetWidth;
    host.classList.add("is-new");
  }

  // «خطوتك التالية» opens on the grade this browser keeps («هذا صفّي»).
  function setupNext(root) {
    let grade = null;
    try { grade = localStorage.getItem("wadih:grade"); } catch (e) { /* storage blocked */ }
    if (!/^grade-1[0-2]$/.test(grade || "")) return;
    for (const input of (root || document).querySelectorAll("input[data-next-grade]")) {
      if (input.value === grade) input.checked = true;
    }
  }
  setupNext(document);
})();
