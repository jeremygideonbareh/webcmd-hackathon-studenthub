import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { CustomEase } from "gsap/CustomEase";
import { Book, BookOpen, KeyRound } from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { StudentAuthModal } from "@/components/student-auth-modal";

// Register GSAP Plugins safely
if (typeof window !== "undefined") {
  gsap.registerPlugin(CustomEase);
}

export function SterlingGateKineticNavigation() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [kpModalOpen, setKpModalOpen] = useState(false);
  const { user, isLevel1Authenticated, isLevel2Authenticated } = useAuth();

  // Initial Setup & Hover Effects
  useEffect(() => {
    if (!containerRef.current) return;

    try {
      if (!gsap.parseEase("main")) {
        CustomEase.create("main", "0.65, 0.01, 0.05, 0.99");
        gsap.defaults({ ease: "main", duration: 0.7 });
      }
    } catch (e) {
      gsap.defaults({ ease: "power2.out", duration: 0.7 });
    }

    const ctx = gsap.context(() => {
      const menuItems = containerRef.current!.querySelectorAll(".menu-list-item[data-shape]");
      const shapesContainer = containerRef.current!.querySelector(".ambient-background-shapes");

      menuItems.forEach((item) => {
        const shapeIndex = item.getAttribute("data-shape");
        const shape = shapesContainer ? shapesContainer.querySelector(`.bg-shape-${shapeIndex}`) : null;

        if (!shape) return;
        const shapeEls = shape.querySelectorAll(".shape-element");

        const onEnter = () => {
          if (shapesContainer) {
            shapesContainer.querySelectorAll(".bg-shape").forEach((s) => s.classList.remove("active"));
          }
          shape.classList.add("active");

          gsap.fromTo(
            shapeEls,
            { scale: 0.5, opacity: 0, rotation: -10 },
            { scale: 1, opacity: 1, rotation: 0, duration: 0.6, stagger: 0.08, ease: "back.out(1.7)", overwrite: "auto" }
          );
        };

        const onLeave = () => {
          gsap.to(shapeEls, {
            scale: 0.8,
            opacity: 0,
            duration: 0.3,
            ease: "power2.in",
            onComplete: () => shape.classList.remove("active"),
            overwrite: "auto",
          });
        };

        item.addEventListener("mouseenter", onEnter);
        item.addEventListener("mouseleave", onLeave);

        (item as any)._cleanup = () => {
          item.removeEventListener("mouseenter", onEnter);
          item.removeEventListener("mouseleave", onLeave);
        };
      });
    }, containerRef);

    return () => {
      ctx.revert();
      if (containerRef.current) {
        const items = containerRef.current.querySelectorAll(".menu-list-item[data-shape]");
        items.forEach((item: any) => item._cleanup && item._cleanup());
      }
    };
  }, []);

  // Menu Open/Close Animation Effect
  useEffect(() => {
    if (!containerRef.current) return;

    const ctx = gsap.context(() => {
      const navWrap = containerRef.current!.querySelector(".nav-overlay-wrapper");
      const menu = containerRef.current!.querySelector(".menu-content");
      const overlay = containerRef.current!.querySelector(".overlay");
      const bgPanels = containerRef.current!.querySelectorAll(".backdrop-layer");
      const menuLinks = containerRef.current!.querySelectorAll(".nav-link");
      const fadeTargets = containerRef.current!.querySelectorAll("[data-menu-fade]");

      const menuButton = containerRef.current!.querySelector(".nav-close-btn");
      const menuButtonTexts = menuButton?.querySelectorAll("p");
      const menuButtonIcon = menuButton?.querySelector(".menu-button-icon");

      const tl = gsap.timeline();

      if (isMenuOpen) {
        if (navWrap) navWrap.setAttribute("data-nav", "open");

        tl.set(navWrap, { display: "block" })
          .set(menu, { xPercent: 0 }, "<");

        if (menuButtonTexts && menuButtonTexts.length > 0) {
          tl.fromTo(menuButtonTexts, { yPercent: 0 }, { yPercent: -100, stagger: 0.2 });
        }
        if (menuButtonIcon) {
          tl.fromTo(menuButtonIcon, { rotate: 0 }, { rotate: 315 }, "<");
        }

        tl.fromTo(overlay, { autoAlpha: 0 }, { autoAlpha: 1 }, "<")
          .fromTo(bgPanels, { xPercent: 101 }, { xPercent: 0, stagger: 0.12, duration: 0.575 }, "<")
          .fromTo(menuLinks, { yPercent: 140, rotate: 10 }, { yPercent: 0, rotate: 0, stagger: 0.05 }, "<+=0.35");

        if (fadeTargets.length) {
          tl.fromTo(fadeTargets, { autoAlpha: 0, yPercent: 50 }, { autoAlpha: 1, yPercent: 0, stagger: 0.04, clearProps: "all" }, "<+=0.2");
        }
      } else {
        if (navWrap) navWrap.setAttribute("data-nav", "closed");

        tl.to(overlay, { autoAlpha: 0 })
          .to(menu, { xPercent: 120 }, "<");

        if (menuButtonTexts && menuButtonTexts.length > 0) {
          tl.to(menuButtonTexts, { yPercent: 0 }, "<");
        }
        if (menuButtonIcon) {
          tl.to(menuButtonIcon, { rotate: 0 }, "<");
        }

        tl.set(navWrap, { display: "none" });
      }
    }, containerRef);

    return () => ctx.revert();
  }, [isMenuOpen]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isMenuOpen) {
        setIsMenuOpen(false);
      }
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isMenuOpen]);

  const toggleMenu = () => setIsMenuOpen((prev) => !prev);
  const closeMenu = () => setIsMenuOpen(false);

  return (
    <div ref={containerRef} className="relative z-50">
      {/* Top Navbar Header */}
      <div className="site-header-wrapper">
        <header className="header py-4 px-6 flex items-center justify-between border-b bg-background/90 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button
              onClick={toggleMenu}
              className="flex items-center gap-2 rounded-xl border bg-card px-3 py-1.5 shadow-sm hover:bg-accent transition-all focus-visible:outline-none"
              aria-label="Toggle Sterling Gate Kinetic Menu"
            >
              {isMenuOpen ? (
                <BookOpen className="h-5 w-5 text-primary animate-pulse" />
              ) : (
                <Book className="h-5 w-5 text-muted-foreground" />
              )}
              <span className="text-xs font-bold tracking-tight">Atlas</span>
            </button>
          </div>

          <div className="flex items-center gap-4">
            <div
              className="nav-toggle-label cursor-pointer text-xs font-mono uppercase tracking-wider text-muted-foreground hover:text-foreground hidden sm:block"
              onClick={toggleMenu}
            >
              <span className="toggle-text">Explore Menu</span>
            </div>

            <button
              role="button"
              className="nav-close-btn flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold hover:bg-accent transition-colors bg-card shadow-sm"
              onClick={toggleMenu}
            >
              <div className="menu-button-text overflow-hidden h-4">
                <p className="p-large transition-transform">{isMenuOpen ? "Close" : "Menu"}</p>
              </div>
              <div className="icon-wrap">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="12"
                  height="12"
                  viewBox="0 0 16 16"
                  fill="none"
                  className="menu-button-icon transition-transform"
                >
                  <path d="M7.33333 16L7.33333 -3.2055e-07L8.66667 -3.78832e-07L8.66667 16L7.33333 16Z" fill="currentColor" />
                  <path d="M16 8.66667L-2.62269e-07 8.66667L-3.78832e-07 7.33333L16 7.33333L16 8.66667Z" fill="currentColor" />
                </svg>
              </div>
            </button>
          </div>
        </header>
      </div>

      {/* Fullscreen Sterling Gate Kinetic Overlay Navigation */}
      <section className="fullscreen-menu-container">
        <div data-nav="closed" className="nav-overlay-wrapper fixed inset-0 z-50 hidden">
          <div className="overlay absolute inset-0 bg-black/75 backdrop-blur-md" onClick={closeMenu}></div>

          <nav className="menu-content absolute right-0 top-0 bottom-0 w-full max-w-lg bg-[#121216] border-l border-white/10 p-8 shadow-2xl overflow-y-auto z-10 flex flex-col justify-between">
            <div className="menu-bg absolute inset-0 overflow-hidden pointer-events-none">
              <div className="backdrop-layer first absolute inset-0 bg-primary/20"></div>
              <div className="backdrop-layer second absolute inset-0 bg-pink-500/10"></div>
              <div className="backdrop-layer absolute inset-0 bg-[#121216]"></div>

              {/* Abstract Ambient Background Shapes */}
              <div className="ambient-background-shapes absolute inset-0 opacity-80">
                <svg className="bg-shape bg-shape-1 absolute inset-0 w-full h-full" viewBox="0 0 400 400" fill="none">
                  <circle className="shape-element" cx="80" cy="120" r="40" fill="rgba(99,102,241,0.25)" />
                  <circle className="shape-element" cx="300" cy="80" r="60" fill="rgba(139,92,246,0.2)" />
                </svg>

                <svg className="bg-shape bg-shape-2 absolute inset-0 w-full h-full" viewBox="0 0 400 400" fill="none">
                  <path className="shape-element" d="M0 200 Q100 100, 200 200 T 400 200" stroke="rgba(99,102,241,0.3)" strokeWidth="60" fill="none" />
                </svg>

                <svg className="bg-shape bg-shape-3 absolute inset-0 w-full h-full" viewBox="0 0 400 400" fill="none">
                  <circle className="shape-element" cx="50" cy="50" r="8" fill="rgba(99,102,241,0.4)" />
                  <circle className="shape-element" cx="150" cy="150" r="12" fill="rgba(236,72,153,0.35)" />
                </svg>

                <svg className="bg-shape bg-shape-4 absolute inset-0 w-full h-full" viewBox="0 0 400 400" fill="none">
                  <path className="shape-element" d="M100 100 Q150 50, 200 100 Q250 150, 200 200 Q150 250, 100 200 Q50 150, 100 100" fill="rgba(99,102,241,0.2)" />
                </svg>

                <svg className="bg-shape bg-shape-5 absolute inset-0 w-full h-full" viewBox="0 0 400 400" fill="none">
                  <line className="shape-element" x1="0" y1="100" x2="300" y2="400" stroke="rgba(99,102,241,0.25)" strokeWidth="30" />
                </svg>
              </div>
            </div>

            {/* Menu Header */}
            <div className="relative z-10 pt-4 flex items-center justify-between border-b border-white/10 pb-4">
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <span className="text-lg font-bold text-white tracking-tight">Atlas Intelligence</span>
              </div>
              <button
                onClick={closeMenu}
                className="rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-white/80 hover:bg-white/10"
              >
                Close ✕
              </button>
            </div>

            {/* Menu Items List */}
            <div className="menu-content-wrapper relative z-10 py-8">
              <p className="text-[10px] uppercase font-mono text-primary tracking-widest mb-4">
                Platform Navigation
              </p>
              <ul className="menu-list space-y-5">
                <li className="menu-list-item" data-shape="1">
                  <a href="#home" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    01. Overview & Home
                  </a>
                </li>
                <li className="menu-list-item" data-shape="2">
                  <a href="#how-it-works" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    02. How Atlas Works
                  </a>
                </li>
                <li className="menu-list-item" data-shape="3">
                  <a href="#advisor" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    03. AI Resume Advisor
                  </a>
                </li>
                <li className="menu-list-item" data-shape="4">
                  <a href="#jobs" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    04. Matched Internships
                  </a>
                </li>
                <li className="menu-list-item" data-shape="5">
                  <a href="#scholarships" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    05. Scholarships & Aid
                  </a>
                </li>
                <li className="menu-list-item" data-shape="1">
                  <a href="#discounts" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    06. Student Deals & Perks
                  </a>
                </li>
                <li className="menu-list-item" data-shape="2">
                  <a href="#housing" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    07. Campus Housing & PGs
                  </a>
                </li>
                <li className="menu-list-item" data-shape="3">
                  <a href="#attendance" onClick={closeMenu} className="nav-link text-2xl sm:text-3xl font-extrabold text-white hover:text-primary transition-all">
                    08. Attendance Risk (Level 2)
                  </a>
                </li>
              </ul>
            </div>

            {/* Menu Footer Student Session */}
            <div className="relative z-10 pt-4 border-t border-white/10 text-xs text-white/70 space-y-2">
              {isLevel1Authenticated ? (
                <div className="flex items-center justify-between">
                  <span className="truncate">Verified: {user?.email} ({user?.stream})</span>
                  {!isLevel2Authenticated && (
                    <button
                      onClick={() => {
                        closeMenu();
                        setKpModalOpen(true);
                      }}
                      className="text-primary font-semibold hover:underline flex items-center gap-1"
                    >
                      <KeyRound className="h-3.5 w-3.5" /> Connect KP Portal
                    </button>
                  )}
                </div>
              ) : (
                <p>Guest Session — Log in to save recommendations</p>
              )}
            </div>
          </nav>
        </div>
      </section>

      <StudentAuthModal
        isOpen={kpModalOpen}
        onClose={() => setKpModalOpen(false)}
        onSuccess={() => {}}
      />
    </div>
  );
}

export default SterlingGateKineticNavigation;
