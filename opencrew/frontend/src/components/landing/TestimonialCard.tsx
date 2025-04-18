import React from 'react';
import Image from 'next/image';
import { Badge } from '~/components/ui/badge'; // Keep Badge import
import { cn } from '~/lib/utils';

// Define the props interface (keep existing props)
interface TestimonialCardProps {
  avatarSrc: string;
  quote: string;
  rating: number; // Keep prop for data consistency, even if not displayed
  name: string;
  position: string;
  visaStatus?: 'H-1B' | 'OPT' | 'Green Card' | 'Citizen' | 'Other';
  className?: string;
}

// Adopt the structure and styling from ReviewCard example
export function TestimonialCard({
  avatarSrc,
  quote,
  // rating, // Rating is not displayed in this design
  name,
  position,
  visaStatus,
  className,
}: TestimonialCardProps) {
  return (
    <figure
      className={cn(
        // Base styles from ReviewCard example
        "relative h-full cursor-pointer overflow-hidden rounded-xl border p-4",
        // Light mode styles from ReviewCard
        "border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]",
        // Dark mode styles (assuming dark mode might be added later)
        "dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]",
        // Allow external classes to override/extend
        className,
      )}
    >
      {/* Header section with avatar and name/position */}
      <div className="flex flex-row items-center gap-2">
        <Image
          className="rounded-full"
          width={32} // Use smaller avatar size like ReviewCard
          height={32}
          alt={`${name} avatar`}
          src={avatarSrc}
        />
        <div className="flex flex-col">
          {/* Name */}
          <figcaption className="text-sm font-medium text-gray-900 dark:text-white">
            {name}
          </figcaption>
          {/* Position */}
          <p className="text-xs font-medium text-gray-600 dark:text-white/40">
            {position}
          </p>
          {/* Optional Visa Status Badge */}
          {visaStatus && (
            <Badge variant="outline" className="mt-1 text-xs w-fit"> {/* Make badge fit content */}
              {visaStatus}
            </Badge>
          )}
        </div>
      </div>
      {/* Quote */}
      <blockquote className="mt-2 text-sm text-gray-700 dark:text-gray-300">
        {quote} {/* Removed surrounding quotes for cleaner look */}
      </blockquote>
    </figure>
  );
}
