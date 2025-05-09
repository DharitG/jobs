'use client';

import React from 'react';
import Image from 'next/image'; // Use Next.js Image for optimization
import { Button } from './ui/button'; // Assuming shadcn/ui button
import { Badge } from './ui/badge'; // Assuming shadcn/ui badge
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Define props for the JobCard
interface JobCardProps {
  id: string | number; // ID is required for dnd-kit
  logoUrl?: string; // Optional logo URL
  companyName: string;
  jobTitle: string;
  location?: string | null; // Allow null
  stage?: string; // Renamed from status for consistency
  ctaLink?: string; // Link for a Call To Action button
  ctaText?: string; // Text for CTA button, e.g., 'View Job', 'Apply'
}

// Placeholder logo if none provided
const defaultLogo = "/placeholder-logo.svg"; // You'll need to add a placeholder SVG

// Use React.forwardRef to allow ref passing from dnd-kit
export const JobCard = React.forwardRef<HTMLDivElement, JobCardProps>((
  { 
    id, // Destructure id
    logoUrl = defaultLogo, 
    companyName, 
    jobTitle, 
    location, 
    stage, // Use renamed prop
    ctaLink, 
    ctaText = 'View' 
  }, ref) => {

  const { 
    attributes,
    listeners,
    setNodeRef, 
    transform,
    transition,
    isDragging, // Can use this for styling while dragging
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1, // Example: make card semi-transparent while dragging
    zIndex: isDragging ? 10 : undefined, // Ensure dragged item is on top
  };

  // Design System: 3-col grid: logo 56x56, job meta, right-side CTA.
  // Hover → outline primary-500/20 + slight lift.
  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      {...attributes} 
      {...listeners} 
      className="group grid grid-cols-[auto_1fr_auto] items-center gap-4 p-4 border border-border rounded-design-md bg-card shadow-1 transition-all duration-150 ease-out hover:shadow-md hover:border-primary/20 hover:-translate-y-px touch-none" // Use theme classes: border-border, bg-card, hover:border-primary/20
    >
      {/* Column 1: Logo */}
      <div className="flex-shrink-0">
        <Image 
          src={logoUrl} 
          alt={`${companyName} logo`} 
          width={56} 
          height={56} 
          className="rounded-md object-contain border border-border" // Use theme class: border-border
          onError={(e) => (e.currentTarget.src = defaultLogo)} // Fallback
        />
      </div>
 
      {/* Column 2: Job Meta */}
      <div className="overflow-hidden">
        <p className="font-bold text-card-foreground truncate" title={companyName}>{companyName}</p> {/* Use theme class: text-card-foreground */}
        <p className="text-card-foreground truncate" title={jobTitle}>{jobTitle}</p> {/* Use theme class: text-card-foreground */}
        {location && <p className="text-sm text-muted-foreground truncate" title={location}>{location}</p>} {/* Use theme class: text-muted-foreground */}
      </div>

      {/* Column 3: Stage Badge & CTA */}
      <div className="flex flex-col items-end gap-2">
        {stage && (
          <Badge variant="outline" className="text-xs font-semibold uppercase tracking-wider">{stage}</Badge>
        )}
        {ctaLink && (
          <Button 
            variant="ghost" 
            size="sm" 
            asChild // Use asChild if linking with Next.js Link
            className="h-8 px-3" // Rely on ghost variant for colors
            // Prevent button click from triggering drag
            onClick={(e) => e.stopPropagation()} 
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
          >
            {/* If using Next Link: <Link href={ctaLink}>{ctaText}</Link> */}
             <a href={ctaLink} target="_blank" rel="noopener noreferrer">{ctaText}</a>
          </Button>
        )}
      </div>
    </div>
  );
});

// Add display name for better debugging
JobCard.displayName = 'JobCard';
