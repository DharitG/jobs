import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "~/lib/utils"

const buttonVariants = cva(
  // Base styles: Apply design system radius, transition, focus
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-design-md text-sm font-medium transition-all duration-150 ease-out-cubic disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2", // Adjusted focus ring per design system
  {
    variants: {
      variant: {
        // Primary Button (default)
        default:
          "bg-primary-500 text-white shadow-1 hover:bg-primary-600 hover:-translate-y-px hover:shadow-md", // Use design system colors/shadows/hover
        // Destructive Button
        destructive:
          "bg-error text-white shadow-1 hover:bg-error/90 focus-visible:ring-error/50", // Use error color, add shadow-1
        // Secondary Button (using outline variant)
        outline:
          "border border-primary-500 bg-transparent text-primary-500 hover:bg-primary-500/10", // Use design system spec for secondary
        // Secondary (shadcn default - keep for potential internal use?)
        secondary:
          "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80", // Keep original secondary for now
        // Ghost Button
        ghost:
          "text-grey-90 hover:bg-primary-500/10 hover:text-primary-500", // Use design system spec
        // Link Button
        link: "text-primary-500 underline-offset-4 hover:underline", // Use primary-500
      },
      size: {
        // Keep sizes, radius is applied in base
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 gap-1.5 px-3 has-[>svg]:px-2.5", // Removed rounded-md here, applied in base
        lg: "h-10 px-6 has-[>svg]:px-4", // Removed rounded-md here, applied in base
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
