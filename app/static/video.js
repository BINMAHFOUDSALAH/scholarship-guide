// Click-to-play video. The page loads nothing from YouTube until the student clicks;
// then we replace the link with the privacy-enhanced player (youtube-nocookie.com).
// When the clip ends, we put our own cover back, so YouTube's grid of suggested videos never
// shows. (YouTube's small logo/title link inside the player is required by its terms and stays.)

const YOUTUBE_ID = /^[A-Za-z0-9_-]{11}$/;
const PLAYER_ORIGIN = "https://www.youtube-nocookie.com";

document.querySelectorAll(".video-facade[data-youtube-id]").forEach((link) => {
  link.addEventListener("click", (event) => {
    const id = link.dataset.youtubeId;
    if (!YOUTUBE_ID.test(id)) return; // not a valid id: let the normal link open instead

    event.preventDefault();
    const params = new URLSearchParams({
      autoplay: "1",
      rel: "0",              // suggestions only from the same channel, never random ones
      iv_load_policy: "3",   // no annotation overlays
      playsinline: "1",      // play inside the page on iPhone
      enablejsapi: "1",      // lets us know when the clip ends
      origin: location.origin,
    });
    const player = document.createElement("iframe");
    player.src = `${PLAYER_ORIGIN}/embed/${id}?${params}`;
    player.title = "المقطع الأصلي";
    player.allow = "autoplay; encrypted-media; picture-in-picture";
    player.allowFullscreen = true;
    player.referrerPolicy = "strict-origin-when-cross-origin";
    player.className = "video-player";

    // Ask the player to tell us about state changes (the documented postMessage protocol,
    // without loading YouTube's extra API script).
    player.addEventListener("load", () => {
      const send = (message) => player.contentWindow.postMessage(JSON.stringify(message), PLAYER_ORIGIN);
      send({ event: "listening", id: 1, channel: "widget" });
      send({ event: "command", func: "addEventListener", args: ["onStateChange"], id: 1, channel: "widget" });
    });

    function onMessage(message) {
      if (message.origin !== PLAYER_ORIGIN || message.source !== player.contentWindow) return;
      let data;
      try {
        data = JSON.parse(message.data);
      } catch {
        return;
      }
      const ended =
        (data.event === "onStateChange" && data.info === 0) ||
        (data.event === "infoDelivery" && data.info && data.info.playerState === 0);
      if (ended) {
        window.removeEventListener("message", onMessage);
        player.replaceWith(link); // back to our cover; clicking it plays again
        link.focus();
      }
    }
    window.addEventListener("message", onMessage);

    link.replaceWith(player);
  });
});
