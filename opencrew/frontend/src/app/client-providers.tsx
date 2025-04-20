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

  // No need to manually handle redirectUri here,
  // the Auth0 SDK handles the callback URL automatically.

  return (
    <Auth0Provider
      domain={auth0Domain}
      clientId={auth0ClientId}
      authorizationParams={{
        // redirect_uri is handled automatically by the SDK on callback
        audience: auth0Audience,
      }}
      // The SDK will automatically handle the redirect by checking window.location
      // upon initialization after the redirect from Auth0.
    >
      <TRPCReactProvider>{children}</TRPCReactProvider>
    </Auth0Provider>
  );
}
