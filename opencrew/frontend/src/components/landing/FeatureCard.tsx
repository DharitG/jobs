import React from 'react';
import { cn } from '~/lib/utils';
import type { LucideIcon } from 'lucide-react'; // Import type for icon component
import { Badge } from '~/components/ui/badge'; // Import Badge component
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "~/components/ui/card"; // Import Card components

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  badge?: string; // Add optional badge prop
  className?: string;
}

export function FeatureCard({ icon: Icon, title, description, badge, className }: FeatureCardProps) {
  return (
    <Card
      className={cn(
        "relative flex flex-col items-center text-center transition-all duration-200 ease-out hover:-translate-y-1 hover:shadow-lg", // Keep hover effect, remove redundant styles
        className
      )}
    >
      {/* Badge (Optional) - Positioned top-right relative to Card */}
      {badge && (
        <Badge variant="outline" className="absolute top-3 right-3">
          {badge}
        </Badge>
      )}
      <CardHeader className="items-center pb-4"> {/* Center header items, reduce bottom padding */}
        {/* Icon in circle */}
        <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-primary-500/10">
          <Icon className="h-6 w-6 text-primary-500" />
        </div>
        {/* Title */}
        <CardTitle className="font-display text-lg font-semibold text-grey-90">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Description */}
        <p className="text-sm text-grey-40 leading-relaxed line-clamp-2"> {/* Use line-clamp for 2 lines */}
          {description}
        </p>
      </CardContent>
    </Card>
  );
}
