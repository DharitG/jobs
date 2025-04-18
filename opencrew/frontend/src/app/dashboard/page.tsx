'use client'; // Dashboard will likely need client-side interactions

import React from 'react';
// import { ProgressMeter } from '~/components/ProgressMeter'; // No longer needed here
import { PipelineBoard } from '~/components/PipelineBoard'; // Import the board
import { DailyStreak } from '~/components/DailyStreak'; // Import DailyStreak
import { VisaPulse } from '~/components/VisaPulse'; // Import VisaPulse
import { api } from '~/trpc/react'; // Import tRPC client hook
import { Skeleton } from '~/components/ui/skeleton'; // Import Skeleton

// Define ApplicationStage type (consider moving to a shared types file)
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';

// Define the expected structure from the API (matches ApplicationItem in PipelineBoard)
// Ensure this matches the actual return type of your tRPC procedure
interface ApiApplicationItem {
  id: string | number; // Keep as string | number to match potential backend ID types
  companyName: string;
  jobTitle: string;
  location?: string | null; // Allow null
  stage: ApplicationStage;
  logoUrl?: string;
  ctaLink?: string;
}

export default function DashboardPage() {

  // Fetch applications using tRPC
  const { data: applications, isLoading, error } = api.application.list.useQuery(); // ASSUMING this procedure exists

  // --- Loading State --- 
  if (isLoading) {
    // Render skeleton loader matching the board structure
    return (
      <div className="px-4 py-8 h-screen flex flex-col">
        <h1 className="text-2xl font-bold mb-6 text-grey-90 flex-shrink-0">Application Pipeline</h1>
        <div className="flex-grow overflow-hidden">
          <div className="flex space-x-4 pb-4">
            {[...Array(4)].map((_, colIndex) => ( // Simulate 4 columns
              <div key={colIndex} className="flex-shrink-0 w-72 bg-grey-05 rounded-md shadow-sm">
                {/* Skeleton Header */}
                <div className="sticky top-0 z-10 p-3 bg-grey-05 rounded-t-md border-b border-grey-20 shadow-sm">
                  <div className="flex justify-between items-center">
                    <Skeleton className="h-5 w-24" />
                    <Skeleton className="h-5 w-8 rounded-full" />
                  </div>
                </div>
                {/* Skeleton Cards */}
                <div className="p-3 space-y-3">
                  {[...Array(3)].map((_, cardIndex) => ( // Simulate 3 cards per column
                    <div key={cardIndex} className="p-4 rounded-md border border-grey-20 bg-white space-y-3">
                       <div className="flex items-center space-x-3">
                          <Skeleton className="h-10 w-10 rounded-md" />
                          <div className="space-y-1 flex-grow">
                             <Skeleton className="h-4 w-3/4" />
                             <Skeleton className="h-4 w-1/2" />
                          </div>
                       </div>
                       <Skeleton className="h-4 w-1/3" />
                       <Skeleton className="h-8 w-20 rounded-md ml-auto" /> 
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // --- Error State --- 
  if (error) {
    return (
      <div className="px-4 py-8 h-screen flex flex-col items-center justify-center">
        <h1 className="text-2xl font-bold mb-6 text-error">Application Pipeline</h1>
        <p className="text-error">Failed to load applications: {error.message}</p>
      </div>
    );
  }

  // --- Success State --- 
  // Filter out rejected applications for the main board display
  // Ensure the fetched data conforms to ApiApplicationItem structure before filtering
  const activeApplications = (applications || []).filter(
    (app: ApiApplicationItem): app is ApiApplicationItem => app.stage !== 'Rejected'
  );

  // TODO: Fetch user's plan to determine historyLimitDays for VisaPulse
  const userPlan = 'free'; // Placeholder
  const visaPulseHistoryLimit = userPlan === 'free' ? 7 : undefined; // Show full history for paid plans

  return (
    // Use grid layout for main content and sidebar
    <div className="px-4 py-8 h-screen flex flex-col">
      <h1 className="text-3xl font-bold mb-6 text-grey-90 flex-shrink-0 font-display">Dashboard</h1>
      
      <div className="flex-grow grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
        {/* Main Content Area (Pipeline Board) */}
        <div className="lg:col-span-2 flex flex-col overflow-hidden">
          <h2 className="text-xl font-semibold mb-4 text-grey-90 flex-shrink-0">Application Pipeline</h2>
          <div className="flex-grow overflow-hidden"> {/* Container for board overflow control */}
            <PipelineBoard initialApplications={activeApplications} />
          </div>
        </div>

        {/* Sidebar Area */}
        <aside className="lg:col-span-1 flex flex-col space-y-6 overflow-y-auto scrollbar-thin">
           <h2 className="text-xl font-semibold text-grey-90 flex-shrink-0">Insights</h2>
           {/* Daily Streak Component */}
           <DailyStreak initialStreak={5} /> {/* Placeholder initial streak */}
           
           {/* VisaPulse Component */}
           <VisaPulse historyLimitDays={visaPulseHistoryLimit} />

           {/* Add other sidebar components here later (e.g., QuotaRing) */}
        </aside>
      </div>
    </div>
  );
}
