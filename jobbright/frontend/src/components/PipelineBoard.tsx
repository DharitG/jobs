'use client';

import React, { useState, useCallback } from 'react';
import { JobCard } from './JobCard'; // Import JobCard
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
  location?: string;
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
    <div className="flex-shrink-0 w-72 bg-grey-05 rounded-md shadow-sm">
      {/* Sticky Header */}
      <div className="sticky top-0 z-10 p-3 bg-grey-05 rounded-t-md border-b border-grey-20 shadow-sm">
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

    // Optimistic update for visual feedback
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
    }
  }, [applications, findContainer]);

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