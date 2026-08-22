"use client";

import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export interface TimezoneClock {
  tz: string;
  label: string;
}

export interface WorkPageHeroProps {
  videoSrc?: string;
  poster?: string;
  videoType?: "auto" | "video" | "iframe";
  topWord?: string;
  rightWord?: string;
  bottomWord?: string;
  accentColor?: string;
  textColor?: string;
  backgroundColor?: string;
  showClocks?: boolean;
  clocks?: TimezoneClock[];
  scrollDistance?: string;
  className?: string;
}

const DEFAULT_VIDEO_URL =
  "https://res.cloudinary.com/dsuwzuaxp/video/upload/video1_horxtt.mp4";

const DEFAULT_CLOCKS: TimezoneClock[] = [
  { tz: "Asia/Kolkata", label: "INDIA" },
  { tz: "America/New_York", label: "NEW YORK" },
  { tz: "Asia/Dubai", label: "DUBAI" },
];

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

export const WorkPageHero: React.FC<WorkPageHeroProps> = ({
  videoSrc = DEFAULT_VIDEO_URL,
  poster,
  videoType = "auto",
  topWord = "atlas",
  rightWord = "student",
  bottomWord = "hub",
  textColor = "currentColor",
  backgroundColor = "transparent",
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
          {/* Top Word: atlas */}
          <div className="absolute top-[4%] left-[6%] sm:left-[10%] flex justify-start">
            <span
              className="font-black uppercase tracking-tighter leading-none select-none text-left"
              style={{
                color: "#FF9398",
                fontSize: "clamp(2.5rem, 8.5vw, 8.5rem)",
                fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              }}
            >
              {topWord}
            </span>
          </div>

          {/* Right Word: student */}
          <div className="absolute right-[4%] top-[38%] flex items-center justify-end">
            <span
              className="font-black uppercase tracking-tighter leading-none select-none text-right drop-shadow-lg"
              style={{
                color: textColor,
                fontSize: "clamp(2.5rem, 8.5vw, 8.5rem)",
                fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              }}
            >
              {rightWord}
            </span>
          </div>

          {/* Bottom Word: hub */}
          <div className="absolute bottom-[4%] right-[6%] sm:right-[10%] flex justify-end">
            <span
              className="font-normal italic uppercase leading-none select-none text-right"
              style={{
                color: "#D14836",
                fontSize: "clamp(3rem, 10.5vw, 9.5rem)",
                fontFamily: "Georgia, 'Times New Roman', Cambria, serif",
              }}
            >
              {bottomWord}
            </span>
          </div>

          {/* ── World Clocks Column ── */}
          {showClocks && clocks.length > 0 && (
            <div
              className="absolute left-[clamp(1rem,3vw,3.5rem)] top-1/2 -translate-y-1/2 flex flex-col gap-3 font-mono text-[clamp(9px,1vw,11px)] uppercase tracking-[0.15em] opacity-90"
              style={{ color: "#ECD06F" }}
            >
              {clocks.map(({ tz, label }) => (
                <div
                  key={tz}
                  className="flex items-center gap-[clamp(0.4rem,1vw,1.2rem)] font-medium"
                >
                  <span className="tabular-nums font-semibold text-[#FF9398]">{formatTime(tz)}</span>
                  <span style={{ color: textColor }}>{label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Center Expanding Video Pill ── */}
        <div
          ref={videoWrapperRef}
          className="absolute z-20 overflow-hidden shadow-2xl transition-[border-radius] border border-black/10 dark:border-white/10"
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
