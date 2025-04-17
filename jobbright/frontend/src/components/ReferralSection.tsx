'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label'; // Import Label
import { Copy, Gift } from 'lucide-react'; // Icons
import { useToast } from '~/hooks/use-toast';

// TODO: Fetch referral code, credits, and history via tRPC
// TODO: Implement logic to copy referral link

export function ReferralSection() {
  // Placeholder state - replace with tRPC query later
  const [referralCode, setReferralCode] = useState('JOBBRIGHT123'); // Example code
  const [creditsEarned, setCreditsEarned] = useState(10); // Example credits ($)
  const isLoading = false; // Placeholder
  const error = null; // Placeholder
  const { toast } = useToast();

  const referralLink = `https://jobbright.ai/signup?ref=${referralCode}`;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(referralLink)
      .then(() => {
        toast({ title: "Link Copied!", description: "Referral link copied to clipboard." });
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
        toast({ title: "Copy Failed", description: "Could not copy link.", variant: "destructive" });
      });
  };

  if (isLoading) {
    return <Card className="animate-pulse h-48"></Card>;
  }

  if (error) {
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading referral data.</Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Gift className="mr-2 h-5 w-5 text-primary-500" />
          Referrals & Credits
        </CardTitle>
        <CardDescription>Share JobBright and earn credits towards your subscription.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="referral-link" className="text-xs font-semibold text-grey-40">Your Referral Link</Label>
          <div className="flex space-x-2 mt-1">
            <Input id="referral-link" value={referralLink} readOnly />
            <Button variant="outline" size="icon" onClick={handleCopyLink} title="Copy link">
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <p className="text-sm">
            Credits Earned: <span className="font-semibold text-accent">${creditsEarned}</span>
          </p>
          {/* TODO: Display referral history/status */}
        </div>
      </CardContent>
      {/* <CardFooter>
        <p className="text-xs text-grey-40">Credits are applied automatically to your next bill.</p>
      </CardFooter> */}
    </Card>
  );
}
