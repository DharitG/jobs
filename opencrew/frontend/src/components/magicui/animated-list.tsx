"use client"

import { cn } from "~/lib/utils" // Adjusted path
import { AnimatePresence, motion } from "framer-motion" // Use framer-motion
import React, { type ComponentPropsWithoutRef, useEffect, useMemo, useState } from "react"

export function AnimatedListItem({ children }: { children: React.ReactNode }) {
  const animations = {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1, originY: 0 },
    exit: { scale: 0, opacity: 0 },
    transition: { type: "spring", stiffness: 350, damping: 40 },
  }

  return (
    <motion.div {...animations} layout className="mx-auto w-full">
      {children}
    </motion.div>
  )
}

export interface AnimatedListProps extends ComponentPropsWithoutRef<"div"> {
  children: React.ReactNode
  delay?: number
}

export const AnimatedList = React.memo(({ children, className, delay = 1000, ...props }: AnimatedListProps) => {
  const [index, setIndex] = useState(0)
  const childrenArray = useMemo(() => React.Children.toArray(children), [children])

  useEffect(() => {
    // No need to check index < childrenArray.length - 1 for looping
    const timeout = setTimeout(() => {
      setIndex((prevIndex) => (prevIndex + 1) % childrenArray.length)
    }, delay)

    return () => clearTimeout(timeout)
    // Removed index from dependency array to ensure continuous looping based on delay
  }, [delay, childrenArray.length])

  const itemsToShow = useMemo(() => {
    // Ensure index wraps around correctly
    const currentIndex = index % childrenArray.length;
    // Slice and reverse logic might need adjustment depending on desired visual effect
    // This implementation shows items accumulating and then restarting
    const result = childrenArray.slice(0, currentIndex + 1).reverse()
    return result
  }, [index, childrenArray])

  return (
    <div className={cn(`flex flex-col items-center gap-4`, className)} {...props}>
      <AnimatePresence>
        {itemsToShow.map((item) => (
          // Ensure key is stable and unique for each child element
          <AnimatedListItem key={(item as React.ReactElement).key ?? index}>
             {item}
          </AnimatedListItem>
        ))}
      </AnimatePresence>
    </div>
  )
})

AnimatedList.displayName = "AnimatedList"
