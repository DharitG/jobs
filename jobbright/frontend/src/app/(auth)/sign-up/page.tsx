"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import Link from "next/link";
import { Chrome } from "lucide-react";

export default function SignUpPage() {
  const { loginWithRedirect, isLoading } = useAuth0();

  const handleGoogleSignUp = () => {
    loginWithRedirect({
      authorizationParams: {
        connection: 'google-oauth2',
      },
    });
  };

  const handleEmailSignUp = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    loginWithRedirect({
      authorizationParams: {
      },
    });
  };

  return (
    <div className="container flex h-[calc(100vh-theme(spacing.14))] items-center justify-center">
      <Card className="w-full max-w-sm">
        <form onSubmit={handleEmailSignUp}>
          <CardHeader>
            <CardTitle className="text-2xl">Sign Up</CardTitle>
            <CardDescription>
              Sign up via Google or enter your details.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Button 
              variant="outline" 
              className="w-full" 
              type="button" 
              onClick={handleGoogleSignUp} 
              disabled={isLoading}
            >
              <Chrome className="mr-2 h-4 w-4" />
              Sign up with Google
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
              <Label htmlFor="full-name">Full Name</Label>
              <Input 
                id="full-name" 
                placeholder="Max Robinson" 
                required 
                disabled={isLoading}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="m@example.com" 
                required 
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
              {isLoading ? "Loading..." : "Sign Up with Email"}
            </Button>
            <p className="mt-4 text-xs text-center text-muted-foreground">
              Already have an account?{" "}
              <Link href="/sign-in" className="underline">
                Sign in
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
} 