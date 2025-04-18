"use client";
import Link from "next/link";
import Image from "next/image"; // Import Image component
import { Github, Linkedin, Twitter } from "lucide-react"; // Import social icons from lucide-react

// Links from the original OpenCrew footer
const footerLinks = {
  product: [
    { name: "Features", href: "/#wow-features" },
    { name: "Pricing", href: "/#pricing" },
    { name: "Blog", href: "/blog" },
  ],
  company: [
    { name: "About", href: "/about" },
    { name: "Careers", href: "/careers" },
    { name: "Press", href: "/press" },
  ],
  legal: [
    { name: "Terms", href: "/terms" },
    { name: "Privacy", href: "/privacy" },
    { name: "AI Disclosure", href: "/ai-disclosure" },
  ],
  help: [
    { name: "Support", href: "/support" },
    { name: "API Docs", href: "/docs" },
    { name: "Status", href: "/status" },
  ],
};

// Social links from the original OpenCrew footer
const socialLinks = [
  { name: "GitHub", href: "https://github.com/your-org/opencrew", Icon: Github }, // Update href later
  { name: "LinkedIn", href: "https://linkedin.com/company/opencrew", Icon: Linkedin }, // Update href later
  { name: "Twitter", href: "https://twitter.com/opencrew", Icon: Twitter }, // Update href later
];


export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    // Adopted structure from the new design
    <footer className="w-full text-white relative overflow-hidden">
      {/* Showcase gradient background */}
      <div className="absolute inset-0 bg-gradient-to-tr from-blue-900 via-purple-900 to-pink-900 z-0"></div> {/* Example gradient, adjust as needed */}

      {/* Background grid pattern for texture */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMjIiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djZoNnYtNmgtNnptNiA2djZoNnYtNmgtNnptLTEyIDBoNnY2aC02di02em0xMiAwaDZ2NmgtNnYtNnoiLz48cGF0aCBkPSJNMTIgMTJoNnY2aC02di02em06IDBoNnY2aC02di02em0xMiAwaDZ2NmgtNnYtNnptLTEyIDBoNnY2aC02di02em0xMiAwaDZ2NmgtNnYtNnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20 z-0"></div>

      {/* Two-part layout */}
      <div className="flex flex-col" style={{ minHeight: '800px' }}> {/* Keep min-height from new design */}
        {/* Empty space to show gradient */}
        <div className="flex-grow"></div>

        {/* Content container positioned at the bottom */}
        <div className="px-4 pb-8 relative z-10">
          <div className="max-w-6xl mx-auto"> {/* Increased max-width for 6 columns */}
            {/* Unified black rounded container */}
            <div className="bg-black rounded-3xl px-10 py-16 md:px-16 md:py-20 shadow-2xl border border-neutral-800 w-full flex flex-col justify-between min-h-[400px]">
              {/* Top part: Main content grid - Adjusted to md:grid-cols-6 */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-8 md:gap-12">
                {/* Logo and Copyright - Spanning 2 columns */}
                <div className="col-span-2">
                  <div className="flex flex-col space-y-4">
                     {/* OpenCrew Logo */}
                     <Link href="/" className="inline-block mb-2">
                       <Image
                         src="/assets/f5ed6ae4-3d2b-488d-9048-65a12d962da6.png"
                         alt="OpenCrew Logo"
                         width={140}
                         height={35}
                         className="h-auto"
                       />
                     </Link>
                    {/* OpenCrew Description */}
                    <p className="text-neutral-400 text-sm">
                      OpenCrew cuts weeks off your job hunt with AI‑tailored applications.
                    </p>
                    {/* OpenCrew Copyright */}
                    <p className="text-neutral-500 text-xs pt-4">
                      © {currentYear} OpenCrew Inc. All rights reserved.
                    </p>
                  </div>
                </div>

                {/* Product Links */}
                <div className="col-span-1">
                  <h3 className="text-lg font-semibold mb-4">Product</h3>
                  <ul className="space-y-2">
                    {footerLinks.product.map((link) => (
                      <li key={link.name}>
                        <Link href={link.href} className="text-neutral-400 hover:text-white transition-colors text-sm">
                          {link.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Company Links */}
                <div className="col-span-1">
                  <h3 className="text-lg font-semibold mb-4">Company</h3>
                  <ul className="space-y-2">
                    {footerLinks.company.map((link) => (
                      <li key={link.name}>
                        <Link href={link.href} className="text-neutral-400 hover:text-white transition-colors text-sm">
                          {link.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>

                 {/* Legal Links */}
                 <div className="col-span-1">
                  <h3 className="text-lg font-semibold mb-4">Legal</h3>
                  <ul className="space-y-2">
                    {footerLinks.legal.map((link) => (
                      <li key={link.name}>
                        <Link href={link.href} className="text-neutral-400 hover:text-white transition-colors text-sm">
                          {link.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>

                 {/* Help Links */}
                 <div className="col-span-1">
                  <h3 className="text-lg font-semibold mb-4">Help</h3>
                  <ul className="space-y-2">
                    {footerLinks.help.map((link) => (
                      <li key={link.name}>
                        <Link href={link.href} className="text-neutral-400 hover:text-white transition-colors text-sm">
                          {link.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Bottom part: Wrapper for Divider and Bottom Section */}
              <div className="mt-16">
                {/* Divider */}
                <div className="border-t border-neutral-800 my-8"></div>

                {/* Bottom section: Social links */}
                <div className="flex justify-center md:justify-end items-center">
                  {/* Social Media Icons */}
                  <div className="flex space-x-4">
                     {socialLinks.map((link) => (
                       <Link key={link.name} href={link.href} target="_blank" rel="noopener noreferrer" className="text-neutral-400 hover:text-white transition-colors">
                         <link.Icon className="h-6 w-6" /> {/* Use Lucide icon component */}
                         <span className="sr-only">{link.name}</span>
                       </Link>
                     ))}
                  </div>
                  {/* Removed "Made with love" text */}
                </div>
              </div>
            </div> {/* End of Unified black container */}
          </div>
        </div>
      </div>
    </footer>
  );
}
