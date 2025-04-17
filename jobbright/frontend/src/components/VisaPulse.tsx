'use client';

import React from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { api } from '~/trpc/react';
import { differenceInDays, parseISO, format } from 'date-fns';
// Import Accordion components
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion"; 

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

  // --- Success State (Filter, Group, and Display) ---
  const now = new Date();
  const filteredItems = (items || [])
    .map(item => ({ ...item, parsedDate: parseISO(item.date) }))
    .filter(item => differenceInDays(now, item.parsedDate) <= historyLimitDays)
    .sort((a, b) => b.parsedDate.getTime() - a.parsedDate.getTime());

  // Group items by date string (e.g., "Apr 17, 2025")
  const groupedItems = filteredItems.reduce((acc, item) => {
    const dateKey = format(item.parsedDate, 'MMM d, yyyy');
    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    acc[dateKey].push(item);
    return acc;
  }, {} as Record<string, typeof filteredItems>); // Type assertion for accumulator

  const dateKeys = Object.keys(groupedItems); // Get sorted dates

  // Design System: Vertical timeline dots coloured by status. Collapsible daily items.
  return (
    <div className="p-4 border border-grey-20 rounded-design-md bg-white shadow-1 mt-6"> {/* Use design radius */}
      <h3 className="text-lg font-semibold mb-4 text-grey-90">VisaPulse Timeline (Last {historyLimitDays} Days)</h3>
      {dateKeys.length > 0 ? (
        <Accordion type="single" collapsible className="w-full" defaultValue={dateKeys[0]}> {/* Default open first day */}
          {dateKeys.map((dateKey) => (
            <AccordionItem value={dateKey} key={dateKey} className="border-b border-grey-20 last:border-b-0">
              <AccordionTrigger className="text-md font-semibold text-grey-90 hover:no-underline py-3">
                {dateKey}
              </AccordionTrigger>
              <AccordionContent className="pt-1 pb-3">
                {/* Render the timeline list for this specific day */}
                <ol className="relative border-l border-grey-20 ml-2">
                  {groupedItems[dateKey]?.map((item, index, arr) => ( // Added optional chaining ?.map
                    <li key={item.id} className={`mb-4 ml-6 ${index === arr.length - 1 ? 'mb-0' : ''}`}> {/* Adjusted margin */}
                      <span 
                        className={`absolute flex items-center justify-center w-3 h-3 ${getStatusColor(item.status)} rounded-full -left-1.5 top-1 ring-4 ring-white`}
                        title={item.status}
                      ></span>
                      {/* Removed redundant date time, it's in the AccordionTrigger */}
                      <h4 className="flex items-center mb-0.5 text-md font-semibold text-grey-90">
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
                    size="sm" 
                    className="text-xs h-7 px-2" // Adjusted height slightly
                    onClick={() => console.log('Lawyer chat clicked for item:', item.id)} // Placeholder action
                 >
                    Chat with Lawyer
                 </Button>
              </div>
            </li>
                  ))}
                </ol>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
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
