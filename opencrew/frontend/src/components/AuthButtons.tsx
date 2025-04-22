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
            variant="ghost" // Make login look like text
            onClick={handleLogin}
            className="text-sm font-medium text-grey-90 hover:text-grey-60 dark:text-neutral-300 dark:hover:text-neutral-100" // Ensure text color visible
          >
            Log In
          </Button>
          <Button
            variant="default" // Primary button style for sign up
            onClick={handleSignUp}
            className="bg-primary-500 hover:bg-primary-600 text-white shadow-1 hover:-translate-y-px hover:shadow-md transition-all duration-150 ease-out text-sm"
          >
            Sign Up
          </Button>
        </>
      )}

      {user && (
        <Button
          variant="secondary" // Or ghost, depending on desired prominence
          onClick={handleLogout}
          className="border-primary-500 text-primary-500 hover:bg-primary-500/10 transition-all duration-150 ease-out text-sm"
        >
          Log Out
        </Button>
      )}
    </div>
  );
}