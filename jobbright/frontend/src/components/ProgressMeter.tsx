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
  return (
    <div 
      className={cn("w-full bg-grey-20 rounded-full h-2.5 overflow-hidden shadow-inner", className)} 
      title={`Current Stage: ${currentStage}`} // Add title for accessibility
    >
      <div 
        className={cn(
          "h-full rounded-full transition-all duration-500 ease-out",
          currentStage === 'Rejected' ? 'bg-error' : 'bg-primary-500' // Use error color if rejected
          // Add gradient sweep animation class here later if implemented
        )}
        style={{ width: `${percentage}%` }} 
      />
      {/* Removed segment mapping logic */}
      {/* Removed optional text labels */}
    </div>
  );
}
