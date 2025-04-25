import { z } from "zod";
import { TRPCError } from "@trpc/server";

import {
  createTRPCRouter,
  protectedProcedure,
} from "~/server/api/trpc";
import { env } from "~/env.js";

// Define the expected data structure from the backend dashboard endpoint
const dashboardStatsSchema = z.object({
  user_plan: z.string(), // e.g., "Free Plan", "Pro Plan"
  daily_applies_used: z.number().int().nonnegative(),
  daily_apply_limit: z.number().int().positive(),
  total_applications_sent: z.number().int().nonnegative(),
  jobs_matched_today: z.number().int().nonnegative(),
  interview_rate_7d: z.number().nonnegative(), // Assuming percentage 0-100
});

// Define the schema for user preferences (matching backend expectations)
// Adjust fields and types based on the actual backend user model/schema
const userPreferencesSchema = z.object({
  preferred_job_titles: z.array(z.string()).optional().nullable(),
  preferred_locations: z.array(z.string()).optional().nullable(),
  minimum_salary_preference: z.number().int().positive().optional().nullable(), // e.g., 80000, 100000
  // Add other relevant preferences here (e.g., remote_only, visa_sponsorship_needed)
});

// Define the input schema for updating preferences
const updatePreferencesInputSchema = userPreferencesSchema; // Reuse for input validation

export const userRouter = createTRPCRouter({
  getDashboardStats: protectedProcedure // Requires user to be logged in
    .output(dashboardStatsSchema) // Define the expected output structure
    .query(async ({ ctx }) => {
      const userId = ctx.user.id; // User ID from middleware
      const accessToken = ctx.accessToken; // Token from middleware
      console.log("Attempting to fetch dashboard stats for user:", userId);

      // This should always be present due to protectedProcedure
      if (!accessToken) {
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Access token missing.' });
      }

      // --- TODO: Replace with actual backend API call ---
      // const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/users/me/dashboard`; // Example URL
      // console.log("Fetching dashboard stats from:", backendUrl);
      // try {
      //   const response = await fetch(backendUrl, {
      //     headers: {
      //       Authorization: `Bearer ${accessToken}`,
      //     },
      //   });
      //   if (!response.ok) {
      //     const errorText = await response.text();
      //     console.error(`Backend error fetching dashboard stats: ${response.status} ${response.statusText}`, errorText);
      //     const errorData = JSON.parse(errorText || '{}');
      //     throw new TRPCError({
      //       code: 'INTERNAL_SERVER_ERROR',
      //       message: errorData.detail || `Failed to fetch dashboard stats (Status: ${response.status})`,
      //     });
      //   }
      //   const data = await response.json();
      //   console.log("Received dashboard stats data from backend:", data);
      //
      //   // Validate data against the schema
      //   const validationResult = dashboardStatsSchema.safeParse(data);
      //   if (!validationResult.success) {
      //      console.error("Backend dashboard stats validation failed:", validationResult.error.flatten());
      //      throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Invalid dashboard stats format received from backend.' });
      //   }
      //   return validationResult.data;
      // } catch (error) {
      //   console.error("Error fetching dashboard stats:", error);
      //   if (error instanceof TRPCError) {
      //     throw error; // Re-throw TRPC errors
      //   }
      //   throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'An unexpected error occurred while fetching dashboard stats.' });
      // }
      // --- End TODO ---

      // --- Placeholder Data (Remove once API call is implemented) ---
      console.warn("Using placeholder dashboard stats data!");
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      return {
        user_plan: "Free Plan (Mock)",
        daily_applies_used: 15,
        daily_apply_limit: 50,
        total_applications_sent: 1234,
        jobs_matched_today: 80,
        interview_rate_7d: 12.0,
      };
      // --- End Placeholder Data ---
    }),

 // Procedure to get user preferences
 getPreferences: protectedProcedure
   .output(userPreferencesSchema)
   .query(async ({ ctx }) => {
     const userId = ctx.user.id;
     const accessToken = ctx.accessToken;
     console.log("Attempting to fetch preferences for user:", userId);

     if (!accessToken) {
       throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Access token missing.' });
     }

     // --- TODO: Replace with actual backend API call to fetch preferences ---
     // Example: GET /api/users/me
     // const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/users/me`;
     // try {
     //   const response = await fetch(backendUrl, { /* headers with auth */ });
     //   if (!response.ok) throw new Error("Failed to fetch preferences");
     //   const data = await response.json();
     //   // Assuming backend returns the full user object, parse it
     //   const validationResult = userPreferencesSchema.safeParse(data.preferences ?? {}); // Adjust based on actual response structure
     //   if (!validationResult.success) throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Invalid preference data from backend.' });
     //   return validationResult.data;
     // } catch (error) { /* Handle errors */ }
     // --- End TODO ---

     // --- Placeholder Data ---
     console.warn("Using placeholder user preferences!");
     await new Promise(resolve => setTimeout(resolve, 300));
     return {
       preferred_job_titles: ["swe"], // Match value from SelectItem
       preferred_locations: ["remote"], // Match value from SelectItem
       minimum_salary_preference: 100000, // Representing $100k+
     };
     // --- End Placeholder Data ---
   }),

 // Procedure to update user preferences
 updatePreferences: protectedProcedure
   .input(updatePreferencesInputSchema)
   .mutation(async ({ ctx, input }) => {
     const userId = ctx.user.id;
     const accessToken = ctx.accessToken;
     console.log(`Attempting to update preferences for user ${userId}:`, input);

     if (!accessToken) {
       throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Access token missing.' });
     }

     // --- TODO: Replace with actual backend API call to update preferences ---
     // Example: PUT /api/users/me or PATCH /api/users/me/preferences
     // const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/users/me/preferences`; // Example
     // try {
     //   const response = await fetch(backendUrl, {
     //     method: 'PATCH', // or PUT
     //     headers: {
     //       'Content-Type': 'application/json',
     //       Authorization: `Bearer ${accessToken}`,
     //     },
     //     body: JSON.stringify(input),
     //   });
     //   if (!response.ok) {
     //     const errorText = await response.text();
     //     console.error(`Backend error updating preferences: ${response.status}`, errorText);
     //     throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Failed to update preferences.' });
     //   }
     //   // const updatedData = await response.json(); // Optional: return updated prefs
     //   console.log("Preferences updated successfully via backend.");
     //   return { success: true };
     // } catch (error) { /* Handle errors */ }
     // --- End TODO ---

     // --- Placeholder Logic ---
     console.warn("Simulating preference update!");
     await new Promise(resolve => setTimeout(resolve, 500));
     // Simulate potential failure? For now, assume success.
     if (input.preferred_job_titles?.includes("fail")) { // Example failure condition
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Simulated backend failure updating preferences.' });
     }
     return { success: true };
     // --- End Placeholder Logic ---
   }),
});