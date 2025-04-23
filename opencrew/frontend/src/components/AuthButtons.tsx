'use client';

import React from 'react';
import { useSupabaseClient, useUser } from '@supabase/auth-helpers-react';
import { Button } from './ui/button';
import type { Database } from '~/lib/supabase_types';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast'; // Import toast for logout feedback

// Define props for the trigger functions
interface AuthButtonsProps {
  onSignInClick: () => void;
  onSignUpClick: () => void;
}

export function AuthButtons({ onSignInClick, onSignUpClick }: AuthButtonsProps) {
  const supabase = useSupabaseClient<Database>();
  const user = useUser();
  const router = useRouter();

  // Removed handleLogin and handleSignUp as they are now handled by props

  // Handle logout remains mostly the same, adding toast feedback
  const handleLogout = async () => {
    const toastId = toast.loading('Logging out...');
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error('Error logging out:', error.message);
      toast.error(`Logout failed: ${error.message}`, { id: toastId });
    } else {
      toast.success('Logged out successfully!', { id: toastId });
      // Redirect to home page after logout for better UX
      router.push('/');
      router.refresh(); // Ensures user state is updated visually
    }
  };

  return (
    <div className="flex items-center gap-4">
      {!user && (
        <>
          {/* Call the functions passed via props */}
          <Button
            variant="ghost"
            onClick={onSignInClick} // Use prop function
            className="text-sm font-medium text-grey-40 hover:text-grey-90 dark:text-neutral-300"
          >
            Log In
          </Button>
          <Button
            variant="default"
            onClick={onSignUpClick} // Use prop function
            className="text-sm"
          >
            Get Started {/* Keep text as Get Started */}
          </Button>
        </>
      )}

      {user && (
        <Button
          variant="secondary"
          onClick={handleLogout}
          className="border-primary-500 text-primary-500 hover:bg-primary-500/10 transition-all duration-150 ease-out text-sm"
        >
          Log Out
        </Button>
      )}
    </div>
  );
}