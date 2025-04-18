import React from 'react';
import { SectionHeading } from './SectionHeading';
import { FeatureCard } from './FeatureCard';
import { CheckCircle } from 'lucide-react'; // Example icon

// Sample Data (Replace with actual features)
const features = [
  {
    icon: CheckCircle, // Replace with appropriate icons
    title: "1-Click Auto-Apply",
    description: "Submit 50+ tailored applications per hour across major job boards.",
    badge: "Core",
  },
  {
    icon: CheckCircle,
    title: "Visa-Safe Filters",
    description: "Target jobs explicitly sponsoring H-1B, OPT, or Green Card.",
    badge: "Core",
  },
  {
    icon: CheckCircle,
    title: "AI Resume Tailoring",
    description: "Automatically highlight relevant skills for each specific job description.",
    badge: "Pro",
  },
  {
    icon: CheckCircle,
    title: "GPT-4o Cover Letters",
    description: "Generate personalized cover letters that pass AI detection.",
    badge: "Pro",
  },
   {
    icon: CheckCircle,
    title: "Interview Flash Cards",
    description: "Practice common interview questions tailored to the roles you apply for.",
    badge: "Pro",
  },
  {
    icon: CheckCircle,
    title: "Guaranteed Resume Review",
    description: "Get expert feedback on your resume within 24 hours.",
    badge: "Elite",
  },
];

export function WowFeaturesGrid() {
  return (
    <section id="wow-features" className="py-16 md:py-24 bg-white"> {/* White background */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Differentiators"
          title="Why OpenCrew Wins" // Updated name
          className="mb-12 md:mb-16"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              badge={feature.badge}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
