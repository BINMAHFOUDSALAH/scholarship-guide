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
        if (extra) small.append((english ? "، " : "") + extra);
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
      // The first load can finish after the student left the box; opening then would push the results down.
      if (document.activeElement !== input) return;
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
      // Typing: at most 8 majors in total, so the list stays scannable on a phone (Baymard: 4–8 on
      // mobile). An empty box keeps the full list, which works as "browse by field".
      let room = q ? 8 : Infinity;
      let hidden = 0;
      for (const g of d.fields) {
        const all = q ? g.majors.filter((m) => m.key.includes(q)) : g.majors;
        const majors = all.slice(0, Math.max(room, 0));
        hidden += all.length - majors.length;
        room -= majors.length;
        if (!majors.length) continue;
        panel.append(group("تخصصات مجال: " + g.title_ar, majors.map((m) =>
          option(m.name_ar + (m.masters_only ? " (ماجستير فقط)" : ""), m.name_en, "", () => onMajor(m)))));
      }
      if (hidden) {
        const more = document.createElement("p");
        more.className = "suggest-empty";
        more.textContent = "وتخصصات أخرى (" + hidden + "). اكتب كلمة أدق، أو اضغط «ابحث».";
        panel.append(more);
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

    let quietClear = false;
    input.addEventListener("focus", render);
    input.addEventListener("input", () => {
      if (quietClear) { quietClear = false; return; }
      render();
    });
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
        // First Escape closes the list and keeps the text (ARIA combobox pattern). Without
        // preventDefault, a search box also clears itself, and that "input" reopened all 157 majors.
        // A second Escape lets the browser clear the box, without reopening the list.
        if (!panel.hidden) {
          event.preventDefault();
          close();
        } else if (input.value) {
          quietClear = true; // an empty box fires no "input", so only flag a real clear
        }
      }
    });
    // Closing the list moves what's under it (on the explorer it takes its own space), so it never closes
    // in the middle of a press: the click must reach what the student pressed (decision 058).
    let pressing = false;
    let closeAfterPress = false;
    document.addEventListener("pointerdown", () => { pressing = true; }, true);
    // A press can end without a click (released elsewhere, or a touch that became a scroll): close
    // then, a moment later, after any click from it has been delivered.
    function released() {
      pressing = false;
      if (closeAfterPress) {
        closeAfterPress = false;
        setTimeout(() => { if (document.activeElement !== input) close(); }, 400);
      }
    }
    document.addEventListener("pointerup", released, true);
    document.addEventListener("pointercancel", released, true);
    // A tap anywhere else closes the list, once the tap is done. Needed on iPhones too, where tapping a
    // non-focusable spot (a tag's label, the page background) doesn't blur the input.
    document.addEventListener("click", (event) => {
      if (!panel.hidden && event.target !== input && !panel.contains(event.target)) close();
    });
    input.addEventListener("blur", () => setTimeout(() => {
      if (pressing) closeAfterPress = true; else close();
    }, 150));
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

    // Removing a filter (its ✕, or «مسح الكل»): clear only the fields the link names (data-remove)
    // in the live form, and keep everything else. Never copy the link's href into the form: it was
    // drawn with the previous results, so a second ✕ pressed before the new results arrive would
    // bring back the filter removed a moment earlier (decision 048).
    let removals = 0;
    results.addEventListener("click", (event) => {
      const link = event.target.closest("a[data-applied]");
      if (!link) return;
      event.preventDefault();
      combobox.close();
      // Where the removed tag sat, so focus can land on the one that takes its place. Tags only: landing
      // on «مسح الكل» meant a second Enter would clear every filter.
      const tags = () => [...results.querySelectorAll("a.applied-x")];
      const position = tags().indexOf(link);
      for (const name of (link.dataset.remove || "").split(" ")) {
        if (name === "q") input.value = "";
        else if (form.elements[name]) form.elements[name].value = "";
      }
      syncFields();
      const mine = ++removals;
      update().then(() => {
        // Two ✕ pressed quickly: only the last one moves focus, once its results are in. (Otherwise the
        // first focused a tag in the old results, which were then replaced, and focus fell to the page.)
        if (mine !== removals) return;
        // The tag now in the same place (or the last one); with none left, the results themselves.
        // Never the search box: focusing it opened the suggestions (157 majors) over the results.
        const left = tags();
        ((position >= 0 && left[Math.min(position, left.length - 1)]) || results).focus();
      });
    });

    // «اختر المجال» under إمداد (decision 058): set the field in the live form instead of reloading the page.
    results.addEventListener("click", (event) => {
      const link = event.target.closest("a[data-pick-field]");
      if (!link) return;
      event.preventDefault();
      const params = new URL(link.href).searchParams;
      track.value = params.get("track");
      syncFields();
      field.value = params.get("field");
      update().then(() => results.focus());
    });

    // ---------- the الرواد destination (decision 060) ----------
    // Shown while «المسار» is الرواد. The chart follows the «الدولة» filter: the chosen country's
    // constellation lights up with a path from home. Its chips set that filter in the live form.
    const rowwad = document.querySelector("[data-rowwad]");
    const explorerHeader = document.querySelector("[data-explorer-header]");
    const chart = rowwad && rowwad.querySelector("[data-chart]");
    const readout = rowwad && rowwad.querySelector("[data-chart-readout]");
    const country = form.elements.country;

    function chipFor(code) {
      return rowwad.querySelector('[data-country-chip="' + code + '"]');
    }

    // The line under the chart: the totals, or the chosen country with its count.
    function restReadout() {
      const chip = country.value && chipFor(country.value);
      readout.textContent = chip
        ? chip.querySelector("span").textContent + ": " + chip.querySelector(".country-chip-count").textContent + " في القائمة أدناه"
        : readout.dataset.default;
    }

    function syncRowwad() {
      if (!rowwad) return;
      const on = track.value === "arruaad";
      rowwad.hidden = !on;
      if (explorerHeader) explorerHeader.hidden = on;
      document.body.classList.toggle("page-rowwad", on);
      const code = on && chart.querySelector('.chart-country[data-country="' + country.value + '"]') ? country.value : "";
      if (code) chart.dataset.active = code; else delete chart.dataset.active;
      for (const el of chart.querySelectorAll("[data-country]")) el.classList.toggle("is-active", el.dataset.country === code);
      for (const chip of rowwad.querySelectorAll("[data-country-chip]")) {
        if (chip.dataset.countryChip === code) chip.setAttribute("aria-current", "true");
        else chip.removeAttribute("aria-current");
      }
      restReadout();
    }

    if (rowwad) {
      rowwad.addEventListener("click", (event) => {
        const chip = event.target.closest("a[data-country-chip]");
        if (!chip) return;
        event.preventDefault();
        // The chosen chip again clears the country; any other chip replaces it. Only «الدولة» changes.
        const code = chip.dataset.countryChip;
        track.value = "arruaad";
        country.value = country.value === code ? "" : code;
        syncFields();
        syncRowwad();
        update();
      });
      // Pointing at a star names it under the chart (the chart's links are for a mouse; the table has them all).
      chart.addEventListener("pointerover", (event) => {
        const star = event.target.closest(".chart-star");
        if (star) readout.textContent = star.dataset.rank + ". " + star.dataset.name;
      });
      chart.addEventListener("pointerout", (event) => {
        if (event.target.closest(".chart-star")) restReadout();
      });
      form.addEventListener("change", syncRowwad);
      results.addEventListener("click", (event) => {
        if (event.target.closest("a[data-applied]")) setTimeout(syncRowwad); // after the ✕ clears its fields
      });
    }

    syncFields();
    countFilters();
    layout();
    lastQuery = formQuery(form);
    syncRowwad();
  }

  // ---------- 3. back to results ----------

  // Coming back to the list puts the student where they were (owner, 2026-10-12). Phone browsers often
  // reload the page on Back, and the filter panel folding on load shifts it, so the browser's own scroll
  // restore lands in the wrong place or at the top. We remember which university was opened and bring
  // that row back into view. sessionStorage: this tab only, cleared when it closes; ids only.
  const RETURN_KEY = "wadih:return";
  const store = {
    get() { try { return JSON.parse(sessionStorage.getItem(RETURN_KEY) || "null"); } catch (e) { return null; } },
    set(v) { try { sessionStorage.setItem(RETURN_KEY, JSON.stringify(v)); } catch (e) { /* storage blocked: browser default */ } },
    clear() { try { sessionStorage.removeItem(RETURN_KEY); } catch (e) { /* ignore */ } },
  };
  if (results) {
    // We restore the place ourselves, so the browser's own restore can't jump to the top after us.
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";

    results.addEventListener("click", (event) => {
      const link = event.target.closest('a[href*="/universities/"]');
      const match = link && new URL(link.href).pathname.match(/^\/universities\/([a-z0-9-]+)$/);
      if (match) {
        // Where the tapped university sat on the screen, so it can come back to exactly the same spot.
        store.set({ list: location.pathname + location.search, id: match[1], y: window.scrollY,
                    top: link.getBoundingClientRect().top, at: Date.now() });
      }
    });

    // Puts the university back where it was on the screen. Moves only when it's off by more than a few
    // pixels, so calling it again (or when the browser already restored the place) causes no jump.
    function bringBack(saved) {
      const row = [...results.querySelectorAll('a[href*="/universities/"]')]
        .find((a) => new URL(a.href).pathname === "/universities/" + saved.id);
      if (!row) {
        if (Math.abs(window.scrollY - saved.y) > 4) window.scrollTo(0, saved.y);
        return;
      }
      const off = row.getBoundingClientRect().top - (typeof saved.top === "number" ? saved.top : window.innerHeight / 3);
      if (Math.abs(off) > 4) window.scrollTo(0, window.scrollY + off);
    }

    // Returns true when this visit is a return to the list the student left.
    function tryReturn(isBack) {
      const saved = store.get();
      const fresh = saved && Date.now() - saved.at < 30 * 60 * 1000;
      if (!fresh || saved.list !== location.pathname + location.search || !(isBack || saved.returning)) return false;
      store.clear();
      // Once now, and once more after the fonts are ready (they can change row heights), but only if the
      // row is actually off and the student hasn't touched the page yet. No repeated re-centering.
      let moved = false;
      for (const type of ["touchstart", "wheel", "keydown", "mousedown"]) {
        window.addEventListener(type, () => { moved = true; }, { once: true, passive: true });
      }
      bringBack(saved);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (!moved) bringBack(saved); });
      return true;
    }

    const nav = (performance.getEntriesByType("navigation")[0] || {}).type;
    if (!tryReturn(nav === "back_forward") && nav !== "back_forward") store.clear();
    // Instant Back (the browser's back-forward cache) shows the page as it was without running this
    // script again; pageshow still fires, with persisted = true.
    window.addEventListener("pageshow", (event) => { if (event.persisted) tryReturn(true); });
  }

  const back = document.querySelector("a[data-back-link]");
  if (back) {
    // Our «الرجوع إلى نتائج البحث» link: mark the return, so the list restores the place even when the
    // link opens the list fresh (no referrer, or a new tab's first page).
    back.addEventListener("click", () => {
      const saved = store.get();
      if (saved) store.set({ ...saved, returning: true });
    });
  }
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
