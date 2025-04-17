'use client';

import React from 'react';
import { Badge } from './ui/badge'; // Use Badge for status dots
import { Button } from './ui/button'; // Import Button component
import { api } from '~/trpc/react'; // Import tRPC hook
import { differenceInDays, parseISO, format } from 'date-fns'; // Import date-fns helpers

// Define potential visa status types (expand as needed)
type VisaStatus = 'Info' | 'Action Required' | 'Upcoming Deadline' | 'Submitted' | 'Approved' | 'Unknown';

// Define structure for a timeline item
interface VisaTimelineItem {
  id: string | number;
  date: string; // Or Date object
  title: string;
  description?: string;
  status: VisaStatus;
  // Add link or action if needed
}

// Define props for the VisaPulse component (historyLimitDays is now the only prop)
interface VisaPulseProps {
  historyLimitDays?: number; // e.g., 7 for free tier
}

// Helper to get color based on status
const getStatusColor = (status: VisaStatus): string => {
  switch (status) {
    case 'Info':
    case 'Submitted':
      return 'bg-primary-500'; // Use primary for info/submitted
    case 'Action Required':
    case 'Upcoming Deadline':
      return 'bg-warning'; // Use warning
    case 'Approved':
      return 'bg-accent'; // Use success/accent
    case 'Unknown':
    default:
      return 'bg-grey-40'; // Default grey
  }
};

export function VisaPulse({ historyLimitDays = 7 }: VisaPulseProps) {

  const { data: items, isLoading, error } = api.visa.listTimeline.useQuery();

  // --- Loading State ---
  if (isLoading) {
    return (
      <div className="p-4 border border-grey-20 rounded-md bg-white shadow-1 mt-6 animate-pulse">
        <div className="h-6 bg-grey-20 rounded w-3/4 mb-4"></div>
        <div className="space-y-4 ml-2 border-l border-grey-20 pl-8">
           <div className="h-4 bg-grey-20 rounded w-1/2"></div>
           <div className="h-4 bg-grey-20 rounded w-3/4"></div>
           <div className="h-4 bg-grey-20 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  // --- Error State ---
  if (error) {
     return (
      <div className="p-4 border border-error/50 rounded-md bg-error/10 shadow-1 mt-6 text-error">
        <h3 className="text-lg font-semibold mb-2">VisaPulse Error</h3>
        <p className="text-sm">Could not load timeline: {error.message}</p>
      </div>
    );
  }

  // --- Success State (Filter and Display) ---
  const now = new Date();
  const filteredItems = (items || [])
    .map(item => ({ ...item, parsedDate: parseISO(item.date) })) // Parse dates first
    .filter(item => differenceInDays(now, item.parsedDate) <= historyLimitDays)
    .sort((a, b) => b.parsedDate.getTime() - a.parsedDate.getTime()); // Sort descending (most recent first)

  // Design System: Vertical timeline dots coloured by status.
  return (
    <div className="p-4 border border-grey-20 rounded-md bg-white shadow-1 mt-6">
      <h3 className="text-lg font-semibold mb-4 text-grey-90">VisaPulse Timeline (Last {historyLimitDays} Days)</h3>
      {filteredItems.length > 0 ? ( // Use filteredItems
        <ol className="relative border-l border-grey-20 dark:border-gray-700 ml-2">
          {/* Add types for item and index */}
          {filteredItems.map((item: typeof filteredItems[number], index: number) => ( 
            <li key={item.id} className={`mb-6 ml-6 ${index === filteredItems.length - 1 ? 'mb-0' : ''}`}> 
              <span 
                className={`absolute flex items-center justify-center w-3 h-3 ${getStatusColor(item.status)} rounded-full -left-1.5 top-1 ring-4 ring-white dark:ring-gray-900 dark:bg-blue-900`}
                title={item.status}
              ></span>
              <time className="mb-1 text-xs font-normal leading-none text-grey-40 dark:text-gray-500">
                {/* Format date using date-fns */}
                {format(item.parsedDate, 'MMM d, yyyy')} 
              </time>
              <h4 className="flex items-center mb-0.5 text-md font-semibold text-grey-90 dark:text-white">
                {item.title}
                {/* Optional: Add status badge next to title */}
                {/* <Badge variant="outline" className="ml-2 text-xs">{item.status}</Badge> */}
              </h4>
              {item.description && (
                <p className="text-sm font-normal text-grey-40 dark:text-gray-400">
                  {item.description}
                </p>
              )}
              {/* Placeholder for Pro Tier Lawyer Chat Button */}
              {/* TODO: Conditionally render this based on user's plan */}
              <div className="mt-2">
                 <Button 
                    variant="outline" 
                    size="sm" // Changed from "xs" to "sm"
                    className="text-xs h-6 px-2" // Keep custom classes for smaller appearance
                    onClick={() => console.log('Lawyer chat clicked for item:', item.id)} // Placeholder action
                 >
                    Chat with Lawyer
                 </Button>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p className="text-sm text-grey-40">No recent visa updates found.</p>
      )}
      {/* Add Visa Advice Disclaimer */}
      <p className="mt-4 text-xs text-grey-40 italic">
        *Disclaimer: VisaPulse provides informational updates based on publicly available data and predictions. It is not legal advice. Consult with an immigration attorney for advice specific to your situation.
      </p>

      {/* Loss Aversion / Upgrade Prompt for Free Tier */}
      {historyLimitDays && historyLimitDays > 0 && ( // Show only if a limit is set
         <div className="mt-4 p-3 bg-primary-500/10 border border-primary-500/20 rounded-md text-center">
            <p className="text-sm font-medium text-primary-600">
               You're viewing the last {historyLimitDays} days of updates.
            </p>
            <p className="text-xs text-primary-500/90 mt-1">
               Upgrade to Pro to unlock the full history and lawyer chat access.
            </p>
            {/* TODO: Add actual upgrade button/link */}
            {/* <Button size="sm" className="mt-2">Upgrade Now</Button> */}
         </div>
      )}
    </div>
  );
}
