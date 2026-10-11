// «قائمتي»: universities the student saved, kept in this browser only (decision 035).
// What's stored: university ids (e.g. "stanford-university"), newest first, in localStorage under
// "wadih:saved". Nothing is sent to us except when the «قائمتي» page asks the server to draw the rows
// (the ids only, never stored). Without JavaScript, or with storage blocked, the save buttons stay hidden.
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

  if (!storageWorks()) return;

  // ---------- the header link «قائمتي (n)» ----------

  function renderHeader() {
    const n = read().length;
    for (const link of document.querySelectorAll("[data-mylist-link]")) {
      link.hidden = n === 0 && link.getAttribute("aria-current") === null;
      const count = link.querySelector("[data-mylist-count]");
      if (count) count.textContent = n ? String(n) : "";
    }
  }

  // ---------- «✓ في قائمتك» markers in lists ----------

  function renderMarkers(root) {
    const saved = new Set(read());
    for (const marker of (root || document).querySelectorAll("[data-saved-marker]")) {
      marker.hidden = !saved.has(marker.dataset.savedMarker);
    }
  }

  // ---------- the save button on a university page ----------

  function setupSaveButtons() {
    for (const button of document.querySelectorAll("button[data-save]")) {
      const id = button.dataset.save;
      const label = button.querySelector("[data-save-label]");
      const note = document.querySelector('[data-save-note="' + id + '"]');
      const status = document.querySelector("[data-save-status]");

      const render = () => {
        const saved = read().includes(id);
        button.classList.toggle("is-saved", saved);
        label.textContent = saved ? "أزِل من قائمتي" : "احفظ في قائمتي";
        if (note) note.hidden = !saved;
      };

      button.addEventListener("click", () => {
        const ids = read();
        const saved = ids.includes(id);
        const next = saved ? ids.filter((x) => x !== id) : [id, ...ids];
        if (!write(next)) {
          if (status) status.textContent = "تعذّر الحفظ في هذا المتصفح.";
          return;
        }
        render();
        renderHeader();
        if (status) status.textContent = saved ? "أُزيلت من قائمتك." : "حُفظت في قائمتك على هذا الجهاز.";
      });

      render();
      button.hidden = false;
    }
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
  renderMarkers();
  setupSaveButtons();
  setupListPage();
  document.addEventListener("wadih:results", (event) => renderMarkers(event.detail.root));
  // Another tab saved or removed something: keep this one in step.
  window.addEventListener("storage", (event) => {
    if (event.key !== KEY) return;
    renderHeader();
    renderMarkers();
  });
})();
