'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { UserCheck, CalendarCheck } from 'lucide-react'; // Example icons

// TODO: Fetch coach details and availability from backend
// TODO: Implement scheduling/messaging functionality

export function SuccessCoachSection() {
  // Placeholder: Assume user is eligible (Elite tier)
  const isEligible = true; 
  const isLoading = false; // Placeholder
  const error = null; // Placeholder

  const handleBookSession = () => {
    console.log("Booking session with success coach...");
    alert("Success coach booking integration pending.");
    // TODO: Implement booking logic
  };

  if (!isEligible) {
    // Optionally show an upgrade prompt if not eligible
    return null; 
  }

  if (isLoading) {
    return <Card className="animate-pulse h-40"></Card>;
  }

  if (error) {
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading coach details.</Card>;
  }

  // Placeholder content
  const coachName = "Alex Chen"; 
  const nextAvailable = "Tomorrow at 2:00 PM PST";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <UserCheck className="mr-2 h-5 w-5 text-primary-500" />
          Personal Success Coach
        </CardTitle>
        <CardDescription>Your dedicated coach, {coachName}, is here to help.</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-grey-90 mb-2">
          Get personalized guidance, resume reviews, and interview strategies.
        </p>
        <p className="text-sm text-grey-40">
          Next available slot: {nextAvailable}
        </p>
      </CardContent>
      <CardFooter>
        <Button onClick={handleBookSession}>
          <CalendarCheck className="mr-2 h-4 w-4" />
          Book Session
        </Button>
      </CardFooter>
    </Card>
  );
}
