import React from 'react';
import type { Metadata } from 'next'; // Use type-only import
import { PricingSection } from '~/components/landing/PricingSection';
import { FaqSection } from '~/components/landing/FaqSection'; // Re-use FAQ section
import { GuaranteeSection } from '~/components/landing/GuaranteeSection'; // Re-use Guarantee section
import { FinalCtaSection } from '~/components/landing/FinalCtaSection'; // Re-use Final CTA

// Optional: Add specific metadata for the pricing page
export const metadata: Metadata = {
  title: 'Pricing – OpenCrew', // Updated name
  description: 'Choose the OpenCrew plan that fits your job search needs. Start free or upgrade for unlimited applications and premium features.', // Updated name
  openGraph: {
    title: 'Pricing – OpenCrew', // Updated name
    description: 'Choose the OpenCrew plan that fits your job search needs.', // Updated name
    url: 'https://opencrew.ai/pricing', // Updated name
  },
   twitter: {
    title: 'Pricing – OpenCrew', // Updated name
    description: 'Choose the OpenCrew plan that fits your job search needs.', // Updated name
  },
};


// Re-use FAQ data or define specific ones for pricing page
const pricingFaqs = [
   {
    question: "What counts as an 'application' towards the monthly limit?",
    answer: "Each job you instruct OpenCrew to apply for counts as one application, regardless of whether it's successfully submitted (e.g., due to CAPTCHAs or unexpected application flows).", // Updated name
  },
  {
    question: "Can I upgrade or downgrade my plan anytime?",
    answer: "Yes, you can change your plan at any time through your account settings. Upgrades take effect immediately, while downgrades apply at the end of your current billing cycle.",
  },
  {
    question: "Is there a free trial for Pro or Elite plans?",
    answer: "We don't offer traditional time-limited trials. Instead, our Free plan allows you to use core features like basic job matching and up to 50 auto-applies per month to see how OpenCrew works for you.", // Updated name
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards (Visa, Mastercard, American Express) processed securely via Stripe.",
  },
   {
    question: "What is the refund policy?",
    answer: "We offer a 14-day money-back guarantee on your first subscription payment for Pro or Elite plans if you're not satisfied. See our Terms of Service for full details.",
  },
];


export default function PricingPage() {
  return (
    <div>
      {/* Use the existing PricingSection component */}
      <PricingSection />

      {/* Re-use the Guarantee Section */}
      <GuaranteeSection />

      {/* Re-use or adapt the FAQ Section */}
      {/* Option 1: Re-use the exact same FAQ section */}
      {/* <FaqSection /> */}

      {/* Option 2: Pass specific FAQs to the FaqSection (if component is adapted) */}
      {/* <FaqSection faqs={pricingFaqs} /> */}

      {/* Option 3: Create a simplified FAQ section here if needed */}
       <section id="pricing-faq" className="py-16 md:py-24 bg-white">
         <div className="container mx-auto px-4 max-w-3xl">
           <h2 className="text-3xl font-bold text-center mb-12">Pricing Questions</h2>
           <Accordion type="single" collapsible className="w-full">
             {pricingFaqs.map((faq, index) => (
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


      {/* Re-use the Final CTA Section */}
      <FinalCtaSection />
    </div>
  );
}

// Note: Need to import Accordion components if using Option 3
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
