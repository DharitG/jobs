"use client";

import { Auth0Provider } from "@auth0/auth0-react";
import { TRPCReactProvider } from "~/trpc/react";
import { type ReactNode } from 'react';

// Read environment variables directly within the Client Component
const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
const auth0ClientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
const auth0Audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE;

interface ClientProvidersProps {
  children: ReactNode;
}

export function ClientProviders({ children }: ClientProvidersProps) {
  // Basic check within the component
  if (!auth0Domain || !auth0ClientId || !auth0Audience) {
    console.error("Auth0 environment variables missing in ClientProviders!");
    return null; // Return null if config is missing
  }

  // Use window.location.origin safely inside the client component
  const redirectUri = typeof window !== 'undefined' ? window.location.origin : '';

  // If redirectUri is not available yet (might happen briefly), 
  // potentially return a loading state or null.
  if (!redirectUri) {
    // Return null while waiting for redirectUri to be determined client-side
    // This prevents children rendering without providers.
    console.warn("Redirect URI not available yet in ClientProviders, waiting..."); 
    return null; 
  }

  return (
    <Auth0Provider
      domain={auth0Domain}
      clientId={auth0ClientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience: auth0Audience,
      }}
    >
      <TRPCReactProvider>{children}</TRPCReactProvider>
    </Auth0Provider>
  );
} 