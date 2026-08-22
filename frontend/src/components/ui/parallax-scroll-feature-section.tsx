'use client'

import { useRef } from "react"
import { motion, useScroll, useTransform } from 'framer-motion'
import { ArrowDown, Sparkles } from "lucide-react"

export const ParallaxScrollFeatureSection = () => {
    const sections = [
        {
            id: 1,
            title: "01. Knowledge Pro Attendance Calculus",
            description: "Direct integration with Christ University Knowledge Pro portal. Real-time class attendance tracking, risk margin warnings, and intelligent class simulator.",
            imageUrl: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80',
            reverse: false
        },
        {
            id: 2,
            title: "02. 3-Tier AI Career & Skill Advisor",
            description: "Powered by Groq LPU (llama-3.3-70b @ 500 tok/sec), local Ollama deepseek-r1, and TF-IDF vector search. Custom roadmap analysis for BTech, Psychology, BBA, and MBA.",
            imageUrl: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80',
            reverse: true
        },
        {
            id: 3,
            title: "03. Live WebCMD Housing, Scholarships & Deals",
            description: "Zero static buffer data. Real-time web scraping for student PGs near campus, Internshala postings, scholarships, and stream-based student discounts.",
            imageUrl: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80',
            reverse: false
        }
    ]

    const sectionRefs = sections.map(() => useRef(null));
    
    const scrollYProgress = sections.map((_, index) => {
        return useScroll({
            target: sectionRefs[index],
            offset: ["start end", "center start"]
        }).scrollYProgress;
    });

    const opacityContents = scrollYProgress.map(progress => 
        useTransform(progress, [0, 0.7], [0, 1])
    );
    
    const clipProgresses = scrollYProgress.map(progress => 
        useTransform(progress, [0, 0.7], ["inset(0 100% 0 0)", "inset(0 0% 0 0)"])
    );
    
    const translateContents = scrollYProgress.map(progress => 
        useTransform(progress, [0, 1], [-50, 0])
    );

  return (
    <div id="how-it-works" className="py-20 overflow-hidden">
      <div className='min-h-[40vh] flex flex-col items-center justify-center text-center px-4'>
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-xs font-semibold text-primary mb-4">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Platform Architecture & Flow</span>
        </div>
        <h2 className='text-3xl sm:text-5xl font-black max-w-3xl tracking-tight text-foreground'>
          HOW ATLAS WORKS
        </h2>
        <p className="mt-4 max-w-xl text-sm sm:text-base text-muted-foreground">
          Atlas bridges your student portal, academic performance, career roadmap, and student perks into one unified operating dashboard.
        </p>
        <p className='mt-8 flex items-center gap-2 text-xs font-mono tracking-widest text-primary uppercase'>
          SCROLL TO EXPLORE <ArrowDown size={14} className="animate-bounce" />
        </p>
      </div>

       <div className="flex flex-col md:px-0 px-6 max-w-6xl mx-auto space-y-24">
            {sections.map((section, index) => (
                <div 
                    key={section.id}
                    ref={sectionRefs[index]} 
                    className={`min-h-[60vh] flex flex-col md:flex-row items-center justify-center md:gap-20 gap-10 ${section.reverse ? 'md:flex-row-reverse' : ''}`}
                >
                    <motion.div style={{ y: translateContents[index] }} className="flex-1">
                        <div className="text-2xl sm:text-4xl font-black text-foreground">{section.title}</div>
                        <motion.p 
                            style={{ y: translateContents[index] }} 
                            className="text-muted-foreground text-sm sm:text-base mt-6 leading-relaxed max-w-md"
                        >
                            {section.description}
                        </motion.p>
                    </motion.div>
                    <motion.div 
                        style={{ clipPath: clipProgresses[index], opacity: opacityContents[index] }}
                        className="flex-1 w-full"
                    >
                        <div className="relative rounded-3xl overflow-hidden border border-border shadow-2xl group">
                            <img 
                                src={section.imageUrl} 
                                alt={section.title} 
                                className="w-full h-72 sm:h-96 object-cover transition-transform duration-700 group-hover:scale-105" 
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                        </div>
                    </motion.div>
                </div>
            ))}
        </div>
    </div>
  );
}

export default ParallaxScrollFeatureSection;
