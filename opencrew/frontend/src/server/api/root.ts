import { postRouter } from "~/server/api/routers/post";
import { applicationRouter } from "~/server/api/routers/application";
import { visaRouter } from "~/server/api/routers/visa"; // Import visa router
import { jobRouter } from "~/server/api/routers/job"; // Import job router
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
  visa: visaRouter, // Add visa router
  job: jobRouter, // Add job router
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
