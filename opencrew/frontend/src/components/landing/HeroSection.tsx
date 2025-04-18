"use client"; // Required for framer-motion and potentially button onClick handlers

"use client"; // Required for framer-motion and potentially button onClick handlers

import React from 'react';
import { Button } from '~/components/ui/button';
import { cn } from '~/lib/utils';
import { motion } from 'framer-motion'; // Import motion
import { VideoModal } from './VideoModal'; // Import the modal component

export function HeroSection() {
  // Placeholder state and handler for modal
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const scrollToPricing = () => {
    const pricingSection = document.getElementById('pricing');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      // Replaced bg-grey-5 and inline style with gradient classes, removed top padding (pt-20 md:pt-24)
      className="relative flex min-h-[85vh] items-center bg-gradient-to-r from-primary-500 to-accent" // Removed pt-20 md:pt-24
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
            <Button variant="ghost" size="lg" onClick={openModal}>
              Watch 90-sec Demo
            </Button>
          </div>
        </motion.div> {/* Closing tag for left column motion.div */}

        {/* Column R: Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut", delay: 0.1 }} // Add slight delay
          className="flex justify-center" // This div gets wrapped
        >
          {/* Mockup card with video */}
          {/* Added padding p-4 to the container, reverted video classes */}
          <div className="relative w-full max-w-[640px] aspect-[640/420] rounded-design-md shadow-1 ring-1 ring-primary-500/10 overflow-hidden p-4 bg-white dark:bg-black"> {/* Added padding and explicit background */}
            {/* Replace with actual video source */}
            <video
              className="absolute inset-0 h-full w-full object-contain" // Reverted to inset-0, h/w-full, object-contain
              src="/placeholder-pipeline-animation.mp4" // Placeholder path
              autoPlay
              loop
              muted
              playsInline
              poster="/placeholder-poster.jpg" // Optional poster image
            >
              Your browser does not support the video tag.
            </video>
            {/* Optional: Add a subtle overlay or play button if needed */}
          </div>
        </motion.div> {/* Closing tag for right column motion.div */}
      </div>

      {/* Render Video Modal */}
      <VideoModal
        isOpen={isModalOpen}
        onClose={closeModal}
        videoSrc="/placeholder-demo-video.mp4" // Replace with actual demo video path
      />

      {/* Optional: Add subtle SVG spark illustration absolutely positioned */}
      {/* <img src="/spark.svg" alt="" className="absolute bottom-0 right-0 w-32 h-32 opacity-50" /> */}
    </section>
  );
}
