"use client";

import React from 'react';
import { usePathname } from 'next/navigation';
import { Navbar } from '~/components/layout/navbar';
import { Footer } from '~/components/layout/footer';

interface ConditionalLayoutProps {
  children: React.ReactNode;
}

export function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const pathname = usePathname();
  const isDashboard = pathname === '/dashboard'; // Check if the current path is the dashboard

  return (
    <>
      {!isDashboard && <Navbar />} {/* Render Navbar only if NOT on dashboard */}
      {/* Apply negative top margin only when Navbar is present */}
      <main className={!isDashboard ? "mt-[-72px]" : ""}>{children}</main>
      {!isDashboard && <Footer />} {/* Render Footer only if NOT on dashboard */}
    </>
  );
}