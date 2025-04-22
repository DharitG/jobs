import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import type { Database } from '~/lib/supabase_types'; // Assuming types exist

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();

  // Create a Supabase client configured to use cookies
  const supabase = createMiddlewareClient<Database>({ req, res });

  // Refresh session if expired - important!
  await supabase.auth.getSession();

  // Optionally, you could add logic here to protect routes based on session:
  // const { data: { session } } = await supabase.auth.getSession();
  // if (!session && req.nextUrl.pathname.startsWith('/dashboard')) {
  //   // Redirect unauthenticated users trying to access protected routes
  //   const redirectUrl = req.nextUrl.clone();
  //   redirectUrl.pathname = '/sign-in';
  //   return NextResponse.redirect(redirectUrl);
  // }

  return res;
}

// Ensure the middleware is only called for relevant paths.
// Adjust the matcher config based on your project structure and needs.
// Avoid matching API routes, static files (_next/static), images, etc.
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - assets (public assets) - Adjust if your public assets folder is different
     * - logos (public logos) - Adjust if your public assets folder is different
     */
    '/((?!api|_next/static|_next/image|favicon.ico|assets|logos).*)',
  ],
};