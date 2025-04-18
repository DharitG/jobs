import Link from "next/link";
import Image from "next/image"; // Import Image component
import { Github, Linkedin, Twitter } from "lucide-react"; // Import social icons

const footerLinks = {
  product: [
    { name: "Features", href: "/#wow-features" }, // Link to relevant section ID
    { name: "Pricing", href: "/#pricing" },
    { name: "Blog", href: "/blog" }, // Assuming a blog page exists or will exist
  ],
  company: [
    { name: "About", href: "/about" }, // Assuming pages exist or will exist
    { name: "Careers", href: "/careers" },
    { name: "Press", href: "/press" },
  ],
  legal: [
    { name: "Terms", href: "/terms" },
    { name: "Privacy", href: "/privacy" },
    { name: "AI Disclosure", href: "/ai-disclosure" }, // Assuming page exists or will exist
  ],
  help: [
    { name: "Support", href: "/support" }, // Assuming pages exist or will exist
    { name: "API Docs", href: "/docs" },
    { name: "Status", href: "/status" },
  ],
};

const socialLinks = [
  // TODO: Replace with actual OpenCrew social links when available
  { name: "GitHub", href: "https://github.com/your-org/opencrew", Icon: Github },
  { name: "LinkedIn", href: "https://linkedin.com/company/opencrew", Icon: Linkedin },
  { name: "Twitter", href: "https://twitter.com/opencrew", Icon: Twitter },
];

export function Footer() {
  return (
    <footer className="border-t border-grey-20 bg-grey-5 text-grey-90"> {/* Use grey-5 background */}
      {/* Aim for ~280px height using padding */}
      <div className="container mx-auto px-4 py-16 md:py-20"> {/* Increased padding */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 mb-12"> {/* 5th col for logo/social on larger screens */}
          {/* Logo Column */}
          <div className="col-span-2 md:col-span-4 lg:col-span-1 mb-8 lg:mb-0">
             {/* Add the logo here */}
             <Link href="/" className="inline-block mb-4">
               <Image
                 src="/assets/f5ed6ae4-3d2b-488d-9048-65a12d962da6.png"
                 alt="OpenCrew Logo"
                 width={140} // Adjust width as needed
                 height={35} // Adjust height as needed
                 className="h-auto" // Maintain aspect ratio
               />
             </Link>
             <p className="text-sm text-grey-40 mt-4 max-w-xs">
               OpenCrew cuts weeks off your job hunt with AI‑tailored applications.
             </p>
          </div>

          {/* Link Columns */}
          <div>
            <h3 className="text-sm font-semibold text-grey-90 mb-4">Product</h3>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-sm text-grey-40 hover:text-grey-90 transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-grey-90 mb-4">Company</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-sm text-grey-40 hover:text-grey-90 transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-grey-90 mb-4">Legal</h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-sm text-grey-40 hover:text-grey-90 transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-grey-90 mb-4">Help</h3>
            <ul className="space-y-3">
              {footerLinks.help.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-sm text-grey-40 hover:text-grey-90 transition-colors">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Row: Copyright and Social Links */}
        <div className="border-t border-grey-20 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-grey-40 text-center md:text-left">
            © {new Date().getFullYear()} OpenCrew Inc. All rights reserved.
          </p>
          <div className="flex items-center space-x-4">
            {socialLinks.map((link) => (
              <Link key={link.name} href={link.href} target="_blank" rel="noopener noreferrer" className="text-grey-40 hover:text-grey-90 transition-colors">
                <link.Icon className="h-5 w-5" />
                <span className="sr-only">{link.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
