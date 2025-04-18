"use client"; // Required for useState and hooks

// Remove unused imports
// import { useState } from "react";
// import { useRouter } from "next/navigation"; // For redirection
import { useAuth0 } from "@auth0/auth0-react"; // Import useAuth0
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import Link from "next/link";
// import { api } from "~/trpc/react"; // Use ~ alias for tRPC
import type { RouterOutputs } from "~/trpc/react"; // Import RouterOutputs for type safety
import type { TRPCClientError } from "@trpc/client"; // Import error type
import type { AppRouter } from "~/server/api/root"; // Import AppRouter for error type
import { Chrome } from "lucide-react"; // Import Google icon

export default function SignInPage() {
  const { loginWithRedirect, isLoading } = useAuth0(); // Get login function and loading state

  const handleGoogleSignIn = () => {
    loginWithRedirect({
      authorizationParams: {
        connection: 'google-oauth2', // Specify Google connection
      },
    });
  };

  const handleEmailSignIn = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // For email/password, Auth0 Universal Login handles the form,
    // so we just trigger the redirect without specific connection.
    loginWithRedirect(); 
  };

  return (
    <div className="container flex h-[calc(100vh-theme(spacing.14))] items-center justify-center">
      <Card className="w-full max-w-sm">
        <form onSubmit={handleEmailSignIn}> 
          <CardHeader>
            <CardTitle className="text-2xl">Sign In</CardTitle>
            <CardDescription>
              Sign in via Google or enter your email.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Button 
              variant="outline" 
              className="w-full" 
              type="button" 
              onClick={handleGoogleSignIn} 
              disabled={isLoading} // Disable buttons when Auth0 is loading
            >
              <Chrome className="mr-2 h-4 w-4" /> 
              Sign in with Google
            </Button>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="m@example.com" 
                required 
                // Note: Input fields are now handled by Auth0's Universal Login page
                // We keep them visually but they don't need state/onChange.
                // Consider removing them entirely or replacing with a message.
                // For now, just disabling them while loading.
                disabled={isLoading} 
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                required 
                disabled={isLoading}
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Loading..." : "Sign In with Email"} {/* Update button text */}
            </Button>
            <p className="mt-4 text-xs text-center text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/sign-up" className="underline">
                Sign up
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
} 