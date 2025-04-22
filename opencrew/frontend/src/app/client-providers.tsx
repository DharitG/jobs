"use client";

import { useState } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { SessionContextProvider } from '@supabase/auth-helpers-react';
import { TRPCReactProvider } from "~/trpc/react";
import { type ReactNode } from 'react';
import type { Database } from '~/lib/supabase_types'; // Assuming you'll create this types file

interface ClientProvidersProps {
  children: ReactNode;
}

// Read Supabase environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export function ClientProviders({ children }: ClientProvidersProps) {
  // Basic check for Supabase config
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error("Supabase environment variables NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are missing!");
    // Optionally return a loading state or an error message component
    return null;
  }

  // useState is needed because createClientComponentClient can only be called
  // inside a Client Component, and we need to pass it to the provider.
  const [supabaseClient] = useState(() =>
    createClientComponentClient<Database>({ // Use your Database types if available
      supabaseUrl: supabaseUrl!,
      supabaseKey: supabaseAnonKey!,
    })
  );

  return (
    <SessionContextProvider supabaseClient={supabaseClient}>
      <TRPCReactProvider>{children}</TRPCReactProvider>
    </SessionContextProvider>
  );
}
