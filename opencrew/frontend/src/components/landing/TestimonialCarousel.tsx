"use client";

import React from 'react';
import Autoplay from "embla-carousel-autoplay"; // Import autoplay plugin
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "~/components/ui/carousel"; // Import shadcn Carousel
import { SectionHeading } from './SectionHeading';
import { TestimonialCard } from './TestimonialCard';
import { cn } from '~/lib/utils';

// Sample Data (Replace with actual data source later)
const testimonials = [
  {
    avatarSrc: "/placeholder-avatar-1.jpg",
    quote: "OpenCrew completely changed my job search. I went from 2 applications a day to 50, and landed interviews within weeks!", // Updated name
    rating: 5,
    name: "Priya Sharma",
    position: "Software Engineer @ Meta",
    visaStatus: "H-1B" as const, // Use 'as const' for type safety
  },
  {
    avatarSrc: "/placeholder-avatar-2.jpg",
    quote: "As an international student on OPT, finding eligible jobs was a nightmare. OpenCrew's visa filter is a lifesaver.", // Updated name
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
    quote: "I was skeptical about auto-apply tools, but OpenCrew's quality and tailoring are impressive. Highly recommend.", // Updated name
    rating: 5,
    name: "Maria Garcia",
    position: "UX Designer @ Adobe",
    visaStatus: "Citizen" as const,
  },
];

export function TestimonialCarousel() {
  const plugin = React.useRef(
    Autoplay({ delay: 5000, stopOnInteraction: true, stopOnMouseEnter: true })
  );

  return (
    <section className="bg-grey-5 py-16 md:py-24 overflow-hidden"> {/* Grey background */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Real Results"
          title="Don't Just Take Our Word For It"
          className="mb-12 md:mb-16"
        />

        <Carousel
          plugins={[plugin.current]} // Use autoplay plugin
          opts={{
            align: "start",
            loop: true,
          }}
          className="w-full" // Carousel container
        >
          <CarouselContent className="-ml-4"> {/* Adjust margin for spacing */}
            {testimonials.map((testimonial, index) => (
              <CarouselItem key={index} className="pl-4 md:basis-1/2 lg:basis-1/3"> {/* Spacing and responsive basis */}
                <div className="p-1 h-full"> {/* Padding for item content */}
                  <TestimonialCard {...testimonial} className="h-full" /> {/* Ensure card takes full height */}
                </div>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious className="absolute left-[-50px] top-1/2 -translate-y-1/2 fill-black" /> {/* Position nav buttons */}
          <CarouselNext className="absolute right-[-50px] top-1/2 -translate-y-1/2 fill-black" />
        </Carousel>
      </div>
    </section>
  );
}
