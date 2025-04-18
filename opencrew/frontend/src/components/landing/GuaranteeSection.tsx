import React from 'react';
import { ShieldCheck } from 'lucide-react'; // Use ShieldCheck or similar icon
import { cn } from '~/lib/utils';

export function GuaranteeSection() {
  return (
    <section
      className={cn(
        "flex items-center justify-center text-center text-white",
        "bg-gradient-to-r from-primary-500 to-accent", // Gradient background
        "min-h-[40vh]" // Minimum height 40vh
      )}
    >
      <div className="container mx-auto px-4 py-12 md:py-16">
        <ShieldCheck className="mx-auto mb-6 h-16 w-16 opacity-90" /> {/* Large icon */}
        <p className="text-2xl md:text-3xl font-semibold leading-tight max-w-2xl mx-auto">
          Land an interview in 30 days or your money back—no fine print.
        </p>
      </div>
    </section>
  );
}
