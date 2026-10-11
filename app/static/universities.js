// Universities explorer: update the results as the student types or changes a filter.
// Without this script the form still works: pressing "ابحث" reloads the page with the results.
(function () {
  const form = document.querySelector("[data-explorer]");
  const results = document.getElementById("results");
  if (!form || !results || !window.fetch) return;

  const track = form.elements.track;
  const field = form.elements.field;

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

  form.addEventListener("input", (event) => {
    if (event.target === form.elements.q) later();
  });
  form.addEventListener("change", (event) => {
    if (event.target === track) syncFields();
    if (event.target !== form.elements.q) update();
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    update();
  });

  syncFields();
})();
