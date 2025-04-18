"use client";

import React, { useState, useEffect } from 'react'; // Import useState, useEffect
import { FileTextIcon } from "@radix-ui/react-icons";
import { Send, ShieldCheck, PencilRuler, GraduationCap } from "lucide-react"; // Using lucide-react icons
import { useTheme } from "next-themes"; // Import useTheme
import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid"; // Adjusted path
import { Particles } from "~/components/magicui/particles"; // Import Particles
import { SectionHeading } from './SectionHeading';
import { cn } from '~/lib/utils'; // Import cn

// Define OpenCrew features mapped to the new Bento Grid structure
const openCrewFeatures = [
  {
    Icon: Send,
    name: "1-Click Auto-Apply",
    description: "Submit 50+ tailored applications per hour across major job boards.",
    href: "#", // Update href as needed
    cta: "Learn more",
    background: <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-indigo-100 to-purple-100 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30 opacity-60"></div>, // Example background
    className: "lg:row-start-1 lg:row-end-4 lg:col-start-2 lg:col-end-3", // Tall middle column
  },
  {
    Icon: FileTextIcon, // Using Radix icon here
    name: "AI Resume Tailoring",
    description: "Automatically highlight relevant skills for each specific job description.",
    href: "#",
    cta: "Learn more",
    background: <div className="absolute inset-0 bg-gradient-to-br from-teal-100 via-cyan-100 to-sky-100 dark:from-teal-900/30 dark:via-cyan-900/30 dark:to-sky-900/30 opacity-60"></div>, // Example background
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-3", // Medium height, first column
  },
  {
    Icon: ShieldCheck,
    name: "Visa-Safe Filters",
    description: "Target jobs explicitly sponsoring H-1B, OPT, or Green Card.",
    href: "#",
    cta: "Learn more",
    background: <div className="absolute inset-0 bg-gradient-to-br from-green-100 via-lime-100 to-emerald-100 dark:from-green-900/30 dark:via-lime-900/30 dark:to-emerald-900/30 opacity-60"></div>, // Example background
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-3 lg:row-end-4", // Short, first column
  },
  {
    Icon: PencilRuler, // Icon for generation/crafting
    name: "GPT-4o Cover Letters",
    description: "Generate personalized cover letters that pass AI detection.",
    href: "#",
    cta: "Learn more",
    background: <div className="absolute inset-0 bg-gradient-to-br from-amber-100 via-orange-100 to-red-100 dark:from-amber-900/30 dark:via-orange-900/30 dark:to-red-900/30 opacity-60"></div>, // Example background
    className: "lg:col-start-3 lg:col-end-3 lg:row-start-1 lg:row-end-2", // Short, third column
  },
  {
    Icon: GraduationCap, // Icon for learning/prep
    name: "Interview Flash Cards",
    description: "Practice common interview questions tailored to the roles you apply for.",
    href: "#",
    cta: "Learn more",
    background: <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-100 via-pink-100 to-rose-100 dark:from-fuchsia-900/30 dark:via-pink-900/30 dark:to-rose-900/30 opacity-60"></div>, // Example background
    className: "lg:col-start-3 lg:col-end-3 lg:row-start-2 lg:row-end-4", // Medium height, third column
  },
];

export function WowFeaturesGrid() {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    // Add relative positioning for the absolute Particles component
    <section id="wow-features" className="relative py-16 md:py-24 bg-background overflow-hidden"> {/* Add relative and overflow-hidden */}
       <Particles
         className="absolute inset-0 -z-10" // Ensure it's behind content
         quantity={100}
         ease={80}
         color={color}
         refresh
       />
      <div className="container mx-auto px-4 relative z-10"> {/* Ensure content is above particles */}
        <SectionHeading
          badge="Differentiators"
          title="Why OpenCrew Wins"
          className="mb-12 md:mb-16"
        />

        {/* Render the new Bento Grid layout */}
        <BentoGrid className="lg:grid-rows-3"> {/* Apply the specific row layout */}
          {openCrewFeatures.map((feature) => (
            <BentoCard key={feature.name} {...feature} />
          ))}
        </BentoGrid>
      </div>
    </section>
  );
}
