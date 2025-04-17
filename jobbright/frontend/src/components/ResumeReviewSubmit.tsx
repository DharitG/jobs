'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Send, CheckCheck, Clock } from 'lucide-react'; // Icons
import { useToast } from '~/hooks/use-toast';

// TODO: Fetch current review status/history via tRPC
// TODO: Implement mutation to submit resume for review via tRPC

export function ResumeReviewSubmit() {
  // Placeholder state - replace with tRPC query later
  const [reviewStatus, setReviewStatus] = useState<'idle' | 'pending' | 'completed'>('idle'); 
  const [lastSubmission, setLastSubmission] = useState<Date | null>(null); // Example
  const isLoading = false; // Placeholder for loading status
  const error = null; // Placeholder for error loading status
  const isSubmitting = false; // Placeholder for submission loading state
  const { toast } = useToast();

  // Placeholder: Assume user is eligible (Elite tier)
  const isEligible = true; 

  const handleSubmitReview = () => {
    console.log("Submitting resume for 24h review...");
    // TODO: Call tRPC mutation
    // mutation.mutate(..., { onSuccess: () => setReviewStatus('pending'), ... })
    alert("Resume review submission pending integration.");
    setReviewStatus('pending'); // Optimistic update
    setLastSubmission(new Date());
    toast({ title: "Review Requested", description: "Your resume has been submitted for review (24h turnaround)." });
  };

  if (!isEligible) {
    // Optionally show an upgrade prompt if not eligible
    return null; 
  }

  if (isLoading) {
    return <Card className="animate-pulse h-36"></Card>;
  }

  if (error) {
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading review status.</Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Guaranteed Résumé Review (24h)</CardTitle>
        <CardDescription>Get expert feedback on your resume within 24 hours.</CardDescription>
      </CardHeader>
      <CardContent>
        {reviewStatus === 'idle' && (
          <p className="text-sm text-grey-40">Submit your latest resume for review.</p>
        )}
        {reviewStatus === 'pending' && lastSubmission && (
          <div className="flex items-center text-sm text-warning">
            <Clock className="mr-2 h-4 w-4" />
            <span>Review pending (Submitted: {lastSubmission.toLocaleString()}). Expected within 24h.</span>
          </div>
        )}
         {reviewStatus === 'completed' && lastSubmission && (
          <div className="flex items-center text-sm text-accent">
            <CheckCheck className="mr-2 h-4 w-4" />
            <span>Review completed! Check your feedback.</span> 
            {/* TODO: Link to feedback */}
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button 
          onClick={handleSubmitReview} 
          disabled={reviewStatus === 'pending' || isSubmitting}
        >
          <Send className="mr-2 h-4 w-4" />
          {reviewStatus === 'pending' ? 'Review Pending' : 'Submit for Review'}
        </Button>
      </CardFooter>
    </Card>
  );
}
