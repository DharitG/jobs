"use client";

import React, { useState, useEffect } from 'react'; // Import useState, useEffect
import { FileTextIcon } from "@radix-ui/react-icons";
import { Send, ShieldCheck, LayoutDashboard } from "lucide-react"; // Using lucide-react icons
import { useTheme } from "next-themes"; // Import useTheme

import { cn } from "~/lib/utils";
import AnimatedBeamMultipleOutputDemo from "~/components/examples/animated-beam-multiple-outputs"; // Adjusted path
import AnimatedListDemo from "~/components/examples/animated-list-demo"; // Adjusted path
import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid"; // Adjusted path
import { Marquee } from "~/components/magicui/marquee"; // Adjusted path
import { Particles } from "~/components/magicui/particles"; // Import Particles
import { SectionHeading } from './SectionHeading'; // Keep SectionHeading

// Define file types for Marquee background
const fileTypes = [
  { name: "Resume.pdf", body: "Your professional summary." },
  { name: "Profile.docx", body: "Detailed work history." },
  { name: "LinkedIn Import", body: "Quickly sync your profile." },
  { name: "CoverLetter.txt", body: "Tailored introductions." },
];

// Define OpenCrew features for Bento Grid
const openCrewFeatures = [
  {
    Icon: Send, // Use Send icon for auto-apply
    name: "1-Click Auto-Apply",
    description: "AI tailors your profile and submits applications automatically.",
    href: "#", // Link to feature details or signup
    cta: "Learn more",
    className: "col-span-3 lg:col-span-2", // Span 2 columns on large screens
    background: (
      <AnimatedListDemo className="absolute right-2 top-4 h-[300px] w-full scale-75 border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_100%)] group-hover:scale-90" />
    ),
  },
   {
    Icon: ShieldCheck, // Use ShieldCheck for visa safety
    name: "Visa-Safe Filters",
    description: "Focus only on jobs matching your visa sponsorship needs.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-1", // Span 1 column
    background: <div className="absolute inset-0 bg-gradient-to-br from-green-100 via-blue-100 to-purple-100 dark:from-green-900/30 dark:via-blue-900/30 dark:to-purple-900/30 opacity-50"></div>, // Simple gradient background
  },
  {
    Icon: FileTextIcon, // Use FileTextIcon for import
    name: "Instant Profile Import",
    description: "Import your LinkedIn profile or resume in seconds.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-1", // Span 1 column
    background: (
      <Marquee
        pauseOnHover
        className="absolute top-10 [--duration:20s] [mask-image:linear-gradient(to_top,transparent_40%,#000_100%)] "
      >
        {fileTypes.map((f, idx) => (
          <figure
            key={idx}
            className={cn(
              "relative w-32 cursor-pointer overflow-hidden rounded-xl border p-4",
              "border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]",
              "dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]",
              "transform-gpu blur-[1px] transition-all duration-300 ease-out hover:blur-none",
            )}
          >
            <div className="flex flex-row items-center gap-2">
              <div className="flex flex-col">
                <figcaption className="text-sm font-medium dark:text-white ">{f.name}</figcaption>
              </div>
            </div>
            <blockquote className="mt-2 text-xs">{f.body}</blockquote>
          </figure>
        ))}
      </Marquee>
    ),
  },
  {
    Icon: LayoutDashboard, // Use LayoutDashboard for matching/tracking
    name: "AI Matching & Dashboard",
    description: "Discover relevant jobs and track your pipeline effortlessly.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-2", // Span 2 columns
    background: (
      <AnimatedBeamMultipleOutputDemo className="absolute right-2 top-4 h-[300px] border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_100%)] group-hover:scale-105" />
    ),
  },
];

export function ProductTourSection() {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    // Keep the section ID and adjust padding/background as needed
    // Add relative positioning for the absolute Particles component
    <section id="product-tour" className="relative py-16 md:py-24 bg-background overflow-hidden"> {/* Add relative and overflow-hidden */}
       <Particles
         className="absolute inset-0 -z-10" // Ensure it's behind content
         quantity={100}
         ease={80}
         color={color}
         refresh
       />
      <div className="container mx-auto px-4 relative z-10"> {/* Ensure content is above particles */}
        <SectionHeading
          badge="Pipeline to Offer"
          title="See OpenCrew in Action"
          className="mb-12 md:mb-16"
        />

        {/* Render the Bento Grid */}
        <BentoGrid className="lg:grid-cols-3"> {/* Ensure 3 columns on large screens */}
          {openCrewFeatures.map((feature, idx) => (
            <BentoCard key={idx} {...feature} />
          ))}
        </BentoGrid>
      </div>
    </section>
  );
}
