"use client";

import React from 'react';
import { cn } from '~/lib/utils';
import { Marquee } from '~/components/magicui/marquee'; // Use the updated Marquee component
import { SectionHeading } from './SectionHeading';
import { TestimonialCard } from './TestimonialCard'; // Use the existing TestimonialCard

// Existing Testimonial Data
const testimonials = [
  {
    avatarSrc: "/placeholder-avatar-1.jpg",
    quote: "OpenCrew completely changed my job search. I went from 2 applications a day to 50, and landed interviews within weeks!",
    rating: 5,
    name: "Priya Sharma",
    position: "Software Engineer @ Meta",
    visaStatus: "H-1B" as const,
  },
  {
    avatarSrc: "/placeholder-avatar-2.jpg",
    quote: "As an international student on OPT, finding eligible jobs was a nightmare. OpenCrew's visa filter is a lifesaver.",
    rating: 5,
    name: "Chen Wei",
    position: "Data Scientist @ Netflix",
    visaStatus: "OPT" as const,
  },
  {
    avatarSrc: "/placeholder-avatar-3.jpg",
    quote: "The auto-apply feature saved me countless hours. I could focus on interview prep instead of filling out forms.",
    rating: 4,
    name: "Ahmed Khan",
    position: "Cloud Architect @ AWS",
    visaStatus: "Green Card" as const,
  },
   {
    avatarSrc: "/placeholder-avatar-4.jpg",
    quote: "I was skeptical about auto-apply tools, but OpenCrew's quality and tailoring are impressive. Highly recommend.",
    rating: 5,
    name: "Maria Garcia",
    position: "UX Designer @ Adobe",
    visaStatus: "Citizen" as const,
  },
  // Add more testimonials if needed to fill the marquee better, or rely on the repeat prop.
  // For demonstration, let's duplicate the first two for a total of 6
   {
    avatarSrc: "/placeholder-avatar-1.jpg", // Duplicate
    quote: "OpenCrew completely changed my job search. I went from 2 applications a day to 50, and landed interviews within weeks!",
    rating: 5,
    name: "Priya Sharma",
    position: "Software Engineer @ Meta",
    visaStatus: "H-1B" as const,
  },
  {
    avatarSrc: "/placeholder-avatar-2.jpg", // Duplicate
    quote: "As an international student on OPT, finding eligible jobs was a nightmare. OpenCrew's visa filter is a lifesaver.",
    rating: 5,
    name: "Chen Wei",
    position: "Data Scientist @ Netflix",
    visaStatus: "OPT" as const,
  },
];

// Split testimonials for two rows
const firstRow = testimonials.slice(0, Math.ceil(testimonials.length / 2));
const secondRow = testimonials.slice(Math.ceil(testimonials.length / 2));

export function TestimonialCarousel() {
  return (
    <section className="bg-grey-5 py-16 md:py-24 relative overflow-hidden"> {/* Added relative positioning */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Real Results"
          title="Don't Just Take Our Word For It"
          className="mb-12 md:mb-16"
        />
      </div>

      {/* Marquee Container */}
      {/* Using the structure from MarqueeDemo example */}
      <div className="relative flex w-full flex-col items-center justify-center overflow-hidden">
        <Marquee pauseOnHover className="[--duration:60s] [--gap:1rem]"> {/* Adjusted duration and gap */}
          {firstRow.map((testimonial, index) => (
            // Use existing TestimonialCard, apply width constraint
            <TestimonialCard key={`${testimonial.name}-${index}-1`} {...testimonial} className="w-80 md:w-96" /> // Added width
          ))}
        </Marquee>
        <Marquee reverse pauseOnHover className="[--duration:60s] [--gap:1rem]"> {/* Adjusted duration and gap */}
          {secondRow.map((testimonial, index) => (
            // Use existing TestimonialCard, apply width constraint
            <TestimonialCard key={`${testimonial.name}-${index}-2`} {...testimonial} className="w-80 md:w-96" /> // Added width
          ))}
        </Marquee>

        {/* Gradient Overlays for fade effect */}
        {/* Adjusted background color to match section bg */}
        <div className="pointer-events-none absolute inset-y-0 left-0 w-1/4 bg-gradient-to-r from-grey-5 to-transparent"></div>
        <div className="pointer-events-none absolute inset-y-0 right-0 w-1/4 bg-gradient-to-l from-grey-5 to-transparent"></div>
      </div>
    </section>
  );
}
