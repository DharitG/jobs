'use client';

import React from 'react';

interface QuotaRingProps {
  remaining: number;
  total: number; // Need total to calculate percentage
  size?: number; // Diameter of the ring
  strokeWidth?: number; // Thickness of the ring
}

export function QuotaRing({ 
  remaining, 
  total, 
  size = 40, 
  strokeWidth = 4 
}: QuotaRingProps) {
  const percentage = total > 0 ? Math.max(0, Math.min(100, (remaining / total) * 100)) : 0;
  // Tailwind doesn't directly support conic-gradient percentages easily for arbitrary values.
  // We'll use a style attribute for the background.
  // Colors from design system: primary-500 (#3E6DFF), grey-20 (#E1E4F0)
  const gradientStyle = {
    background: `conic-gradient(#3E6DFF ${percentage}%, #E1E4F0 ${percentage}%)`,
  };

  return (
    <div 
      className="relative rounded-full flex items-center justify-center"
      style={{ width: `${size}px`, height: `${size}px`, ...gradientStyle }}
      title={`${remaining} / ${total} applications remaining`}
    >
      {/* Inner circle to create the ring effect */}
      <div 
        className="absolute bg-white rounded-full flex items-center justify-center"
        style={{ 
          width: `${size - strokeWidth * 2}px`, 
          height: `${size - strokeWidth * 2}px` 
        }}
      >
        <span className="text-xs font-semibold text-grey-90">
          {remaining}
        </span>
      </div>
    </div>
  );
}
