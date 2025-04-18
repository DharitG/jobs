"use client";

import React, { useState } from 'react';
import { SectionHeading } from './SectionHeading';
import { PricingTierCard } from './PricingTierCard';
import { Switch } from '~/components/ui/switch'; // Import shadcn Switch
import { Label } from '~/components/ui/label'; // Import shadcn Label
import { cn } from '~/lib/utils';
import { ScrollFadeIn } from './ScrollFadeIn'; // Import animation component

// Define pricing tiers data (replace with actual data source)
const tiers = [
  {
    tierName: "Free",
    priceMonthly: 0,
    description: "Get started and land your first interviews.",
    features: [
      "50 Auto-applications / month",
      "Basic Visa Filtering (OPT/CPT)",
      "LinkedIn Profile Import",
      "Standard Job Matching",
      "Community Support",
    ],
    buttonText: "Start for Free",
    buttonVariant: "outline" as const, // Use outline for free tier
  },
  {
    tierName: "Pro",
    priceMonthly: 29,
    priceAnnual: 290, // Example annual price (12 * 29 * ~0.83 = ~290)
    description: "Accelerate your search with unlimited power.",
    features: [
      "Unlimited Auto-applications",
      "Advanced Visa Filtering (H-1B, etc.)",
      "GPT-4o Resume & Cover Letter Rewrites",
      "Interview Flash Cards (AI Q&A)",
      "Priority Support Chat Bot",
      "Browser Extension Auto-fill",
      "VisaPulse Lawyer Chat Access",
    ],
    buttonText: "Get Started with Pro",
    buttonVariant: "default" as const, // Use primary for paid tiers
    isFeatured: true, // Highlight Pro tier
  },
  {
    tierName: "Elite",
    priceMonthly: 99,
    priceAnnual: 990, // Example annual price
    description: "White-glove service for serious job seekers.",
    features: [
      "All Pro features, plus:",
      "Personal Success Coach",
      "Guaranteed 24h Résumé Review",
      "Custom Domain Email Alias",
      "Warm Intro Finder Access",
      "Stealth Mode Options",
      "Dedicated Account Manager",
    ],
    buttonText: "Go Elite",
    buttonVariant: "default" as const,
  },
];

export function PricingSection() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annually'>('monthly');

  const handleToggle = (checked: boolean) => {
    setBillingCycle(checked ? 'annually' : 'monthly');
  };

  return (
    <section id="pricing" className="bg-white py-16 md:py-24 min-h-[100vh] flex flex-col justify-center"> {/* White background, 100vh min-height */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Pricing"
          title="Choose Your Plan"
          className="mb-8 md:mb-10"
        />

        {/* Monthly/Annual Toggle */}
        <div className="flex items-center justify-center space-x-3 mb-12">
          <Label htmlFor="billing-cycle" className={cn("font-medium", billingCycle === 'monthly' ? 'text-primary-500' : 'text-grey-40')}>
            Monthly
          </Label>
          <Switch
            id="billing-cycle"
            checked={billingCycle === 'annually'}
            onCheckedChange={handleToggle}
            aria-label="Toggle billing cycle"
          />
          <Label htmlFor="billing-cycle" className={cn("font-medium", billingCycle === 'annually' ? 'text-primary-500' : 'text-grey-40')}>
            Annually <span className="text-xs text-accent">(Save ~17%)</span> {/* Example discount text */}
          </Label>
        </div>

        {/* Pricing Cards Grid */}
        {/* Wrap the grid container in ScrollFadeIn */}
        <ScrollFadeIn className="flex flex-col items-center justify-center gap-8 lg:flex-row lg:items-stretch">
          {tiers.map((tier, index) => (
            // Optionally add delay to each card
            <PricingTierCard
              key={tier.tierName}
              // delay={index * 0.1} // Add delay prop if desired
              {...tier}
              billingCycle={billingCycle}
            />
          ))}
        </ScrollFadeIn>

        {/* Microcopy */}
        <p className="mt-12 text-center text-sm text-grey-40">
          Cancel anytime • 30-day money-back guarantee
        </p>
      </div>
    </section>
  );
}
