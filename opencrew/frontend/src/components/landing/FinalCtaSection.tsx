"use client"; // Needed for button onClick handler

import React from 'react';
import { Button } from '~/components/ui/button';
import { useAuth0 } from "@auth0/auth0-react"; // To handle signup redirect
import { cn } from '~/lib/utils';

export function FinalCtaSection() {
  const { loginWithRedirect } = useAuth0();

  // Redirect to signup flow
  const handleGetStarted = () => loginWithRedirect({ authorizationParams: { screen_hint: "signup" } });

  return (
    <section
      className={cn(
        "flex items-center justify-center text-center",
        "bg-grey-90 text-white", // Dark background, white text
        "min-h-[45vh]" // Minimum height 45vh
      )}
    >
      <div className="container mx-auto px-4 py-16 md:py-20">
        <h2 className="mb-6 font-display text-3xl font-bold md:text-4xl">
          Ready to skip the job-search grind?
        </h2>
        <Button size="lg" onClick={handleGetStarted} className="mb-4">
          Get Started Free
        </Button>
        <p className="text-sm text-grey-40">
          Takes 2 minutes · No credit card required
        </p>
      </div>
    </section>
  );
}
