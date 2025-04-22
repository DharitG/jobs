"use client"; // Needed for button onClick handler

import React from 'react';
import { Button } from '~/components/ui/button';
// import { useAuth0 } from "@auth0/auth0-react"; // REMOVED - Unused Auth0 import
import { cn } from '~/lib/utils';

export function FinalCtaSection() {
  // Removed unused Auth0 hook call and handler function

  return (
    <section
      className={cn(
        "flex items-center justify-center text-center",
        "bg-white text-grey-90", // White background, dark grey text
        "min-h-[45vh]" // Minimum height 45vh
      )}
    >
      <div className="container mx-auto px-4 py-16 md:py-20">
        <h2 className="mb-12 font-display text-3xl font-bold md:text-4xl">
          OpenCrew by the Numbers
        </h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Ticker 1 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"Interviews booked today"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">127</p> {/* Inherits text-grey-90 */}
          </div>
          {/* Ticker 2 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"Avg. days to first interview"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">5.3</p> {/* Inherits text-grey-90 */}
          </div>
          {/* Ticker 3 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"H-1B-friendly roles matched in the last 24 hrs"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">3,842</p> {/* Inherits text-grey-90 */}
          </div>
          {/* Ticker 4 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"Resumes turbo-tuned by our AI so far"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">74,192</p> {/* Inherits text-grey-90 */}
          </div>
          {/* Ticker 5 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"Applications submitted while users slept last night"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">18,450</p> {/* Inherits text-grey-90 */}
          </div>
          {/* Ticker 6 */}
          <div className="ticker-item text-center">
            <p className="text-sm text-grey-60 mb-1">"Offers accepted this month"</p> {/* Darker grey for title */}
            <p className="text-4xl font-bold mb-1">312</p> {/* Inherits text-grey-90 */}
          </div>
        </div>
      </div>
    </section>
  );
}
