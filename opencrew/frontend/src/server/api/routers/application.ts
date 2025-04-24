import { z } from "zod";
import { TRPCError } from "@trpc/server"; // Import TRPCError

import {
  createTRPCRouter,
  protectedProcedure, // Assuming users must be logged in
  // publicProcedure, // Use if endpoint should be public
} from "~/server/api/trpc";
import { env } from "~/env.js"; // Use ~ alias which should be configured in tsconfig

// Define the expected structure from the backend API
// This should match schemas.Application in the backend, adjust as needed
const applicationSchema = z.object({
  id: z.number(), // Or z.string() if UUIDs are used
  job_id: z.number(), // Or z.string()
  user_id: z.number(), // Or z.string()
  status: z.enum(['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Wishlist']), // Match backend enum/states
  application_date: z.string().datetime().optional().nullable(), // Assuming ISO string format
  notes: z.string().optional().nullable(),
  // Add related Job details if the backend endpoint includes them
  job: z.object({
      id: z.number(), // Or z.string()
      title: z.string(),
      company: z.string(),
      location: z.string().optional().nullable(),
      // Add other relevant job fields like logoUrl, ctaLink if available
  }).optional(), // Make job optional if not always included
});

// Define schema for updating application status
const updateStatusInputSchema = z.object({
  applicationId: z.number(), // Or z.string() if using UUIDs
  newStatus: z.enum(['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Wishlist']), // Must match backend enum
});

export const applicationRouter = createTRPCRouter({
  list: protectedProcedure // Requires user to be logged in
    .query(async ({ ctx }) => {
      // Access user and token directly from the context populated by the middleware
      const userId = ctx.user.id; // Access the user ID directly from ctx.user
      const accessToken = ctx.accessToken; // Access the token directly from ctx.accessToken
      console.log("Attempting to fetch applications for user:", userId);

      // The protectedProcedure already ensures user and accessToken exist.
      // Redundant checks can be removed, but keeping this one for extra safety is fine.
      if (!accessToken) {
        // This check is somewhat redundant due to protectedProcedure but acts as a safeguard.
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Access token missing after authentication middleware.' });
      }

      // 2. Construct Backend API URL
      const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/applications/`; 
      console.log("Fetching applications from:", backendUrl);

      try {
        // 3. Make fetch request
        const response = await fetch(backendUrl, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        // 4. Handle response and errors
        if (!response.ok) {
           const errorText = await response.text(); // Get error text for debugging
           console.error(`Backend error: ${response.status} ${response.statusText}`, errorText);
           const errorData = JSON.parse(errorText || '{}'); // Try parsing JSON error detail
           throw new TRPCError({ 
             code: 'INTERNAL_SERVER_ERROR', 
             message: errorData.detail || `Failed to fetch applications (Status: ${response.status})` 
           });
        }
        const data = await response.json();
        console.log("Received data from backend:", data);

        // 5. Validate data (adjust schema if backend returns nested job details)
        // Assuming backend returns List[schemas.Application] where Application includes Job details
        const backendResponseSchema = z.array(applicationSchema); // Use the schema defined above
        const validationResult = backendResponseSchema.safeParse(data);

        if (!validationResult.success) {
           console.error("Backend API response validation failed:", validationResult.error.flatten());
           throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Invalid data format received from backend.' });
        }
        
        // 6. Map data to the format expected by the frontend component (ApiApplicationItem in dashboard/page.tsx)
        // Ensure the stage mapping is correct
        type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected'; // From dashboard page
        
        const mappedData = validationResult.data.map(app => {
            // Basic mapping, assuming 'status' from backend maps directly to 'stage'
            // Add checks or transformations if needed
            const stage = app.status as ApplicationStage; // Cast needed if enum values differ slightly

            return {
                id: app.id.toString(), // Ensure ID is string if needed by frontend component
                companyName: app.job?.company ?? 'N/A',
                jobTitle: app.job?.title ?? 'N/A',
                location: app.job?.location,
                stage: stage, 
                // logoUrl: app.job?.logoUrl, // Uncomment if backend provides this
                // ctaLink: app.job?.ctaLink, // Uncomment if backend provides this
            };
        });
        console.log("Mapped data for frontend:", mappedData);
        return mappedData;

      } catch (error) {
        // Handle fetch errors or TRPCErrors thrown above
        console.error("Error fetching applications:", error);
        if (error instanceof TRPCError) {
          throw error; // Re-throw TRPC errors
        }
        // Throw a generic error for other fetch issues
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'An unexpected error occurred while fetching applications.' });
      }
    }),

  // Add other procedures like create, update, delete later
  // Example:
  // create: protectedProcedure
  //   .input(z.object({ jobId: z.number(), status: z.string() }))
  //   .mutation(async ({ ctx, input }) => {
  //     // ... implementation ...
  //   }),

  updateStatus: protectedProcedure
    .input(updateStatusInputSchema)
    .mutation(async ({ ctx, input }) => {
      const { applicationId, newStatus } = input;
      // Access user and token directly from the context
      const userId = ctx.user.id;
      const accessToken = ctx.accessToken;

      console.log(`Attempting to update application ${applicationId} to status ${newStatus} for user ${userId}`);

      // Redundant check, protectedProcedure guarantees accessToken exists
      if (!accessToken) {
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Access token missing after authentication middleware.' });
      }

      // Construct backend URL for the specific application
      const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/applications/${applicationId}`;
      
      try {
        const response = await fetch(backendUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          // Backend expects schemas.ApplicationUpdate - send only the status
          body: JSON.stringify({ status: newStatus }), 
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Backend error updating status: ${response.status} ${response.statusText}`, errorText);
          const errorData = JSON.parse(errorText || '{}');
          // Handle specific backend errors like quota exceeded (429)
           if (response.status === 429) {
             throw new TRPCError({
               code: 'TOO_MANY_REQUESTS',
               message: errorData.detail || 'Auto-apply quota reached.',
             });
           }
          throw new TRPCError({
            code: 'INTERNAL_SERVER_ERROR',
            message: errorData.detail || `Failed to update application status (Status: ${response.status})`,
          });
        }

        // Return the updated application data from the backend response
        const updatedApplication = await response.json();
        // Optional: Validate response with applicationSchema if needed
        console.log(`Successfully updated application ${applicationId} status to ${newStatus}`);
        return updatedApplication; // Or return a simple success message

      } catch (error) {
        console.error(`Error updating application ${applicationId} status:`, error);
        if (error instanceof TRPCError) {
          throw error; // Re-throw known TRPC errors
        }
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'An unexpected error occurred while updating application status.' });
      }
    }),
});
