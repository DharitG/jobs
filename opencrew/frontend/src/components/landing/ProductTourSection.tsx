import React from 'react';
import { SectionHeading } from './SectionHeading';
import { CheckListItem } from './CheckListItem'; // Import CheckListItem
import Image from 'next/image'; // Import Image

// Sample Data (Replace with actual steps/features)
const tourSteps = [
  { text: "Import your profile (LinkedIn/Resume)" },
  { text: "Set your job preferences & filters (Visa, Remote, etc.)" },
  { text: "AI tailors your application for matching jobs" },
  { text: "Applications submitted automatically" },
  { text: "Track progress on your dashboard" },
];

export function ProductTourSection() {
  return (
    <section id="product-tour" className="py-16 md:py-24 bg-white"> {/* White background */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Pipeline to Offer"
          title="See OpenCrew in Action" // Updated name
          className="mb-12 md:mb-16"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left Column: Steps/Checklist */}
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-grey-90">How it Works:</h3>
            <ul className="space-y-4">
              {tourSteps.map((step, index) => (
                <CheckListItem key={index}>{step.text}</CheckListItem> // Pass text as children
              ))}
            </ul>
             <p className="mt-6 text-grey-40">
               OpenCrew handles the tedious application process while you sip your coffee. {/* Updated name */}
             </p>
          </div>

          {/* Right Column: Image/GIF */}
          <div className="relative aspect-video rounded-design-md overflow-hidden shadow-1 ring-1 ring-primary-500/10">
             {/* Replace with actual product image/gif */}
             <Image
               src="/placeholder-auto-apply.gif" // Replace with actual image/gif path
               alt="OpenCrew Auto-Apply Process" // Updated name
               layout="fill"
               objectFit="cover"
             />
          </div>
        </div>
      </div>
    </section>
  );
}
