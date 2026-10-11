// Universities explorer: update the results as the student types or changes a filter, and show
// our own suggestions panel (majors grouped by field, then universities).
// Without this script the form still works: pressing "ابحث" reloads the page with the results.
(function () {
  const form = document.querySelector("[data-explorer]");
  const results = document.getElementById("results");
  if (!form || !results || !window.fetch) return;

  const track = form.elements.track;
  const field = form.elements.field;
  const input = form.elements.q;
  const panel = document.getElementById("q-suggest");

  // ---------- filters ----------

  // The field list only makes sense for إمداد and البحث والتطوير; show that track's fields only.
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
  }

  let timer = null;
  let latest = 0;
  async function update() {
    const params = new URLSearchParams(new FormData(form));
    for (const [key, value] of [...params]) if (!value) params.delete(key);
    const query = params.toString();
    history.replaceState(null, "", query ? "?" + query : location.pathname);
    params.set("partial", "1");
    const ticket = ++latest;
    results.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(form.action + "?" + params.toString());
      if (ticket !== latest) return; // a newer search already started
      results.innerHTML = await response.text();
    } finally {
      if (ticket === latest) results.removeAttribute("aria-busy");
    }
  }

  function later() {
    clearTimeout(timer);
    timer = setTimeout(update, 250);
  }

  // ---------- suggestions ----------

  // The same forgiving match as the server: case, accents, and Arabic letter variants.
  function normalize(text) {
    return (text || "")
      .replace(/[أإآ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي")
      .normalize("NFKD").replace(/[̀-ًͯ-ْـ]/g, "")
      .toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  }

  let data = null;
  async function loadSuggestions() {
    if (data) return data;
    const response = await fetch(input.dataset.suggest);
    data = await response.json();
    for (const g of data.fields) for (const m of g.majors) m.key = normalize(m.name_ar + " " + m.name_en);
    for (const u of data.universities) u.key = normalize((u.name_ar || "") + " " + u.name_en);
    return data;
  }

  let options = [];
  let active = -1;

  function option(text, hint, value) {
    const el = document.createElement("div");
    el.className = "suggest-option";
    el.setAttribute("role", "option");
    el.id = "q-opt-" + options.length;
    el.dataset.value = value;
    el.append(text);
    if (hint) {
      const small = document.createElement("small");
      small.lang = "en";
      small.dir = "ltr";
      small.textContent = hint;
      el.append(small);
    }
    el.addEventListener("mousedown", (event) => {
      event.preventDefault(); // keep focus in the input
      choose(el);
    });
    options.push(el);
    return el;
  }

  function heading(text) {
    const el = document.createElement("p");
    el.className = "suggest-group";
    el.setAttribute("role", "presentation");
    el.textContent = text;
    return el;
  }

  async function render() {
    const d = await loadSuggestions();
    const q = normalize(input.value);
    panel.replaceChildren();
    options = [];
    active = -1;

    if (q) {
      const unis = d.universities.filter((u) => u.key.includes(q)).slice(0, 6);
      if (unis.length) {
        panel.append(heading("الجامعات"));
        for (const u of unis) panel.append(option(u.name_ar || u.name_en, u.name_ar ? u.name_en : "", u.name_ar || u.name_en));
      }
    }
    for (const g of d.fields) {
      const majors = q ? g.majors.filter((m) => m.key.includes(q)) : g.majors;
      if (!majors.length) continue;
      panel.append(heading("تخصصات مجال: " + g.title_ar));
      for (const m of majors) panel.append(option(m.name_ar + (m.masters_only ? " (ماجستير فقط)" : ""), m.name_en, m.name_ar));
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
    el.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function choose(el) {
    input.value = el.dataset.value;
    close();
    update();
  }

  input.addEventListener("focus", render);
  input.addEventListener("input", () => {
    render();
    later();
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
      choose(options[active]);
    } else if (event.key === "Escape") {
      close();
    }
  });
  input.addEventListener("blur", () => setTimeout(close, 120));

  // ---------- form ----------

  form.addEventListener("change", (event) => {
    if (event.target === track) syncFields();
    if (event.target !== input) update();
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    close();
    update();
  });

  syncFields();
})();
