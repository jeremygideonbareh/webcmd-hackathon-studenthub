"use client";

import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

// ---------------------------------------------------------------------------
// Types & Defaults
// ---------------------------------------------------------------------------
export interface TimezoneClock {
  tz: string;
  label: string;
}

export interface WorkPageHeroProps {
  /**
   * Video source URL. Supports direct video files (.mp4, .webm, cdn streams)
   * or iframe embeds (Cloudinary player, Vimeo, YouTube).
   */
  videoSrc?: string;
  /** Video poster / thumbnail image URL */
  poster?: string;
  /** Explicitly set video rendering mode, or auto-detect based on URL */
  videoType?: "auto" | "video" | "iframe";
  /** Top overlay word (default: "creating") */
  topWord?: string;
  /** Right side overlay word (default: "your") */
  rightWord?: string;
  /** Bottom overlay word (default: "story") */
  bottomWord?: string;
  /** Accent color for highlighted text and clock timestamps (default: "#f97316") */
  accentColor?: string;
  /** Secondary text color (default: "#000000") */
  textColor?: string;
  /** Background color of the hero viewport (default: "#fafafa") */
  backgroundColor?: string;
  /** Whether to display the live world timezone clocks */
  showClocks?: boolean;
  /** Array of timezones and city labels to display in the live clocks */
  clocks?: TimezoneClock[];
  /** GSAP ScrollTrigger end scroll distance (default: "+=150%") */
  scrollDistance?: string;
  /** Additional container CSS classes */
  className?: string;
}

const DEFAULT_VIDEO_URL =
  "https://res.cloudinary.com/dsuwzuaxp/video/upload/video1_horxtt.mp4";

const DEFAULT_CLOCKS: TimezoneClock[] = [
  { tz: "Asia/Kolkata", label: "INDIA" },
  { tz: "America/New_York", label: "NEW YORK" },
  { tz: "Asia/Dubai", label: "DUBAI" },
];

// ---------------------------------------------------------------------------
// Helper – Live World Timezone Clock Hook
// ---------------------------------------------------------------------------
function useLiveTime() {
  const [time, setTime] = useState<Date>(() => new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (tz: string) => {
    try {
      return new Intl.DateTimeFormat("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        timeZone: tz,
        hour12: false,
      }).format(time);
    } catch {
      return "--:--:--";
    }
  };

  return { formatTime };
}

// ---------------------------------------------------------------------------
// Component – WorkPageHero / ScrollExpandHero
// ---------------------------------------------------------------------------
export const WorkPageHero: React.FC<WorkPageHeroProps> = ({
  videoSrc = DEFAULT_VIDEO_URL,
  poster,
  videoType = "auto",
  topWord = "atlas",
  rightWord = "student",
  bottomWord = "hub",
  accentColor = "#f97316",
  textColor = "#000000",
  backgroundColor = "#fafafa",
  showClocks = true,
  clocks = DEFAULT_CLOCKS,
  scrollDistance = "+=150%",
  className = "",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoWrapperRef = useRef<HTMLDivElement>(null);
  const textGroupRef = useRef<HTMLDivElement>(null);
  const { formatTime } = useLiveTime();

  const isDirectVideo =
    videoType === "video" ||
    (videoType === "auto" &&
      !videoSrc.includes("player.cloudinary.com") &&
      !videoSrc.includes("youtube.com") &&
      !videoSrc.includes("vimeo.com") &&
      /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(videoSrc));

  useGSAP(
    () => {
      if (!containerRef.current || !videoWrapperRef.current || !textGroupRef.current) {
        return;
      }

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: scrollDistance,
          scrub: true,
          pin: true,
        },
      });

      tl.to(
        videoWrapperRef.current,
        {
          top: "0%",
          left: "0%",
          bottom: "0%",
          right: "0%",
          borderRadius: "0rem",
          ease: "none",
        },
        0
      ).to(
        textGroupRef.current,
        {
          opacity: 0,
          scale: 1.15,
          filter: "blur(12px)",
          ease: "none",
        },
        0
      );
    },
    { scope: containerRef, dependencies: [scrollDistance] }
  );

  return (
    <div
      className={`relative w-full overflow-hidden ${className}`}
      style={{ background: backgroundColor }}
    >
      <section
        ref={containerRef}
        className="relative h-screen min-h-[520px] w-full overflow-hidden select-none"
      >
        {/* ── Animated Kinetic Typography Overlay ── */}
        <div
          ref={textGroupRef}
          className="absolute inset-0 z-30 pointer-events-none flex flex-col justify-between"
          style={{ willChange: "transform, opacity, filter" }}
        >
          {/* Top Word */}
          <div className="absolute top-[2%] inset-x-0 flex justify-center">
            <span
              className="font-black tracking-tighter leading-none select-none text-center"
              style={{
                color: accentColor,
                fontSize: "clamp(3.5rem, 11vw, 11rem)",
                fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              }}
            >
              {topWord}
            </span>
          </div>

          {/* Right Word */}
          <div className="absolute right-[3%] top-[38%] flex items-center">
            <span
              className="font-black tracking-tighter leading-none select-none"
              style={{
                color: textColor,
                fontSize: "clamp(3.5rem, 11vw, 11rem)",
                fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              }}
            >
              {rightWord}
            </span>
          </div>

          {/* Bottom Word (Serif / Editorial) */}
          <div className="absolute bottom-[2%] inset-x-0 flex justify-center">
            <span
              className="font-normal italic leading-none select-none text-center"
              style={{
                color: accentColor,
                fontSize: "clamp(4rem, 14vw, 13rem)",
                fontFamily: "Georgia, 'Times New Roman', Cambria, serif",
              }}
            >
              {bottomWord}
            </span>
          </div>

          {/* ── World Clocks Column ── */}
          {showClocks && clocks.length > 0 && (
            <div
              className="absolute left-[clamp(1.25rem,4vw,5rem)] top-1/2 -translate-y-1/2 flex flex-col gap-3 font-mono text-[clamp(9px,1.1vw,12px)] uppercase tracking-[0.15em] opacity-90"
              style={{ color: accentColor }}
            >
              {clocks.map(({ tz, label }) => (
                <div
                  key={tz}
                  className="flex items-center gap-[clamp(0.5rem,1.2vw,1.5rem)] font-medium"
                >
                  <span className="tabular-nums font-semibold">{formatTime(tz)}</span>
                  <span style={{ color: textColor }}>{label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Center Expanding Video Pill ── */}
        <div
          ref={videoWrapperRef}
          className="absolute z-20 overflow-hidden shadow-2xl transition-[border-radius]"
          style={{
            top: "18%",
            bottom: "18%",
            left: "22%",
            right: "18%",
            borderRadius: "0.75rem",
            willChange: "top, left, right, bottom, border-radius",
          }}
        >
          {isDirectVideo ? (
            <video
              src={videoSrc}
              poster={poster}
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-full object-cover"
            />
          ) : (
            <iframe
              src={videoSrc}
              title="Hero reel video"
              allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
              allowFullScreen
              className="w-full h-full border-none block"
            />
          )}
        </div>
      </section>
    </div>
  );
};

export default WorkPageHero;
