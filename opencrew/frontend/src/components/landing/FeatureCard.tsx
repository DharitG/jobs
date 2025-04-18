import React from 'react';
import { cn } from '~/lib/utils';
import type { LucideIcon } from 'lucide-react'; // Import type for icon component
import { Badge } from '~/components/ui/badge'; // Import Badge component

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  badge?: string; // Add optional badge prop
  className?: string;
}

export function FeatureCard({ icon: Icon, title, description, badge, className }: FeatureCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center rounded-design-md border border-grey-20 bg-white p-6 text-center shadow-1 transition-all duration-200 ease-out hover:-translate-y-1 hover:shadow-lg", // Base card styles + hover effect
        className
      )}
    >
      {/* Badge (Optional) - Positioned top-right */}
      {badge && (
        <Badge variant="outline" className="absolute top-3 right-3">
          {badge}
        </Badge>
      )}
      {/* Icon in circle */}
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary-500/10">
        <Icon className="h-6 w-6 text-primary-500" />
      </div>
      {/* Title (h3) */}
      <h3 className="mb-2 font-display text-lg font-semibold text-grey-90">
        {title}
      </h3>
      {/* 2-line body */}
      <p className="text-sm text-grey-40 leading-relaxed line-clamp-2"> {/* Use line-clamp for 2 lines */}
        {description}
      </p>
    </div>
  );
}
