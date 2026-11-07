// The map (decision 083): pointing at or focusing a country's chip lights that country and its path of light from
// home; everything else recedes. Works for maps drawn later too («خطتي» draws its hub after load).
(function () {
  "use strict";
  function light(chip, on) {
    const wrap = chip && chip.closest("[data-world-wrap]");
    const map = wrap && wrap.querySelector("[data-world]");
    if (!map) return;
    const code = on ? chip.dataset.worldChip : "";
    if (code) map.dataset.active = code; else delete map.dataset.active;
    for (const g of map.querySelectorAll(".world-country")) g.classList.toggle("is-active", g.dataset.country === code);
  }
  for (const [type, on] of [["pointerover", true], ["focusin", true], ["pointerout", false], ["focusout", false]]) {
    document.addEventListener(type, (event) => {
      const chip = event.target.closest && event.target.closest("[data-world-chip]");
      if (chip) light(chip, on);
    });
  }
})();
