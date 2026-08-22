import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

export function SterlingGateKineticNavigation() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

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
    <div ref={containerRef} className="relative z-40">
      <div className="site-header-wrapper">
        <header className="header py-4 px-6 flex items-center justify-between border-b bg-background/95 backdrop-blur">
          <div className="flex items-center gap-2">
            <a href="#" className="flex items-center gap-2 text-lg font-bold">
              <span className="text-primary">Atlas</span> Student Hub
            </a>
          </div>

          <div className="flex items-center gap-4">
            <div className="nav-toggle-label cursor-pointer text-xs font-mono uppercase tracking-wider text-muted-foreground hover:text-foreground" onClick={toggleMenu}>
              <span className="toggle-text">Explore Menu</span>
            </div>

            <button
              role="button"
              className="nav-close-btn flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold hover:bg-accent transition-colors"
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

      <section className="fullscreen-menu-container">
        <div data-nav="closed" className="nav-overlay-wrapper fixed inset-0 z-50 hidden">
          <div className="overlay absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeMenu}></div>
          <nav className="menu-content absolute right-0 top-0 bottom-0 w-full max-w-md bg-card border-l p-8 shadow-2xl overflow-y-auto">
            <div className="menu-content-wrapper space-y-6 pt-12">
              <p className="text-xs uppercase font-mono text-primary tracking-widest">Navigation</p>
              <ul className="menu-list space-y-4">
                <li className="menu-list-item" data-shape="1">
                  <a href="#home" onClick={closeMenu} className="nav-link text-2xl font-bold hover:text-primary transition-colors">
                    Overview & Home
                  </a>
                </li>
                <li className="menu-list-item" data-shape="2">
                  <a href="#how-it-works" onClick={closeMenu} className="nav-link text-2xl font-bold hover:text-primary transition-colors">
                    How Atlas Works
                  </a>
                </li>
                <li className="menu-list-item" data-shape="3">
                  <a href="#attendance" onClick={closeMenu} className="nav-link text-2xl font-bold hover:text-primary transition-colors">
                    Attendance Risk Calculator
                  </a>
                </li>
                <li className="menu-list-item" data-shape="4">
                  <a href="#advisor" onClick={closeMenu} className="nav-link text-2xl font-bold hover:text-primary transition-colors">
                    AI Resume Advisor
                  </a>
                </li>
                <li className="menu-list-item" data-shape="5">
                  <a href="#discounts" onClick={closeMenu} className="nav-link text-2xl font-bold hover:text-primary transition-colors">
                    Student Deals & Perks
                  </a>
                </li>
              </ul>
            </div>
          </nav>
        </div>
      </section>
    </div>
  );
}

export default SterlingGateKineticNavigation;
