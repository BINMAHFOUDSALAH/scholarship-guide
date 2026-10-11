// The universities search (decision 035). Everything here is an enhancement: without JavaScript
// the form submits normally and the server renders the same results.
//
// 1. Suggestions for any search box with data-suggest (the explorer and the homepage):
//    universities first, then majors grouped by their field. Choosing a university opens its page
//    (a confirmed choice); choosing a major searches for it.
// 2. On the explorer: live results as you type or change a filter, removable filter tags,
//    filters folded behind «الفلاتر» on phones, a status line for screen readers, an error state.
// 3. On a university page: «الرجوع إلى نتائج البحث» goes back in history when the results page is
//    the previous page, so the list comes back where you left it.
(function () {
  if (!window.fetch) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // The same forgiving match as the server: case, accents, and Arabic letter variants.
  // Removed marks: Latin accents (U+0300–036F), Arabic short vowels (U+064B–0652), tatweel (U+0640).
  // Written as \u escapes: the marks are invisible, and a typo here once removed every Arabic letter.
  function normalize(text) {
    return (text || "")
      .replace(/[أإآ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي")
      .normalize("NFKD").replace(/[\u0300-\u036f\u064b-\u0652\u0640]/g, "")
      .toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  }

  // ---------- 1. suggestions (an ARIA combobox) ----------

  let data = null;
  async function loadSuggestions(url) {
    if (data) return data;
    const response = await fetch(url);
    if (!response.ok) throw new Error("suggestions " + response.status);
    data = await response.json();
    for (const g of data.fields) for (const m of g.majors) m.key = normalize(m.name_ar + " " + m.name_en);
    for (const u of data.universities) u.key = normalize((u.name_ar || "") + " " + u.name_en);
    return data;
  }

  function setupCombobox(input, onUniversity, onMajor) {
    const panel = document.getElementById(input.getAttribute("aria-controls"));
    if (!panel) return { close() {} };
    let options = [];
    let active = -1;
    let groupCount = 0;

    // One suggestion: the Arabic name, then a quiet line with the English name (left to right)
    // and, for universities, the country.
    function option(text, english, extra, choose) {
      const el = document.createElement("div");
      el.className = "suggest-option";
      el.setAttribute("role", "option");
      el.setAttribute("aria-selected", "false");
      el.id = input.id + "-opt-" + options.length;
      const main = document.createElement("span");
      main.textContent = text;
      el.append(main);
      if (english || extra) {
        const small = document.createElement("small");
        if (english) {
          const en = document.createElement("span");
          en.lang = "en";
          en.dir = "ltr";
          en.textContent = english;
          small.append(en);
        }
        if (extra) small.append((english ? " · " : "") + extra);
        el.append(small);
      }
      el.addEventListener("mousedown", (event) => event.preventDefault()); // keep focus in the input
      el.addEventListener("click", () => choose());
      el.choose = choose;
      options.push(el);
      return el;
    }

    function group(title, items) {
      const wrap = document.createElement("div");
      wrap.setAttribute("role", "group");
      const heading = document.createElement("p");
      heading.className = "suggest-group";
      heading.id = input.id + "-group-" + groupCount++;
      heading.setAttribute("role", "presentation");
      heading.textContent = title;
      wrap.setAttribute("aria-labelledby", heading.id);
      wrap.append(heading, ...items);
      return wrap;
    }

    async function render() {
      let d;
      try {
        d = await loadSuggestions(input.dataset.suggest);
      } catch (e) {
        return; // no suggestions; the search itself still works
      }
      const q = normalize(input.value);
      panel.replaceChildren();
      options = [];
      active = -1;
      groupCount = 0;

      if (q) {
        const unis = d.universities.filter((u) => u.key.includes(q)).slice(0, 6);
        if (unis.length) {
          panel.append(group("جامعات: تفتح صفحة الجامعة", unis.map((u) =>
            option(u.name_ar || u.name_en, u.name_ar ? u.name_en : "", u.country_ar, () => onUniversity(u)))));
        }
      }
      for (const g of d.fields) {
        const majors = q ? g.majors.filter((m) => m.key.includes(q)) : g.majors;
        if (!majors.length) continue;
        panel.append(group("تخصصات مجال: " + g.title_ar, majors.map((m) =>
          option(m.name_ar + (m.masters_only ? " (ماجستير فقط)" : ""), m.name_en, "", () => onMajor(m)))));
      }
      if (!options.length) {
        const empty = document.createElement("p");
        empty.className = "suggest-empty";
        empty.textContent = "لا اقتراحات. اضغط «ابحث» للبحث بالنص كما كتبته.";
        panel.append(empty);
      }
      open();
    }

    function open() {
      panel.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }

    function close() {
      panel.hidden = true;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      active = -1;
    }

    function highlight(index) {
      if (!options.length) return;
      if (active >= 0) options[active].setAttribute("aria-selected", "false");
      active = (index + options.length) % options.length;
      const el = options[active];
      el.setAttribute("aria-selected", "true");
      input.setAttribute("aria-activedescendant", el.id);
      el.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
    }

    input.addEventListener("focus", render);
    input.addEventListener("input", render);
    input.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (panel.hidden) render(); else highlight(active + 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        highlight(active - 1);
      } else if (event.key === "Enter" && !panel.hidden && active >= 0) {
        event.preventDefault();
        options[active].choose();
      } else if (event.key === "Escape") {
        close();
      }
    });
    input.addEventListener("blur", () => setTimeout(close, 150));
    return { close };
  }

  function universityUrl(u, from) {
    return "/universities/" + encodeURIComponent(u.id) + (from === null ? "" : "?from=" + encodeURIComponent(from));
  }

  // The current search as a query string (only non-empty fields).
  function formQuery(form) {
    const params = new URLSearchParams(new FormData(form));
    for (const [key, value] of [...params]) if (!value) params.delete(key);
    return params.toString();
  }

  // Search boxes outside the explorer (the homepage): a major runs the search, a university opens.
  for (const input of document.querySelectorAll("input[data-suggest]")) {
    const form = input.form;
    if (!form || form.hasAttribute("data-explorer")) continue;
    setupCombobox(input,
      (u) => { location.href = universityUrl(u, null); },
      (m) => { input.value = m.name_ar; form.submit(); });
  }

  // ---------- 2. the explorer ----------

  const form = document.querySelector("form[data-explorer]");
  const results = document.getElementById("results");
  if (form && results) {
    const input = form.elements.q;
    const track = form.elements.track;
    const field = form.elements.field;
    const status = document.querySelector("[data-results-status]");
    const toggle = form.querySelector("[data-filters-toggle]");
    const panel = document.getElementById("filters-panel");
    const filterCount = form.querySelector("[data-filters-count]");
    const filterNames = ["track", "field", "country", "lang"];
    const fieldHint = document.getElementById("field-hint");

    // The field list only applies to إمداد and البحث والتطوير: show that track's fields only.
    // The select stays visible with a hint saying why it's unavailable (never hidden silently).
    function syncFields() {
      const t = track.value;
      const usable = t === "emdad" || t === "rnd";
      field.disabled = !usable;
      for (const group of field.querySelectorAll("optgroup")) {
        group.hidden = group.dataset.track !== t;
        for (const option of group.querySelectorAll("option")) option.disabled = group.hidden;
      }
      const selected = field.selectedOptions[0];
      if (!usable || (selected && selected.disabled)) field.value = "";
      if (fieldHint) fieldHint.hidden = usable; // the hint says why the list is unavailable
    }

    function countFilters() {
      const n = filterNames.filter((name) => form.elements[name].value).length;
      filterCount.textContent = n ? "(" + n + ")" : "";
    }

    // Phones: filters fold behind a button, results come first. Wider screens: always open.
    const narrow = window.matchMedia("(max-width: 759px)");
    function setOpen(open) {
      toggle.setAttribute("aria-expanded", String(open));
      panel.hidden = !open;
    }
    function layout() {
      if (narrow.matches) {
        toggle.hidden = false;
        setOpen(toggle.getAttribute("aria-expanded") === "true");
      } else {
        toggle.hidden = true;
        panel.hidden = false;
      }
    }
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    narrow.addEventListener("change", layout);

    let timer = null;
    let latest = 0;
    let lastQuery = null;

    function showError() {
      const box = document.createElement("div");
      box.className = "notice notice--warn results-error";
      box.setAttribute("role", "alert");
      const text = document.createElement("p");
      text.textContent = "تعذّر تحديث النتائج. تحقق من اتصالك بالإنترنت، ثم حاول مرة أخرى.";
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "btn btn--secondary";
      retry.textContent = "حاول مرة أخرى";
      retry.addEventListener("click", () => { lastQuery = null; update(); });
      box.append(text, retry);
      results.replaceChildren(box);
    }

    async function update() {
      countFilters();
      const query = formQuery(form);
      if (query === lastQuery) return;
      lastQuery = query;
      // Keep the address in sync, so Back, reload, and sharing show the same results.
      history.replaceState(null, "", query ? "?" + query : location.pathname);
      const ticket = ++latest;
      results.setAttribute("aria-busy", "true");
      try {
        const response = await fetch(form.action + "?" + (query ? query + "&" : "") + "partial=1");
        if (!response.ok) throw new Error("results " + response.status);
        const html = await response.text();
        if (ticket !== latest) return; // a newer search already started
        results.innerHTML = html;
        const meta = results.querySelector("[data-summary]");
        if (status && meta) status.textContent = meta.dataset.summary;
        document.dispatchEvent(new CustomEvent("wadih:results", { detail: { root: results } }));
      } catch (error) {
        if (ticket === latest) showError();
      } finally {
        if (ticket === latest) results.removeAttribute("aria-busy");
      }
    }

    function later() {
      clearTimeout(timer);
      timer = setTimeout(update, 250);
    }

    const combobox = setupCombobox(input,
      (u) => { location.href = universityUrl(u, formQuery(form)); },
      (m) => { input.value = m.name_ar; combobox.close(); update(); });

    input.addEventListener("input", later);
    form.addEventListener("change", (event) => {
      if (event.target === track) syncFields();
      if (event.target !== input) update();
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      combobox.close();
      lastQuery = null; // pressing «ابحث» always refreshes
      update();
    });

    // Removing a filter tag (or «مسح الكل»): apply the link's search to the form, then update.
    results.addEventListener("click", (event) => {
      const link = event.target.closest("a[data-applied]");
      if (!link) return;
      event.preventDefault();
      const params = new URL(link.href).searchParams;
      input.value = params.get("q") || "";
      for (const name of filterNames) form.elements[name].value = params.get(name) || "";
      syncFields();
      if (params.get("field")) field.value = params.get("field");
      update().then(() => {
        const next = results.querySelector("a[data-applied]");
        (next || input).focus();
      });
    });

    syncFields();
    countFilters();
    layout();
    lastQuery = formQuery(form);
  }

  // ---------- 3. back to results ----------

  const back = document.querySelector("a[data-back-link]");
  if (back && document.referrer && history.length > 1) {
    let from = null;
    try { from = new URL(document.referrer); } catch (e) { from = null; }
    if (from && from.origin === location.origin && from.pathname === "/universities") {
      back.addEventListener("click", (event) => {
        event.preventDefault();
        history.back(); // the browser restores the list and the scroll position
      });
    }
  }
})();
