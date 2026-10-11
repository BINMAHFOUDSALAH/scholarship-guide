// Draws the share-preview image (app/static/img/og-image.png, 1200x630).
//
// How to regenerate: run the site locally, open http://127.0.0.1:8000, paste this file into
// the browser console, and save the PNG it produces. It runs in the browser on purpose: the
// browser already has our fonts and joins Arabic letters correctly, which many image tools don't.

async function drawShareImage() {
  await Promise.all([
    document.fonts.load('700 150px "Noto Naskh Arabic"'),
    document.fonts.load('600 40px "IBM Plex Sans Arabic"'),
    document.fonts.load('400 40px "IBM Plex Sans Arabic"'),
  ]);

  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 630;
  const ctx = canvas.getContext("2d");

  // Paper
  ctx.fillStyle = "#f6f1e6";
  ctx.fillRect(0, 0, 1200, 630);

  // Mount Tuwaiq on the horizon (same shapes as partials/path-art.html, 1200x160 at the bottom)
  ctx.save();
  ctx.translate(0, 470);
  const shape = (d, color) => { ctx.fillStyle = color; ctx.fill(new Path2D(d)); };
  shape("M0 160 L0 120 L200 108 L420 100 L600 84 L760 92 L1000 80 L1200 96 L1200 160 Z", "#dfe2d5");
  shape("M0 160 L0 132 L300 114 L520 100 L700 72 L820 58 L900 42 L958 34 L990 46 L1040 160 Z", "#c0cbbb");
  shape("M1040 160 L1100 150 L1200 146 L1200 160 Z", "#c0cbbb");
  shape("M956 35 L990 46 L1040 160 L930 160 Z", "#94ab99");
  ctx.strokeStyle = "rgba(246, 241, 230, 0.6)";
  ctx.lineWidth = 2;
  ctx.stroke(new Path2D("M944 80 L1006 80 M937 116 L1022 116 M932 145 L1034 145"));
  ctx.restore();

  // Logo mark, top right (Arabic reads from the right): the same drawing as favicon.svg (decision 036)
  const mark = new Image();
  mark.src = "/static/favicon.svg";
  await mark.decode();
  ctx.drawImage(mark, 1000, 62, 150, 150);

  // Text, right-aligned
  ctx.direction = "rtl";
  ctx.textAlign = "right";
  ctx.fillStyle = "#16302a";
  ctx.font = '700 150px "Noto Naskh Arabic"';
  ctx.fillText("واضح", 970, 200);

  ctx.font = '600 52px "IBM Plex Sans Arabic"';
  ctx.fillText("مستقبلك بعد الثانوية، بوضوح", 1130, 330);

  ctx.fillStyle = "#4e605a";
  ctx.font = '400 34px "IBM Plex Sans Arabic"';
  ctx.fillText("دليل مجاني لطلاب الثانوية في السعودية", 1130, 400);

  return canvas.toDataURL("image/png");
}
