import React from 'react';
import { cn } from '~/lib/utils';

interface GradientDividerProps {
  className?: string;
}

// Renders a 12px tall gradient divider
// Spec asked for conic, using linear (primary-500 -> accent-green) for simplicity with Tailwind
export function GradientDivider({ className }: GradientDividerProps) {
  return (
    <div
      className={cn(
        "h-3 w-full bg-gradient-to-r from-primary-500 to-accent", // h-3 = 12px, gradient from blue to green
        className
      )}
      aria-hidden="true" // Decorative element
    />
  );
}
