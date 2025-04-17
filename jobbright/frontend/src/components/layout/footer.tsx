import Link from "next/link"; // Import Link

export function Footer() {
  return (
    <footer className="py-6 md:px-8 md:py-0 border-t border-grey-20 bg-background"> {/* Add border and background */}
      <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
        <p className="text-balance text-center text-sm leading-loose text-grey-40 md:text-left"> {/* Use grey-40 */}
          © {new Date().getFullYear()} JobBright. All rights reserved.
        </p>
        {/* Footer Links */}
        <div className="flex gap-4">
           <Link href="/privacy" className="text-sm text-grey-40 hover:text-primary-500 transition-colors">
             Privacy Policy
           </Link>
           <Link href="/terms" className="text-sm text-grey-40 hover:text-primary-500 transition-colors">
             Terms of Service
           </Link>
        </div>
      </div>
    </footer>
  );
}
