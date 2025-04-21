import { z } from "zod";
import { createTRPCRouter, protectedProcedure } from "~/server/api/trpc";
import { env } from "~/env"; // Using t3-env for backend URL
import { TRPCError } from "@trpc/server";
import { getAccessToken } from "@auth0/nextjs-auth0"; // Added import

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
  parseAndTailor: protectedProcedure
    .input(ResumeParseRequestSchema)
    .output(ResumeParseResponseSchema) // Define expected output structure
    .mutation(async ({ ctx, input }) => {
      const backendUrl = env.NEXT_PUBLIC_BACKEND_API_URL; // Get backend URL from env
      const apiEndpoint = `${backendUrl}/api/v1/resumes/parse-and-tailor`;
      // Retrieve access token for backend API
      let accessToken: string | undefined;
      try {
          // Note: getAccessToken requires {req, res} which might not be directly in ctx depending on setup.
          // This assumes ctx.req and ctx.res are available, which might need adjustment in trpc.ts context creation.
          // If ctx.req/res aren't available, this approach won't work server-side directly in tRPC middleware/procedure.
          // An alternative is passing the token from the client, but less secure.
          // *** Check your tRPC context setup to ensure req/res are passed ***
          if (ctx.req && ctx.res) {
              const tokenResult = await getAccessToken(ctx.req, ctx.res, {
                  scopes: [], // Add necessary scopes if backend API requires them
              });
              accessToken = tokenResult.accessToken;
          }
      } catch (error) {
           console.error("[tRPC] Failed to get access token:", error);
           throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Could not retrieve access token." });
      }


      if (!accessToken) {
          throw new TRPCError({ code: "UNAUTHORIZED", message: "Access token is missing." });
      }
      if (!backendUrl || backendUrl === "https://your-backend-deployment-url-here") {
           throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Backend API URL is not configured." });
      }


      console.log(`[tRPC] Calling backend: ${apiEndpoint} for user ${ctx.session.user.sub}, resume ID: ${input.resume_id}`);


      try {
        const response = await fetch(apiEndpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${accessToken}`,
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