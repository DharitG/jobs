import { z } from "zod";
import { TRPCError } from "@trpc/server";

import {
  createTRPCRouter,
  protectedProcedure, // Assuming visa info requires login
} from "~/server/api/trpc";
import { env } from "~/env.js";

// Define the structure for a timeline item (matches frontend component)
const visaTimelineItemSchema = z.object({
  id: z.union([z.string(), z.number()]),
  date: z.string(), // Keep as string for now, parsing/validation can happen on frontend
  title: z.string(),
  description: z.string().optional(),
  status: z.enum(['Info', 'Action Required', 'Upcoming Deadline', 'Submitted', 'Approved', 'Unknown']),
});

// Mock data for placeholder implementation
const MOCK_VISA_DATA = [
    { id: 1, date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), title: "I-765 Submitted", description: "OPT application sent.", status: "Submitted" },
    { id: 2, date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), title: "Passport Scan Requested", description: "Upload required by ISSS.", status: "Action Required" },
    { id: 3, date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(), title: "Visa Interview Scheduled", description: "Appointment confirmed for next month.", status: "Info" },
    { id: 4, date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(), title: "SEVIS Fee Paid", description: "Confirmation received.", status: "Info" },
    { id: 5, date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), title: "I-20 Received", description: "Document received from university.", status: "Info" },
    { id: 6, date: new Date(Date.now() - 0 * 24 * 60 * 60 * 1000).toISOString(), title: "Check RFE Status", description: "Potential Request for Evidence.", status: "Upcoming Deadline" },
];


export const visaRouter = createTRPCRouter({
  listTimeline: protectedProcedure
    .query(async ({ ctx }) => {
      const userId = ctx.session?.user?.sub;
      console.log(`Fetching visa timeline for user: ${userId}`);

      // 1. Get Access Token
      const accessToken = ctx.session?.accessToken;
      if (!accessToken) {
        throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Access token not found in session.' });
      }

      // 2. Construct Backend API URL (Assuming endpoint is /visa/timeline)
      const backendUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/visa/timeline`; 
      console.log("Fetching visa timeline from:", backendUrl);

      try {
        // 3. Make fetch request
        const response = await fetch(backendUrl, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        // 4. Handle response and errors
        if (!response.ok) {
           const errorText = await response.text();
           console.error(`Backend error fetching visa timeline: ${response.status} ${response.statusText}`, errorText);
           const errorData = JSON.parse(errorText || '{}');
           throw new TRPCError({ 
             code: 'INTERNAL_SERVER_ERROR', 
             message: errorData.detail || `Failed to fetch visa timeline (Status: ${response.status})` 
           });
        }
        const data = await response.json();
        console.log("Received visa timeline data from backend:", data);

        // 5. Validate data using the defined schema
        const validationResult = z.array(visaTimelineItemSchema).safeParse(data);

        if (!validationResult.success) {
           console.error("Backend visa timeline response validation failed:", validationResult.error.flatten());
           throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'Invalid visa timeline data format received from backend.' });
        }
        
        // 6. Return validated data (no extra mapping needed if schema matches frontend)
        console.log("Returning validated visa timeline data.");
        return validationResult.data;

      } catch (error) {
        // Handle fetch errors or TRPCErrors thrown above
        console.error("Error fetching visa timeline:", error);
        if (error instanceof TRPCError) {
          throw error; // Re-throw TRPC errors
        }
        // Throw a generic error for other fetch issues
        throw new TRPCError({ code: 'INTERNAL_SERVER_ERROR', message: 'An unexpected error occurred while fetching the visa timeline.' });
      }
    }),
    
  // Add other visa-related procedures later (e.g., lawyer booking)
});
