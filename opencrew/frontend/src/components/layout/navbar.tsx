"use client";

import { useState } from "react";
import Link from "next/link";
import { Toaster } from 'react-hot-toast'; // Import Toaster

import { AuthButtons } from "~/components/AuthButtons";
import AuthModal from "~/components/AuthModal"; // Import the new AuthModal
import {
  Navbar as ResizableNavbarRoot,
  NavBody,
  NavItems,
  MobileNav,
  NavbarButton,
  MobileNavHeader,
  MobileNavToggle,
  MobileNavMenu,
} from "~/components/ui/resizable-navbar";
import { cn } from "~/lib/utils";

export function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  // State for AuthModal
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'signin' | 'signup'>('signin');

  const navItems = [
    { name: "Product", link: "/#product-tour" },
    { name: "Pricing", link: "/#pricing" },
    // Add other nav items if needed
  ];

  // Functions to open the modal in specific modes
  const openSignInModal = () => {
    setAuthModalMode('signin');
    setIsAuthModalOpen(true);
    setIsMobileMenuOpen(false); // Close mobile menu if open
  };

  const openSignUpModal = () => {
    setAuthModalMode('signup');
    setIsAuthModalOpen(true);
    setIsMobileMenuOpen(false); // Close mobile menu if open
  };

  return (
    <> {/* Wrap with Fragment to include Toaster */}
      {/* Toaster for react-hot-toast notifications */}
      <Toaster position="top-center" reverseOrder={false} />

      <ResizableNavbarRoot className="top-0 h-[72px]">
        <NavBody className="max-w-screen-2xl">
          <Link href="/" className="relative z-20 mr-auto flex items-center px-2 py-1 text-lg font-bold text-black dark:text-white">
            opencrew
          </Link>
          <NavItems items={navItems} onItemClick={() => setIsMobileMenuOpen(false)} />
          <div className="relative z-20 flex items-center gap-4">
            {/* Pass modal trigger functions to AuthButtons */}
            <AuthButtons onSignInClick={openSignInModal} onSignUpClick={openSignUpModal} />
          </div>
        </NavBody>

        <MobileNav className="max-w-screen-2xl">
          <MobileNavHeader>
            <Link href="/" className="relative z-20 flex items-center px-2 py-1 text-lg font-bold text-black dark:text-white">
              opencrew
            </Link>
            <MobileNavToggle isOpen={isMobileMenuOpen} onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />
          </MobileNavHeader>

          <MobileNavMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)}>
            {navItems.map((item, idx) => (
              <a
                key={`mobile-link-${idx}`}
                href={item.link}
                onClick={() => setIsMobileMenuOpen(false)}
                className="relative text-neutral-600 dark:text-neutral-300"
              >
                <span className="block">{item.name}</span>
              </a>
            ))}
            <div className="flex w-full flex-col gap-4 pt-4">
              {/* Pass modal trigger functions to AuthButtons in mobile menu */}
              <AuthButtons onSignInClick={openSignInModal} onSignUpClick={openSignUpModal} />
            </div>
          </MobileNavMenu>
        </MobileNav>
      </ResizableNavbarRoot>

      {/* Render the AuthModal, controlled by state */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode={authModalMode}
      />
    </>
  );
}
