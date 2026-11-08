// The explainer's Remotion root (marketing/README.md §9, decisions 092, 094). explainer.mjs captures the site, writes
// public/data-tall.json, public/data-wide.json and each film's soundtrack, then renders these compositions at 60 fps:
// the phone site upright (1080×1920) and the desktop site wide (1920×1080).
import { Composition } from "remotion";
import tall from "../public/data-tall.json";
import wide from "../public/data-wide.json";
import { ExplainerTall, ExplainerWide } from "./Explainer";

export const FPS = 60;

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="WadihTall"
      component={ExplainerTall}
      durationInFrames={Math.ceil(tall.plan.total * FPS)}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{ audio: "soundtrack-tall.wav" as string | null }}
    />
    <Composition
      id="WadihWide"
      component={ExplainerWide}
      durationInFrames={Math.ceil(wide.plan.total * FPS)}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{ audio: "soundtrack-wide.wav" as string | null }}
    />
  </>
);
