import * as React from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function Hero() {
  const rootRef = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const root = rootRef.current;
    if (!root) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".hero-line",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          stagger: 0.12,
          ease: "power3.out",
          scrollTrigger: {
            trigger: root,
            start: "top 75%",
          },
        }
      );

      gsap.fromTo(
        ".hero-kicker",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }
      );

      gsap.to(root, {
        opacity: 0.15,
        scale: 0.98,
        ease: "none",
        scrollTrigger: {
          trigger: root,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    }, root);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={rootRef}
      className="flex min-h-[70vh] items-center justify-center px-4 py-20"
    >
      <div className="mx-auto max-w-3xl text-center">
        <p className="hero-kicker mb-4 text-sm font-medium uppercase tracking-widest text-primary">
          Atlas · Student Hub
        </p>
        <h1 className="hero-line text-4xl font-bold tracking-tight sm:text-6xl">
          Know your attendance risk.
        </h1>
        <p className="hero-line mt-4 text-lg font-light text-muted-foreground sm:text-2xl">
          Find the right internship. Land the right room.
        </p>
        <p className="hero-line mt-6 text-sm text-muted-foreground">
          Everything runs on your real portal data — no mock numbers.
        </p>
      </div>
    </section>
  );
}
