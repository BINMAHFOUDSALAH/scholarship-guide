// The explainer's Remotion root (marketing/README.md §9, decision 092). explainer.mjs captures the site, writes
// public/data.json and the soundtrack, then renders this composition: 1080×1920 at 60 fps.
import { Composition } from "remotion";
import data from "../public/data.json";
import { Explainer } from "./Explainer";

export const FPS = 60;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="WadihExplainer"
    component={Explainer}
    durationInFrames={Math.ceil(data.plan.total * FPS)}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ audio: "soundtrack.wav" }}
  />
);
