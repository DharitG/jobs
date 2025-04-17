'use client'; // Dashboard will likely need client-side interactions

import React from 'react';
// import { ProgressMeter } from '~/components/ProgressMeter'; // No longer needed here
import { PipelineBoard } from '~/components/PipelineBoard'; // Import the board
import { api } from '~/trpc/react'; // Import tRPC client hook
// Import other dashboard components later

// Define ApplicationStage type (consider moving to a shared types file)
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';

// Define the expected structure from the API (matches ApplicationItem in PipelineBoard)
// Ensure this matches the actual return type of your tRPC procedure
interface ApiApplicationItem {
  id: string | number;
  companyName: string;
  jobTitle: string;
  location?: string;
  stage: ApplicationStage;
  logoUrl?: string;
  ctaLink?: string;
}

export default function DashboardPage() {

  // Fetch applications using tRPC
  const { data: applications, isLoading, error } = api.application.list.useQuery(); // ASSUMING this procedure exists

  // --- Loading State --- 
  if (isLoading) {
    return (
      <div className="px-4 py-8 h-screen flex flex-col items-center justify-center">
        <h1 className="text-2xl font-bold mb-6 text-grey-90">Application Pipeline</h1>
        <p className="text-grey-40">Loading applications...</p>
        {/* TODO: Add a skeleton loader for the board */}
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

  return (
    // Removed container mx-auto to allow board to potentially span wider
    <div className="px-4 py-8 h-screen flex flex-col">
      <h1 className="text-2xl font-bold mb-6 text-grey-90 flex-shrink-0">Application Pipeline</h1>
      
      {/* Render the Pipeline Board */}
      <div className="flex-grow overflow-hidden"> {/* Added container for board overflow control */}
        <PipelineBoard initialApplications={activeApplications} />
      </div>

      {/* Other dashboard sections like Insights, VisaPulse can go here */}
    </div>
  );
} 