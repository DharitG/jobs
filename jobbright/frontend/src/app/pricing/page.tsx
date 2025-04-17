'use client'; // Likely needs client-side interaction for toggles or buttons

import React, { useState } from 'react';
import { Button } from '~/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '~/components/ui/card';
import { Check } from 'lucide-react'; // Icon for feature lists
// import { Tabs, TabsList, TabsTrigger, TabsContent } from "~/components/ui/tabs"; // For Monthly/Annual toggle

// Define tier structures (expand with actual features and pricing)
const tiers = {
  monthly: [
    {
      name: 'Free',
      price: '$0',
      frequency: '/ month',
      description: 'Get started finding jobs.',
      features: [
        '50 Auto-applies / month',
        'Basic Job Matching',
        'VisaPulse (7-day history)',
        'Limited Resume Edits',
      ],
      cta: 'Current Plan',
      disabled: true,
    },
    {
      name: 'Pro',
      price: '$29',
      frequency: '/ month',
      description: 'Supercharge your job search.',
      features: [
        'Unlimited Auto-applies',
        'Advanced Job Matching',
        'GPT-4o Resume & Cover Letters',
        'Interview Flash Cards',
        'VisaPulse Lawyer Chat',
        'Priority Support',
      ],
      cta: 'Upgrade to Pro',
      disabled: false, // Enable based on user's current plan later
    },
    {
      name: 'Elite',
      price: '$99',
      frequency: '/ month',
      description: 'Personalized career acceleration.',
      features: [
        'All Pro features',
        'Personal Success Coach',
        'Guaranteed Resume Review (24h)',
        'Warm Intro Finder',
        'Custom Domain Email Alias',
      ],
      cta: 'Upgrade to Elite',
      disabled: false, // Enable based on user's current plan later
    },
  ],
  annual: [
     // TODO: Add annual pricing tiers with discounts
     {
      name: 'Free',
      price: '$0',
      frequency: '/ year',
      description: 'Get started finding jobs.',
      features: [
        '50 Auto-applies / month',
        'Basic Job Matching',
        'VisaPulse (7-day history)',
        'Limited Resume Edits',
      ],
      cta: 'Current Plan',
      disabled: true,
    },
     {
      name: 'Pro',
      price: '$290', // Example discount
      frequency: '/ year',
      description: 'Supercharge your job search.',
       features: [
        'Unlimited Auto-applies',
        'Advanced Job Matching',
        'GPT-4o Resume & Cover Letters',
        'Interview Flash Cards',
        'VisaPulse Lawyer Chat',
        'Priority Support',
      ],
      cta: 'Upgrade to Pro (Annual)',
      disabled: false, 
    },
     {
      name: 'Elite',
      price: '$990', // Example discount
      frequency: '/ year',
      description: 'Personalized career acceleration.',
       features: [
        'All Pro features',
        'Personal Success Coach',
        'Guaranteed Resume Review (24h)',
        'Warm Intro Finder',
        'Custom Domain Email Alias',
      ],
      cta: 'Upgrade to Elite (Annual)',
      disabled: false, 
    },
  ],
};

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const handleUpgradeClick = (tierName: string) => {
    console.log(`Upgrade button clicked for ${tierName} (${billingCycle})`);
    // TODO: Implement Stripe checkout logic here or redirect
  };

  const currentTiers = tiers[billingCycle];

  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-center mb-4 text-grey-90 font-display">
        Choose Your Plan
      </h1>
      <p className="text-center text-grey-40 mb-8 max-w-xl mx-auto">
        Select the plan that best fits your job search needs and career goals. Cancel anytime.
      </p>

      {/* TODO: Implement Monthly/Annual Toggle using Tabs */}
      {/* <Tabs defaultValue="monthly" onValueChange={(value) => setBillingCycle(value as 'monthly' | 'annual')} className="w-[400px] mx-auto mb-8">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="monthly">Monthly</TabsTrigger>
          <TabsTrigger value="annual">Annual (Save ~15%)</TabsTrigger>
        </TabsList>
      </Tabs> */}
       <div className="text-center mb-8">
         {/* Basic Toggle Placeholder */}
         <Button 
            variant={billingCycle === 'monthly' ? 'default' : 'outline'} 
            onClick={() => setBillingCycle('monthly')}
            className="mr-2"
          >
            Monthly
          </Button>
         <Button 
            variant={billingCycle === 'annual' ? 'default' : 'outline'} 
            onClick={() => setBillingCycle('annual')}
          >
            Annual (Save!)
          </Button>
       </div>


      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {currentTiers.map((tier) => (
          <Card key={tier.name} className={`flex flex-col ${tier.name === 'Pro' ? 'border-primary-500 border-2' : ''}`}>
            <CardHeader>
              <CardTitle className="font-display text-xl">{tier.name}</CardTitle>
              <CardDescription>{tier.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex-grow">
              <div className="mb-6">
                <span className="text-4xl font-bold text-grey-90">{tier.price}</span>
                <span className="text-sm text-grey-40">{tier.frequency}</span>
              </div>
              <ul className="space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center text-sm text-grey-90">
                    <Check className="h-4 w-4 mr-2 text-accent flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                variant={tier.name === 'Pro' ? 'default' : 'outline'} 
                disabled={tier.disabled}
                onClick={() => !tier.disabled && handleUpgradeClick(tier.name)}
              >
                {tier.cta}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* TODO: Add FAQ section */}
      {/* <div className="mt-16">
         <h2 className="text-2xl font-bold text-center mb-8 text-grey-90 font-display">Frequently Asked Questions</h2>
         <Accordion type="single" collapsible className="w-full max-w-2xl mx-auto">
            ... AccordionItems ...
         </Accordion>
      </div> */}
    </div>
  );
}
