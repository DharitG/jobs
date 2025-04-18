'use client';

import React from 'react';
import { Badge } from '~/components/ui/badge';
import { Award, CheckCircle2 } from 'lucide-react'; // Example icons

interface MilestoneBadgeProps {
  title: string;
  achieved: boolean;
  icon?: 'award' | 'check'; // Optional icon type
  variant?: 'default' | 'secondary' | 'outline' | 'destructive'; // Badge variants
}

export function MilestoneBadge({ 
  title, 
  achieved, 
  icon = 'check', 
  variant = 'secondary' 
}: MilestoneBadgeProps) {

  const IconComponent = icon === 'award' ? Award : CheckCircle2;

  return (
    <Badge 
      variant={achieved ? 'default' : variant} // Use default variant when achieved
      className={`transition-opacity duration-300 ${achieved ? 'opacity-100' : 'opacity-50'}`}
    >
      <IconComponent 
        className={`mr-1 h-3 w-3 ${achieved ? 'text-accent' : ''}`} 
      />
      {title}
    </Badge>
  );
}

// Example Usage (would likely be driven by backend data/events):
// <MilestoneBadge title="First Application Sent" achieved={true} icon="award" />
// <MilestoneBadge title="10 Applications Sent" achieved={false} />
