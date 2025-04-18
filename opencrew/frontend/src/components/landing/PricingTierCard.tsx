import React from 'react';
import { Button } from '~/components/ui/button';
import { CheckListItem } from './CheckListItem'; // Re-use CheckListItem
import { cn } from '~/lib/utils';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  // CardFooter // Optional: Could move button here
} from "~/components/ui/card";

interface PricingTierCardProps {
  tierName: string;
  priceMonthly: string | number;
  priceAnnual?: string | number; // Optional annual price
  description: string;
  features: string[];
  buttonText: string;
  buttonVariant: React.ComponentProps<typeof Button>['variant'];
  isFeatured?: boolean; // For the standout outline on "Pro"
  billingCycle: 'monthly' | 'annually'; // To display correct price
  className?: string;
}

export function PricingTierCard({
  tierName,
  priceMonthly,
  priceAnnual,
  description,
  features,
  buttonText,
  buttonVariant,
  isFeatured = false,
  billingCycle,
  className,
}: PricingTierCardProps) {

  const displayPrice = billingCycle === 'annually' && priceAnnual !== undefined
    ? priceAnnual
    : priceMonthly;

  const pricePeriod = billingCycle === 'annually' ? '/ year' : '/ month';
  const isFree = displayPrice === 0 || displayPrice === 'Free';

  return (
    <Card
      className={cn(
        "flex w-full max-w-[360px] flex-col", // Base styles, 360px width
        isFeatured ? "ring-2 ring-primary-500 ring-offset-2" : "", // Standout outline
        className
      )}
    >
      <CardHeader className="pb-4"> {/* Adjust padding */}
        {/* Tier Name */}
        <CardTitle className="mb-1 font-display text-xl font-semibold text-grey-90">{tierName}</CardTitle>
        {/* Description */}
        <CardDescription className="text-sm text-grey-40">{description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-grow flex-col"> {/* Allow content to grow */}
        {/* Price */}
        <div className="mb-6">
          <span className="text-4xl font-bold font-display text-grey-90">
            {isFree ? 'Free' : `$${displayPrice}`}
          </span>
          {!isFree && (
            <span className="ml-1 text-sm text-grey-40">{pricePeriod}</span>
          )}
        </div>

        {/* Action Button */}
        <Button variant={buttonVariant} className="w-full mb-8">
          {buttonText}
        </Button>

        {/* Features List */}
        <ul className="flex-grow space-y-3 text-left"> {/* Allow list to take remaining space */}
          {features.map((feature, index) => (
            <CheckListItem key={index}>{feature}</CheckListItem>
          ))}
        </ul>
      </CardContent>
      {/* Optional: Move Button to CardFooter if desired
      <CardFooter>
        <Button variant={buttonVariant} className="w-full">
          {buttonText}
        </Button>
      </CardFooter>
      */}
    </Card>
  );
}
