/**
 * YOU PROBABLY DON'T NEED TO EDIT THIS FILE, UNLESS:
 * 1. You want to modify request context (see Part 1).
 * 2. You want to create a new middleware or type of procedure (see Part 3).
 *
 * TL;DR - This is where all the tRPC server stuff is created and plugged in. The pieces you will
 * need to use are documented accordingly near the end.
 */
import { initTRPC, TRPCError } from "@trpc/server";
// Auth0 imports removed as getSession seems incompatible here. Relying on header check for now.
// import { type Session, getSession } from '@auth0/nextjs-auth0/edge'; 
import type { NextRequest } from 'next/server'; // Import NextRequest type
import superjson from "superjson";
import { ZodError } from "zod";
import { jwtVerify, createRemoteJWKSet } from 'jose'; // Import jose for JWT validation
import { env } from '~/env.js'; // Import env variables

// Session type based on validated JWT payload
interface Session {
  user: {
    sub: string; // Auth0 user ID (subject claim from JWT)
    // Add other claims from token if needed (e.g., permissions)
  };
  accessToken: string; // The validated access token
}
// NOTE: We might need access to req/res for getSession.
// This depends on how createTRPCContext is called in the actual API route handler.
// If req/res are not available directly in context, alternative Auth0 validation might be needed.

/**
 * 1. CONTEXT
 *
 * This section defines the "contexts" that are available in the backend API.
 *
 * These allow you to access things when processing a request, like the database, the session, etc.
 *
 * This helper generates the "internals" for a tRPC context. The API handler and RSC clients each
 * wrap this and provides the required context.
 *

/**
 * 1. CONTEXT
 *
 * Defines the context accessible in procedures. Includes the request object
 * and potentially the user session after authentication middleware.
 *
 * @see https://trpc.io/docs/server/context
 */
interface CreateContextOptions {
  headers: Headers;
  req: NextRequest; // Use the imported NextRequest type
  session?: Session | null; // Use the imported Session type
}

export const createTRPCContext = async (opts: CreateContextOptions) => {
  // We might not need to do anything async here initially,
  // but keeping it async allows for future additions (e.g., DB connection per request)
  return {
    headers: opts.headers,
    req: opts.req,
    session: opts.session, // Pass session if already available (e.g., from middleware upstream)
  };
};

// Define the context type including the session potentially added by middleware
type Context = Awaited<ReturnType<typeof createTRPCContext>>;

/**
 * 2. INITIALIZATION
 *
 * This is where the tRPC API is initialized, connecting the context and transformer. We also parse
 * ZodErrors so that you get typesafety on the frontend if your procedure fails due to validation
 * errors on the backend.
 */
const t = initTRPC.context<Context>().create({ // Use the defined Context type
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
 *
 * @see https://trpc.io/docs/server/server-side-calls
 */
export const createCallerFactory = t.createCallerFactory;

/**
 * 3. ROUTER & PROCEDURE (THE IMPORTANT BIT)
 *
 * These are the pieces you use to build your tRPC API. You should import these a lot in the
 * "/src/server/api/routers" directory.
 */

/**
 * This is how you create new routers and sub-routers in your tRPC API.
 *
 * @see https://trpc.io/docs/router
 */
export const createTRPCRouter = t.router;

/**
 * Middleware for timing procedure execution and adding an artificial delay in development.
 *
 * You can remove this if you don't like it, but it can help catch unwanted waterfalls by simulating
 * network latency that would occur in production but not in local development.
 */
const timingMiddleware = t.middleware(async ({ next, path }) => {
  const start = Date.now();

  if (t._config.isDev) {
    // artificial delay in dev
    const waitMs = Math.floor(Math.random() * 400) + 100;
    await new Promise((resolve) => setTimeout(resolve, waitMs));
  }

  const result = await next();

  const end = Date.now();
  console.log(`[TRPC] ${path} took ${end - start}ms to execute`);

  return result;
});

/**
 * Public (unauthenticated) procedure
 *
 * This is the base piece you use to build new queries and mutations on your tRPC API. It does not
 * guarantee that a user querying is authorized, but you can still access user session data if they
 * are logged in.
 */
export const publicProcedure = t.procedure.use(timingMiddleware);

/** Reusable middleware that enforces users are logged in using Auth0. */
const enforceUserIsAuthed = t.middleware(async ({ ctx, next }) => {
  // getSession requires req/res, but we only have req in NextRequest edge/serverless context.
  // Auth0 SDK might handle this internally when passed the request object.
  // Let's try passing the NextRequest directly. Check Auth0 docs if this fails.
  // Note: getSession might not work reliably in all edge environments.
  try {
    // 1. Get token from header
    const authHeader = ctx.headers.get("authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      console.log("[Auth Middleware] No Bearer token found in header.");
      throw new TRPCError({ code: "UNAUTHORIZED", message: "Authorization header missing or invalid." });
    }
    const token = authHeader.split(' ')[1];
    if (!token) {
       console.log("[Auth Middleware] Bearer token value missing.");
       throw new TRPCError({ code: "UNAUTHORIZED", message: "Bearer token missing." });
    }

    // 2. Create JWKSet URL from Auth0 domain
    const JWKS = createRemoteJWKSet(
      new URL(`https://${env.NEXT_PUBLIC_AUTH0_DOMAIN}/.well-known/jwks.json`)
    );

    // 3. Verify the token
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: `https://${env.NEXT_PUBLIC_AUTH0_DOMAIN}/`, // Must match issuer claim in token
      audience: env.NEXT_PUBLIC_AUTH0_AUDIENCE, // Must match audience claim
    });

    // 4. Check if payload and user identifier (sub) exist
    if (!payload || !payload.sub) {
      console.error("[Auth Middleware] JWT verification succeeded but payload or sub claim is missing.");
      throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Invalid token payload." });
    }

    console.log("[Auth Middleware] JWT verified successfully for user:", payload.sub);

    // 5. Add validated session info to context
    const session: Session = {
      user: {
        sub: payload.sub,
        // Add other relevant claims from payload if needed
      },
      accessToken: token,
    };

    return next({
      ctx: {
        ...ctx, // Keep existing context (headers, req)
        session: session, // Add the validated session object
      },
    });

  } catch (error: any) {
     console.error("[Auth Middleware] JWT validation failed:", error.message || error);
     // Handle specific JWT errors (e.g., expired, invalid signature)
     if (error.code === 'ERR_JWT_EXPIRED') {
        throw new TRPCError({ code: "UNAUTHORIZED", message: "Token expired." });
     }
     if (error.code?.startsWith('ERR_JWT')) {
        throw new TRPCError({ code: "UNAUTHORIZED", message: "Invalid token." });
     }
     // Handle JWKS fetch errors
     if (error.code === 'ERR_JOSE_GENERIC' || error.message?.includes('request failed')) {
         throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Could not fetch validation keys." });
     }
     // Generic error
     throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Authentication check failed." });
  }
});

/**
 * Protected (authenticated) procedure
 *
 * If you want a query or mutation to ONLY be accessible to logged in users, use this. It verifies
 * the session is valid and guarantees `ctx.session.user` is not null.
 *
 * @see https://trpc.io/docs/procedures
 */
export const protectedProcedure = t.procedure.use(timingMiddleware).use(enforceUserIsAuthed);
