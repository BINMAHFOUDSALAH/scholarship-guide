// Theme toggle: light ↔ dark (decision 060).
// Until the student picks one, the site follows the device's setting (and changes with it).
// Their choice is saved in localStorage, which stays on this device and is never sent anywhere.
// Without JavaScript the button stays hidden and the site is shown in light mode.

const THEME_COLORS = { light: "#F6F4EE", dark: "#0c1310" };
const system = window.matchMedia("(prefers-color-scheme: dark)");
const calm = window.matchMedia("(prefers-reduced-motion: reduce)");

function chosenTheme() {
  try {
    const t = localStorage.getItem("theme");
    return t === "dark" || t === "light" ? t : null;
  } catch {
    return null; // storage can be blocked (e.g. private mode)
  }
}

function applyTheme(theme) {
  if (theme === "dark") {
    document.documentElement.dataset.theme = "dark";
  } else {
    delete document.documentElement.dataset.theme;
  }
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = THEME_COLORS[theme];
}

function saveTheme(theme) {
  try {
    localStorage.setItem("theme", theme);
  } catch {
    // Not saved, but the theme still changes for this visit.
  }
}

const button = document.querySelector(".theme-toggle");

if (button) {
  const label = button.querySelector(".theme-toggle-label");
  let current = chosenTheme() || (system.matches ? "dark" : "light");

  // The label names the mode you'll switch TO, which is clearer for a two-state switch.
  const render = () => {
    const next = current === "dark" ? "فاتح" : "داكن";
    label.textContent = next;
    button.setAttribute("aria-label", `التبديل إلى الوضع ال${next}`);
    button.setAttribute("aria-pressed", current === "dark" ? "true" : "false");
  };

  // The whole page cross-fades while the sky's own pieces (sun to moon, the stars) move on their own.
  // Short, never blocks a click, and skipped for anyone who asked for less motion.
  const switchTo = (theme) => {
    current = theme;
    const change = () => { applyTheme(theme); render(); };
    if (document.startViewTransition && !calm.matches) {
      document.documentElement.classList.add("theme-changing");
      const t = document.startViewTransition(change);
      t.finished.finally(() => document.documentElement.classList.remove("theme-changing"));
    } else {
      change();
    }
  };

  button.addEventListener("click", () => {
    const next = current === "dark" ? "light" : "dark";
    saveTheme(next);
    switchTo(next);
  });

  // The device switched (e.g. at sunset): follow it, unless the student chose a theme here.
  system.addEventListener("change", () => {
    if (!chosenTheme()) switchTo(system.matches ? "dark" : "light");
  });

  applyTheme(current);
  render();
  button.hidden = false;
}
