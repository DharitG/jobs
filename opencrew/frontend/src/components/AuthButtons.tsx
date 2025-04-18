'use client';

import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from './ui/button'; // Assuming shadcn/ui button is here

export function AuthButtons() {
  const { loginWithRedirect, logout, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <Button variant="outline" disabled>Loading...</Button>; // Use outline or ghost for loading
  }

  return (
    <div>
      {!isAuthenticated && (
        <Button
          variant="default" // shadcn's default often maps to primary
          onClick={() => loginWithRedirect()}
          className="bg-primary-500 hover:bg-primary-600 text-white shadow-1 hover:-translate-y-px hover:shadow-md transition-all duration-150 ease-out" // Apply design system styles
        >
          Log In
        </Button>
      )}

      {isAuthenticated && (
        <Button
          variant="secondary" // Or ghost, depending on desired prominence
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          className="border-primary-500 text-primary-500 hover:bg-primary-500/10 transition-all duration-150 ease-out" // Apply design system styles
        >
          Log Out
        </Button>
      )}
    </div>
  );
} 