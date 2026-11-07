// The map (decisions 083, 085): pointing at or focusing a country's chip lights that country and its path of light from
// home; everything else recedes. On a touch screen there is no pointing, so the first tap on a chip lights it (the
// chip turns lime) and a second tap on the same chip opens its universities. Works for maps drawn later too («خطتي»
// draws its hub after load).
(function () {
  "use strict";
  let picked = null; // the chip a touch lit, waiting for its second tap

  function light(chip, on) {
    const wrap = chip && chip.closest("[data-world-wrap]");
    const map = wrap && wrap.querySelector("[data-world]");
    if (!map) return;
    const code = on ? chip.dataset.worldChip : "";
    if (code) map.dataset.active = code; else delete map.dataset.active;
    for (const g of map.querySelectorAll(".world-country")) g.classList.toggle("is-active", g.dataset.country === code);
  }

  function pick(chip) {
    if (picked && picked !== chip) picked.classList.remove("is-picked");
    picked = chip;
    if (chip) chip.classList.add("is-picked");
  }

  const chipOf = (event) => event.target.closest && event.target.closest("[data-world-chip]");

  // A pointer (mouse or pen hovering): light while it's over a chip. Touches are handled on tap, below.
  for (const [type, on] of [["pointerover", true], ["pointerout", false]]) {
    document.addEventListener(type, (event) => {
      const chip = chipOf(event);
      if (chip && event.pointerType !== "touch" && chip !== picked) light(chip, on);
    });
  }
  // The keyboard: light while a chip has focus (Enter opens it, as any link).
  for (const [type, on] of [["focusin", true], ["focusout", false]]) {
    document.addEventListener(type, (event) => {
      const chip = chipOf(event);
      if (chip && chip !== picked && chip.matches(":focus-visible, :not(:focus)")) light(chip, on);
    });
  }

  let lastTouch = 0;
  document.addEventListener("pointerdown", (event) => { if (event.pointerType === "touch") lastTouch = Date.now(); }, true);
  document.addEventListener("click", (event) => {
    const touch = Date.now() - lastTouch < 1000;
    const chip = chipOf(event);
    if (!chip) {
      if (picked) { light(picked, false); pick(null); }
      return;
    }
    if (!touch || chip === picked) return; // a mouse click, or the second tap: open the country
    event.preventDefault();
    if (picked) light(picked, false);
    pick(chip);
    light(chip, true);
  });
})();
