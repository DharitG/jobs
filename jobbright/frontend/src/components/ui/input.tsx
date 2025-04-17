import * as React from "react"

import { cn } from "~/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        // Base styles from design system + existing structure
        "flex h-9 w-full min-w-0 rounded-design-md border border-grey-20 bg-background px-3 py-1 text-base text-grey-90", // Use design system colors/radius, set bg to background
        "placeholder:text-grey-40", // Use design system placeholder color
        "transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium", // Keep file styles, basic transition
        "outline-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", // Keep outline/disabled styles
        // Focus state from design system
        "focus-visible:border-primary-500 focus-visible:ring-2 focus-visible:ring-primary-500/40 focus-visible:ring-offset-0", // Apply design system focus ring (2px inset outline equivalent)
        // Error state from design system
        "aria-[invalid=true]:border-error aria-[invalid=true]:ring-2 aria-[invalid=true]:ring-error/50", // Apply design system error ring
        // Remove dark mode styles for now
        // "dark:bg-input/30 dark:aria-invalid:ring-destructive/40",
        className
      )}
      {...props}
    />
  )
}

export { Input }
