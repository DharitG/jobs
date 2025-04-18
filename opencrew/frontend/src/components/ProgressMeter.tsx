'use client';

import React from 'react';
import { cn } from '~/lib/utils'; // Import cn utility

// Define possible stages for type safety
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';

// Define props for the component
interface ProgressMeterProps {
  currentStage: ApplicationStage;
  className?: string; // Allow passing additional classes
}

const stages: ApplicationStage[] = ['Applied', 'Screening', 'Interview', 'Offer'];

// Helper function to get progress percentage
const getProgressPercentage = (stage: ApplicationStage): number => {
  if (stage === 'Rejected') {
    return 0; // Or handle differently if needed
  }
  const stageIndex = stages.indexOf(stage);
  if (stageIndex === -1) {
    return 0; // Default to 0 if stage not found (e.g., initial state)
  }
  // Calculate percentage based on completing the stage (e.g., 'Applied' means 25% done)
  return ((stageIndex + 1) / stages.length) * 100;
};

export function ProgressMeter({ currentStage, className }: ProgressMeterProps) {
  const percentage = getProgressPercentage(currentStage);

  // Design System: Horizontal bar, 4 segments (represented by width)
  // TODO: Visually represent the 4 distinct segments (Applied, Screening, Interview, Offer)
  // TODO: Implement animated gradient sweep on stage change as per design system
  // This might involve adding a specific class or using a style property for the gradient animation
  return (
    <div 
      className={cn(
        "relative w-full bg-grey-20 rounded-full h-2.5 overflow-hidden shadow-inner", // Added relative positioning
        className
      )} 
      title={`Current Stage: ${currentStage}`} // Add title for accessibility
    >
      {/* Segment dividers (visual representation) */}
      {/* These sit behind the main progress bar */}
      <div className="absolute top-0 bottom-0 left-1/4 w-px bg-white/50 z-0"></div>
      <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white/50 z-0"></div>
      <div className="absolute top-0 bottom-0 left-3/4 w-px bg-white/50 z-0"></div>

      {/* Main progress bar */}
      <div 
        className={cn(
          "absolute top-0 left-0 h-full rounded-full transition-all duration-500 ease-out z-10", // Added absolute positioning and z-index
          currentStage === 'Rejected' ? 'bg-error' : 'bg-primary-500', // Use error color if rejected
          // TODO: Add class for gradient sweep animation here, e.g., 'animate-gradient-sweep'
        )}
        style={{ width: `${percentage}%` }}
        data-testid="progress-bar-inner" // Added for testing
      />
    </div>
  );
}
