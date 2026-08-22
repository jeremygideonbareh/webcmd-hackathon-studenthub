import {
  GraduationCap,
  Briefcase,
  Home,
  FileText,
  ArrowRight,
} from "lucide-react";

// Atlas services — the three core features of the platform
const services = [
  {
    title: "Attendance Radar",
    description:
      "Know exactly which classes you can skip and which you can't afford to miss.",
    href: "#attendance",
    icon: GraduationCap,
    image:
      "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=512&q=80",
  },
  {
    title: "Internship Matcher",
    description:
      "Find internships you're actually qualified for, ranked by your skills and GPA.",
    href: "#jobs",
    icon: Briefcase,
    image:
      "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=512&q=80",
  },
  {
    title: "Housing Finder",
    description:
      "Affordable living spaces near campus, matched to your budget.",
    href: "#housing",
    icon: Home,
    image:
      "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=512&q=80",
  },
  {
    title: "AI Resume Lab Analyzer",
    description:
      "AI resume feedback, ATS score analysis, and instant bullet optimization.",
    href: "https://resume-lab-one.vercel.app/",
    external: true,
    icon: FileText,
    image:
      "https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=512&q=80",
  },
];

export function ServicesSection() {
  return (
    <section
      id="services"
      aria-labelledby="services-heading"
      className="w-full px-4 py-16 sm:px-6 sm:py-20 lg:py-24"
    >
      <div className="mx-auto max-w-5xl">
        <div className="mb-12 text-center sm:mb-16">
          <h2 id="services-heading" className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            How Atlas helps you
          </h2>
          <p className="mt-3 text-lg font-light text-muted-foreground sm:text-xl">
            Three services, one unified student dashboard.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 lg:gap-6">
          {services.map((service) => (
            <a
              key={service.title}
              href={service.href}
              target={service.external ? "_blank" : undefined}
              rel={service.external ? "noreferrer" : undefined}
              className="group flex min-h-[44px] flex-col overflow-hidden rounded-3xl bg-muted/40 transition-all duration-300 hover:bg-muted/80 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label={`Explore ${service.title}`}
            >
              <div className="relative flex h-44 items-center justify-center overflow-hidden">
                <img
                  src={service.image}
                  alt={`${service.title} illustration`}
                  loading="lazy"
                  decoding="async"
                  className="absolute h-full w-full object-cover transition-transform duration-500 ease-in-out group-hover:scale-105"
                  onError={(e) => {
                    const t = e.currentTarget;
                    t.onerror = null;
                    t.src = `https://placehold.co/512x512/e2e8f0/4a5568?text=${encodeURIComponent(
                      service.title
                    )}`;
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                <service.icon className="relative h-10 w-10 text-white drop-shadow-md" aria-hidden="true" />
              </div>

              <div className="flex flex-1 flex-col p-5">
                <h3 className="text-lg font-semibold">{service.title}</h3>
                <p className="mt-2 flex-1 text-sm text-muted-foreground leading-relaxed">
                  {service.description}
                </p>
                <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
                  Explore Feature
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
                </span>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ServicesSection;
