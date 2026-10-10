// Click-to-play video. The page loads nothing from YouTube until the student clicks;
// then we replace the link with the privacy-enhanced player (youtube-nocookie.com).

const YOUTUBE_ID = /^[A-Za-z0-9_-]{11}$/;

document.querySelectorAll(".video-facade[data-youtube-id]").forEach((link) => {
  link.addEventListener("click", (event) => {
    const id = link.dataset.youtubeId;
    if (!YOUTUBE_ID.test(id)) return; // not a valid id: let the normal link open instead

    event.preventDefault();
    const player = document.createElement("iframe");
    player.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    player.title = "المقطع الأصلي";
    player.allow = "autoplay; encrypted-media; picture-in-picture";
    player.allowFullscreen = true;
    player.referrerPolicy = "strict-origin-when-cross-origin";
    player.className = "video-player";
    link.replaceWith(player);
  });
});
