"use client"; // Add use client directive

import React from 'react';
import { SectionHeading } from './SectionHeading';
import { cn } from '~/lib/utils';
import { Grid, GridPattern } from '~/components/magicui/grid-pattern'; // Import the new grid components

// Combined and expanded feature list
const features = [
  {
    title: "Create Profile",
    description: "Import details from LinkedIn & set your job goals in minutes.",
  },
  {
    title: "Run Your Search",
    description: "Hit 'Go' and let the AI build your auto-apply queue based on your criteria.",
  },
  {
    title: "Track Progress",
    description: "Watch applications send and interviews roll in on your dashboard.",
  },
  {
    title: "Visa Filtering",
    description: "Instantly filter jobs by visa requirements (OPT, CPT, H-1B, etc.).",
  },
  {
    title: "AI Rewrites",
    description: "Get GPT-4o powered resume & cover letter rewrites tailored to each job.",
  },
  {
    title: "Interview Prep",
    description: "Use AI-generated flash cards based on job descriptions to prepare.",
  },
  {
    title: "Browser Extension",
    description: "Auto-fill applications on external sites with our Chrome extension.",
  },
  {
    title: "Priority Support",
    description: "Get help quickly via community forums or priority chat (Pro/Elite).",
  },
];

export function HowItWorksSection() {
  return (
    // Use styling similar to FeaturesSectionDemo example
    <section className="bg-white py-16 md:py-24"> {/* Adjusted padding */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="How It Works" // Updated badge
          title="Effortless Job Searching" // Updated title
          className="mb-12 md:mb-16"
        />

        {/* Grid layout based on FeaturesSectionDemo */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 md:gap-4 max-w-7xl mx-auto"> {/* Adjusted gap */}
          {features.map((feature) => (
            <div
              key={feature.title}
              // Apply styling from the example card
              className="relative bg-gradient-to-b dark:from-neutral-900 from-neutral-100 dark:to-neutral-950 to-white p-6 rounded-3xl overflow-hidden border border-neutral-200 dark:border-neutral-800" // Added border
            >
              {/* Use the Grid component for background pattern */}
              <Grid size={20} />
              {/* Feature Title */}
              <p className="text-base font-bold text-grey-90 dark:text-white relative z-20">
                {feature.title}
              </p>
              {/* Feature Description */}
              <p className="text-neutral-600 dark:text-neutral-400 mt-4 text-sm font-normal relative z-20"> {/* Adjusted text size */}
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
