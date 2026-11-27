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
    button.classList.toggle("is-just-saved", !saved);
    // The light carries the item: the header's count changes when it lands, not before it leaves.
    if (saved || !flyToPlan(button, renderHeader)) renderHeader();
    if (status) status.textContent = t(saved ? "أُزيل من خطتك." : "حُفظ في خطتك على هذا الجهاز.");
  }

  // "Light travels" (decision 083): a saved item's light flies to «خطتي» in the header, so the student sees where it
  // went. Once, short, and not at all with reduced motion or when the header link is out of sight. On landing it calls
  // arrive() (the header's count) and the count gives a small pop. Returns false when nothing flies.
  function flyToPlan(from, arrive) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return false;
    const to = [...document.querySelectorAll("[data-mylist-link]")].find((l) => l.offsetParent);
    if (!to || !from.animate) return false;
    const a = from.getBoundingClientRect();
    const b = to.getBoundingClientRect();
    if (b.bottom < 0) return false;
    const travel = getComputedStyle(document.documentElement).getPropertyValue("--ease-in-out").trim() || "ease-in-out";
    const settle = getComputedStyle(document.documentElement).getPropertyValue("--ease-out").trim() || "ease-out";
    const light = document.createElement("span");
    light.className = "plan-light";
    light.setAttribute("aria-hidden", "true");
    light.style.left = a.left + a.width / 2 - 7 + "px";
    light.style.top = a.top + a.height / 2 - 7 + "px";
    document.body.append(light);
    const dx = b.left + b.width / 2 - (a.left + a.width / 2);
    const dy = b.top + b.height / 2 - (a.top + a.height / 2);
    light.animate([
      { transform: "translate(0, 0) scale(1)", opacity: 1 },
      { transform: `translate(${dx * 0.5}px, ${dy * 0.5 - 40}px) scale(1.2)`, opacity: 1, offset: 0.5 },
      { transform: `translate(${dx}px, ${dy}px) scale(0.5)`, opacity: 0.2 },
    ], { duration: 600, easing: travel }).finished.then(() => {
      light.remove();
      arrive();
      to.classList.add("is-arrived");
      setTimeout(() => to.classList.remove("is-arrived"), 600);
      const count = to.querySelector("[data-mylist-count]");
      if (count && count.animate) {
        count.animate([
          { transform: "scale(1)" },
          { transform: "scale(1.3)", offset: 0.35 },
          { transform: "scale(1)" },
        ], { duration: 320, easing: settle });
      }
    }, () => {
      light.remove();
      arrive();
    });
    return true;
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
    const hub = page.querySelector("[data-plan-hub]");
    const where = page.querySelector("[data-plan-where]");
    const datesBox = page.querySelector("[data-plan-dates]");

    // Each redraw has a ticket: only the latest may touch the page. Removing items quickly on a slow connection
    // started several redraws; an older one arriving last brought back rows already removed (2026-11-27, live site).
    let drawTicket = 0;

    const showEmpty = () => {
      drawTicket++; // nothing in flight may redraw an emptied plan
      loading.hidden = true;
      rows.replaceChildren();
      rows.hidden = true;
      empty.hidden = false;
      if (hub) hub.hidden = true;
      if (where) where.hidden = true;
      if (datesBox) datesBox.hidden = true;
    };

    if (!canStore) {
      page.querySelector("[data-mylist-blocked]").hidden = false;
      return;
    }

    // Draw every row from the server; `focusKey` puts the keyboard back on that row's status after a redraw.
    // The parts of a row that follow its status: the program's state, the date the status changed, the next step.
    const ROW_PARTS = [".plan-program", ".plan-date", ".plan-step"];

    // A status just changed in `keepKey`'s row: update that row's parts in place and keep its select, so the select
    // the student is using stays where it is. (2026-11-27: the whole list was redrawn and focus put on the new
    // select; on an iPhone, focusing a select opens its picker, so the picker came back after every choice and the
    // student couldn't tell it had been saved.)
    function patchRow(old, fresh) {
      for (const sel of ROW_PARTS) {
        const was = old.querySelector(sel);
        const now = fresh.querySelector(sel);
        if (was && now) was.replaceWith(now);
        else if (was) was.remove();
        else if (now) {
          if (sel === ".plan-date") old.querySelector(".plan-status").append(now);
          else if (sel === ".plan-step") old.querySelector(".plan-status").after(now);
          else old.querySelector(".plan-name").after(now);
        }
      }
    }

    // Draw every row from the server. `keepKey`: the row whose status the student just changed (patched in place).
    async function draw(keepKey) {
      const items = read();
      if (!items.length) {
        showEmpty();
        return;
      }
      const first = !rows.children.length;
      const ticket = ++drawTicket;
      if (first) loading.hidden = false;
      const fresh = document.createElement("template");
      try {
        const response = await fetch(page.dataset.rowsUrl, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ v: 1, items }),
        });
        if (!response.ok) throw new Error("rows " + response.status);
        const html = await response.text();
        if (ticket !== drawTicket) return; // a newer redraw (or an emptied plan) replaced this one
        fresh.innerHTML = html;
        // The parts come with the rows: the next step above them; the dates in order, then the map, under them, so
        // the saved items come first.
        for (const [name, box] of [["hub", hub], ["dates", datesBox], ["where", where]]) {
          const part = fresh.content.querySelector(`template[data-plan-part="${name}"]`);
          if (box) {
            box.replaceChildren(part ? part.content.cloneNode(true) : "");
            box.hidden = !part;
          }
          if (part) part.remove();
        }
        const freshRows = [...fresh.content.querySelectorAll("[data-mylist-item]")];
        const oldRows = [...rows.querySelectorAll("[data-mylist-item]")];
        const sameRows = keepKey && freshRows.length === oldRows.length
          && freshRows.every((li, i) => li.dataset.mylistItem === oldRows[i].dataset.mylistItem);
        if (sameRows) {
          freshRows.forEach((li, i) => {
            if (li.dataset.mylistItem === keepKey) patchRow(oldRows[i], li);
            else oldRows[i].replaceWith(li);
          });
        } else {
          rows.replaceChildren(fresh.content);
        }
      } catch (e) {
        if (ticket === drawTicket) failed.hidden = false;
        return;
      } finally {
        if (ticket === drawTicket) loading.hidden = true;
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
    }

    // «حُفظ» beside the select, so a sighted student sees the choice was kept (the status line says it for screen
    // readers). It stays until the next change.
    function showSaved(select) {
      for (const old of rows.querySelectorAll(".plan-saved")) old.remove();
      const note = document.createElement("span");
      note.className = "plan-saved";
      note.setAttribute("aria-hidden", "true");
      note.textContent = t("حُفظ");
      select.after(note);
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
      showSaved(select);
      // The next step and the date follow the new status. «قُبلت» lights the row once (decision 083).
      draw(key).then(() => {
        if (select.value !== "accepted") return;
        const row = rows.querySelector('[data-mylist-item="' + key + '"]');
        if (row) row.classList.add("is-accepted");
      });
    });

    // «أضف المواعيد إلى تقويمك»: the server turns the plan into an .ics file and forgets it; the phone opens it.
    // The button sits with the dates, under the rows (redesign v3), so the whole page listens.
    if (hub) page.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-plan-ics]");
      if (!button) return;
      button.disabled = true;
      try {
        const response = await fetch(hub.dataset.icsUrl, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ v: 1, items: read() }),
        });
        if (!response.ok) throw new Error("ics " + response.status);
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement("a");
        link.href = url;
        link.download = "wadih-plan.ics";
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 10000);
        status.textContent = t("نُزّل ملف المواعيد. افتحه لتضيفها إلى تقويمك.");
      } catch (e) {
        status.textContent = t("تعذّر تجهيز ملف المواعيد. حاول مرة أخرى.");
      } finally {
        button.disabled = false;
      }
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
      const nextKey = next && next.dataset.mylistItem;
      item.remove();
      renderHeader();
      status.textContent = t("أُزيل {name} من خطتك.").replace("{name}", name);
      if (nextKey) {
        next.querySelector("button[data-remove]").focus();
        // The hub's counts, dates and map follow the plan (the rows are redrawn, then focus is put back).
        draw().then(() => {
          const again = rows.querySelector('button[data-remove="' + nextKey + '"]');
          if (again) again.focus();
        });
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
