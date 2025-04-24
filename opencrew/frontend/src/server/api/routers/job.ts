import { z } from "zod";
import { createTRPCRouter, protectedProcedure } from "~/server/api/trpc";
import { TRPCError } from "@trpc/server";

// Placeholder for the expected shape of a Job object returned by the backend API
// Adapt this based on the actual backend schema (schemas/job.py -> Job)
const jobSchema = z.object({
  id: z.number(),
  title: z.string(),
  company: z.string(),
  location: z.string().nullable(),
  url: z.string().url(),
  description: z.string().nullable(),
  source: z.string().nullable(),
  date_posted: z.date().nullable(),
  // Add other relevant fields like visa_sponsorship_available if needed
});

export const jobRouter = createTRPCRouter({
  /**
   * Fetches jobs matched to the user's primary resume.
   */
  getMatchedJobs: protectedProcedure
    .input(z.object({ limit: z.number().optional().default(20) }))
    .output(z.array(jobSchema)) // Define the expected output shape
    .query(async ({ ctx, input }) => {
      const userId = ctx.user.id; // Access the user ID directly from ctx.user

      console.log(`Fetching matched jobs for user: ${userId}`);

      // --- Step 1: Get User's Resume Embedding (Requires Backend API Endpoint) ---
      let resumeEmbedding: number[] | null = null;
      try {
        // TODO: Replace with actual backend API call
        // Example: const embeddingResponse = await fetch(`${process.env.BACKEND_API_URL}/users/me/resume/embedding`, { headers: ctx.authHeaders });
        // if (!embeddingResponse.ok) throw new Error("Failed to fetch resume embedding");
        // const embeddingData = await embeddingResponse.json();
        // resumeEmbedding = embeddingData.embedding; // Assuming the structure

        // Placeholder implementation:
        console.warn("Placeholder: Fetching resume embedding is not implemented.");
        // Simulate finding an embedding for testing purposes
        // In a real scenario, fetch this from the backend based on the user's resume
        // resumeEmbedding = Array(384).fill(0.1); // Example embedding

        if (!resumeEmbedding) {
           console.log(`User ${userId} has no resume embedding found.`);
           return []; // Return empty if no embedding
        }

      } catch (error) {
        console.error("Error fetching resume embedding:", error);
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: "Failed to get user resume embedding.",
          cause: error,
        });
      }

       // --- Step 2: Search Qdrant via Backend API (Requires Backend API Endpoint) ---
      let matchedJobIds: number[] = [];
      try {
          // TODO: Replace with actual backend API call to search Qdrant
          // Example: const searchResponse = await fetch(`${process.env.BACKEND_API_URL}/jobs/search/similar`, {
          //   method: 'POST',
          //   headers: { ...ctx.authHeaders, 'Content-Type': 'application/json' },
          //   body: JSON.stringify({ embedding: resumeEmbedding, limit: input.limit })
          // });
          // if (!searchResponse.ok) throw new Error("Failed to search similar jobs");
          // const searchData = await searchResponse.json(); // Assuming backend returns { results: [{id: number, score: number}, ...] }
          // matchedJobIds = searchData.results.map((hit: { id: number }) => hit.id);

          // Placeholder implementation:
          console.warn("Placeholder: Searching similar jobs via backend is not implemented.");
          // Simulate finding some job IDs for testing
          // matchedJobIds = [1, 5, 10]; // Example job IDs

          if (matchedJobIds.length === 0) {
              console.log(`No similar jobs found for user ${userId}`);
              return [];
          }

      } catch (error) {
          console.error("Error searching for similar jobs:", error);
          throw new TRPCError({
              code: "INTERNAL_SERVER_ERROR",
              message: "Failed to search for similar jobs.",
              cause: error,
          });
      }

      // --- Step 3: Fetch Job Details from Backend API (Requires Backend API Endpoint) ---
      try {
          // TODO: Replace with actual backend API call to get jobs by IDs
          // Example: const jobsResponse = await fetch(`${process.env.BACKEND_API_URL}/jobs/batch`, {
          //   method: 'POST',
          //   headers: { ...ctx.authHeaders, 'Content-Type': 'application/json' },
          //   body: JSON.stringify({ job_ids: matchedJobIds })
          // });
          // if (!jobsResponse.ok) throw new Error("Failed to fetch job details");
          // const jobsData = await jobsResponse.json(); // Assuming backend returns list of job objects
          // const validatedJobs = z.array(jobSchema).parse(jobsData); // Validate against schema
          // return validatedJobs;

          // Placeholder implementation:
          console.warn("Placeholder: Fetching job details by ID is not implemented.");
          // Simulate returning dummy job data for testing
          const dummyJobs = matchedJobIds.map(id => ({
              id: id,
              title: `Software Engineer ${id}`,
              company: `Tech Corp ${id}`,
              location: "Remote",
              url: `https://example.com/job/${id}`,
              description: `Description for job ${id}`,
              source: "Indeed",
              date_posted: new Date(),
          }));
          const validatedJobs = z.array(jobSchema).parse(dummyJobs);
          return validatedJobs;

      } catch (error) {
          console.error("Error fetching job details:", error);
           if (error instanceof z.ZodError) {
               console.error("Zod validation error:", error.issues);
                throw new TRPCError({
                    code: "INTERNAL_SERVER_ERROR",
                    message: "Failed to validate job data from backend.",
                    cause: error,
                });
           }
          throw new TRPCError({
              code: "INTERNAL_SERVER_ERROR",
              message: "Failed to fetch job details.",
              cause: error,
          });
      }
    }),

  // Add other job-related procedures here later (e.g., getJobById, etc.)
});
