import React from 'react';
import { SectionHeading } from './SectionHeading';
import { cn } from '~/lib/utils';
import { ScrollFadeIn } from './ScrollFadeIn'; // Import animation component

const steps = [
  { number: "01", text: "Create profile → pick goals" },
  { number: "02", text: "Hit “Run My Search” → auto‑apply queue spins" },
  { number: "03", text: "Open dashboard → watch interviews roll in" },
];

export function HowItWorksSection() {
  return (
    <section className="bg-grey-5 py-16 md:py-24 min-h-[80vh] flex flex-col justify-center"> {/* Changed to grey-5 background, 80vh min-height */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Simplicity"
          title="Get Started in 3 Easy Steps"
          className="mb-12 md:mb-16"
        />

        {/* Wrap the steps container in ScrollFadeIn */}
        <ScrollFadeIn className="flex justify-center">
          <div className="relative flex flex-col items-start space-y-8 md:space-y-12">
            {/* Vertical Connector Line */}
            <div className="absolute left-6 top-8 bottom-8 w-1 bg-grey-20 rounded-full md:left-8" aria-hidden="true"></div>

            {steps.map((step, index) => (
              <div key={step.number} className="relative flex items-center space-x-6 md:space-x-8 pl-16 md:pl-20">
                {/* Number Circle */}
                <div className="z-10 flex h-12 w-12 items-center justify-center rounded-full bg-primary-500 text-white font-bold text-lg flex-shrink-0 md:h-16 md:w-16 md:text-xl">
                  {step.number}
                </div>
                {/* Step Text */}
                <p className="text-lg font-medium text-grey-90 md:text-xl">
                  {step.text}
                </p>
              </div>
            ))}
          </div>
        </ScrollFadeIn>
      </div>
    </section>
  );
}
