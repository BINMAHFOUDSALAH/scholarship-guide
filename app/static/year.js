// «السنة في سطر» (decision 083): on a phone the year scrolls sideways; start with today in the middle.
// Works in both directions: scrollBy takes the physical distance between today's line and the box's centre.
(function () {
  "use strict";
  for (const box of document.querySelectorAll("[data-year-scroll]")) {
    const today = box.querySelector(".yl-today");
    if (!today || box.scrollWidth <= box.clientWidth) continue;
    const a = today.getBoundingClientRect();
    const b = box.getBoundingClientRect();
    box.scrollBy({ left: a.left + a.width / 2 - (b.left + b.width / 2), behavior: "instant" });
  }
})();
