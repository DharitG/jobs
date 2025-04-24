import { initTRPC, TRPCError } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";
import type { NextRequest } from 'next/server';
// Import createClient instead of createRouteHandlerClient for manual cookie handling
import { createClient, type User as SupabaseUser, type SupabaseClient } from '@supabase/supabase-js';
import { env } from "~/env.js"; // Need env vars for standard client

// Define the structure we expect in the context for authenticated users
interface AuthContext {
  user: SupabaseUser;
  accessToken: string; // Access token from Supabase session (will be asserted non-null in protected procedure)
  supabase: SupabaseClient<any>; // Add the request-specific Supabase client instance
}

/**
 * 1. CONTEXT
 *
 * Defines the context accessible in procedures. Includes the request object
 * and potentially the user session after authentication middleware.
 */
interface CreateContextOptions {
  headers: Headers;
  req: NextRequest;
  // Session/User/Token will be added by middleware, not passed directly during creation
}

export const createTRPCContext = async (opts: CreateContextOptions) => {
  // No need to fetch session here, middleware will handle it
  return {
    headers: opts.headers,
    req: opts.req,
    user: null as SupabaseUser | null, // Initialize user as null
    accessToken: null as string | null, // Initialize accessToken as null
    supabase: null as SupabaseClient<any> | null, // Initialize supabase client as null
  };
};

// Define the context type including the user, accessToken, and supabase client potentially added by middleware
type Context = Awaited<ReturnType<typeof createTRPCContext>> & Partial<AuthContext>;


/**
 * 2. INITIALIZATION
 */
const t = initTRPC.context<Context>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

/**
 * Create a server-side caller.
 */
export const createCallerFactory = t.createCallerFactory;

/**
 * 3. ROUTER & PROCEDURE
 */
export const createTRPCRouter = t.router;

/**
 * Middleware for timing procedure execution (optional).
 */
const timingMiddleware = t.middleware(async ({ next, path }) => {
    const start = Date.now();
    // Removed artificial delay for clarity
    const result = await next();
    const end = Date.now();
    console.log(`[TRPC] ${path} took ${end - start}ms to execute`);
    return result;
});

/**
 * Public (unauthenticated) procedure
 */
export const publicProcedure = t.procedure.use(timingMiddleware);

/**
 * Reusable middleware that enforces users are logged in using Supabase.
 */
const enforceUserIsAuthed = t.middleware(async ({ ctx, next }) => {
  // --- Manual Cookie Handling Approach ---
  const supabase = createClient(
    env.NEXT_PUBLIC_SUPABASE_URL!,
    env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  try {
    // 1. Get the combined auth cookie
    const authCookieName = 'sb-lcrhinqqwewlvprvqzvn-auth-token'; // Use the name found in browser
    const authCookie = ctx.req.cookies.get(authCookieName);

    let user: SupabaseUser | null = null;
    let currentAccessToken: string | null = null;
    let currentRefreshToken: string | null = null;

    if (authCookie?.value) {
       try {
         // 2. Parse the JSON array from the cookie value
         const sessionData = JSON.parse(authCookie.value);
         if (Array.isArray(sessionData) && sessionData.length >= 2) {
             currentAccessToken = sessionData[0]; // First element is Access Token
             currentRefreshToken = sessionData[1]; // Second element is Refresh Token
         } else {
              console.warn(`[Auth Middleware] Invalid format found in cookie ${authCookieName}`);
         }
       } catch (parseError) {
            console.error(`[Auth Middleware] Failed to parse JSON from cookie ${authCookieName}:`, parseError);
       }
    } else {
        console.log(`[Auth Middleware] Auth cookie '${authCookieName}' not found.`);
    }

    // Proceed only if we successfully extracted both tokens
    if (currentAccessToken && currentRefreshToken) {
      // 3. Set the session in the Supabase client manually
      const { error: sessionError } = await supabase.auth.setSession({
        access_token: currentAccessToken,
        refresh_token: currentRefreshToken,
      });

      if (sessionError) {
        console.error("[Auth Middleware] Supabase setSession error:", sessionError.message);
        // Don't throw yet, try getUser to see if session is still somehow valid or if token is expired
      }

      // 4. Verify the user with the manually set session
      const { data: { user: sessionUser }, error: getUserError } = await supabase.auth.getUser();

      if (getUserError) {
        // Log specific getUser errors (e.g., invalid JWT, expired token)
        console.error(`[Auth Middleware] Supabase getUser error after setSession (Code: ${getUserError.code}): ${getUserError.message}`);
        // Only proceed as unauthenticated if getUser fails for reasons other than token issues handled by setSession
      } else if (sessionUser) {
        console.log("[Auth Middleware] Supabase session verified via manual setSession for user:", sessionUser.id);
        user = sessionUser;
        // Access token is already assigned to currentAccessToken from parsed cookie
      } else {
         console.log("[Auth Middleware] No active Supabase user could be derived after setSession.");
      }
    }
    // else: Handled by the check below if tokens weren't extracted


    // 5. Check if authentication was successful (user and token must be non-null)
    if (!user || !currentAccessToken) {
       // Log details if auth failed after attempting token extraction
       if (currentAccessToken || currentRefreshToken) {
           console.log("[Auth Middleware] Authentication failed despite finding tokens. User invalid or expired?");
       }
      throw new TRPCError({ code: "UNAUTHORIZED", message: "Not authenticated." });
    }

    // 6. Add the validated Supabase user object, access token, and client instance to the context
    return next({
      ctx: {
        ...ctx, // Keep existing context (headers, req)
        user: user, // Add the Supabase user object
        accessToken: currentAccessToken, // Add the access token
        supabase: supabase, // Add the request-specific Supabase client (now standard client)
      },
    });

  } catch (error: any) {
     // Handle potential errors during client creation or session verification
     if (error instanceof TRPCError) {
         throw error; // Re-throw known TRPC errors
     }
     console.error("[Auth Middleware] Unexpected error:", error.message || error);
     throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Authentication check failed unexpectedly." });
  }
});

/**
 * Protected (authenticated) procedure
 * Guarantees `ctx.user` is a valid Supabase User object and `ctx.accessToken` is a string.
 */
export const protectedProcedure = t.procedure
  .use(timingMiddleware)
  .use(enforceUserIsAuthed)
  // Add refinement to guarantee user and accessToken are not null in protected procedures type-wise
  .use(opts => {
      // Also ensure the supabase client is present in the context
      if (!opts.ctx.user || !opts.ctx.accessToken || !opts.ctx.supabase) {
        // This should technically be caught by enforceUserIsAuthed, but good for type safety
        throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Context enrichment failed.' });
      }
      return opts.next({
        ctx: {
          ...opts.ctx,
          // Assert user, accessToken, and supabase are non-null for downstream procedures
          user: opts.ctx.user,
          accessToken: opts.ctx.accessToken,
          supabase: opts.ctx.supabase,
        },
      });
    });
