"use client";

import Link from "next/link";
import Image from "next/image"; // Import Image component
import { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "~/components/ui/button";
// Removed Sparkles import
import { cn } from "~/lib/utils";
// Removed Confetti and useWindowSize imports

// Note: This Navbar is modified for the landing page spec.
// Original logic for authenticated users (Dashboard link, QuotaRing, Logout) is removed for clarity.
// Consider creating a separate LandingNavbar or adding conditional logic if needed elsewhere.

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const { loginWithRedirect } = useAuth0();
  // Removed showConfetti state and width/height

  // Handle scroll detection
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 32); // Trigger after 32px scroll as per spec
    };
    window.addEventListener("scroll", handleScroll);
    // Initial check in case page loads already scrolled
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogin = () => loginWithRedirect();

  // Reverted handleGetStarted to simple redirect
  const handleGetStarted = () => loginWithRedirect({ authorizationParams: { screen_hint: "signup" } });

  return (
    <nav
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-300 ease-in-out",
        // Apply background and blur effect when scrolled
        scrolled
          ? "border-b border-grey-20 bg-grey-5/90 backdrop-blur supports-[backdrop-filter]:bg-grey-5/90"
          : "bg-transparent border-b border-transparent" // Transparent initially
      )}
      style={{ height: '72px' }} // Set height as per spec
    >
      <div className="container flex h-full max-w-screen-2xl items-center"> {/* Ensure h-full */}
        {/* Logo */}
        <Link href="/" className="mr-auto flex items-center">
          {/* Replace Sparkles and text with Image */}
          <Image
            src="/assets/f5ed6ae4-3d2b-488d-9048-65a12d962da6.png"
            alt="OpenCrew Logo"
            width={120} // Adjust width as needed
            height={30} // Adjust height as needed
            className="h-auto" // Maintain aspect ratio
          />
          {/* Optional: Keep the text name if desired, or remove */}
          {/* <span className="font-bold font-display text-lg text-primary-500 ml-2">OpenCrew</span> */}
        </Link>

        {/* Landing Page Navigation Links & CTA */}
        <div className="flex items-center space-x-4">
          {/* Use specified classes for links */}
          <Link href="/#product-tour" scroll={true} className="mx-4 text-sm font-medium text-grey-40 hover:text-grey-90 transition-colors">
            Product
          </Link>
          <Link href="/#pricing" scroll={true} className="mx-4 text-sm font-medium text-grey-40 hover:text-grey-90 transition-colors">
            Pricing
          </Link>
          {/* Login button using ghost variant */}
          <Button onClick={handleLogin} variant="ghost" size="sm" className="mx-4 text-sm font-medium text-grey-40 hover:text-grey-90">
            Login
          </Button>
          {/* Get Started CTA */}
          <Button onClick={handleGetStarted} variant="default" size="sm">
            Get Started
          </Button>
        </div>
      </div>
    </nav>
  );
}
