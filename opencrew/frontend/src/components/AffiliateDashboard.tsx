'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import { Copy, Link, Users, DollarSign } from 'lucide-react'; // Icons
import { useToast } from '~/hooks/use-toast';

// TODO: Fetch affiliate code, stats (clicks, signups, earnings), payout info via tRPC
// TODO: Implement payout request logic

export function AffiliateDashboard() {
  // Placeholder state - replace with tRPC query later
  const [affiliateCode, setAffiliateCode] = useState('PARTNERXYZ'); // Example code
  const [clicks, setClicks] = useState(150);
  const [signups, setSignups] = useState(25);
  const [earnings, setEarnings] = useState(125.50); // Example earnings ($)
  const isLoading = false; // Placeholder
  const error = null; // Placeholder
  const { toast } = useToast();

  const affiliateLink = `https://opencrew.ai/?aff=${affiliateCode}`; // Updated domain

  const handleCopyLink = () => {
    navigator.clipboard.writeText(affiliateLink)
      .then(() => {
        toast({ title: "Link Copied!", description: "Affiliate link copied to clipboard." });
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
        toast({ title: "Copy Failed", description: "Could not copy link.", variant: "destructive" });
      });
  };

  const handlePayoutRequest = () => {
     console.log("Requesting payout...");
     alert("Payout request integration pending.");
     // TODO: Implement payout request mutation
  };

  if (isLoading) {
    return <Card className="animate-pulse h-64"></Card>;
  }

  if (error) {
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading affiliate data.</Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Affiliate Partner Dashboard</CardTitle>
        <CardDescription>Track your referrals and earnings.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Referral Link */}
        <div>
          <Label htmlFor="affiliate-link" className="text-xs font-semibold text-grey-40">Your Unique Referral Link</Label>
          <div className="flex space-x-2 mt-1">
            <Input id="affiliate-link" value={affiliateLink} readOnly />
            <Button variant="outline" size="icon" onClick={handleCopyLink} title="Copy link">
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-grey-40">Clicks</p>
            <p className="text-xl font-semibold flex items-center justify-center">
              <Link className="mr-1 h-4 w-4 text-primary-500" /> {clicks}
            </p>
          </div>
          <div>
            <p className="text-xs text-grey-40">Signups</p>
            <p className="text-xl font-semibold flex items-center justify-center">
               <Users className="mr-1 h-4 w-4 text-primary-500" /> {signups}
            </p>
          </div>
          <div>
            <p className="text-xs text-grey-40">Earnings</p>
            <p className="text-xl font-semibold flex items-center justify-center">
               <DollarSign className="mr-1 h-4 w-4 text-accent" /> {earnings.toFixed(2)}
            </p>
          </div>
        </div>
        
        {/* Payout */}
        <div>
           {/* TODO: Display payout history/threshold */}
           <Button onClick={handlePayoutRequest} disabled={earnings <= 0}> {/* Example condition */}
              Request Payout
           </Button>
        </div>
      </CardContent>
    </Card>
  );
}
