// Theme toggle: light (the default for everyone) ↔ dark.
// The choice is saved in localStorage, which stays on this device and is never sent anywhere.
// Without JavaScript the button stays hidden and the site is shown in light mode.

const THEME_COLORS = { light: "#F6F4EE", dark: "#101713" };

function savedTheme() {
  try {
    return localStorage.getItem("theme") === "dark" ? "dark" : "light";
  } catch {
    return "light"; // storage can be blocked (e.g. private mode)
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
    if (theme === "dark") {
      localStorage.setItem("theme", "dark");
    } else {
      localStorage.removeItem("theme");
    }
  } catch {
    // Not saved, but the theme still changes for this visit.
  }
}

const button = document.querySelector(".theme-toggle");

if (button) {
  const label = button.querySelector(".theme-toggle-label");
  let current = savedTheme();

  // The label names the mode you'll switch TO, which is clearer for a two-state switch.
  const render = () => {
    const next = current === "dark" ? "فاتح" : "داكن";
    label.textContent = next;
    button.setAttribute("aria-label", `التبديل إلى الوضع ال${next}`);
    button.setAttribute("aria-pressed", current === "dark" ? "true" : "false");
  };

  button.addEventListener("click", () => {
    current = current === "dark" ? "light" : "dark";
    applyTheme(current);
    saveTheme(current);
    render();
  });

  applyTheme(current);
  render();
  button.hidden = false;
}
