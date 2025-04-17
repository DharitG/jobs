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

      // TODO: Replace with actual fetch call to backend API endpoint
      // e.g., GET /visa/timeline
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500)); 

      // Return mock data for now
      console.log("Returning mock visa timeline data.");
      
      // Validate mock data (good practice)
      const validationResult = z.array(visaTimelineItemSchema).safeParse(MOCK_VISA_DATA);
      if (!validationResult.success) {
          console.error("Mock data validation failed:", validationResult.error);
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Invalid mock data." });
      }
      
      return validationResult.data;
    }),
    
  // Add other visa-related procedures later (e.g., lawyer booking)
});
