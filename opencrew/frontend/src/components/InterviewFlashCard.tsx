'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { RefreshCw } from 'lucide-react'; // Icon for flipping/revealing

// TODO: Fetch actual flashcard Q&A from backend via tRPC
interface FlashCardData {
  id: string | number;
  question: string;
  answer: string;
  topic?: string; // e.g., "Behavioral", "Technical"
}

// Placeholder data
const placeholderCard: FlashCardData = {
  id: 1,
  question: "Tell me about a time you faced a challenging technical problem and how you solved it.",
  answer: "Think STAR method: Situation (Describe the context), Task (What was required?), Action (What did YOU do?), Result (What was the outcome?). Example: Refactored a legacy API endpoint that was causing performance bottlenecks, reducing latency by 70%...",
  topic: "Behavioral / Technical"
};

export function InterviewFlashCard() {
  const [isFlipped, setIsFlipped] = useState(false);
  const [cardData, setCardData] = useState<FlashCardData>(placeholderCard);
  // Placeholder for loading/error state if fetching data
  const isLoading = false; 
  const error = null;

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  // TODO: Implement function to fetch next card
  const handleNextCard = () => {
    console.log("Fetching next card...");
    // Placeholder: Reset to initial card for now
    setCardData(placeholderCard); 
    setIsFlipped(false); 
    // Add tRPC query/mutation call here later
  };

  if (isLoading) {
    return (
      <Card className="w-full max-w-md mx-auto animate-pulse">
        <CardHeader>
          <div className="h-5 bg-grey-20 rounded w-1/4 mb-2"></div>
          <div className="h-6 bg-grey-20 rounded w-3/4"></div>
        </CardHeader>
        <CardContent className="min-h-[150px]">
           <div className="h-4 bg-grey-20 rounded w-full mb-2"></div>
           <div className="h-4 bg-grey-20 rounded w-5/6"></div>
        </CardContent>
        <CardFooter className="flex justify-end">
           <div className="h-9 w-24 bg-grey-20 rounded-md"></div>
        </CardFooter>
      </Card>
    );
  }

  if (error) {
     return (
      <Card className="w-full max-w-md mx-auto border-error/50 bg-error/10 text-error">
        <CardHeader>
          <CardTitle>Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Could not load flashcard.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        {cardData.topic && <CardDescription>{cardData.topic}</CardDescription>}
        <CardTitle className="text-lg">
          {isFlipped ? "Answer" : "Question"}
        </CardTitle>
      </CardHeader>
      <CardContent className="min-h-[150px]"> {/* Ensure minimum height */}
        <p className="text-grey-90">
          {isFlipped ? cardData.answer : cardData.question}
        </p>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={handleFlip}>
          <RefreshCw className="mr-2 h-4 w-4" />
          {isFlipped ? "Show Question" : "Show Answer"}
        </Button>
        {/* TODO: Add button to fetch next card */}
        {/* <Button onClick={handleNextCard}>Next Card</Button> */}
      </CardFooter>
    </Card>
  );
}
