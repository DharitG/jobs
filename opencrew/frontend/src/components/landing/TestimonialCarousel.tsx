"use client";

import React, { useState, useEffect } from 'react';
import { useInView } from 'react-intersection-observer';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import { SectionHeading } from './SectionHeading';
import { TestimonialCard } from './TestimonialCard';
import { cn } from '~/lib/utils';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

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
  const { ref, inView } = useInView({
    triggerOnce: true, // Only trigger once when it comes into view
    threshold: 0.1, // Trigger when 10% of the component is visible
  });

  const [hasBeenViewed, setHasBeenViewed] = useState(false);

  useEffect(() => {
    if (inView) {
      setHasBeenViewed(true);
    }
  }, [inView]);

  return (
    <section ref={ref} className="bg-grey-5 py-16 md:py-24 overflow-hidden"> {/* Grey background */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Real Results"
          title="Don't Just Take Our Word For It"
          className="mb-12 md:mb-16"
        />

        {/* Conditional Rendering for Lazy Loading */}
        {hasBeenViewed ? (
          <Swiper
            modules={[Navigation, Pagination, Autoplay]}
            spaceBetween={30} // Space between slides
            slidesPerView={1} // Default slides per view
            loop={true}
            autoplay={{
              delay: 5000, // Autoplay delay
              disableOnInteraction: true,
            }}
            pagination={{ clickable: true }}
            navigation={true}
            breakpoints={{
              // Responsive breakpoints
              768: { // md
                slidesPerView: 2,
                spaceBetween: 40,
              },
              1024: { // lg
                slidesPerView: 3,
                spaceBetween: 50,
              },
            }}
            className="pb-12" // Add padding bottom for pagination
          >
            {testimonials.map((testimonial, index) => (
              <SwiperSlide key={index} className="h-auto pb-4"> {/* Ensure slides have height auto */}
                <TestimonialCard {...testimonial} className="h-full" /> {/* Pass props and ensure full height */}
              </SwiperSlide>
            ))}
          </Swiper>
        ) : (
          // Placeholder while loading or not in view
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-[300px] bg-white rounded-design-md shadow-1 animate-pulse"></div> // Simple pulse placeholder
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
