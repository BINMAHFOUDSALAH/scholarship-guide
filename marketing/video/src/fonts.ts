// The site's own self-hosted fonts (app/static/fonts.css, SIL Open Font License), copied into public/fonts by
// explainer.mjs: IBM Plex Sans Arabic for text, Noto Naskh Arabic for titles. Each comes as an Arabic and a Latin file.
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

const AR = "U+0600-06FF, U+0750-077F, U+0870-08FF, U+200C-200E, U+2010-2011, U+FB50-FDFF, U+FE70-FEFC";
const LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2212, U+FEFF, U+FFFD";

export const fontsReady = Promise.all([
  ...["400", "600", "700"].flatMap((weight) => [
    loadFont({ family: "IBM Plex Sans Arabic", url: staticFile(`fonts/ibm-plex-sans-arabic-arabic-${weight}.woff2`), weight, unicodeRange: AR }),
    loadFont({ family: "IBM Plex Sans Arabic", url: staticFile(`fonts/ibm-plex-sans-arabic-latin-${weight}.woff2`), weight, unicodeRange: LATIN }),
  ]),
  loadFont({ family: "Noto Naskh Arabic", url: staticFile("fonts/noto-naskh-arabic-arabic-700.woff2"), weight: "700", unicodeRange: AR }),
  loadFont({ family: "Noto Naskh Arabic", url: staticFile("fonts/noto-naskh-arabic-latin-700.woff2"), weight: "700", unicodeRange: LATIN }),
]);
