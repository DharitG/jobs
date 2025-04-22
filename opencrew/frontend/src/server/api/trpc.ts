import { initTRPC, TRPCError } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";
import type { NextRequest } from 'next/server';
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'; // Supabase helper
import { cookies } from 'next/headers'; // To access cookies server-side
import type { User as SupabaseUser } from '@supabase/supabase-js'; // Supabase User type
// import { env } from '~/env.js'; // Removed unused Auth0 env vars

// Define the structure we expect in the context for authenticated users
interface AuthContext {
  user: SupabaseUser;
  accessToken: string; // Access token from Supabase session (will be asserted non-null in protected procedure)
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
  };
};

// Define the context type including the user and accessToken potentially added by middleware
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
  // Create a Supabase client specific to this server-side request context
  // Needs cookies from the request to determine authentication state.
  const cookieStore = cookies(); // Get cookie store from Next.js headers
  // Explicitly type Database as any if types are not generated/available
  const supabase = createRouteHandlerClient<any>({ cookies: () => cookieStore });

  try {
    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
        console.error("[Auth Middleware] Supabase getSession error:", error.message);
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Failed to get session.' });
    }

    if (!session || !session.user || !session.access_token) {
      console.log("[Auth Middleware] No active Supabase session, user, or access token found.");
      throw new TRPCError({ code: "UNAUTHORIZED", message: "Not authenticated." });
    }

    console.log("[Auth Middleware] Supabase session verified for user:", session.user.id);

    // Add the validated Supabase user object and access token to the context
    return next({
      ctx: {
        ...ctx, // Keep existing context (headers, req)
        user: session.user, // Add the Supabase user object
        accessToken: session.access_token, // Add the access token
      },
    });

  } catch (error: any) {
     // Handle potential errors during client creation or session fetching
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
      if (!opts.ctx.user || !opts.ctx.accessToken) {
        // This should technically be caught by enforceUserIsAuthed, but good for type safety
        throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Context enrichment failed.' });
      }
      return opts.next({
        ctx: {
          ...opts.ctx,
          // Assert user and accessToken are non-null for downstream procedures
          user: opts.ctx.user,
          accessToken: opts.ctx.accessToken,
        },
      });
    });
