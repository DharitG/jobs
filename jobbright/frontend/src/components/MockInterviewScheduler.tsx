'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Calendar, Clock } from 'lucide-react'; // Icons for scheduling

// TODO: Integrate with a scheduling service/API (e.g., Calendly, or custom backend)
// TODO: Fetch available slots from backend
// TODO: Implement booking mutation via tRPC

export function MockInterviewScheduler() {
  // Placeholder state
  const [isScheduling, setIsScheduling] = useState(false); // Example state if modal is used
  const isLoading = false; // Placeholder for loading state
  const error = null; // Placeholder for error state

  const handleScheduleClick = () => {
    console.log("Initiating mock interview scheduling...");
    // Placeholder: Open a modal or navigate to a scheduling page
    alert("Mock interview scheduling integration pending.");
    // TODO: Implement actual scheduling logic (e.g., open Calendly link, call API)
  };

  if (isLoading) {
    // Optional: Add a loading skeleton
    return <Card className="animate-pulse h-32"></Card>;
  }

  if (error) {
    // Optional: Add error display
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading scheduler.</Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mock Interview Practice</CardTitle>
        <CardDescription>Schedule a practice session with an AI or a coach.</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Placeholder content - could display upcoming session or available slots */}
        <p className="text-sm text-grey-40">Book a session to hone your interview skills.</p>
      </CardContent>
      <CardFooter>
        <Button onClick={handleScheduleClick}>
          <Calendar className="mr-2 h-4 w-4" />
          Schedule Session
        </Button>
      </CardFooter>
    </Card>
  );
}
