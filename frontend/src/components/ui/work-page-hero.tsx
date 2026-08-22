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
  topWord = "ATLAS",
  rightWord = "STUDENT",
  bottomWord = "HUB",
  backgroundColor = "#0b0b0e",
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
        {/* ── Animated Aalto Kinetic Typography Overlay ── */}
        <div
          ref={textGroupRef}
          className="absolute inset-0 z-30 pointer-events-none flex flex-col justify-between"
          style={{ willChange: "transform, opacity, filter" }}
        >
          {/* Top Word: ATLAS (Aalto Display Font with Coral -> Terracotta Gradient) */}
          <div className="absolute top-[2%] inset-x-0 flex justify-center">
            <span
              className="font-extrabold uppercase tracking-tighter leading-none select-none text-center"
              style={{
                background: "linear-gradient(135deg, #FF9398 0%, #D14836 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontSize: "clamp(4rem, 13vw, 13rem)",
                fontFamily: "'Syne', 'Bebas Neue', sans-serif",
                textShadow: "0 10px 30px rgba(209, 72, 54, 0.2)",
              }}
            >
              {topWord}
            </span>
          </div>

          {/* Right Word: STUDENT (Aalto Display Font in Crisp White Accent) */}
          <div className="absolute right-[3%] top-[36%] flex items-center">
            <span
              className="font-extrabold uppercase tracking-tighter leading-none select-none drop-shadow-2xl"
              style={{
                color: "#FFFFFF",
                fontSize: "clamp(3.8rem, 12vw, 12rem)",
                fontFamily: "'Syne', 'Bebas Neue', sans-serif",
              }}
            >
              {rightWord}
            </span>
          </div>

          {/* Bottom Word: HUB (Aalto Display Font in Terracotta -> Gold Gradient) */}
          <div className="absolute bottom-[2%] inset-x-0 flex justify-center">
            <span
              className="font-extrabold uppercase tracking-tighter leading-none select-none text-center"
              style={{
                background: "linear-gradient(135deg, #D14836 0%, #ECD06F 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                fontSize: "clamp(4.5rem, 15vw, 14rem)",
                fontFamily: "'Syne', 'Bebas Neue', sans-serif",
              }}
            >
              {bottomWord}
            </span>
          </div>

          {/* ── World Clocks Column ── */}
          {showClocks && clocks.length > 0 && (
            <div
              className="absolute left-[clamp(1.25rem,4vw,5rem)] top-1/2 -translate-y-1/2 flex flex-col gap-3 font-mono text-[clamp(9px,1.1vw,12px)] uppercase tracking-[0.15em] opacity-90"
              style={{ color: "#ECD06F" }}
            >
              {clocks.map(({ tz, label }) => (
                <div
                  key={tz}
                  className="flex items-center gap-[clamp(0.5rem,1.2vw,1.5rem)] font-medium"
                >
                  <span className="tabular-nums font-semibold text-[#FF9398]">{formatTime(tz)}</span>
                  <span style={{ color: "#FFFFFF" }}>{label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Center Expanding Video Pill ── */}
        <div
          ref={videoWrapperRef}
          className="absolute z-20 overflow-hidden shadow-2xl transition-[border-radius] border border-white/10"
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
