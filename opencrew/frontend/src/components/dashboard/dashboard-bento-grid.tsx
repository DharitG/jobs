import type React from "react"
import { ArrowRightIcon } from "@radix-ui/react-icons"
import type { ComponentPropsWithoutRef, ReactNode } from "react"

import { Button } from "~/components/ui/button" // Adjusted path
import { cn } from "~/lib/utils" // Adjusted path

interface DashboardBentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode
  className?: string
}

interface DashboardBentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string
  className: string
  background: ReactNode
  Icon?: React.ElementType // Make Icon optional
  description?: string // Made optional
  href?: string // Made optional
  cta?: string // Made optional
  customContent?: ReactNode // Renamed prop
  footerContent?: ReactNode // New prop for fixed footer
  children?: ReactNode // Added children prop
}

const DashboardBentoGrid = ({ children, className, ...props }: DashboardBentoGridProps) => {
  return (
    <div className={cn("grid w-full auto-rows-[22rem] grid-cols-3 gap-4", className)} {...props}>
      {children}
    </div>
  )
}

const DashboardBentoCard = ({ name, className, background, Icon, description, href, cta, customContent, footerContent, children, ...props }: DashboardBentoCardProps) => ( // Added children
  <div
    key={name}
    className={cn(
      "group relative col-span-3 flex flex-col overflow-hidden rounded-xl",
      // light styles
      "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
      // dark styles
      "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
      className,
    )}
    {...props}
  >
    <div>{background}</div>
    {/* Add bottom padding to account for the absolute footer height (adjust pb-16 as needed) */}
    {/* Make this container a flex column and allow it to grow */}
    <div className="pointer-events-none z-10 flex flex-grow flex-col gap-1 p-6 pb-16 transition-all duration-300">
      {/* Conditionally render Icon */}
      {Icon && <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75 dark:text-neutral-300" />}
      <h3 className="text-xl font-semibold text-neutral-700 dark:text-neutral-300">{name}</h3>
      <p className="max-w-lg text-neutral-400">{description}</p>
      {/* Render children if provided, otherwise fallback to customContent */}
      <div className="mt-4 flex-grow">
        {children ?? customContent}
      </div>
    </div>

    {/* Render CTA button only if href and cta are provided */}
    {href && cta && (
    <div
      className={cn(
        "pointer-events-none absolute bottom-0 flex w-full translate-y-10 transform-gpu flex-row items-center p-4 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100",
      )}
    >
      <Button variant="ghost" asChild size="sm" className="pointer-events-auto">
        <a href={href}>
          {cta}
          <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
        </a>
      </Button>
    </div>
    )}
    <div className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-black/[.03] group-hover:dark:bg-neutral-800/10" />
    {/* Absolute positioned footer */}
    {footerContent && (
      <div className="absolute bottom-0 left-0 right-0 z-20">
        {footerContent}
      </div>
    )}
  </div>
)

export { DashboardBentoCard, DashboardBentoGrid }