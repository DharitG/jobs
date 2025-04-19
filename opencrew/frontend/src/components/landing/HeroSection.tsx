"use client"; // Required for framer-motion and potentially button onClick handlers

"use client"; // Required for framer-motion and potentially button onClick handlers

import React from 'react'; // Keep React import
import { Button } from '~/components/ui/button';
import { cn } from '~/lib/utils';
import { motion } from 'framer-motion'; // Import motion
// Removed VideoModal import
import HeroVideoDialog from '~/components/magicui/hero-video-dialog'; // Import the new component

export function HeroSection() {
  // Removed modal state and handlers

  const scrollToPricing = () => {
    const pricingSection = document.getElementById('pricing');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      // Replaced bg-grey-5 and inline style with gradient classes, removed top padding (pt-20 md:pt-24)
      className="relative flex min-h-[85vh] items-center showcase-gradient" // Replaced gradient classes with showcase-gradient
    >
      {/* Removed Masking overlay div */}

      {/* Removed relative z-10 from content container, Added pt-[72px] to compensate for negative margin on main */}
      <div className="container mx-auto grid grid-cols-1 items-center gap-12 px-4 pt-[72px] md:grid-cols-2 lg:gap-20">
        {/* Column L: Text Content */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="text-center md:text-left" // This div gets wrapped
        >
          <h1 className="font-display text-5xl font-bold leading-tight text-grey-90">
            Stop applying. <br /> Start interviewing.
          </h1>
          <p className="mt-4 max-w-lg text-xl text-grey-40 md:mx-0 mx-auto">
            50 tailored applications in the next hour—while you grab coffee.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row justify-center md:justify-start gap-3">
            <Button variant="default" size="lg" onClick={scrollToPricing}>
              Get Started Free
            </Button>
            {/* Removed the separate "Watch Demo" button as the video dialog is clickable */}
          </div>
        </motion.div> {/* Closing tag for left column motion.div */}

        {/* Column R: Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut", delay: 0.1 }} // Add slight delay
          className="flex justify-center" // This div gets wrapped
        >
          {/* Replace the old video div with HeroVideoDialog */}
          <HeroVideoDialog
            className="w-full max-w-[640px]" // Apply max width
            // Use placeholder paths from the old video element
            // NOTE: The new component expects a full video URL (e.g., YouTube embed) for the modal
            // Using the placeholder MP4 for now, but this might need adjustment for iframe usage
            videoSrc="/placeholder-pipeline-animation.mp4" // Placeholder path for modal video
            thumbnailSrc="/placeholder-poster.jpg" // Placeholder path for thumbnail
            thumbnailAlt="OpenCrew Pipeline Animation"
            animationStyle="from-center" // Example animation style
          />
        </motion.div> {/* Closing tag for right column motion.div */}
      </div>

      {/* Removed VideoModal rendering */}

      {/* Optional: Add subtle SVG spark illustration absolutely positioned */}
      {/* <img src="/spark.svg" alt="" className="absolute bottom-0 right-0 w-32 h-32 opacity-50" /> */}
    </section>
  );
}
