'use client';

import React, { useState, useEffect } from 'react';
import { useSupabaseClient } from '@supabase/auth-helpers-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Image from 'next/image'; // Import Next Image
import { IconBrandGithub, IconBrandGoogle } from "@tabler/icons-react";
import { Loader2 } from "lucide-react";

import { Modal } from '~/components/ui/modal'; // Use the new Modal
import { Input } from "~/components/ui/input"; // Use Aceternity Input
import { Label } from "~/components/ui/label"; // Use Aceternity Label
import { cn } from '~/lib/utils';
import type { Database } from '~/lib/supabase_types';

// Re-using helper components from sign-in/sign-up pages for styling consistency
const बॉटमग्रैडीएंटAuthModal = () => {
  return (
    <>
      <span className="absolute inset-x-0 -bottom-px block h-px w-full bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-0 transition duration-500 group-hover/btn:opacity-100" />
      <span className="absolute inset-x-10 -bottom-px mx-auto block h-px w-1/2 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-0 blur-sm transition duration-500 group-hover/btn:opacity-100" />
    </>
  );
};

const लेबलइनपुटContainerAuthModal = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return <div className={cn("flex w-full flex-col space-y-2", className)}>{children}</div>;
};

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

export default function AuthModal({ isOpen, onClose, initialMode = 'signin' }: AuthModalProps) {
  const router = useRouter();
  const supabase = useSupabaseClient<Database>();
  const [isSignIn, setIsSignIn] = useState(initialMode === 'signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState(''); // Changed from 'name' for consistency
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingGoogle, setIsLoadingGoogle] = useState(false);
  const [isLoadingGithub, setIsLoadingGithub] = useState(false);

  // Reset state when mode changes or modal opens/closes
  useEffect(() => {
    setIsSignIn(initialMode === 'signin');
    setEmail('');
    setPassword('');
    setFullName('');
    setErrorMessage(null);
    setIsLoading(false);
    setIsLoadingGoogle(false);
    setIsLoadingGithub(false);
  }, [isOpen, initialMode]);


  // --- Supabase Handlers ---
  const handleGoogleAuth = async () => {
    setIsLoadingGoogle(true);
    setErrorMessage(null);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) {
      toast.error(error.message);
      setErrorMessage(error.message);
      setIsLoadingGoogle(false);
    }
    // Supabase handles redirection
  };

  const handleGithubAuth = async () => {
    setIsLoadingGithub(true);
    setErrorMessage(null);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) {
      toast.error(error.message);
      setErrorMessage(error.message);
      setIsLoadingGithub(false);
    }
     // Supabase handles redirection
  };

  const handleEmailPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);
    const commonOptions = {
        redirectTo: `${window.location.origin}/auth/callback`,
    };

    try {
      if (isSignIn) {
        // Sign In Logic
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
          // options: commonOptions // redirectTo not typically needed for password sign-in
        });

        if (error) throw error;

        toast.success('Successfully signed in!');
        router.push('/dashboard'); // Redirect on success
        onClose(); // Close modal

      } else {
        // Sign Up Logic
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
            emailRedirectTo: `${window.location.origin}/auth/callback`, // For email verification link
          },
        });

        if (error) throw error;

        toast.success('Account created! Check email for verification.');
        // Don't auto-login or redirect here, wait for verification
        // Optionally switch to sign-in view or keep sign-up view with message
        // For simplicity, we'll just close the modal after showing the message.
        // setEmail(''); // Clear form optionally
        // setPassword('');
        // setFullName('');
        onClose(); // Close modal
      }
    } catch (error: any) {
        console.error("Auth Error:", error);
        const displayError = error.message || 'An unexpected error occurred.';
        toast.error(displayError);
        setErrorMessage(displayError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Use the base Modal component, adjust max-width for the two-column layout
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-4xl p-0" hideCloseButton>
      {/* Apply two-column flex layout */}
      <div className="flex h-[80vh] max-h-[700px] overflow-hidden rounded-lg">
        {/* Left side - Form (45%) */}
        <div className="w-[45%] p-8 overflow-y-auto bg-white dark:bg-black">
          <div className="relative flex h-full flex-col justify-center max-w-sm mx-auto"> {/* Added relative positioning */}
            {/* Close button inside the form column */}
             <button
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
              aria-label="Close"
            >
               <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>

            <h2 className="text-xl font-bold text-neutral-800 dark:text-neutral-200 mb-4">
              {isSignIn ? 'Welcome back' : 'Join OpenCrew'}
            </h2>
            <p className="mt-2 mb-6 max-w-sm text-sm text-neutral-600 dark:text-neutral-300">
              {isSignIn ? 'Sign in to continue.' : 'Create your account.'}
            </p>

            {/* Combined Email/Password Form */}
            <form onSubmit={handleEmailPasswordSubmit} className="space-y-4">
              {!isSignIn && (
                <लेबलइनपुटContainerAuthModal>
                  <Label htmlFor="full-name">Full Name</Label>
                  <Input
                    id="full-name"
                    placeholder="Ada Lovelace"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required={!isSignIn}
                    disabled={isLoading || isLoadingGoogle || isLoadingGithub}
                  />
                </लेबलइनपुटContainerAuthModal>
              )}

              <लेबलइनपुटContainerAuthModal>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  placeholder="you@domain.com"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading || isLoadingGoogle || isLoadingGithub}
                />
              </लेबलइनपुटContainerAuthModal>

              <लेबलइनपुटContainerAuthModal>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  placeholder="••••••••"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6} // Supabase default min length
                  disabled={isLoading || isLoadingGoogle || isLoadingGithub}
                />
                 {!isSignIn && (
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Password must be at least 6 characters
                    </p>
                  )}
              </लेबलइनपुटContainerAuthModal>

              {/* Forgot password - Add later if needed */}
              {/* {isSignIn && (
                 <div className="flex justify-end">
                    <button
                      type="button"
                      className="text-xs text-indigo-600 hover:text-indigo-500 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      Forgot password?
                    </button>
                  </div>
              )} */}

                {/* Error Message Display */}
               {errorMessage && (
                 <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 p-3 rounded-lg">
                   {errorMessage}
                 </div>
               )}

              {/* Submit Button */}
              <button
                className="group/btn relative block h-10 w-full rounded-md bg-gradient-to-br from-black to-neutral-600 font-medium text-white shadow-[0px_1px_0px_0px_#ffffff40_inset,0px_-1px_0px_0px_#ffffff40_inset] dark:bg-zinc-800 dark:from-zinc-900 dark:to-zinc-900 dark:shadow-[0px_1px_0px_0px_#27272a_inset,0px_-1px_0px_0px_#27272a_inset] disabled:opacity-50 disabled:cursor-not-allowed"
                type="submit"
                disabled={isLoading || isLoadingGoogle || isLoadingGithub}
              >
                 {(isLoading) && <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />}
                {isSignIn ? 'Sign in' : 'Create account'}
                <बॉटमग्रैडीएंटAuthModal />
              </button>
            </form>

             {/* Divider */}
            <div className="my-6 h-[1px] w-full bg-gradient-to-r from-transparent via-neutral-300 to-transparent dark:via-neutral-700" />

             {/* OAuth Buttons */}
            <div className="flex flex-col space-y-4">
                <button
                  className="group/btn shadow-input relative flex h-10 w-full items-center justify-center space-x-2 rounded-md bg-gray-50 px-4 font-medium text-black dark:bg-zinc-900 dark:shadow-[0px_0px_1px_1px_#262626] disabled:opacity-50 disabled:cursor-not-allowed"
                  type="button"
                  onClick={handleGithubAuth}
                  disabled={isLoading || isLoadingGoogle || isLoadingGithub}
                >
                  {isLoadingGithub ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <IconBrandGithub className="h-4 w-4 text-neutral-800 dark:text-neutral-300" />}
                  <span className="text-sm text-neutral-700 dark:text-neutral-300">
                     {isSignIn ? 'Sign in' : 'Sign up'} with GitHub
                  </span>
                  <बॉटमग्रैडीएंटAuthModal />
                </button>
                <button
                  className="group/btn shadow-input relative flex h-10 w-full items-center justify-center space-x-2 rounded-md bg-gray-50 px-4 font-medium text-black dark:bg-zinc-900 dark:shadow-[0px_0px_1px_1px_#262626] disabled:opacity-50 disabled:cursor-not-allowed"
                  type="button"
                  onClick={handleGoogleAuth}
                  disabled={isLoading || isLoadingGoogle || isLoadingGithub}
                >
                  {isLoadingGoogle ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <IconBrandGoogle className="h-4 w-4 text-neutral-800 dark:text-neutral-300" />}
                  <span className="text-sm text-neutral-700 dark:text-neutral-300">
                    {isSignIn ? 'Sign in' : 'Sign up'} with Google
                  </span>
                  <बॉटमग्रैडीएंटAuthModal />
                </button>
            </div>

             {/* Toggle Sign in/Sign up */}
            <p className="mt-6 text-center text-sm text-gray-600 dark:text-neutral-400">
              {isSignIn ? "Don't have an account? " : 'Already have an account? '}
              <button
                onClick={() => setIsSignIn(!isSignIn)}
                className="font-semibold text-blue-500 hover:underline dark:text-blue-400"
                disabled={isLoading || isLoadingGoogle || isLoadingGithub}
              >
                {isSignIn ? 'Sign up' : 'Sign in'}
              </button>
            </p>

          </div>
        </div>
         {/* Right side - Image Area (55%) */}
         <div className="w-[55%] relative bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-zinc-900 dark:to-black rounded-r-lg overflow-hidden hidden md:block">
           {/* Add the Image component */}
           <Image
            src="/assets/heaven.jpeg" // Updated image path
            alt="OpenCrew Authentication"
            fill // Make image cover the div
            className="object-cover" // Cover scaling
            sizes="(max-width: 768px) 0vw, 55vw" // Optimize image loading
            priority // Prioritize loading if above the fold
           />
           {/* Optional overlay text if needed */}
           {/* <div className="absolute inset-0 flex items-center justify-center bg-black/10">
              <p className="text-center text-xl font-semibold text-white px-4">
                Join the Crew! <br /> Landing your dream job starts here.
             </p>
            </div> */}
           {/* The div below closes the right-side image area (line 310) */}
         </div>
        {/* The div below closes the main flex container (line 162) */}
       </div>
     </Modal>
   );
 }