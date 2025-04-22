import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import type { Database } from '~/lib/supabase_types'; // Assuming types exist

export const dynamic = 'force-dynamic'; // Ensure dynamic handling

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');

  if (code) {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient<Database>({ cookies: () => cookieStore });
    try {
      await supabase.auth.exchangeCodeForSession(code);
      // Successfully exchanged code for session
    } catch (error) {
      console.error("Error exchanging code for session:", error);
      // Handle the error appropriately, maybe redirect to an error page
      // For now, redirecting back to the origin might prompt login again
      return NextResponse.redirect(requestUrl.origin + '/error?message=AuthCallbackFailed');
    }
  } else {
    console.warn("Callback received without a code parameter.");
    // Handle missing code, maybe redirect to login
     return NextResponse.redirect(requestUrl.origin + '/sign-in?message=CallbackCodeMissing');
  }

  // URL to redirect to after sign in process completes
  // Defaulting to origin (homepage) or a dashboard page
  return NextResponse.redirect(requestUrl.origin + '/dashboard'); // Adjust target route as needed
}