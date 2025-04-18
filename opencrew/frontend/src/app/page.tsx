import { HydrateClient } from "~/trpc/server"; // Keep HydrateClient for tRPC setup

// Import all the landing page sections
import { HeroSection } from "~/components/landing/HeroSection";
import { TrustBar } from "~/components/landing/TrustBar";
import { ProductTourSection } from "~/components/landing/ProductTourSection";
import { WowFeaturesGrid } from "~/components/landing/WowFeaturesGrid";
import { HowItWorksSection } from "~/components/landing/HowItWorksSection";
import { TestimonialCarousel } from "~/components/landing/TestimonialCarousel";
import { PricingSection } from "~/components/landing/PricingSection";
// Removed GuaranteeSection import
import { FaqSection } from "~/components/landing/FaqSection";
import { FinalCtaSection } from "~/components/landing/FinalCtaSection";

// Note: Navbar and Footer are typically placed in layout.tsx for sitewide consistency.
// This page component renders the main content between the Navbar and Footer.

export default function Home() {
  return (
    <HydrateClient> {/* Keep HydrateClient wrapper */}
      <main className="flex flex-col bg-white"> {/* Use white background as base, sections override */}
        {/* Render sections in order */}
        <HeroSection />
        <TrustBar />
        <ProductTourSection />
        <WowFeaturesGrid />
        <HowItWorksSection />
        <TestimonialCarousel />
        <PricingSection />
        {/* Removed GuaranteeSection component */}
        <FaqSection />
        <FinalCtaSection />
      </main>
    </HydrateClient>
  );
}
