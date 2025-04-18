import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '~/lib/utils';

interface CheckListItemProps {
  children: React.ReactNode;
  className?: string;
  iconClassName?: string;
}

export function CheckListItem({ children, className, iconClassName }: CheckListItemProps) {
  return (
    <li className={cn("flex items-start space-x-3", className)}>
      <Check
        className={cn(
          "mt-1 h-4 w-4 flex-shrink-0 text-primary-500", // Use primary color for check
          iconClassName
        )}
        aria-hidden="true"
      />
      <span className="text-sm text-grey-90">{children}</span> {/* Use grey-90 for text */}
    </li>
  );
}
