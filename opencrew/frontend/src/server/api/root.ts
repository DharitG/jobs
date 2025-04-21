import { postRouter } from "~/server/api/routers/post";
import { applicationRouter } from "~/server/api/routers/application";
import { visaRouter } from "~/server/api/routers/visa";
import { jobRouter } from "~/server/api/routers/job";
import { resumeRouter } from "~/server/api/routers/resume"; // Added resume router
// import { authRouter } from "~/server/api/routers/auth";
import { createCallerFactory, createTRPCRouter } from "~/server/api/trpc";

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  post: postRouter,
  application: applicationRouter,
  visa: visaRouter,
  job: jobRouter,
  resume: resumeRouter, // Added resume router
  // auth: authRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;

/**
 * Create a server-side caller for the tRPC API.
 * @example
 * const trpc = createCaller(createContext);
 * const res = await trpc.post.all();
 *       ^? Post[]
 */
export const createCaller = createCallerFactory(appRouter);
