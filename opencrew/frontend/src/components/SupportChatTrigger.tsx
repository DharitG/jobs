'use client';

import React from 'react';
import { Button } from '~/components/ui/button';
import { MessageSquare } from 'lucide-react'; // Chat icon

// TODO: Integrate with actual chat widget provider (e.g., Intercom, Crisp)
// TODO: Conditionally render based on user plan (Pro/Elite)

export function SupportChatTrigger() {
  
  const handleOpenChat = () => {
    console.log("Opening support chat widget...");
    // Placeholder: Add chat widget SDK call here
    alert("Support chat integration pending."); 
  };

  // Placeholder: Assume user is eligible for chat for now
  const isEligible = true; 

  if (!isEligible) {
    return null; // Don't render if user is not on Pro/Elite
  }

  return (
    <Button
      variant="default" // Or a custom variant
      size="icon"
      className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50" // Floating button style
      onClick={handleOpenChat}
      title="Priority Support Chat"
    >
      <MessageSquare className="h-6 w-6" />
    </Button>
  );
}
