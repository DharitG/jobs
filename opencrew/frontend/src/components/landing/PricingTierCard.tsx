import React from 'react';
import { Button } from '~/components/ui/button';
import { CheckListItem } from './CheckListItem'; // Re-use CheckListItem
import { cn } from '~/lib/utils';

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
    <div
      className={cn(
        "flex w-full max-w-[360px] flex-col rounded-design-md border border-grey-20 bg-white p-8 shadow-1", // Base styles, 360px width
        isFeatured ? "ring-2 ring-primary-500 ring-offset-2" : "", // Standout outline
        className
      )}
    >
      {/* Tier Name */}
      <h3 className="mb-2 font-display text-xl font-semibold text-grey-90">{tierName}</h3>
      {/* Description */}
      <p className="mb-6 text-sm text-grey-40">{description}</p>

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
      <ul className="space-y-3 text-left">
        {features.map((feature, index) => (
          <CheckListItem key={index}>{feature}</CheckListItem>
        ))}
      </ul>
    </div>
  );
}
