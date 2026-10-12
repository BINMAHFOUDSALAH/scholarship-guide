// «قائمتي»: universities the student saved, kept in this browser only (decision 035).
// What's stored: university ids (e.g. "stanford-university"), newest first, in localStorage under
// "wadih:saved". Nothing is sent to us except when the «قائمتي» page asks the server to draw the rows
// (the ids only, never stored). Without JavaScript, or with storage blocked, the save buttons stay hidden
// and the «قائمتي» page says why.
(function () {
  const KEY = "wadih:saved";
  const MAX = 100;

  function read() {
    try {
      const ids = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(ids) ? ids.filter((id) => /^[a-z0-9-]+$/.test(id)) : [];
    } catch (e) {
      return [];
    }
  }

  function write(ids) {
    try {
      localStorage.setItem(KEY, JSON.stringify(ids.slice(0, MAX)));
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

  const canStore = storageWorks();

  // ---------- the header link «قائمتي (n)» (always visible, decision 039) ----------

  function renderHeader() {
    const n = canStore ? read().length : 0;
    for (const link of document.querySelectorAll("[data-mylist-link]")) {
      const count = link.querySelector("[data-mylist-count]");
      if (count) count.textContent = n ? String(n) : "";
    }
  }

  // ---------- save buttons: the university page's toggle and «احفظ» in result rows ----------

  function renderButtons(root) {
    const saved = new Set(read());
    for (const button of (root || document).querySelectorAll("button[data-save]")) {
      const id = button.dataset.save;
      const isSaved = saved.has(id);
      const label = button.querySelector("[data-save-label]");
      button.classList.toggle("is-saved", isSaved);
      if (button.classList.contains("save-mini")) {
        // A short visible label, with the university's name for screen readers.
        const name = button.dataset.saveName || "";
        label.textContent = isSaved ? "✓ في قائمتك" : "احفظ";
        button.setAttribute("aria-label", isSaved ? "أزِل " + name + " من قائمتي" : "احفظ " + name + " في قائمتي");
      } else {
        label.textContent = isSaved ? "أزِل من قائمتي" : "احفظ في قائمتي";
        const note = document.querySelector('[data-save-note="' + id + '"]');
        if (note) note.hidden = !isSaved;
      }
      button.hidden = false;
      if (button.hasAttribute("data-pending")) {
        button.removeAttribute("data-pending");
        button.removeAttribute("tabindex");
      }
    }
  }

  function toggle(id) {
    const status = document.querySelector("[data-save-status]");
    const ids = read();
    const saved = ids.includes(id);
    const next = saved ? ids.filter((x) => x !== id) : [id, ...ids];
    if (!write(next)) {
      if (status) status.textContent = "تعذّر الحفظ في هذا المتصفح.";
      return;
    }
    renderButtons();
    renderHeader();
    if (status) status.textContent = saved ? "أُزيلت من قائمتك." : "حُفظت في قائمتك على هذا الجهاز.";
  }

  // ---------- the «قائمتي» page ----------

  async function setupListPage() {
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
    const ids = read();
    if (!ids.length) {
      showEmpty();
      return;
    }
    loading.hidden = false;
    try {
      const response = await fetch(page.dataset.rowsUrl + "?partial=1&ids=" + encodeURIComponent(ids.join(",")));
      if (!response.ok) throw new Error("rows " + response.status);
      rows.innerHTML = await response.text();
    } catch (e) {
      failed.hidden = false;
      return;
    } finally {
      loading.hidden = true;
    }
    // Ids the server didn't recognise (e.g. a university no longer in the lists) are dropped quietly.
    const shown = [...rows.querySelectorAll("[data-mylist-item]")].map((li) => li.dataset.mylistItem);
    if (shown.length !== ids.length) write(ids.filter((id) => shown.includes(id)));
    renderHeader();
    if (!shown.length) {
      showEmpty();
      return;
    }
    rows.hidden = false;

    rows.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-remove]");
      if (!button) return;
      const id = button.dataset.remove;
      const item = button.closest("[data-mylist-item]");
      const name = item.querySelector(".uni-name-ar, .uni-name-en").textContent.trim();
      write(read().filter((x) => x !== id));
      // Keep the keyboard in a sensible place: the next row's button, else the previous one, else the title.
      const next = item.nextElementSibling || item.previousElementSibling;
      item.remove();
      renderHeader();
      status.textContent = "أُزيلت " + name + " من قائمتك.";
      if (next) {
        next.querySelector("button[data-remove]").focus();
      } else {
        showEmpty();
        heading.setAttribute("tabindex", "-1");
        heading.focus();
      }
    });
  }

  renderHeader();
  setupListPage();
  // Storage blocked (e.g. some private modes): no save buttons, so nothing pretends to be saved.
  if (!canStore) return;
  renderButtons();
  // One listener for every save button, including result rows drawn later by live updates.
  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-save]");
    if (button) toggle(button.dataset.save);
  });
  document.addEventListener("wadih:results", (event) => renderButtons(event.detail.root));
  // Another tab saved or removed something: keep this one in step.
  window.addEventListener("storage", (event) => {
    if (event.key !== KEY) return;
    renderHeader();
    renderButtons();
  });
})();
