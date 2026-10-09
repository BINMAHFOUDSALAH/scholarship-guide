// Theme toggle: system → light → dark.
// The choice is saved in localStorage, which stays on this device and is never sent anywhere.
// Without JavaScript the button stays hidden and the site follows the system setting.

const THEMES = ["system", "light", "dark"];
const LABELS = { system: "تلقائي", light: "فاتح", dark: "داكن" };

function savedTheme() {
  try {
    const value = localStorage.getItem("theme");
    return THEMES.includes(value) ? value : "system";
  } catch {
    return "system"; // storage can be blocked (e.g. private mode)
  }
}

function applyTheme(theme) {
  if (theme === "system") {
    delete document.documentElement.dataset.theme;
  } else {
    document.documentElement.dataset.theme = theme;
  }
}

function saveTheme(theme) {
  try {
    if (theme === "system") {
      localStorage.removeItem("theme");
    } else {
      localStorage.setItem("theme", theme);
    }
  } catch {
    // Not saved, but the theme still changes for this visit.
  }
}

const button = document.querySelector(".theme-toggle");

if (button) {
  const label = button.querySelector(".theme-toggle-label");
  let current = savedTheme();

  const render = () => {
    label.textContent = LABELS[current];
    button.setAttribute("aria-label", `المظهر: ${LABELS[current]}. اضغط للتغيير`);
  };

  button.addEventListener("click", () => {
    current = THEMES[(THEMES.indexOf(current) + 1) % THEMES.length];
    applyTheme(current);
    saveTheme(current);
    render();
  });

  render();
  button.hidden = false;
}
