'use client';

import React from 'react';
import { useSupabaseClient, useUser } from '@supabase/auth-helpers-react';
import { Button } from './ui/button';
import type { Database } from '~/lib/supabase_types'; // Use type-only import
import { useRouter } from 'next/navigation'; // Import useRouter for navigation

export function AuthButtons() {
  const supabase = useSupabaseClient<Database>();
  const user = useUser();
  const router = useRouter(); // Initialize router

  // Navigate to the sign-in page
  const handleLogin = () => {
    router.push('/sign-in');
  };

  // Navigate to the sign-up page
  const handleSignUp = () => {
    router.push('/sign-up');
  };

  // Handle logout
  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error('Error logging out:', error.message);
      // TODO: Show user-friendly error message
    }
    // You might want to redirect after logout, e.g., router.push('/');
  };

  return (
    <div className="flex items-center gap-4"> {/* Use flex container */}
      {!user && (
        <> {/* Fragment to return multiple buttons */}
          <Button
            variant="ghost" // Keep variant as ghost/secondary equivalent
            onClick={handleLogin}
            className="text-sm font-medium text-grey-40 hover:text-grey-90 dark:text-neutral-300" // Apply old styles
          >
            Log In
          </Button>
          <Button
            variant="default" // Keep variant as primary equivalent
            onClick={handleSignUp}
            className="text-sm" // Apply old styles
          >
            Get Started {/* Change text back to Get Started */}
          </Button>
        </>
      )}

      {user && (
        <Button
          variant="secondary" // Or ghost, depending on desired prominence
          onClick={handleLogout}
          className="border-primary-500 text-primary-500 hover:bg-primary-500/10 transition-all duration-150 ease-out text-sm" // Apply style from provided old AuthButton snippet
        >
          Log Out
        </Button>
      )}
    </div>
  );
}