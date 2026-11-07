// «خطتي» (decision 078, Part B; was «قائمتي», decision 035): universities and program tracks the student
// plans for, kept in this browser only, in localStorage under "wadih:plan":
//   {"v": 1, "items": [{"type": "university", "id": "stanford-university", "status": "thinking", "updated": "2026-11-06"}]}
// Ids, statuses and dates only, newest first. Nothing is sent to us except when the «خطتي» page asks the
// server to draw the rows (the plan itself, never stored). Saves from the old «قائمتي» ("wadih:saved") move
// in once. Without JavaScript, or with storage blocked, the save buttons stay hidden and the page says why.
(function () {
  const t = (text) => (window.WADIH_I18N && window.WADIH_I18N[text]) || text; // English pages (decision 066)
  const KEY = "wadih:plan";
  const OLD_KEY = "wadih:saved";
  const MAX = 100;
  const STATUSES = ["thinking", "preparing", "applied", "accepted", "not_accepted"];
  const ID = /^[a-z0-9-]{1,80}$/;

  // Today in Riyadh (UTC+3), like the server's clock (app/clock.py).
  function today() {
    return new Date(Date.now() + 3 * 3600 * 1000).toISOString().slice(0, 10);
  }

  const keyOf = (item) => item.type + ":" + item.id;

  function valid(item) {
    return item && (item.type === "university" || item.type === "program") && ID.test(item.id || "");
  }

  function read() {
    try {
      const plan = JSON.parse(localStorage.getItem(KEY) || "null");
      const items = plan && Array.isArray(plan.items) ? plan.items : [];
      return items.filter(valid).map((i) => ({
        type: i.type, id: i.id,
        status: STATUSES.includes(i.status) ? i.status : "thinking",
        updated: /^\d{4}-\d{2}-\d{2}$/.test(i.updated || "") ? i.updated : null,
      }));
    } catch (e) {
      return [];
    }
  }

  function write(items) {
    try {
      localStorage.setItem(KEY, JSON.stringify({ v: 1, items: items.slice(0, MAX) }));
      return true;
    } catch (e) {
      return false; // storage full or blocked: the change isn't kept
    }
  }

  function storageWorks() {
    try {
      localStorage.setItem("wadih:test", "1");
      localStorage.removeItem("wadih:test");
      return true;
    } catch (e) {
      return false;
    }
  }

  // The old «قائمتي» (a list of university ids) moves into the plan once, then the old key goes.
  function migrate() {
    try {
      const old = JSON.parse(localStorage.getItem(OLD_KEY) || "null");
      if (!Array.isArray(old)) return;
      const items = read();
      const have = new Set(items.map(keyOf));
      for (const id of old) {
        if (typeof id === "string" && ID.test(id) && !have.has("university:" + id)) {
          items.push({ type: "university", id, status: "thinking", updated: null });
        }
      }
      if (write(items)) localStorage.removeItem(OLD_KEY);
    } catch (e) {
      /* nothing to move */
    }
  }

  const canStore = storageWorks();
  if (canStore) migrate();

  // ---------- the header link «خطتي (n)» and the homepage's return strip ----------

  function renderHeader() {
    const n = canStore ? read().length : 0;
    for (const link of document.querySelectorAll("[data-mylist-link]")) {
      const count = link.querySelector("[data-mylist-count]");
      if (count) count.textContent = n ? String(n) : "";
    }
    for (const strip of document.querySelectorAll("[data-plan-strip]")) strip.hidden = !n;
  }

  // ---------- save buttons: a university page's toggle, «احفظ» in result rows and on program tracks ----------

  const buttonKey = (button) => (button.dataset.saveType || "university") + ":" + button.dataset.save;

  function renderButtons(root) {
    const saved = new Set(read().map(keyOf));
    for (const button of (root || document).querySelectorAll("button[data-save]")) {
      const isSaved = saved.has(buttonKey(button));
      const label = button.querySelector("[data-save-label]");
      button.classList.toggle("is-saved", isSaved);
      if (button.classList.contains("save-mini")) {
        // A short visible label, with the item's name for screen readers.
        const name = button.dataset.saveName || "";
        label.textContent = t(isSaved ? "في خطتك" : "احفظ");
        button.setAttribute("aria-label", t(isSaved ? "أزِل {name} من خطتي" : "احفظ {name} في خطتي").replace("{name}", name));
      } else {
        label.textContent = t(isSaved ? "أزِل من خطتي" : "احفظ في خطتي");
        const note = document.querySelector('[data-save-note="' + button.dataset.save + '"]');
        if (note) note.hidden = !isSaved;
      }
      button.hidden = false;
      if (button.hasAttribute("data-pending")) {
        button.removeAttribute("data-pending");
        button.removeAttribute("tabindex");
      }
    }
  }

  function toggle(button) {
    const status = document.querySelector("[data-save-status]");
    const key = buttonKey(button);
    const items = read();
    const saved = items.some((i) => keyOf(i) === key);
    const next = saved
      ? items.filter((i) => keyOf(i) !== key)
      : [{ type: button.dataset.saveType || "university", id: button.dataset.save, status: "thinking", updated: today() }, ...items];
    if (!write(next)) {
      if (status) status.textContent = t("تعذّر الحفظ في هذا المتصفح.");
      return;
    }
    renderButtons();
    renderHeader();
    if (status) status.textContent = t(saved ? "أُزيل من خطتك." : "حُفظ في خطتك على هذا الجهاز.");
  }

  // ---------- the student's grade (decision 083) ----------
  // «هذا صفّي» on a grade page keeps the grade in this browser ("wadih:grade", a grade page's slug), so the homepage
  // marks it «صفّك». One value, nothing else; pressing again forgets it.
  const GRADE_KEY = "wadih:grade";
  const GRADE = /^grade-1[0-2]$/;

  function readGrade() {
    try {
      const g = localStorage.getItem(GRADE_KEY);
      return GRADE.test(g || "") ? g : null;
    } catch (e) {
      return null;
    }
  }

  function renderGrade() {
    const mine = readGrade();
    for (const button of document.querySelectorAll("button[data-my-grade]")) {
      const on = button.dataset.myGrade === mine;
      button.setAttribute("aria-pressed", String(on));
      button.classList.toggle("is-saved", on);
      button.hidden = false;
    }
    for (const stop of document.querySelectorAll("[data-grade-stop]")) {
      const on = stop.dataset.gradeStop === mine;
      stop.classList.toggle("is-here", on);
      const here = stop.querySelector("[data-grade-here]");
      if (here) here.hidden = !on;
    }
  }

  function toggleGrade(button) {
    const status = document.querySelector("[data-save-status]");
    const on = readGrade() === button.dataset.myGrade;
    try {
      if (on) localStorage.removeItem(GRADE_KEY);
      else localStorage.setItem(GRADE_KEY, button.dataset.myGrade);
    } catch (e) {
      if (status) status.textContent = t("تعذّر الحفظ في هذا المتصفح.");
      return;
    }
    renderGrade();
    if (status) status.textContent = t(on ? "لن نذكّرك بصفّك." : "حُفظ صفّك على هذا الجهاز.");
  }

  // ---------- the «خطتي» page ----------

  async function setupPlanPage() {
    const page = document.querySelector("[data-mylist-page]");
    if (!page) return;
    const rows = page.querySelector("[data-mylist-rows]");
    const empty = page.querySelector("[data-mylist-empty]");
    const loading = page.querySelector("[data-mylist-loading]");
    const failed = page.querySelector("[data-mylist-error]");
    const status = page.querySelector("[data-mylist-status]");
    const heading = page.querySelector("h1");

    const showEmpty = () => {
      rows.replaceChildren();
      rows.hidden = true;
      empty.hidden = false;
    };

    if (!canStore) {
      page.querySelector("[data-mylist-blocked]").hidden = false;
      return;
    }

    // Draw every row from the server; `focusKey` puts the keyboard back on that row's status after a redraw.
    async function draw(focusKey) {
      const items = read();
      if (!items.length) {
        showEmpty();
        return;
      }
      const first = !rows.children.length;
      if (first) loading.hidden = false;
      try {
        const response = await fetch(page.dataset.rowsUrl, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ v: 1, items }),
        });
        if (!response.ok) throw new Error("rows " + response.status);
        rows.innerHTML = await response.text();
      } catch (e) {
        failed.hidden = false;
        return;
      } finally {
        loading.hidden = true;
      }
      failed.hidden = true;
      // Items the server didn't recognise (e.g. a university no longer in the lists) are dropped quietly.
      const shown = [...rows.querySelectorAll("[data-mylist-item]")].map((li) => li.dataset.mylistItem);
      if (shown.length !== items.length) write(items.filter((i) => shown.includes(keyOf(i))));
      renderHeader();
      if (!shown.length) {
        showEmpty();
        return;
      }
      rows.hidden = false;
      if (focusKey) {
        const select = rows.querySelector('select[data-status="' + focusKey + '"]');
        if (select) select.focus();
      }
    }

    rows.addEventListener("change", (event) => {
      const select = event.target.closest("select[data-status]");
      if (!select) return;
      const key = select.dataset.status;
      const items = read().map((i) => (keyOf(i) === key ? { ...i, status: select.value, updated: today() } : i));
      if (!write(items)) {
        status.textContent = t("تعذّر الحفظ في هذا المتصفح.");
        return;
      }
      status.textContent = t("حُفظ: {status}.").replace("{status}", select.options[select.selectedIndex].text);
      draw(key); // the next step and the date follow the new status
    });

    rows.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-remove]");
      if (!button) return;
      const key = button.dataset.remove;
      const item = button.closest("[data-mylist-item]");
      const nameEl = item.querySelector(".uni-name-ar, .uni-name-en, .plan-name");
      const name = nameEl ? nameEl.textContent.trim() : "";
      write(read().filter((i) => keyOf(i) !== key));
      // Keep the keyboard in a sensible place: the next row's button, else the previous one, else the title.
      const next = item.nextElementSibling || item.previousElementSibling;
      item.remove();
      renderHeader();
      status.textContent = t("أُزيل {name} من خطتك.").replace("{name}", name);
      if (next) {
        next.querySelector("button[data-remove]").focus();
      } else {
        showEmpty();
        heading.setAttribute("tabindex", "-1");
        heading.focus();
      }
    });

    await draw();
  }

  renderHeader();
  setupPlanPage();
  // Storage blocked (e.g. some private modes): no save buttons, so nothing pretends to be saved.
  if (!canStore) return;
  renderButtons();
  renderGrade();
  // One listener for every save button, including result rows drawn later by live updates.
  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-save]");
    if (button) toggle(button);
    const grade = event.target.closest("button[data-my-grade]");
    if (grade) toggleGrade(grade);
  });
  document.addEventListener("wadih:results", (event) => renderButtons(event.detail.root));
  // Another tab changed the plan: keep this one in step.
  window.addEventListener("storage", (event) => {
    if (event.key === GRADE_KEY) renderGrade();
    if (event.key !== KEY) return;
    renderHeader();
    renderButtons();
  });
})();
