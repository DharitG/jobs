import React from 'react';
import { cn } from '~/lib/utils';

interface SectionHeadingProps {
  badge?: string;
  title: string;
  className?: string;
  titleClassName?: string;
  badgeClassName?: string;
}

export function SectionHeading({
  badge,
  title,
  className,
  titleClassName,
  badgeClassName,
}: SectionHeadingProps) {
  return (
    <div className={cn("flex flex-col items-center text-center", className)}>
      {badge && (
        <span
          className={cn(
            "mb-3 rounded-full bg-primary-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-primary-500",
            badgeClassName
          )}
        >
          {badge}
        </span>
      )}
      <h2
        className={cn(
          "font-display text-3xl font-bold leading-tight text-grey-90 md:text-4xl", // Adjusted size slightly from design system h2 for common use
          titleClassName
        )}
      >
        {title}
      </h2>
    </div>
  );
}
