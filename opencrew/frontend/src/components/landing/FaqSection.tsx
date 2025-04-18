"use client";

import React from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { SectionHeading } from './SectionHeading';

// Sample FAQ Data (Replace with actual data source later)
const faqs = [
  {
    question: "How does the auto-apply feature work?",
    answer: "Our AI analyzes your profile and the job description to tailor your application materials (like highlighting relevant skills from your resume). Then, it navigates the job board or ATS to submit the application on your behalf, handling common fields and questions.",
  },
  {
    question: "Is using OpenCrew safe for visa applications (H-1B, OPT)?", // Updated name
    answer: "Yes. OpenCrew is designed with visa holders in mind. Our filters help you target roles specifically open to your status. We don't automate anything that would violate terms of service or put your application at risk. We focus on efficiency and targeting, not circumventing rules.", // Updated name
  },
  {
    question: "How is my personal data and resume information protected?",
    answer: "We take data privacy seriously. Your data is encrypted both in transit and at rest. We only use your information to provide the OpenCrew service and never sell it to third parties. You can request data deletion at any time. See our Privacy Policy for full details.", // Updated name
  },
  {
    question: "Will my applications get flagged by Applicant Tracking Systems (ATS)?",
    answer: "No. OpenCrew helps tailor your existing resume and cover letter information for each application, improving its relevance. It doesn't use deceptive techniques. The applications are submitted through standard channels, appearing as if you applied manually, but much faster.", // Updated name
  },
  {
    question: "What job boards and ATS are supported?",
    answer: "We currently support major job boards like LinkedIn, Indeed, and Greenhouse, with more being added regularly. Our goal is to cover the most common platforms used by tech companies.",
  },
  {
    question: "Can I customize the applications before they are sent?",
    answer: "Yes, for Pro and Elite users, you have the option to review and edit AI-generated cover letters or application answers before submission. The Free tier uses a more automated approach based on your primary resume.",
  },
];

export function FaqSection() {
  return (
    <section id="faq" className="py-16 md:py-24 bg-white"> {/* White background */}
      <div className="container mx-auto px-4">
        <SectionHeading
          badge="Questions?"
          title="Frequently Asked Questions"
          className="mb-12 md:mb-16"
        />

        <Accordion type="single" collapsible className="w-full max-w-3xl mx-auto">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left text-lg font-medium">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-grey-40">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
