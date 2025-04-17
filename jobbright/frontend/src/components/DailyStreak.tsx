'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Flame } from 'lucide-react'; // Using Flame icon for streak

// TODO: Fetch actual streak data from backend via tRPC
// Define props if needed (e.g., initial streak count)
interface DailyStreakProps {
  initialStreak?: number;
}

export function DailyStreak({ initialStreak = 0 }: DailyStreakProps) {
  // Placeholder state - replace with tRPC query later
  const [streakCount, setStreakCount] = useState(initialStreak); 
  // Placeholder for loading/error state if fetching data
  const isLoading = false; 
  const error = null;

  if (isLoading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Daily Streak</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center p-6">
          <div className="h-10 w-20 bg-grey-20 rounded-md"></div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Daily Streak</CardTitle>
        </CardHeader>
        <CardContent className="text-center text-error p-6">
          <p>Error loading streak.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Daily Streak</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-center p-6">
        <Flame className={`h-8 w-8 mr-2 ${streakCount > 0 ? 'text-warning' : 'text-grey-40'}`} />
        <span className="text-3xl font-bold text-grey-90">{streakCount}</span>
        <span className="text-sm text-grey-40 ml-1.5">days</span>
      </CardContent>
      {/* Optional: Add encouragement message based on streak */}
      {/* <CardFooter> <p className="text-xs text-center text-grey-40">Keep it up!</p> </CardFooter> */}
    </Card>
  );
}
