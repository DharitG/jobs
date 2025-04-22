import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  /**
   * Specify your server-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars.
   */
  server: {
    NODE_ENV: z.enum(["development", "test", "production"]),
    // Auth0 server-side variables REMOVED
    // AUTH0_SECRET: z.string().min(1),
    // AUTH0_BASE_URL: z.string().url(),
    // AUTH0_ISSUER_BASE_URL: z.string().url(),
    // AUTH0_CLIENT_ID: z.string().min(1),
    // AUTH0_CLIENT_SECRET: z.string().min(1),
  },

  /**
   * Specify your client-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars. To expose them to the client, prefix them with
   * `NEXT_PUBLIC_`.
   */
  client: {
    // NEXT_PUBLIC_CLIENTVAR: z.string(),
    NEXT_PUBLIC_BACKEND_API_URL: z.string().url(),
    // Supabase client-side vars ADDED
    NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
    // Auth0 client-side variables REMOVED
    // NEXT_PUBLIC_AUTH0_DOMAIN: z.string().min(1),
    // NEXT_PUBLIC_AUTH0_AUDIENCE: z.string().min(1),
    // NEXT_PUBLIC_AUTH0_CLIENT_ID: z.string().min(1),
  },

  /**
   * You can't destruct `process.env` as a regular object in the Next.js edge runtimes (e.g.
   * middlewares) or client-side so we need to destruct manually.
   */
  runtimeEnv: {
    NODE_ENV: process.env.NODE_ENV,
    // Server-side Auth0 REMOVED
    // AUTH0_SECRET: process.env.AUTH0_SECRET,
    // AUTH0_BASE_URL: process.env.AUTH0_BASE_URL,
    // AUTH0_ISSUER_BASE_URL: process.env.AUTH0_ISSUER_BASE_URL,
    // AUTH0_CLIENT_ID: process.env.AUTH0_CLIENT_ID,
    // AUTH0_CLIENT_SECRET: process.env.AUTH0_CLIENT_SECRET,
    // Client-side vars
    // NEXT_PUBLIC_CLIENTVAR: process.env.NEXT_PUBLIC_CLIENTVAR,
    NEXT_PUBLIC_BACKEND_API_URL: process.env.NEXT_PUBLIC_BACKEND_API_URL,
    // Supabase Client-side vars ADDED
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    // Auth0 Client-side REMOVED
    // NEXT_PUBLIC_AUTH0_DOMAIN: process.env.NEXT_PUBLIC_AUTH0_DOMAIN,
    // NEXT_PUBLIC_AUTH0_AUDIENCE: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE, // Added back
    // NEXT_PUBLIC_AUTH0_CLIENT_ID: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID,
  },
  /**
   * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially
   * useful for Docker builds.
   */
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
  /**
   * Makes it so that empty strings are treated as undefined. `SOME_VAR: z.string()` and
   * `SOME_VAR=''` will throw an error.
   */
  emptyStringAsUndefined: true,
});
