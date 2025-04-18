import React from 'react';
import { SectionHeading } from './SectionHeading';
import { cn } from '~/lib/utils';
import { ScrollFadeIn } from './ScrollFadeIn'; // Import animation component
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "~/components/ui/card"; // Import Card components

const steps = [
  { number: "01", title: "Create Profile", description: "Import details & set your job goals." },
  { number: "02", title: "Run Your Search", description: "Hit 'Go' and let the auto-apply queue build." },
  { number: "03", title: "Watch Interviews Roll In", description: "Track progress on your dashboard." },
];

export function HowItWorksSection() {
  return (
    <section className="bg-grey-5 py-16 md:py-24"> {/* Removed min-height and flex centering */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Simplicity"
          title="Get Started in 3 Easy Steps"
          className="mb-12 md:mb-16"
        />

        {/* Grid layout for steps */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <ScrollFadeIn key={step.number} delay={index * 0.15}>
              <Card className="flex h-full flex-col text-center"> {/* Use Card, full height */}
                <CardHeader>
                  {/* Number Circle */}
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-500 text-white font-bold text-xl">
                    {step.number}
                  </div>
                  {/* Step Title */}
                  <CardTitle className="text-lg font-semibold text-grey-90">
                    {step.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Step Description */}
                  <p className="text-sm text-grey-40">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            </ScrollFadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
