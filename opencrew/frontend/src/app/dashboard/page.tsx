'use client';

import React, { useState, useRef } from 'react';
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
    // Ensure this container fills the space provided by the parent (DashboardBentoCard's content area)
    <div className="flex flex-col h-full relative">
      {/* Image Preview Area - Takes up available space */}
      <div className="flex-grow flex items-center justify-center relative p-2"> {/* Added padding */}
        {/* Left Button */}
         <Button
          variant="ghost"
          size="icon"
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-background/50 hover:bg-background/80 rounded-full disabled:opacity-30"
          onClick={onPrev}
          disabled={logs.length <= 1}
          aria-label="Previous Activity"
        >
          <ChevronLeft size={24} />
        </Button>

        {/* Image Container */}
         <div className="relative w-full h-full"> {/* Image container fills the flex-grow space */}
           <Image
             key={currentLog.id} // Add key to force re-render on change
             src={currentLog.imageUrl}
             alt={`Activity Log ${currentLog.id}`}
             layout="fill"
             objectFit="contain" // Use contain to see the whole image
             className="rounded-md"
             priority={true}
           />
         </div>

        {/* Right Button */}
         <Button
          variant="ghost"
          size="icon"
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-background/50 hover:bg-background/80 rounded-full disabled:opacity-30"
          onClick={onNext}
          disabled={logs.length <= 1}
          aria-label="Next Activity"
        >
          <ChevronRight size={24} />
        </Button>
      </div>
      {/* Summary Text - Fixed at the bottom */}
      <p className="text-sm text-center text-grey-600 dark:text-grey-400 truncate p-3 border-t border-grey-200 dark:border-grey-800 flex-shrink-0"> {/* Added padding and flex-shrink-0 */}
        {currentLog.summary}
      </p>
    </div>
  );
};
// --- End Activity Log Viewer Component ---


export default function DashboardPage() {

  const userPlan = 'Free Plan';
  const dailyAppliesUsed = 15;
  const dailyApplyLimit = 50;
  const totalApplicationsSent = 1234;
  const jobsMatchedToday = 80;
  const interviewRate = 12;

  // --- State for Activity Log ---
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([
    { id: 1, imageUrl: "/assets/image.png", summary: "Applied to Software Engineer at Google" },
    { id: 2, imageUrl: "/assets/heaven.jpeg", summary: "Matched with Product Manager at Meta" },
    { id: 3, imageUrl: "/assets/fullimage.png", summary: "Sent follow-up email to Apple recruiter" },
    // Add more sample logs as needed
  ]);
  const [currentLogIndex, setCurrentLogIndex] = useState(0);
  // --- End State for Activity Log ---


  const [resumes, setResumes] = useState([
    { id: 1, name: "Software_Eng_Resume_v3.pdf" },
    { id: 2, name: "Product_Manager_Final.docx" },
  ]);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && resumes.length < 5) {
      console.log("Selected file:", file.name);
      const newResume = { id: Date.now(), name: file.name };
      setResumes([...resumes, newResume]);
      event.target.value = '';
    } else if (resumes.length >= 5) {
        alert("You can upload a maximum of 5 resumes.");
        event.target.value = '';
    }
  };

  const handleDeleteResume = (id: number) => {
    console.log("Deleting resume with id:", id);
    setResumes(resumes.filter(resume => resume.id !== id));
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // --- Handlers for Activity Log ---
  const handleNextActivity = () => {
    setCurrentLogIndex((prevIndex) => (prevIndex + 1) % activityLogs.length);
  };

  const handlePrevActivity = () => {
    setCurrentLogIndex((prevIndex) =>
      prevIndex === 0 ? activityLogs.length - 1 : prevIndex - 1
    );
  };
  // --- End Handlers for Activity Log ---

  // Define features for the Bento Grid
  // Note: We will render the Activity Log card specially below
  const features = [
    // --- Main Auto Apply Progress Card ---
    {
      name: "Auto Apply Progress",
      description: "",
      href: "#",
      cta: "View Activity",
      background: <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 opacity-30 dark:from-blue-900/30 dark:to-indigo-900/30"></div>,
      className: "col-span-2",
      customContent: (
        <div className="flex-grow flex flex-col items-center justify-center text-center h-full">
          <p className="text-7xl font-semibold text-grey-900 dark:text-white mb-3">
            {dailyAppliesUsed} / {dailyApplyLimit}
          </p>
          <Progress
              value={(dailyAppliesUsed / dailyApplyLimit) * 100}
              className={cn(
                  "w-3/4 h-2 bg-grey-200 dark:bg-grey-700",
                  "[&_[data-slot=progress-indicator]]:bg-blue-500 dark:[&_[data-slot=progress-indicator]]:bg-blue-400"
              )}
          />
        </div>
      ),
      footerContent: (
        <div className="grid grid-cols-3 gap-4 text-left border-t border-grey-200 dark:border-grey-800 p-4 bg-background/80 backdrop-blur-sm">
           <div>
              <p className="text-xs text-grey-500 dark:text-grey-500">Total Sent</p>
              <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{totalApplicationsSent}</p>
           </div>
           <div>
              <p className="text-xs text-grey-500 dark:text-grey-500">Matched Today</p>
              <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{jobsMatchedToday}</p>
           </div>
           <div>
              <p className="text-xs text-grey-500 dark:text-grey-500">Interview Rate (7d)</p>
              <p className="text-lg font-medium text-grey-700 dark:text-grey-300">{interviewRate}%</p>
           </div>
        </div>
      )
    },
    // --- Preferences Card ---
    {
      name: "Preferences",
      description: "Set your job search criteria.",
      background: <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-teal-100 opacity-30 dark:from-green-900/30 dark:to-teal-900/30"></div>,
      className: "col-span-1",
      customContent: (
        <div className="space-y-4 p-2">
          {/* Title Preference */}
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="pref-title">Title</Label>
            <Select>
              <SelectTrigger id="pref-title" className="w-full">
                <SelectValue placeholder="Select job title..." />
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
            <Select>
              <SelectTrigger id="pref-location" className="w-full">
                <SelectValue placeholder="Select location..." />
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
            <Select>
              <SelectTrigger id="pref-salary" className="w-full">
                <SelectValue placeholder="Select minimum salary..." />
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
        </div>
      )
    },
    // --- Resume Card ---
    {
      name: "Resumes",
      description: "", // description is optional now
      href: "#",
      cta: "Manage All",
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
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
          {/* Bottom controls (count and add button) */}
          <div className="flex items-center justify-between mt-auto pt-2 border-t border-grey-200 dark:border-grey-800">
               <p className="text-xs text-grey-400 dark:text-grey-600">
                  {resumes.length} / 5 Resumes
               </p>
               <Button
                  variant="outline"
                  size="icon"
                  onClick={triggerFileInput}
                  disabled={resumes.length >= 5}
                  className={cn("h-8 w-8", resumes.length >= 5 ? "opacity-50 cursor-not-allowed" : "")}
                  aria-label="Upload Resume"
               >
                 <Plus size={16} />
               </Button>
          </div>
        </div>
      )
    },
    // --- Activity Log Card (Definition Simplified) ---
    {
      name: "Activity Log",
      // Removed props that are no longer needed or handled dynamically
      background: <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-pink-100 opacity-30 dark:from-purple-900/30 dark:to-pink-900/30"></div>,
      className: "col-span-2",
    },
  ];


  const handleUpgradeClick = () => {
    console.log('Upgrade button clicked');
  };

  return (
    <TooltipProvider>
      <Input
        id="resume-upload"
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
        accept=".pdf,.docx"
        disabled={resumes.length >= 5}
      />

      <div className="h-screen flex flex-col bg-grey-05 dark:bg-black">
        <header className="w-full bg-white dark:bg-grey-900 shadow-sm flex-shrink-0 px-4 py-3 border-b border-grey-200 dark:border-grey-800">
          <div className="container mx-auto flex items-center justify-between">
            <span className="text-lg font-bold text-black dark:text-white">
              opencrew
            </span>
            <div className="flex items-center space-x-4">
               <span className="text-sm font-medium text-grey-60 dark:text-grey-400">
                  {userPlan} &nbsp;|&nbsp; {dailyAppliesUsed}/{dailyApplyLimit} Today
               </span>
               <Tooltip>
                 <TooltipTrigger asChild>
                   <Button onClick={handleUpgradeClick} variant="default" size="sm">
                      Upgrade
                   </Button>
                 </TooltipTrigger>
                 <TooltipContent>
                   <p>Apply to 200 jobs/day – 10x your reach!</p>
                 </TooltipContent>
               </Tooltip>
               <button className="text-grey-500 hover:text-grey-700 dark:text-grey-400 dark:hover:text-white transition-colors" aria-label="Help">
                  <HelpCircle size={20} />
               </button>
               <button className="text-grey-500 hover:text-grey-700 dark:text-grey-400 dark:hover:text-white transition-colors" aria-label="User Profile">
                  <UserCircle size={24} />
               </button>
            </div>
          </div>
        </header>
        <div className="flex-grow flex items-center justify-center px-4 py-8 overflow-y-auto">
           <div className="container mx-auto w-full max-w-4xl">
              <DashboardBentoGrid className="grid-cols-1 md:grid-cols-3">
                 {/* Dynamically render cards, injecting ActivityLogViewer */}
                 {features.map((feature, idx) => {
                   if (feature.name === "Activity Log") {
                     return (
                       // Pass props explicitly, do not spread feature
                       <DashboardBentoCard
                         key={idx}
                         name={feature.name}
                         className={feature.className}
                         background={feature.background}
                         // Do not pass description, href, cta, customContent, footerContent
                       >
                         {/* Inject ActivityLogViewer here as children */}
                         <ActivityLogViewer
                           logs={activityLogs}
                           currentIndex={currentLogIndex}
                           onNext={handleNextActivity}
                           onPrev={handlePrevActivity}
                         />
                       </DashboardBentoCard>
                     );
                   } else {
                     // Render other cards normally by spreading all feature props
                     return (
                       <DashboardBentoCard key={idx} {...feature} />
                     );
                   }
                 })}
              </DashboardBentoGrid>
           </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
