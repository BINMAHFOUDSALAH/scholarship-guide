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

  if (!write(read())) return; // storage blocked: no picks, the toggles stay hidden

  const say = (text) => {
    const status = document.querySelector("[data-save-status]");
    if (status) status.textContent = text;
  };

  // The comparison page sets the picks to what it shows (a link someone sent, a column removed).
  const page = document.querySelector("[data-compare-page]");
  if (page) write((page.dataset.compareIds || "").split(",").filter((id) => ID.test(id)));

  function render(root) {
    const ids = read();
    for (const button of (root || document).querySelectorAll("button[data-compare]")) {
      const on = ids.includes(button.dataset.compare);
      button.setAttribute("aria-pressed", String(on));
      button.querySelector("[data-compare-label]").textContent = t(on ? "في المقارنة" : "قارن");
      button.hidden = false;
    }
    renderTray(ids);
  }

  let tray = null;
  function renderTray(ids) {
    if (page) return; // the page is the comparison
    if (!ids.length) {
      if (tray) tray.hidden = true;
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

  document.addEventListener("wadih:results", (event) => render(event.detail.root));
  window.addEventListener("storage", (event) => { if (event.key === KEY) render(); });
  // Back to a page kept in memory: its buttons show the picks of now.
  window.addEventListener("pageshow", (event) => { if (event.persisted) render(); });
  render();
})();
