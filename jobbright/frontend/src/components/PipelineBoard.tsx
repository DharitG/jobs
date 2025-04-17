'use client';

import React, { useState, useCallback } from 'react';
import { JobCard } from './JobCard'; // Import JobCard
import { api } from '~/trpc/react'; // Import tRPC hook
import { useToast } from '~/hooks/use-toast'; // Import useToast hook
import {
  DndContext,
  closestCenter, // Or closestCorners, rectIntersection
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import type {
  DragEndEvent,
  DragOverEvent,
  DragStartEvent,
} from '@dnd-kit/core'; // Fix: Use type-only imports
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy, // Strategy for items within a column
  rectSortingStrategy,       // Strategy for columns themselves (if needed)
  arrayMove,
} from '@dnd-kit/sortable';

// Define stages for columns (can be imported from a shared types file later)
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';
const pipelineStages: ApplicationStage[] = ['Applied', 'Screening', 'Interview', 'Offer']; // Exclude Rejected from main columns?

// Define the structure of an application item (adjust as needed)
interface ApplicationItem {
  id: string | number;
  companyName: string;
  jobTitle: string;
  location?: string | null; // Allow null
  stage: ApplicationStage;
  logoUrl?: string;
  ctaLink?: string;
}

// Define props for the PipelineBoard
interface PipelineBoardProps {
  initialApplications: ApplicationItem[]; // Rename prop for clarity
}

// Helper component for each column (makes managing sortable context easier)
function PipelineColumn({ stage, applications }: { stage: ApplicationStage, applications: ApplicationItem[] }) {
  return (
    <div className="flex-shrink-0 w-72 bg-grey-05 rounded-design-md shadow-sm"> {/* Use design radius */}
      {/* Sticky Header */}
      <div className="sticky top-0 z-10 p-3 bg-grey-05 rounded-t-design-md border-b border-grey-20 shadow-sm"> {/* Use design radius */}
        <h3 className="text-sm font-semibold text-grey-90 flex justify-between items-center">
          <span>{stage}</span>
          <span className="text-xs font-normal bg-grey-20 text-grey-90 rounded-full px-2 py-0.5">
            {applications.length}
          </span>
        </h3>
      </div>

      {/* Sortable Context for items within this column */}
      <SortableContext 
        items={applications.map(app => app.id)} 
        strategy={verticalListSortingStrategy}
      >
        <div className="p-3 space-y-3 h-[calc(100vh-12rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-grey-40 scrollbar-track-grey-20/50"> 
          {applications.length > 0 ? (
            applications.map(app => (
              <JobCard 
                key={app.id} 
                id={app.id}
                companyName={app.companyName} 
                jobTitle={app.jobTitle} 
                location={app.location}
                logoUrl={app.logoUrl}
                ctaLink={app.ctaLink} 
                ctaText="Details"
              />
            ))
          ) : (
            <div className="text-center text-sm text-grey-40 py-4">
              Drop jobs here
            </div>
          )}
        </div>
      </SortableContext>
    </div>
  );
}

export function PipelineBoard({ initialApplications }: PipelineBoardProps) {
  const [applications, setApplications] = useState<ApplicationItem[]>(initialApplications);
  const [activeId, setActiveId] = useState<string | number | null>(null); // Track the currently dragged item
  const utils = api.useUtils(); // Get tRPC utils for cache invalidation
  const { toast } = useToast(); // Get toast function

  // --- tRPC Mutation ---
  const updateStatusMutation = api.application.updateStatus.useMutation({
    // Add 'variables' as the second argument to onSuccess
    onSuccess: (updatedAppData, variables) => { 
      // Optional: Update the specific item in the cache for faster UI update
      // utils.application.list.setData(undefined, (oldData) => ... ); 
      // Or simply invalidate the list query to refetch
      utils.application.list.invalidate();
      console.log('Application status updated successfully via mutation:', updatedAppData);
      toast({
        title: "Status Updated",
        description: `Moved job to ${variables.newStatus}.`, // Use variables from mutation input
        variant: "default", // Or a custom success variant if defined
      });
    },
    onError: (error, variables) => {
      console.error('Failed to update application status:', error);
      toast({
        title: "Update Failed",
        description: error.message || "Could not update application status.",
        variant: "destructive",
      });
      // --- Revert Optimistic Update ---
      // Find the original stage of the item before the optimistic update
      const originalItem = initialApplications.find(app => app.id === variables.applicationId);
      if (originalItem) {
        setApplications(prev => {
           const index = prev.findIndex(app => app.id === variables.applicationId);
           if (index !== -1) {
             const revertedApps = [...prev];
             // Ensure ID is preserved when reverting
             revertedApps[index] = { ...revertedApps[index]!, stage: originalItem.stage }; 
             // We might need to re-sort or re-position based on original order if needed
             return revertedApps; 
           }
           return prev;
        });
      } else {
         // Fallback: Invalidate cache to refetch correct state if original not found
         utils.application.list.invalidate();
      }
    },
  });

  // Group applications by stage for rendering columns
  const groupedApplications = pipelineStages.reduce((acc, stage) => {
    acc[stage] = applications.filter(app => app.stage === stage);
    return acc;
  }, {} as Record<ApplicationStage, ApplicationItem[]>);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const findContainer = useCallback((id: string | number): ApplicationStage | null => {
    for (const stage of pipelineStages) {
      if (groupedApplications[stage]?.some(app => app.id === id)) {
          return stage;
      }
    }
    return null;
  }, [groupedApplications]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id);
  }, []);

  // Handle dragging OVER a column (potential drop target)
  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event;
    const activeId = active.id;
    const overId = over?.id;

    if (!overId || activeId === overId) {
      return;
    }

    const activeContainer = findContainer(activeId);
    const overContainer = pipelineStages.includes(overId as ApplicationStage) 
                          ? overId as ApplicationStage 
                          : findContainer(overId);

    if (!activeContainer || !overContainer || activeContainer === overContainer) {
      return;
    }

    // --- Optimistic Update ---
    // Note: This happens BEFORE the mutation call in handleDragEnd
    // We will revert this in the mutation's onError handler if needed.
    setApplications((prev) => {
      const activeIndex = prev.findIndex((app) => app.id === activeId);
      if (activeIndex === -1) return prev;

      const updatedApps = [...prev];
      // Ensure the ID is carried over correctly when updating stage
      updatedApps[activeIndex] = { ...updatedApps[activeIndex]!, stage: overContainer }; 
      return updatedApps;
    });
  }, [findContainer]); // Ensure findContainer is stable

  // Handle drag END (finalize position)
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeContainer = findContainer(active.id);
    const overContainer = pipelineStages.includes(over.id as ApplicationStage) 
                          ? over.id as ApplicationStage 
                          : findContainer(over.id);

    if (!activeContainer || !overContainer) return;
    
    const activeIndex = applications.findIndex((app) => app.id === active.id);
    if (activeIndex === -1) return; // Item not found
    
    const activeItem = { ...applications[activeIndex]! }; // Get a non-null copy

    if (activeContainer === overContainer) {
      // Reordering within the same container
      const overIndex = applications.findIndex((app) => app.id === over.id);
      if (activeIndex !== overIndex && overIndex !== -1) {
        setApplications((items) => arrayMove(items, activeIndex, overIndex));
      }
    } else {
      // Moving to a different container
      setApplications((items) => {
        const itemsInNewContainer = items.filter(i => i.stage === overContainer && i.id !== active.id);
        const overIsItem = !pipelineStages.includes(over.id as ApplicationStage);
        let targetIndex = itemsInNewContainer.length; // Default to end

        if (overIsItem) {
          const visualOverIndex = itemsInNewContainer.findIndex(i => i.id === over.id);
          if (visualOverIndex !== -1) {
            targetIndex = visualOverIndex;
          }
        }

        // Calculate the actual index in the full list where the item should be inserted
        let insertAtIndex = items.length; // Default to end of whole list
        let itemsBeforeTarget = 0;
        let itemsInTargetCount = 0;
        for(let i=0; i < items.length; i++) {
            if (items[i]!.id === active.id) continue; // Skip the dragged item
            if (items[i]!.stage === overContainer) {
                 if (itemsInTargetCount === targetIndex) {
                    insertAtIndex = i;
                    break;
                 }
                 itemsInTargetCount++;
            } 
        }
        
        // Construct the new array
        const newItems = items.filter(i => i.id !== active.id);
        return [
          ...newItems.slice(0, insertAtIndex),
          { ...activeItem, stage: overContainer }, // Ensure id is preserved
          ...newItems.slice(insertAtIndex),
        ];
      });

      // --- Persist Change via tRPC Mutation ---
      // Only call mutation if stage actually changed
      if (activeContainer !== overContainer) {
        // Ensure ID is a number if required by the backend/mutation schema
        const numericId = typeof active.id === 'string' ? parseInt(active.id, 10) : active.id; 
        if (!isNaN(numericId)) {
           updateStatusMutation.mutate({
             applicationId: numericId,
             newStatus: overContainer, // The stage of the column dropped onto
           });
         } else {
            console.error("Invalid application ID for mutation:", active.id);
            toast({
              title: "Update Failed",
              description: "Invalid application ID.",
              variant: "destructive",
            });
         }
       }
     }
   }, [applications, findContainer, updateStatusMutation, initialApplications, utils, toast]); // Add toast to dependency array

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter} // Adjust collision strategy as needed
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-grey-40 scrollbar-track-grey-20">
        {pipelineStages.map(stage => (
           // Pass stage id to make column itself a droppable container
          <PipelineColumn key={stage} stage={stage} applications={groupedApplications[stage] || []} />
        ))}
      </div>
       {/* Consider adding DragOverlay for smoother visuals */} 
       {/* <DragOverlay>{activeId ? <JobCard ... /> : null}</DragOverlay> */} 
    </DndContext>
  );
}
