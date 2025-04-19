'use client'; // Dashboard will likely need client-side interactions

import React from 'react';
// import { ProgressMeter } from '~/components/ProgressMeter'; // No longer needed here
import { PipelineBoard } from '~/components/PipelineBoard';
import { DailyStreak } from '~/components/DailyStreak';
import { VisaPulse } from '~/components/VisaPulse';
import { JobCard } from '~/components/JobCard'; // Import JobCard
import { api } from '~/trpc/react';
import { Skeleton } from '~/components/ui/skeleton';

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
  const { data: applications, isLoading: isLoadingApplications, error: errorApplications } = api.application.list.useQuery();

  // Fetch matched jobs using tRPC
  // Pass an empty object {} as input to satisfy the procedure definition, even if fields are optional
  const { data: matchedJobs, isLoading: isLoadingJobs, error: errorJobs } = api.job.getMatchedJobs.useQuery({});

  // --- Combined Loading State ---
  if (isLoadingApplications || isLoadingJobs) {
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

  // --- Combined Error State ---
  if (errorApplications || errorJobs) {
    return (
      <div className="px-4 py-8 h-screen flex flex-col items-center justify-center text-center">
        <h1 className="text-3xl font-bold mb-6 text-error font-display">Dashboard Error</h1>
        {errorApplications && <p className="text-error mb-2">Failed to load applications: {errorApplications.message}</p>}
        {errorJobs && <p className="text-error">Failed to load matched jobs: {errorJobs.message}</p>}
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

           {/* Matched Jobs Section */}
           <div className="space-y-3">
              <h3 className="text-lg font-semibold text-grey-90">Matched Jobs</h3>
              {isLoadingJobs ? ( // Show skeletons if jobs are still loading (though main loading handles this)
                 <>
                    <Skeleton className="h-24 w-full rounded-md" />
                    <Skeleton className="h-24 w-full rounded-md" />
                    <Skeleton className="h-24 w-full rounded-md" />
                 </>
              ) : errorJobs ? (
                 <p className="text-sm text-error">Could not load matched jobs.</p>
              ) : matchedJobs && matchedJobs.length > 0 ? (
                 matchedJobs.map((job) => (
                    <JobCard
                       key={job.id}
                       id={job.id}
                       jobTitle={job.title}
                       companyName={job.company}
                       location={job.location}
                       ctaLink={job.url} // Use job URL for the card's main link/button
                       // logoUrl={job.logoUrl} // Add if available in schema/data
                    />
                 ))
              ) : (
                 <p className="text-sm text-grey-60">No matched jobs found yet. Ensure your resume is uploaded!</p>
              )}
           </div>

           {/* Add other sidebar components here later (e.g., QuotaRing) */}
        </aside>
      </div>
    </div>
  );
}
