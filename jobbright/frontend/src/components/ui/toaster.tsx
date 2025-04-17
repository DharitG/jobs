"use client"

import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "~/components/ui/toast" // Use ~ alias
import { useToast } from "~/hooks/use-toast" // Use ~ alias

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {/* Add types for destructured props */}
      {toasts.map(function ({ id, title, description, action, ...props }: {
         id: string; 
         title?: React.ReactNode; 
         description?: React.ReactNode; 
         action?: React.ReactElement; 
         [key: string]: unknown; // Allow other props
        }) {
        return (
          <Toast key={id} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
