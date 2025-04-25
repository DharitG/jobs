'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import type { ChangeEvent } from 'react';
import Image from 'next/image';
import { Button } from '~/components/ui/button';
import { UserCircle, HelpCircle, Settings, Activity, FileText, Trash2, Plus, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';
import { DashboardBentoCard, DashboardBentoGrid } from "~/components/dashboard/dashboard-bento-grid";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Label } from "~/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "~/components/ui/tooltip";
import { Progress } from "~/components/ui/progress";
import { cn } from '~/lib/utils';
import { Input } from '~/components/ui/input';
import { api } from "~/trpc/react";
import { useToast } from "~/hooks/use-toast";

// --- Type for Activity Log ---
interface ActivityLog {
  id: number;
  imageUrl: string;
  summary: string;
}

// --- Props for Activity Log Viewer ---
interface ActivityLogViewerProps {
  logs: ActivityLog[];
  currentIndex: number;
  onNext: () => void;
  onPrev: () => void;
}

// --- Activity Log Viewer Component (Defined Outside DashboardPage) ---
const ActivityLogViewer: React.FC<ActivityLogViewerProps> = ({ logs, currentIndex, onNext, onPrev }) => {
  // Handle empty logs case
  if (logs.length === 0) {
    return <div className="flex items-center justify-center h-full text-grey-500 p-4">No activity yet.</div>;
  }

  // Ensure currentLog is valid before accessing properties
  const currentLog = logs[currentIndex];
  if (!currentLog) {
     return <div className="flex items-center justify-center h-full text-grey-500 p-4">Error displaying log.</div>;
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* Image Preview Area */}
      <div className="flex-grow flex items-center justify-center relative p-2">
        {/* Left Button */}
         <Button
          variant="ghost" size="icon" onClick={onPrev} disabled={logs.length <= 1} aria-label="Previous Activity"
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-background/50 hover:bg-background/80 rounded-full disabled:opacity-30"
        > <ChevronLeft size={24} /> </Button>
        {/* Image Container */}
         <div className="relative w-full h-full">
           <Image key={currentLog.id} src={currentLog.imageUrl} alt={`Activity Log ${currentLog.id}`} layout="fill" objectFit="contain" className="rounded-md" priority={true} />
         </div>
        {/* Right Button */}
         <Button
           variant="ghost" size="icon" onClick={onNext} disabled={logs.length <= 1} aria-label="Next Activity"
           className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-background/50 hover:bg-background/80 rounded-full disabled:opacity-30"
         > <ChevronRight size={24} /> </Button>
      </div>
      {/* Summary Text */}
      <p className="text-sm text-center text-grey-600 dark:text-grey-400 truncate p-3 border-t border-grey-200 dark:border-grey-800 flex-shrink-0">
        {currentLog.summary}
      </p>
    </div>
  );
};
// --- End Activity Log Viewer Component ---


export default function DashboardPage() {

  const { toast } = useToast();

  // --- Fetch Dashboard Stats ---
  const { data: stats, isLoading: isLoadingStats, isError: isErrorStats, error: statsError } = api.user.getDashboardStats.useQuery();
  // --- End Fetch Dashboard Stats ---

  // --- Fetch Preferences ---
  const { data: preferencesData, isLoading: isLoadingPrefs, isError: isErrorPrefs, error: prefsError } = api.user.getPreferences.useQuery();
  // --- End Fetch Preferences ---

  // --- Preference Update Mutation ---
  const utils = api.useUtils();
  const updatePrefsMutation = api.user.updatePreferences.useMutation({
    onSuccess: () => {
      toast({ title: "Preferences Updated", description: "Your changes have been saved." });
      void utils.user.getPreferences.invalidate(); // Invalidate to refetch fresh data if needed
    },
    onError: (error) => {
       toast({
         variant: "destructive",
         title: "Update Failed",
         description: error.message ?? "Could not save preferences.",
       });
    }
  });
  const { mutate: updatePrefs, isPending: isUpdatingPrefs } = updatePrefsMutation; // Use isPending for loading state
  // --- End Preference Update Mutation ---

  // --- Local State for Preferences ---
  const [selectedTitle, setSelectedTitle] = useState<string | undefined>(undefined);
  const [selectedLocation, setSelectedLocation] = useState<string | undefined>(undefined);
  const [selectedSalaryValue, setSelectedSalaryValue] = useState<string | undefined>(undefined);
  // --- End Local State ---

  // Provide default values while loading or on error (errors handled by toasts)
  const userPlan = stats?.user_plan ?? (isLoadingStats ? 'Loading...' : 'N/A');
  const dailyAppliesUsed = stats?.daily_applies_used ?? 0;
  const dailyApplyLimit = stats?.daily_apply_limit ?? 1; // Avoid division by zero
  const totalApplicationsSent = stats?.total_applications_sent ?? 0;
  const jobsMatchedToday = stats?.jobs_matched_today ?? 0;
  const interviewRate = stats?.interview_rate_7d ?? 0;


  // --- Effect for Stats Error Toast ---
  useEffect(() => {
    if (isErrorStats) {
      console.error("Error fetching dashboard stats:", statsError);
      toast({
        variant: "destructive",
        title: "Error Fetching Stats",
        description: statsError?.message ?? "Could not load dashboard details.",
      });
    }
  }, [isErrorStats, toast, statsError]);
  // --- End Stats Effect ---

  // --- Effect for Preferences Error Toast ---
  useEffect(() => {
    if (isErrorPrefs) {
      console.error("Error fetching preferences:", prefsError);
      toast({
        variant: "destructive",
        title: "Error Fetching Preferences",
        description: prefsError?.message ?? "Could not load preferences.",
      });
      // Reset local state on error? Or maybe just disable selects? Resetting for now.
      setSelectedTitle(undefined);
      setSelectedLocation(undefined);
      setSelectedSalaryValue(undefined);
    }
  }, [isErrorPrefs, toast, prefsError]);
  // --- End Preferences Effect ---

  // --- Effect to Sync Fetched Preferences to Local State ---
  useEffect(() => {
    if (preferencesData) {
       setSelectedTitle(preferencesData.preferred_job_titles?.[0]); // Assuming single preference for now
       setSelectedLocation(preferencesData.preferred_locations?.[0]); // Assuming single preference for now

       const salaryNum = preferencesData.minimum_salary_preference;
       let salaryVal: string | undefined = "any"; // Default to 'any' if no match
       if (salaryNum === 80000) salaryVal = "80";
       else if (salaryNum === 100000) salaryVal = "100";
       else if (salaryNum === 120000) salaryVal = "120";
       else if (salaryNum === 150000) salaryVal = "150";
       // If salaryNum is null/undefined, it remains "any"
       setSelectedSalaryValue(salaryVal);
    }
  }, [preferencesData]);
  // --- End Sync Effect ---

  // --- State for Activity Log ---
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([
    { id: 1, imageUrl: "/assets/image.png", summary: "Applied to Software Engineer at Google" },
    { id: 2, imageUrl: "/assets/heaven.jpeg", summary: "Matched with Product Manager at Meta" },
    { id: 3, imageUrl: "/assets/fullimage.png", summary: "Sent follow-up email to Apple recruiter" },
  ]);
  const [currentLogIndex, setCurrentLogIndex] = useState(0);
  // --- End State for Activity Log ---

  // --- State for Resumes ---
  const [resumes, setResumes] = useState([
    { id: 1, name: "Software_Eng_Resume_v3.pdf" },
    { id: 2, name: "Product_Manager_Final.docx" },
  ]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  // --- End State for Resumes ---

  // --- Handlers ---
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => { /* TODO */ };
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  const handleDeleteResume = (id: number) => { /* TODO */ };
  const triggerFileInput = () => { fileInputRef.current?.click(); };
  const handleNextActivity = () => { setCurrentLogIndex((prev) => (prev + 1) % activityLogs.length); };
  const handlePrevActivity = () => { setCurrentLogIndex((prev) => (prev === 0 ? activityLogs.length - 1 : prev - 1)); };
  const handleUpgradeClick = () => { console.log('Upgrade button clicked'); };

  const handlePreferenceChange = useCallback((field: 'title' | 'location' | 'salary', value: string) => {
    let updatedTitle = selectedTitle;
    let updatedLocation = selectedLocation;
    let updatedSalaryValue = selectedSalaryValue;

    // Update local state first
    if (field === 'title') updatedTitle = value;
    else if (field === 'location') updatedLocation = value;
    else if (field === 'salary') updatedSalaryValue = value;

    setSelectedTitle(updatedTitle);
    setSelectedLocation(updatedLocation);
    setSelectedSalaryValue(updatedSalaryValue);

    // Construct payload for mutation
    let payload: {
      preferred_job_titles?: string[] | null;
      preferred_locations?: string[] | null;
      minimum_salary_preference?: number | null;
    } = {};

    payload.preferred_job_titles = updatedTitle ? [updatedTitle] : null; // Assuming single for now
    payload.preferred_locations = updatedLocation ? [updatedLocation] : null; // Assuming single for now

    let salaryNum: number | null = null;
    if (updatedSalaryValue === "80") salaryNum = 80000;
    else if (updatedSalaryValue === "100") salaryNum = 100000;
    else if (updatedSalaryValue === "120") salaryNum = 120000;
    else if (updatedSalaryValue === "150") salaryNum = 150000;
    payload.minimum_salary_preference = salaryNum; // "any" maps to null

    console.log("Updating preferences with payload:", payload);
    updatePrefs(payload);
  }, [updatePrefs, selectedTitle, selectedLocation, selectedSalaryValue]);
  // --- End Handlers ---


  // Define features for the Bento Grid - STATIC properties only
  const features = [
    // --- Main Auto Apply Progress Card (Definition) ---
    {
      name: "Auto Apply Progress",
      description: "", href: "#", cta: "View Activity",
      background: <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 opacity-30 dark:from-blue-900/30 dark:to-indigo-900/30"></div>,
      className: "col-span-2",
    },
    // --- Preferences Card (Definition) ---
    {
      name: "Preferences",
      description: "Set your job search criteria.", // Keep description for card header
      background: <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-teal-100 opacity-30 dark:from-green-900/30 dark:to-teal-900/30"></div>,
      className: "col-span-1",
    },
    // --- Resume Card (Definition with static content) ---
    {
      name: "Resumes",
      description: "", href: "#", cta: "Manage All",
      background: <div className="absolute inset-0 bg-gradient-to-br from-amber-50 to-orange-100 opacity-30 dark:from-amber-900/30 dark:to-orange-900/30"></div>,
      className: "col-span-1",
      customContent: (
        <div className="flex flex-col h-full p-4 relative z-10 space-y-2">
          {/* List of resumes */}
          <div className="flex-grow space-y-2 overflow-y-auto max-h-40 scrollbar-thin mb-2 pr-2">
            {resumes.length === 0 && (
              <p className="text-sm text-grey-500 dark:text-grey-400 text-center pt-2">No resumes uploaded.</p>
            )}
            {resumes.map((resume) => (
              <div key={resume.id} className="flex items-center justify-between bg-white dark:bg-grey-800 p-3 rounded-lg text-base">
                <span className="flex items-center space-x-2 truncate">
                  <FileText size={18} className="text-grey-500 dark:text-grey-400 flex-shrink-0"/>
                  <span className="truncate text-grey-700 dark:text-grey-300">{resume.name}</span>
                </span>
                <button
                  onClick={() => handleDeleteResume(resume.id)}
                  className="text-red-500 hover:text-red-700 dark:hover:text-red-400 ml-2 p-1 rounded hover:bg-red-100/50 dark:hover:bg-red-900/30 flex-shrink-0"
                  aria-label={`Delete ${resume.name}`}
                > <Trash2 size={16} /> </button>
              </div>
            ))}
          </div>
          {/* Bottom controls */}
          <div className="flex items-center justify-between mt-auto pt-2 border-t border-grey-200 dark:border-grey-800">
               <p className="text-xs text-grey-400 dark:text-grey-600"> {resumes.length} / 5 Resumes </p>
               <Button variant="outline" size="icon" onClick={triggerFileInput} disabled={resumes.length >= 5} className={cn("h-8 w-8", resumes.length >= 5 ? "opacity-50 cursor-not-allowed" : "")} aria-label="Upload Resume">
                 <Plus size={16} />
               </Button>
          </div>
        </div>
      )
    },
    // --- Activity Log Card (Definition) ---
    {
      name: "Activity Log",
      background: <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-pink-100 opacity-30 dark:from-purple-900/30 dark:to-pink-900/30"></div>,
      className: "col-span-2",
    },
  ];
  // --- End features array ---


  return (
    <TooltipProvider>
      <Input id="resume-upload" ref={fileInputRef} type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.docx" disabled={resumes.length >= 5} />

      <div className="h-screen flex flex-col bg-grey-05 dark:bg-black">
        {/* --- Header --- */}
        <header className="w-full bg-white dark:bg-grey-900 shadow-sm flex-shrink-0 px-4 py-3 border-b border-grey-200 dark:border-grey-800">
          <div className="container mx-auto flex items-center justify-between">
            <span className="text-lg font-bold text-black dark:text-white">opencrew</span>
            <div className="flex items-center space-x-4">
               <span className="text-sm font-medium text-grey-60 dark:text-grey-400">
                  {isLoadingStats ? 'Loading...' : `${userPlan} | ${dailyAppliesUsed}/${dailyApplyLimit} Today`}
               </span>
               <Tooltip>
                 <TooltipTrigger asChild>
                   <Button onClick={handleUpgradeClick} variant="default" size="sm">Upgrade</Button>
                 </TooltipTrigger>
                 <TooltipContent><p>Apply to 200 jobs/day – 10x your reach!</p></TooltipContent>
               </Tooltip>
               <button className="text-grey-500 hover:text-grey-700 dark:text-grey-400 dark:hover:text-white transition-colors" aria-label="Help"><HelpCircle size={20} /></button>
               <button className="text-grey-500 hover:text-grey-700 dark:text-grey-400 dark:hover:text-white transition-colors" aria-label="User Profile"><UserCircle size={24} /></button>
            </div>
          </div>
        </header>
        {/* --- End Header --- */}

        {/* --- Main Content Area --- */}
        <div className="flex-grow flex items-center justify-center px-4 py-8 overflow-y-auto">
           <div className="container mx-auto w-full max-w-4xl">
              <DashboardBentoGrid className="grid-cols-1 md:grid-cols-3">
                 {/* --- Dynamically Render Cards --- */}
                 {features.map((feature, idx) => {
                   // --- Render Activity Log Card ---
                   if (feature.name === "Activity Log") {
                     return (
                       <DashboardBentoCard key={idx} {...feature}>
                         <ActivityLogViewer logs={activityLogs} currentIndex={currentLogIndex} onNext={handleNextActivity} onPrev={handlePrevActivity} />
                       </DashboardBentoCard>
                     );
                   // --- Render Preferences Card ---
                   } else if (feature.name === "Preferences") {
                     const isPrefsDisabled = isLoadingPrefs || isUpdatingPrefs;
                     return (
                       <DashboardBentoCard
                         key={idx}
                         {...feature} // Spread static props from features array
                         // Pass dynamic content via customContent prop
                         customContent={(
                           <div className={cn("space-y-4 p-2", isPrefsDisabled ? "opacity-50 pointer-events-none" : "")}> {/* Disable interaction while loading/updating */}
                             {/* Title Preference */}
                             <div className="grid w-full max-w-sm items-center gap-1.5">
                               <Label htmlFor="pref-title">Title</Label>
                               <Select value={selectedTitle ?? ''} onValueChange={(value) => handlePreferenceChange('title', value)} disabled={isPrefsDisabled}>
                                 <SelectTrigger id="pref-title" className="w-full">
                                   <SelectValue placeholder={isLoadingPrefs ? "Loading..." : "Select job title..."} />
                                 </SelectTrigger>
                                 <SelectContent>
                                   <SelectItem value="swe">Software Engineer</SelectItem>
                                   <SelectItem value="pm">Product Manager</SelectItem>
                                   <SelectItem value="data">Data Scientist</SelectItem>
                                   <SelectItem value="devops">DevOps Engineer</SelectItem>
                                   <SelectItem value="other">Other</SelectItem>
                                 </SelectContent>
                               </Select>
                             </div>
                             {/* Location Preference */}
                             <div className="grid w-full max-w-sm items-center gap-1.5">
                               <Label htmlFor="pref-location">Location</Label>
                               <Select value={selectedLocation ?? ''} onValueChange={(value) => handlePreferenceChange('location', value)} disabled={isPrefsDisabled}>
                                 <SelectTrigger id="pref-location" className="w-full">
                                   <SelectValue placeholder={isLoadingPrefs ? "Loading..." : "Select location..."} />
                                 </SelectTrigger>
                                 <SelectContent>
                                   <SelectItem value="remote">Remote</SelectItem>
                                   <SelectItem value="sf">San Francisco Bay Area</SelectItem>
                                   <SelectItem value="ny">New York City</SelectItem>
                                   <SelectItem value="sea">Seattle</SelectItem>
                                   <SelectItem value="other">Other</SelectItem>
                                 </SelectContent>
                               </Select>
                             </div>
                             {/* Salary Preference */}
                             <div className="grid w-full max-w-sm items-center gap-1.5">
                               <Label htmlFor="pref-salary">Min Salary</Label>
                               <Select value={selectedSalaryValue ?? ''} onValueChange={(value) => handlePreferenceChange('salary', value)} disabled={isPrefsDisabled}>
                                 <SelectTrigger id="pref-salary" className="w-full">
                                   <SelectValue placeholder={isLoadingPrefs ? "Loading..." : "Select minimum salary..."} />
                                 </SelectTrigger>
                                 <SelectContent>
                                   <SelectItem value="80">$80,000+</SelectItem>
                                   <SelectItem value="100">$100,000+</SelectItem>
                                   <SelectItem value="120">$120,000+</SelectItem>
                                   <SelectItem value="150">$150,000+</SelectItem>
                                   <SelectItem value="any">Any</SelectItem>
                                 </SelectContent>
                               </Select>
                             </div>
                             {/* Saving Indicator */}
                             {isUpdatingPrefs && <p className="text-xs text-blue-500 text-center pt-1">Saving...</p>}
                           </div>
                         )}
                       />
                     );
                   // --- Render Auto Apply Progress Card ---
                   } else if (feature.name === "Auto Apply Progress") {
                     return (
                       <DashboardBentoCard
                         key={idx}
                         {...feature} // Spread static props
                         // Pass dynamic content via customContent and footerContent props
                         customContent={(
                           <div className="flex-grow flex flex-col items-center justify-center text-center h-full">
                             {isLoadingStats ? ( <p className="text-xl text-grey-500">Loading Stats...</p> ) : (
                               <>
                                 <p className="text-7xl font-semibold text-grey-900 dark:text-white mb-3"> {dailyAppliesUsed} / {dailyApplyLimit} </p>
                                 <Progress value={dailyApplyLimit > 0 ? (dailyAppliesUsed / dailyApplyLimit) * 100 : 0} className={cn( "w-3/4 h-2 bg-grey-200 dark:bg-grey-700", "[&_[data-slot=progress-indicator]]:bg-blue-500 dark:[&_[data-slot=progress-indicator]]:bg-blue-400" )} />
                               </>
                             )}
                           </div>
                         )}
                         footerContent={(
                           <div className="grid grid-cols-3 gap-4 text-left border-t border-grey-200 dark:border-grey-800 p-4 bg-background/80 backdrop-blur-sm">
                              <div> <p className="text-xs text-grey-500 dark:text-grey-500">Total Sent</p> <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{isLoadingStats ? '...' : totalApplicationsSent}</p> </div>
                              <div> <p className="text-xs text-grey-500 dark:text-grey-500">Matched Today</p> <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{isLoadingStats ? '...' : jobsMatchedToday}</p> </div>
                              <div> <p className="text-xs text-grey-500 dark:text-grey-500">Interview Rate (7d)</p> <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{isLoadingStats ? '...' : `${interviewRate.toFixed(1)}%`}</p> </div>
                           </div>
                         )}
                       />
                     );
                   // --- Render other cards (like Resumes) ---
                   } else {
                     // Assumes static content is defined in features array (like for Resumes)
                     return (
                       <DashboardBentoCard key={idx} {...feature} />
                     );
                   }
                 })}
                 {/* --- End Dynamic Card Rendering --- */}
              </DashboardBentoGrid>
           </div>
        </div>
        {/* --- End Main Content Area --- */}
      </div>
    </TooltipProvider>
  );
}
