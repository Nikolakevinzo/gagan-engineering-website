import { useState, useCallback } from "react";
import { ChevronLeft, ChevronRight, Play, X } from "lucide-react";
import { normalizeImageUrl } from "@/lib/catalogueData";

const FALLBACK = "https://5.imimg.com/data5/SELLER/Default/2026/3/591026243/LM/XU/AK/4175789/corrugated-sheets-making-machine-500x500.jpeg";

/**
 * ProductGallery — shows up to 5 product images + optional YouTube video.
 * Props:
 *   images    : string[]   — ordered array of image URLs (index 0 = primary)
 *   videoId   : string|null — YouTube video ID (e.g. "dQw4w9WgXcQ")
 *   productName: string    — used for alt text
 */
export default function ProductGallery({ images = [], videoId = null, productName = "" }) {
  // Build the "slots" list: images + optional video at the end
  const hasVideo = Boolean(videoId);
  const slots = images.map((url, i) => ({ type: "image", url: normalizeImageUrl(url), idx: i }));
  if (hasVideo) slots.push({ type: "video", videoId });

  const [active, setActive] = useState(0);
  const [videoPlaying, setVideoPlaying] = useState(false);

  const activeSlot = slots[active] ?? slots[0];

  const prev = useCallback(() => setActive((a) => Math.max(0, a - 1)), []);
  const next = useCallback(() => setActive((a) => Math.min(slots.length - 1, a + 1)), [slots.length]);

  const selectSlot = (idx) => {
    setActive(idx);
    // If navigating away from video while playing, stop it
    if (slots[idx]?.type !== "video") setVideoPlaying(false);
  };

  if (slots.length === 0) {
    return (
      <div className="relative border border-white/10 bg-[#0c0c0e] aspect-[4/3] sm:aspect-[16/11] rounded-xs overflow-hidden shadow-2xl p-4 sm:p-6 flex items-center justify-center">
        <img src={FALLBACK} alt={productName} className="w-full h-full object-contain" />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* ---- Main Panel ---- */}
      <div className="relative border border-white/10 bg-[#0c0c0e] aspect-[4/3] sm:aspect-[16/11] rounded-xs overflow-hidden shadow-2xl group">

        {/* Image or Video */}
        {activeSlot?.type === "image" ? (
          <img
            key={activeSlot.url}
            src={activeSlot.url || FALLBACK}
            alt={`${productName} — view ${(activeSlot.idx ?? 0) + 1}`}
            className="w-full h-full object-contain p-4 sm:p-6"
            onError={(e) => { e.currentTarget.src = FALLBACK; }}
            data-testid="product-gallery-main"
          />
        ) : videoPlaying ? (
          /* Inline YouTube embed — only mounted on click */
          <iframe
            key="yt-embed"
            src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`}
            title={`${productName} — product video`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute inset-0 w-full h-full"
            data-testid="product-gallery-video"
          />
        ) : (
          /* Lazy video thumbnail — no iframe until click */
          <button
            className="absolute inset-0 w-full h-full flex flex-col items-center justify-center gap-3 group/play"
            onClick={() => setVideoPlaying(true)}
            aria-label="Play product video"
            data-testid="product-gallery-play-btn"
          >
            <img
              src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`}
              alt="Video thumbnail"
              className="absolute inset-0 w-full h-full object-cover opacity-60"
            />
            <div className="relative z-10 flex flex-col items-center gap-2">
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-[#FF5722] flex items-center justify-center shadow-2xl group-hover/play:scale-110 transition-transform duration-200">
                <Play className="w-7 h-7 sm:w-9 sm:h-9 text-white fill-white ml-1" />
              </div>
              <span className="mono text-xs text-white/80 uppercase tracking-widest bg-black/60 px-3 py-1 rounded-xs">
                Watch Machine in Action
              </span>
            </div>
          </button>
        )}

        {/* Category badge (only on image view) */}
        {activeSlot?.type === "image" && (
          <div className="absolute top-3 left-3 z-10 bg-black/85 backdrop-blur-md px-2.5 py-1 mono text-[9px] sm:text-[10px] tracking-[0.15em] uppercase text-[#FF5722] border border-[#FF5722]/40 rounded-xs pointer-events-none">
            {activeSlot.idx === 0 ? "Primary Photo" : `Photo ${(activeSlot.idx ?? 0) + 1} / ${images.length}`}
          </div>
        )}

        {/* Prev / Next arrows — only shown when multiple slots */}
        {slots.length > 1 && (
          <>
            <button
              onClick={prev}
              disabled={active === 0}
              className="absolute left-2 top-1/2 -translate-y-1/2 z-10 p-1.5 bg-black/60 hover:bg-black/90 border border-white/20 rounded-xs text-white disabled:opacity-20 disabled:cursor-not-allowed transition-all opacity-0 group-hover:opacity-100"
              aria-label="Previous"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={next}
              disabled={active === slots.length - 1}
              className="absolute right-2 top-1/2 -translate-y-1/2 z-10 p-1.5 bg-black/60 hover:bg-black/90 border border-white/20 rounded-xs text-white disabled:opacity-20 disabled:cursor-not-allowed transition-all opacity-0 group-hover:opacity-100"
              aria-label="Next"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </>
        )}
      </div>

      {/* ---- Thumbnail Strip — only rendered when > 1 slot ---- */}
      {slots.length > 1 && (
        <div
          className="flex gap-2 overflow-x-auto pb-1 scroll-smooth snap-x snap-mandatory scrollbar-hide"
          role="listbox"
          aria-label="Product photos"
        >
          {slots.map((slot, idx) => (
            <button
              key={idx}
              role="option"
              aria-selected={active === idx}
              onClick={() => selectSlot(idx)}
              className={`relative shrink-0 w-16 h-14 sm:w-20 sm:h-16 rounded-xs border-2 overflow-hidden snap-start transition-all duration-150 ${
                active === idx
                  ? "border-[#FF5722] shadow-[0_0_10px_rgba(255,87,34,0.4)]"
                  : "border-white/10 hover:border-white/40 opacity-60 hover:opacity-100"
              }`}
            >
              {slot.type === "image" ? (
                <img
                  src={slot.url}
                  alt={`View ${idx + 1}`}
                  className="w-full h-full object-cover bg-[#0c0c0e]"
                  onError={(e) => { e.currentTarget.src = FALLBACK; }}
                  loading="lazy"
                />
              ) : (
                /* Video thumbnail tile */
                <div className="relative w-full h-full bg-[#0c0c0e]">
                  <img
                    src={`https://img.youtube.com/vi/${slot.videoId}/mqdefault.jpg`}
                    alt="Video"
                    className="w-full h-full object-cover opacity-70"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-6 h-6 rounded-full bg-[#FF5722] flex items-center justify-center">
                      <Play className="w-3 h-3 text-white fill-white ml-0.5" />
                    </div>
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
