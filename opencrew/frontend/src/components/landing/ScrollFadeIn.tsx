"use client";

import React from 'react';
import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { cn } from '~/lib/utils';

interface ScrollFadeInProps {
  children: React.ReactNode;
  className?: string;
  delay?: number; // Optional delay for staggered animations
  threshold?: number; // Optional threshold for triggering the animation
  triggerOnce?: boolean; // Optional: trigger animation only once
  yOffset?: number; // Optional vertical offset for the animation start
  duration?: number; // Optional duration for the animation
}

export function ScrollFadeIn({
  children,
  className,
  delay = 0,
  threshold = 0.15, // Default threshold
  triggerOnce = true,
  yOffset = 40, // Default y-offset
  duration = 0.4, // Default duration
}: ScrollFadeInProps) {
  const controls = useAnimation();
  const { ref, inView } = useInView({
    threshold: threshold,
    triggerOnce: triggerOnce,
  });

  React.useEffect(() => {
    if (inView) {
      controls.start('visible');
    } else if (!triggerOnce) {
      // Optional: Reset animation if triggerOnce is false and element scrolls out of view
      controls.start('hidden');
    }
  }, [controls, inView, triggerOnce]);

  const variants = {
    hidden: { opacity: 0, y: yOffset },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: duration,
        delay: delay,
        ease: 'easeOut', // Matches spec animation timing
      },
    },
  };

  return (
    <motion.div
      ref={ref}
      animate={controls}
      initial="hidden"
      variants={variants}
      className={cn(className)} // Apply className to the motion div
    >
      {children}
    </motion.div>
  );
}
