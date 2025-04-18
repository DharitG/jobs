'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '~/components/ui/card';
import { Label } from '~/components/ui/label';
import { Switch } from '~/components/ui/switch'; // Correct path for Switch
import { Button } from '~/components/ui/button'; // For potential "Connect Slack" button
import { useToast } from '~/hooks/use-toast';

// TODO: Fetch current Slack alert settings via tRPC
// TODO: Implement mutation to update settings via tRPC
// TODO: Implement Slack connection flow (OAuth?)

export function SlackAlertSettings() {
  // Placeholder state - replace with tRPC query later
  const [isEnabled, setIsEnabled] = useState(false); 
  const [isConnecting, setIsConnecting] = useState(false); // Example state for connection process
  const isLoading = false; // Placeholder for loading settings
  const error = null; // Placeholder for error loading settings
  const { toast } = useToast();

  const handleToggleChange = (checked: boolean) => {
    console.log("Slack alerts toggled:", checked);
    // TODO: Call tRPC mutation to update setting
    setIsEnabled(checked); // Optimistic update
    toast({ title: "Settings Updated", description: `Slack alerts ${checked ? 'enabled' : 'disabled'}.` });
  };

  const handleConnectSlack = () => {
     console.log("Connecting to Slack...");
     setIsConnecting(true);
     // TODO: Initiate Slack OAuth flow or backend connection process
     alert("Slack connection flow pending.");
     setTimeout(() => setIsConnecting(false), 1500); // Simulate connection attempt
  };

  if (isLoading) {
    return <Card className="animate-pulse h-24"></Card>;
  }

  if (error) {
    return <Card className="border-error/50 bg-error/10 text-error p-4">Error loading Slack settings.</Card>;
  }

  // Placeholder: Assume not connected yet
  const isConnected = false; 

  return (
    <Card>
      <CardHeader>
        <CardTitle>Slack Alerts</CardTitle>
        <CardDescription>Receive notifications for important events directly in Slack.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!isConnected ? (
           <div className="flex flex-col items-start space-y-2">
             <p className="text-sm text-grey-40">Connect your Slack workspace to enable alerts.</p>
             <Button onClick={handleConnectSlack} disabled={isConnecting}>
                {isConnecting ? 'Connecting...' : 'Connect to Slack'}
             </Button>
           </div>
        ) : (
           <div className="flex items-center space-x-2">
             <Switch
               id="slack-alerts"
               checked={isEnabled}
               onCheckedChange={handleToggleChange}
             />
             <Label htmlFor="slack-alerts">Enable Slack Notifications</Label>
           </div>
           // TODO: Add configuration options (e.g., which channel, which events)
        )}
      </CardContent>
    </Card>
  );
}
