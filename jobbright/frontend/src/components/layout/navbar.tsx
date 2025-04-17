"use client"; // Needed for useAuth0 hook

import Link from "next/link";
import { useAuth0 } from "@auth0/auth0-react"; // Import useAuth0
import { Button } from "~/components/ui/button"; // Use ~ alias
import { QuotaRing } from "~/components/QuotaRing"; // Import QuotaRing

export function Navbar() {
  const { isAuthenticated, loginWithRedirect, logout, isLoading, user } = useAuth0();

  const handleSignIn = () => loginWithRedirect();
  const handleSignUp = () => loginWithRedirect({ authorizationParams: { screen_hint: "signup" } });
  // Ensure logout redirects back to the application
  const handleLogOut = () => logout({ logoutParams: { returnTo: window.location.origin } });

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <Link href="/" className="mr-6 flex items-center space-x-2">
          {/* TODO: Add Logo */}
          <span className="font-bold inline-block">JobBright</span>
        </Link>
        <div className="flex flex-1 items-center justify-end space-x-4">
          {/* TODO: Add Navigation Links (Dashboard, Pricing) - Conditionally show Dashboard? */}
          {/* TODO: Add Navigation Links (Dashboard, Pricing) */}
          {isLoading ? (
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-full bg-muted animate-pulse"></div> {/* Placeholder for QuotaRing */}
              <Button variant="ghost" disabled>Loading...</Button>
            </div>
          ) : isAuthenticated ? (
            <>
              {/* TODO: Fetch actual quota data */}
              <QuotaRing remaining={35} total={50} /> 
              {/* TODO: Add user profile picture/dropdown */} 
              {/* <span className="text-sm text-muted-foreground">{user?.email}</span> */} 
              <Button onClick={handleLogOut} variant="ghost">
                Log Out
              </Button>
            </>
          ) : (
            <>
              <Button onClick={handleSignIn} variant="ghost">
                Sign In
              </Button>
              <Button onClick={handleSignUp}>
                Sign Up
              </Button>
            </>
          )}
          {/* TODO: Add User Dropdown / Profile Icon */}
        </div>
      </div>
    </nav>
  );
}
