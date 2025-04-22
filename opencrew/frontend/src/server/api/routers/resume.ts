import { z } from "zod";
import { createTRPCRouter, protectedProcedure } from "~/server/api/trpc";
import { env } from "~/env"; // Using t3-env for backend URL
import { TRPCError } from "@trpc/server";
// import { getAccessToken } from "@auth0/nextjs-auth0"; // Removed Auth0 import

// Zod schema mirroring Pydantic PdfTextItem
const PdfTextItemSchema = z.object({
  text: z.string(),
  fontName: z.string(),
  width: z.number(),
  height: z.number(),
  x: z.number(),
  y: z.number(),
  hasEOL: z.boolean(),
});

// Zod schema mirroring Pydantic ResumeParseRequest
const ResumeParseRequestSchema = z.object({
  text_items: z.array(PdfTextItemSchema),
  job_description: z.string().optional().nullable(),
  job_id: z.number().optional().nullable(),
  resume_id: z.number().optional().nullable(), // Added resume_id
});

// Zod schema mirroring Pydantic StructuredResume (simplified for now, add details later if needed)
// We mainly care about the structure existing in the response
const StructuredResumeSchema = z.object({
    basic: z.record(z.any()).optional().nullable(),
    objective: z.string().optional().nullable(),
    education: z.array(z.record(z.any())).optional().nullable(),
    experiences: z.array(z.record(z.any())).optional().nullable(),
    projects: z.array(z.record(z.any())).optional().nullable(),
    skills: z.array(z.record(z.any())).optional().nullable(),
});


// Zod schema mirroring Pydantic ResumeParseResponse
const ResumeParseResponseSchema = z.object({
  structured_resume: StructuredResumeSchema,
  message: z.string().optional().nullable(),
});


export const resumeRouter = createTRPCRouter({
  parseAndTailor: protectedProcedure // Uses Supabase authentication via middleware
    .input(ResumeParseRequestSchema)
    .output(ResumeParseResponseSchema) // Define expected output structure
    .mutation(async ({ ctx, input }) => {
      const backendUrl = env.NEXT_PUBLIC_BACKEND_API_URL; // Get backend URL from env
      const apiEndpoint = `${backendUrl}/api/v1/resumes/parse-and-tailor`;

      // Access token is guaranteed by protectedProcedure context refinement
      const accessToken = ctx.accessToken;

      if (!backendUrl || backendUrl === "https://your-backend-deployment-url-here") {
           throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Backend API URL is not configured." });
      }


      console.log(`[tRPC] Calling backend: ${apiEndpoint} for user ${ctx.user.id}, resume ID: ${input.resume_id}`);


      try {
        const response = await fetch(apiEndpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${accessToken}`, // Use token from context
          },
          body: JSON.stringify(input),
        });


        console.log(`[tRPC] Backend response status: ${response.status}`);


        if (!response.ok) {
          let errorBody = "Unknown backend error";
          try {
             const errorJson = await response.json();
             errorBody = errorJson.detail || JSON.stringify(errorJson);
             console.error(`[tRPC] Backend error response:`, errorJson);
          } catch (e) {
             errorBody = await response.text();
             console.error(`[tRPC] Backend error response (non-JSON):`, errorBody);
          }
          throw new TRPCError({
            code: "INTERNAL_SERVER_ERROR", // Adjust code based on status?
            message: `Backend request failed: ${response.status} ${response.statusText} - ${errorBody}`,
          });
        }


        const data: unknown = await response.json();
        console.log(`[tRPC] Backend success response received.`);


        // Validate the response structure before returning
        const validatedData = ResumeParseResponseSchema.safeParse(data);


        if (!validatedData.success) {
            console.error("[tRPC] Backend response validation failed:", validatedData.error);
            throw new TRPCError({
                 code: "INTERNAL_SERVER_ERROR",
                 message: "Received invalid data structure from backend.",
                 cause: validatedData.error,
            });
        }


        console.log(`[tRPC] Successfully parsed and tailored resume via backend.`);
        return validatedData.data;


      } catch (error) {
        console.error("[tRPC] Error in parseAndTailor mutation:", error);
        if (error instanceof TRPCError) {
            throw error; // Re-throw TRPC errors
        }
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: `An unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`,
        });
      }
    }),


  // Add other resume-related procedures here (e.g., get, list, delete - if needed via tRPC)
});