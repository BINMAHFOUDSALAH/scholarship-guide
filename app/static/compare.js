// «قارن» (redesign v3, 2026-11): the student's picks for the comparison, kept in this browser
// (localStorage["wadih:compare"], at most four university ids, nothing else), a «قارن» toggle on each card, and a
// tray at the bottom that opens /compare?u=a,b,c. The comparison page itself is drawn from its address, so it can be
// sent to someone; opening one makes its universities the picks. Without JavaScript the toggles stay hidden.
(function () {
  const t = (text) => (window.WADIH_I18N && window.WADIH_I18N[text]) || text;
  const KEY = "wadih:compare";
  const MAX = 4;
  const ID = /^[a-z0-9-]{1,80}$/;
  const BASE = document.documentElement.dataset.base || "";

  function read() {
    try {
      const ids = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(ids) ? ids.filter((id) => typeof id === "string" && ID.test(id)).slice(0, MAX) : [];
    } catch (e) {
      return [];
    }
  }

  function write(ids) {
    try {
      localStorage.setItem(KEY, JSON.stringify(ids.slice(0, MAX)));
      return true;
    } catch (e) {
      return false;
    }
  }

  // The names bar works even where the browser keeps nothing.
  const comparePage = document.querySelector("[data-compare-page]");
  if (comparePage) {
    stickyNames(comparePage);
    logoFallback(comparePage);
  }

  // A logo file that fails to load shows the university's initials instead, in the same tile, so the names below
  // stay level with their neighbours'.
  function logoFallback(root) {
    for (const img of root.querySelectorAll("[data-compare-logo] img")) {
      const miss = () => img.closest("[data-compare-logo]").classList.add("is-missing");
      if (img.complete && img.naturalWidth === 0) miss();
      else img.addEventListener("error", miss, { once: true });
    }
  }

  if (!write(read())) return; // storage blocked: no picks, the toggles stay hidden

  const say = (text) => {
    const status = document.querySelector("[data-save-status]");
    if (status) status.textContent = text;
  };

  // The comparison page sets the picks to what it shows (a link someone sent, a column removed).
  const page = document.querySelector("[data-compare-page]");
  if (page) write((page.dataset.compareIds || "").split(",").filter((id) => ID.test(id)));

  // Several screens down a phone, the student still sees whose column is whose: once the table's own header has
  // scrolled away, a thin bar with the names stays at the top, its columns over the table's (and following it when
  // the table scrolls sideways with three or four universities). Hidden from screen readers: the table's headers
  // already name every value.
  function stickyNames(root) {
    const bar = root.querySelector("[data-compare-stick]");
    const row = root.querySelector("[data-compare-stick-row]");
    const head = root.querySelector("[data-compare-head]");
    const scroller = root.querySelector("[data-compare-scroll]");
    const table = scroller && scroller.querySelector("table");
    if (!bar || !row || !head || !table) return;
    let frame = 0;
    function place() {
      frame = 0;
      const headBox = head.getBoundingClientRect();
      const tableBox = table.getBoundingClientRect();
      // Shown between the header leaving the screen and the table's last rows.
      const show = headBox.bottom < 0 && tableBox.bottom > 80;
      bar.hidden = !show;
      if (!show) return;
      // Measured from where the row sits untransformed, so it lines up in RTL and LTR alike.
      row.style.width = tableBox.width + "px";
      row.style.transform = "none";
      const rowBox = row.getBoundingClientRect();
      row.style.transform = "translateX(" + (tableBox.left - rowBox.left) + "px)";
    }
    const later = () => { if (!frame) frame = requestAnimationFrame(place); };
    window.addEventListener("scroll", later, { passive: true });
    window.addEventListener("resize", later);
    scroller.addEventListener("scroll", later, { passive: true });
    // «الفروق فقط» changes the table's height.
    root.addEventListener("change", later);
    place();
  }

  function render(root) {
    const ids = read();
    for (const button of (root || document).querySelectorAll("button[data-compare]")) {
      const on = ids.includes(button.dataset.compare);
      button.setAttribute("aria-pressed", String(on));
      button.querySelector("[data-compare-label]").textContent = t(on ? "في المقارنة" : "قارن");
      button.hidden = false;
    }
    renderTray(ids);
    renderEntries(ids);
  }

  let tray = null;
  function renderTray(ids) {
    if (page) return; // the page is the comparison
    if (!ids.length) {
      if (tray) tray.hidden = true;
      clearance(0);
      return;
    }
    if (!tray) {
      tray = document.createElement("div");
      tray.className = "compare-tray";
      tray.setAttribute("role", "region");
      tray.setAttribute("aria-label", t("المقارنة"));
      tray.innerHTML = '<p class="compare-tray-text" data-tray-text></p><div class="compare-tray-actions">' +
        '<button class="btn btn--small btn--quiet" type="button" data-tray-clear></button>' +
        '<a class="btn btn--small" data-tray-open></a></div>';
      tray.querySelector("[data-tray-clear]").textContent = t("مسح");
      tray.querySelector("[data-tray-clear]").addEventListener("click", () => {
        write([]);
        render();
        say(t("أُفرغت المقارنة."));
      });
      document.body.append(tray);
    }
    tray.hidden = false;
    const n = ids.length;
    tray.querySelector("[data-tray-text]").textContent =
      n === 1 ? t("جامعة واحدة في المقارنة. اختر أخرى.") : n === 2 ? t("جامعتان في المقارنة") : t("{n} جامعات في المقارنة").replace("{n}", n);
    const open = tray.querySelector("[data-tray-open]");
    open.textContent = t("قارن الآن");
    open.href = BASE + "/compare?u=" + ids.join(",");
    open.hidden = n < 2;
    clearance(tray.offsetHeight + 24);
  }

  // The tray is fixed at the bottom: keep the page's last controls clear of it, and make a control focused by Tab
  // scroll above it, never under it.
  function clearance(px) {
    document.documentElement.style.scrollPaddingBottom = px ? px + "px" : "";
    document.body.style.paddingBottom = px ? px + "px" : "";
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-compare]");
    if (!button) return;
    const id = button.dataset.compare;
    const ids = read();
    const name = button.dataset.compareName || "";
    if (ids.includes(id)) {
      write(ids.filter((x) => x !== id));
      say(t("أُزيلت {name} من المقارنة.").replace("{name}", name));
    } else if (ids.length >= MAX) {
      say(t("يمكنك مقارنة أربع جامعات على الأكثر. أزل واحدة أولًا."));
      return;
    } else {
      write([...ids, id]);
      say(t("أُضيفت {name} إلى المقارنة.").replace("{name}", name));
    }
    render();
  });

  // «قارن الجامعات» beside the homepage's question: it reopens the comparison the student already has, or opens the
  // page where they choose universities.
  function renderEntries(ids) {
    for (const link of document.querySelectorAll("a[data-compare-entry]")) {
      link.href = BASE + "/compare" + (ids.length ? "?u=" + ids.join(",") : "");
    }
  }

  // The comparison page's picker: a university chosen from the suggestions joins the comparison; a major opens its
  // universities in the Finder, where each has «قارن». universities.js provides the suggestions (loaded after us).
  function setupPicker() {
    const input = document.querySelector("input[data-compare-pick]");
    if (!input || !window.WadihCombobox) return;
    const combobox = window.WadihCombobox(input,
      (u) => {
        const ids = read();
        if (!ids.includes(u.id)) {
          if (ids.length >= MAX) {
            combobox.close();
            say(t("يمكنك مقارنة أربع جامعات على الأكثر. أزل واحدة أولًا."));
            return;
          }
          ids.push(u.id);
        }
        write(ids);
        location.href = BASE + "/compare?u=" + ids.join(",");
      },
      (m) => { location.href = BASE + "/universities?q=" + encodeURIComponent(m.name_ar); },
      { universitiesTitle: t("جامعات: تُضاف إلى المقارنة") });
  }
  // Deferred scripts run in order before DOMContentLoaded, so universities.js has run by then.
  if (window.WadihCombobox || document.readyState === "complete") setupPicker();
  else document.addEventListener("DOMContentLoaded", setupPicker);

  document.addEventListener("wadih:results", (event) => render(event.detail.root));
  window.addEventListener("storage", (event) => { if (event.key === KEY) render(); });
  // Back to a page kept in memory: its buttons show the picks of now.
  window.addEventListener("pageshow", (event) => { if (event.persisted) render(); });
  render();
})();
