"use client";

import React from 'react';
import Image from 'next/image'; // Import Next.js Image component
// @ts-ignore - No readily available types for this package
import Marquee from "react-fast-marquee";
import { cn } from '~/lib/utils';

// Define the logos with their paths and alt text
const logos = [
  { src: '/logos/Google_2015_logo.svg.png', alt: 'Google Logo' },
  { src: '/logos/256577725_612381820192785_1516860531882870200_n.jpg', alt: 'Meta Logo' },
  { src: '/logos/Amazon-Logo.png', alt: 'Amazon Logo' },
  { src: '/logos/pasted-image-0-7.png', alt: 'Microsoft Logo' }, // Assuming this is Microsoft
  { src: '/logos/apple_logo_black.svg_.png', alt: 'Apple Logo' },
  { src: '/logos/Netflix-2016-300x200.webp', alt: 'Netflix Logo' },
  { src: '/logos/salesforce.svg', alt: 'Salesforce Logo' },
  { src: '/logos/McKinsey-Logo.png', alt: 'McKinsey Logo' },
  { src: '/logos/Logo-4.png', alt: 'BCG Logo' }, // Assuming this is BCG
  { src: '/logos/JPMorgan-Chase-Logo-SVG-desktop.jpg', alt: 'JPMorgan Chase Logo' },
];

export function TrustBar() {
  return (
    <section className="bg-grey-5 py-8 md:py-12 overflow-hidden"> {/* Use grey-5 background */}
      <div className="container mx-auto px-4">
        {/* Optional: Add a subtle heading */}
        {/* <p className="text-center text-sm font-medium text-grey-40 mb-6">
          Trusted by engineers from leading companies
        </p> */}
        <Marquee gradient={false} speed={50}>
          {logos.map((logo, index) => (
            <div
              key={index}
              className={cn(
                "mx-8 flex h-10 items-center justify-center px-4", // Maintain centering and padding
                "transition-opacity duration-200 hover:opacity-100 opacity-60", // Keep hover effect
                "relative w-32" // Set width (approx 128px) and relative positioning for Image
              )}
            >
              <Image
                src={logo.src}
                alt={logo.alt}
                layout="fill" // Fill the container div
                objectFit="contain" // Scale down to fit while maintaining aspect ratio
                className="grayscale" // Optional: make logos grayscale for uniformity
              />
            </div>
          ))}
        </Marquee>
      </div>
    </section>
  );
}
