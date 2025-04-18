import React from 'react';
import Image from 'next/image';
import { Star } from 'lucide-react';
import { Card, CardContent } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge'; // Import Badge
import { cn } from '~/lib/utils';

// Define the props interface
interface TestimonialCardProps {
  avatarSrc: string;
  quote: string;
  rating: number;
  name: string;
  position: string;
  visaStatus?: 'H-1B' | 'OPT' | 'Green Card' | 'Citizen' | 'Other'; // Optional visa status
  className?: string; // Allow className to be passed
}

export function TestimonialCard({
  avatarSrc,
  quote,
  rating,
  name,
  position,
  visaStatus,
  className,
}: TestimonialCardProps) {
  return (
    <Card className={cn("overflow-hidden bg-white shadow-1 rounded-design-md", className)}> {/* Use white background */}
      <CardContent className="p-6">
        {/* Rating */}
        <div className="flex items-center mb-4">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={cn(
                "h-5 w-5",
                i < rating ? "text-yellow-400 fill-yellow-400" : "text-grey-20"
              )}
            />
          ))}
        </div>

        {/* Quote */}
        <blockquote className="mb-6 text-grey-90 italic">
          <p>"{quote}"</p>
        </blockquote>

        {/* Author Info */}
        <div className="flex items-center">
          <Image
            src={avatarSrc}
            alt={`${name} avatar`}
            width={48}
            height={48}
            className="rounded-full mr-4"
          />
          <div>
            <p className="font-semibold text-grey-90">{name}</p>
            <p className="text-sm text-grey-40">{position}</p>
            {visaStatus && (
              <Badge variant="outline" className="mt-1 text-xs">
                {visaStatus}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Example Usage (can be removed or kept for reference):
// <TestimonialCard
//   avatarSrc="/path/to/avatar.jpg"
//   quote="OpenCrew saved me weeks of tedious applications and landed me my dream job!" // Updated name
//   rating={5}
//   name="Jane Doe"
//   position="Product Manager @ Startup"
//   visaStatus="H-1B"
// />
