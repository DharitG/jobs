"use client";

import { useState } from "react";
// import { useAuth0 } from "@auth0/auth0-react"; // Removed Auth0
import { AuthButtons } from "~/components/AuthButtons"; // Import AuthButtons
import Link from "next/link"; // Keep Link for the logo text
import {
  Navbar as ResizableNavbarRoot, // Renamed to avoid conflict with the component name
  NavBody,
  NavItems,
  MobileNav,
  NavbarButton,
  MobileNavHeader,
  MobileNavToggle,
  MobileNavMenu,
} from "~/components/ui/resizable-navbar"; // Use path alias
import { cn } from "~/lib/utils"; // Keep cn if needed, though the new component handles its own styling

export function Navbar() {
  // const { loginWithRedirect } = useAuth0(); // Removed Auth0
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    {
      name: "Product",
      link: "/#product-tour",
    },
    {
      name: "Pricing",
      link: "/#pricing",
    },
    // Add other nav items if needed
  ];

  // Removed handleLogin and handleGetStarted as AuthButtons handles this now

  return (
    // Use the ResizableNavbarRoot component. Adjust top positioning if needed (original was top-0, new is top-20 default)
    // Changed sticky top-20 to top-0 and added custom class for height
    <ResizableNavbarRoot className="top-0 h-[72px]">
      {/* Desktop Navigation */}
      <NavBody className="max-w-screen-2xl"> {/* Use container width from old navbar */}
        {/* Replace Logo component with simple text */}
        <Link href="/" className="relative z-20 mr-auto flex items-center px-2 py-1 text-lg font-bold text-black dark:text-white">
          opencrew
        </Link>
        <NavItems items={navItems} onItemClick={() => setIsMobileMenuOpen(false)} />
        <div className="relative z-20 flex items-center gap-4">
           {/* Render AuthButtons which handles login/logout */}
          <AuthButtons />
        </div>
      </NavBody>

      {/* Mobile Navigation */}
      <MobileNav className="max-w-screen-2xl"> {/* Use container width */}
        <MobileNavHeader>
           {/* Replace Logo component with simple text */}
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
              onClick={() => setIsMobileMenuOpen(false)} // Close menu on item click
              className="relative text-neutral-600 dark:text-neutral-300" // Style as needed
            >
              <span className="block">{item.name}</span>
            </a>
          ))}
          <div className="flex w-full flex-col gap-4 pt-4">
             {/* Render AuthButtons which handles login/logout */}
            <AuthButtons />
          </div>
        </MobileNavMenu>
      </MobileNav>
    </ResizableNavbarRoot>
  );
}
