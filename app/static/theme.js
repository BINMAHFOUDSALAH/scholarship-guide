// Theme toggle: light ↔ dark (decision 060).
// Until the student picks one, the site follows the device's setting (and changes with it).
// Their choice is saved in localStorage, which stays on this device and is never sent anywhere.
// Without JavaScript the button stays hidden and the site is shown in light mode.

// Classic scripts share one global scope, so each file names its own helper (a shared `t` broke them).
const themeText = (text) => (window.WADIH_I18N && window.WADIH_I18N[text]) || text; // English pages (decision 066)
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

// Every .theme-toggle on the page (today: the header's) stays in step.
const buttons = [...document.querySelectorAll(".theme-toggle")];

if (buttons.length) {
  let current = chosenTheme() || (system.matches ? "dark" : "light");

  // The label names the mode you'll switch TO, which is clearer for a two-state switch.
  // A switch marked data-long-label says it in full («التبديل إلى الوضع الداكن»); the header's in one word.
  const render = () => {
    const next = current === "dark" ? "فاتح" : "داكن";
    for (const button of buttons) {
      const full = themeText(`التبديل إلى الوضع ال${next}`);
      button.querySelector(".theme-toggle-label").textContent = button.hasAttribute("data-long-label") ? full : themeText(next);
      if (!button.hasAttribute("data-long-label")) button.setAttribute("aria-label", full);
      button.setAttribute("aria-pressed", current === "dark" ? "true" : "false");
    }
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

  for (const button of buttons) {
    button.addEventListener("click", () => {
      const next = current === "dark" ? "light" : "dark";
      saveTheme(next);
      switchTo(next);
    });
  }

  // The device switched (e.g. at sunset): follow it, unless the student chose a theme here.
  system.addEventListener("change", () => {
    if (!chosenTheme()) switchTo(system.matches ? "dark" : "light");
  });

  applyTheme(current);
  render();
  for (const button of buttons) button.hidden = false;
}
