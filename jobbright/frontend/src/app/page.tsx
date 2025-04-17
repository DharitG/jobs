import { AuthButtons } from "~/components/AuthButtons";
import { HydrateClient } from "~/trpc/server"; // Keep HydrateClient if needed for other server components potentially used here later

export default function Home() {
  // Removed the hello tRPC query and prefetch

  return (
    <HydrateClient> {/* Keep HydrateClient wrapper */}
      <main className="flex min-h-screen flex-col items-center bg-grey-5 text-grey-90">
        {/* Navbar would typically go in layout.tsx, but AuthButtons are here for now */}
        <div className="absolute top-4 right-4 z-10">
          <AuthButtons />
        </div>

        <div className="container flex flex-col items-center justify-center gap-8 px-4 py-16 text-center">
          <h1 className="font-display text-4xl font-bold tracking-tight sm:text-6xl">
            Stop applying. <span className="text-primary-500">Start interviewing.</span>
          </h1>
          <p className="max-w-2xl text-lg text-grey-40 sm:text-xl">
            50 fully-tailored applications in the next hour—while you grab coffee.
          </p>
          {/* Placeholder for a primary call-to-action button */}
          {/* <Button size="lg">Get Started</Button> */}

          {/* Removed T3 links, LatestPost, and ProfileImport */}
        </div>

        {/* Placeholder for other landing page sections */}
        {/* <section className="w-full py-12"> ... </section> */}

        {/* Footer would typically go in layout.tsx */}
      </main>
    </HydrateClient>
  );
}
