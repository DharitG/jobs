import "~/styles/globals.css";

import { Inter } from "next/font/google";
import { cookies } from "next/headers";

import { TRPCReactProvider } from "~/trpc/react";
import { ClientProviders } from "./client-providers"; // Import the client provider wrapper
import { ConditionalLayout } from "~/components/layout/conditional-layout"; // Import ConditionalLayout
import { Toaster } from "~/components/ui/toaster"; // Import Toaster

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

// Updated SEO metadata as per spec
export const metadata = {
  title: "OpenCrew – 1-Click Auto‑Apply & Visa‑Safe Job Search", // Updated name
  description: "OpenCrew cuts weeks off your job hunt with AI‑tailored applications, warm intros, and visa‑safe filters. Land interviews faster – free to start.", // Updated name
  icons: [{ rel: "icon", url: "/favicon.ico" }],
  openGraph: {
    title: "OpenCrew – 1-Click Auto‑Apply & Visa‑Safe Job Search", // Updated name
    description: "OpenCrew cuts weeks off your job hunt with AI‑tailored applications, warm intros, and visa‑safe filters. Land interviews faster – free to start.", // Updated name
    url: 'https://opencrew.io', // Corrected production URL
    siteName: 'OpenCrew', // Updated name
    images: [
      {
        url: '/assets/image.png', // Updated OG image path
        width: 1200, // Standard OG image width
        height: 630, // Standard OG image height
        alt: 'OpenCrew Hero Image', // Updated name
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "OpenCrew – 1-Click Auto‑Apply & Visa‑Safe Job Search", // Updated name
    description: "OpenCrew cuts weeks off your job hunt with AI‑tailored applications, warm intros, and visa‑safe filters. Land interviews faster – free to start.", // Updated name
    images: ['/assets/image.png'], // Updated Twitter image path
    // site: '@opencrew', // Replace with actual Twitter handle
    // creator: '@opencrew', // Replace with actual Twitter handle
  },
  // Add other relevant metadata like keywords, author etc. if needed
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`font-sans ${inter.variable}`}>
        <TRPCReactProvider> {/* Removed cookies prop */}
          <ClientProviders> {/* Wrap content with ClientProviders */}
            <ConditionalLayout>{children}</ConditionalLayout> {/* Use ConditionalLayout */}
            <Toaster /> {/* Add Toaster for notifications */}
          </ClientProviders>
        </TRPCReactProvider>
      </body>
    </html>
  );
}
