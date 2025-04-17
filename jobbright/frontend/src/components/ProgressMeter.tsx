'use client';

import React from 'react';

// Define possible stages for type safety
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';

// Define props for the component
interface ProgressMeterProps {
  currentStage: ApplicationStage;
  // Add other relevant props like job title, company, etc. if needed later
}

const stages: ApplicationStage[] = ['Applied', 'Screening', 'Interview', 'Offer'];

export function ProgressMeter({ currentStage }: ProgressMeterProps) {
  const currentStageIndex = stages.indexOf(currentStage);

  // Basic visual representation based on design_system.md
  // Horizontal bar, 4 segments
  return (
    <div className="w-full bg-grey-20 rounded-full h-2.5 dark:bg-gray-700 my-4 shadow-inner">
      <div className="flex h-full rounded-full">
        {stages.map((stage, index) => {
          const isCompleted = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          let bgColor = 'bg-grey-20'; // Default (inactive)
          let segmentWidth = 'w-1/4'; // Assuming 4 equal segments

          if (isCompleted) {
            bgColor = 'bg-primary-500'; // Completed stage
          } else if (isCurrent) {
            // Could add animation or different style for the current active stage
            // For now, same as completed
            bgColor = 'bg-primary-500'; 
            // Example: Animated gradient sweep (complex, add later if needed)
            // bgColor = 'bg-gradient-to-r from-primary-500 to-primary-600 animate-pulse'; 
          }
          
          // Add specific styling for rejected state if needed
          if (currentStage === 'Rejected' && index === 0) {
              bgColor = 'bg-error'; // Show error color if rejected
              // Potentially adjust width or add icon?
          }

          // Add rounding to first and last segments
          let borderRadius = '';
          if (index === 0) borderRadius = 'rounded-l-full';
          if (index === stages.length - 1) borderRadius = 'rounded-r-full';
          // Need to handle case where only one segment is filled (e.g., currentStageIndex = 0)
          if (currentStageIndex === 0 && index === 0) borderRadius = 'rounded-full';
          if (currentStageIndex > 0 && index === currentStageIndex) borderRadius = 'rounded-r-full';
          if (isCompleted && index === currentStageIndex -1 ) borderRadius = 'rounded-l-full';
          if (isCompleted && index < currentStageIndex -1) borderRadius = '';

          return (
            <div 
              key={stage}
              className={`${segmentWidth} ${bgColor} ${borderRadius} h-full transition-colors duration-500 ease-in-out flex items-center justify-center relative`} 
              title={stage}
            >
              {/* Optional: Add tiny dot or icon inside? */}
              {/* Keep it clean for now */}
            </div>
          );
        })}
      </div>
      {/* Optional: Add text labels below the bar */}
      {/* <div className="flex justify-between text-xs text-grey-40 mt-1">
        {stages.map(stage => <span key={stage}>{stage}</span>)}
      </div> */}
    </div>
  );
} 