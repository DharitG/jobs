"use client"

import { cn } from "~/lib/utils" // Adjusted path
import type React from "react"
import { type ComponentPropsWithoutRef, useEffect, useRef, useState } from "react"

interface MousePosition {
  x: number
  y: number
}

function useMousePosition(): MousePosition { // Renamed hook for clarity
  const [mousePosition, setMousePosition] = useState<MousePosition>({
    x: 0,
    y: 0,
  })

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({ x: event.clientX, y: event.clientY })
    }

    window.addEventListener("mousemove", handleMouseMove)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
    }
  }, [])

  return mousePosition
}

interface ParticlesProps extends ComponentPropsWithoutRef<"div"> {
  className?: string
  quantity?: number
  staticity?: number
  ease?: number
  size?: number
  refresh?: boolean
  color?: string
  vx?: number
  vy?: number
}

function hexToRgb(hex: string): number[] {
  hex = hex.replace("#", "")

  if (hex.length === 3) {
    hex = hex
      .split("")
      .map((char) => char + char)
      .join("")
  }

  const hexInt = Number.parseInt(hex, 16)
  const red = (hexInt >> 16) & 255
  const green = (hexInt >> 8) & 255
  const blue = hexInt & 255
  return [red, green, blue]
}

type Circle = {
  x: number
  y: number
  translateX: number
  translateY: number
  size: number
  alpha: number
  targetAlpha: number
  dx: number
  dy: number
  magnetism: number
}

export const Particles: React.FC<ParticlesProps> = ({
  className = "",
  quantity = 100,
  staticity = 50,
  ease = 50,
  size = 0.4,
  refresh = false,
  color = "#ffffff",
  vx = 0,
  vy = 0,
  ...props
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const canvasContainerRef = useRef<HTMLDivElement>(null)
  const context = useRef<CanvasRenderingContext2D | null>(null)
  const circles = useRef<Circle[]>([])
  const mousePosition = useMousePosition() // Use the hook
  const mouse = useRef<{ x: number; y: number }>({ x: 0, y: 0 })
  const canvasSize = useRef<{ w: number; h: number }>({ w: 0, h: 0 })
  const dpr = typeof window !== "undefined" ? window.devicePixelRatio : 1
  const rafID = useRef<number | null>(null)
  const resizeTimeout = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      context.current = canvasRef.current.getContext("2d")
    }
    initCanvas()
    animate()

    const handleResize = () => {
      if (resizeTimeout.current) {
        clearTimeout(resizeTimeout.current)
      }
      resizeTimeout.current = setTimeout(() => {
        initCanvas()
      }, 200)
    }

    window.addEventListener("resize", handleResize)

    // Cleanup function
    return () => {
      if (rafID.current != null) {
        window.cancelAnimationFrame(rafID.current)
      }
      if (resizeTimeout.current) {
        clearTimeout(resizeTimeout.current)
      }
      window.removeEventListener("resize", handleResize)
    }
  }, [color, quantity, staticity, ease, size, vx, vy]) // Add dependencies that affect initialization/animation

  useEffect(() => {
    onMouseMove()
  }, [mousePosition.x, mousePosition.y])

  useEffect(() => {
    initCanvas()
  }, [refresh]) // Rerun initCanvas when refresh prop changes

  const initCanvas = () => {
    resizeCanvas()
    // drawParticles() // drawParticles is called within resizeCanvas now
  }

  const onMouseMove = () => {
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect()
      const { w, h } = canvasSize.current
      // Calculate mouse position relative to the canvas container center
      const x = mousePosition.x - rect.left - w / 2
      const y = mousePosition.y - rect.top - h / 2
      const inside = x < w / 2 && x > -w / 2 && y < h / 2 && y > -h / 2
      // Update mouse ref only if inside the canvas bounds
      if (inside) {
        mouse.current.x = x
        mouse.current.y = y
      } else {
        // Optional: Reset mouse position when outside to stop magnetism effect
         mouse.current.x = 0;
         mouse.current.y = 0;
      }
    }
  }

  const resizeCanvas = () => {
    if (canvasContainerRef.current && canvasRef.current && context.current) {
      circles.current.length = 0 // Clear existing circles
      canvasSize.current.w = canvasContainerRef.current.offsetWidth
      canvasSize.current.h = canvasContainerRef.current.offsetHeight

      canvasRef.current.width = canvasSize.current.w * dpr
      canvasRef.current.height = canvasSize.current.h * dpr
      canvasRef.current.style.width = `${canvasSize.current.w}px`
      canvasRef.current.style.height = `${canvasSize.current.h}px`
      context.current.scale(dpr, dpr)

      // Create new circles based on the quantity prop
      for (let i = 0; i < quantity; i++) {
        circles.current.push(circleParams())
      }
    }
  }

  const circleParams = (): Circle => {
    const x = Math.floor(Math.random() * canvasSize.current.w)
    const y = Math.floor(Math.random() * canvasSize.current.h)
    const translateX = 0
    const translateY = 0
    const pSize = Math.floor(Math.random() * 2) + size
    const alpha = 0
    const targetAlpha = Number.parseFloat((Math.random() * 0.6 + 0.1).toFixed(1))
    const dx = (Math.random() - 0.5) * (vx || 0.1) // Use vx prop or default
    const dy = (Math.random() - 0.5) * (vy || 0.1) // Use vy prop or default
    const magnetism = 0.1 + Math.random() * 4
    return {
      x,
      y,
      translateX,
      translateY,
      size: pSize,
      alpha,
      targetAlpha,
      dx,
      dy,
      magnetism,
    }
  }

  const rgb = hexToRgb(color)

  const drawCircle = (circle: Circle, update = false) => {
    if (context.current) {
      const { x, y, translateX, translateY, size, alpha } = circle
      context.current.translate(translateX, translateY)
      context.current.beginPath()
      context.current.arc(x, y, size, 0, 2 * Math.PI)
      context.current.fillStyle = `rgba(${rgb.join(", ")}, ${alpha})`
      context.current.fill()
      context.current.setTransform(dpr, 0, 0, dpr, 0, 0)

      // No need to push here if update is true, handled in resizeCanvas
      // if (!update) {
      //   circles.current.push(circle)
      // }
    }
  }

  const clearContext = () => {
    if (context.current) {
      context.current.clearRect(0, 0, canvasSize.current.w, canvasSize.current.h)
    }
  }

  // drawParticles function seems redundant as resizeCanvas handles particle creation
  // const drawParticles = () => {
  //   clearContext()
  //   const particleCount = quantity
  //   for (let i = 0; i < particleCount; i++) {
  //     const circle = circleParams()
  //     drawCircle(circle)
  //   }
  // }

  const remapValue = (value: number, start1: number, end1: number, start2: number, end2: number): number => {
    const remapped = ((value - start1) * (end2 - start2)) / (end1 - start1) + start2
    return remapped > 0 ? remapped : 0
  }

  const animate = () => {
    clearContext()
    circles.current.forEach((circle: Circle, i: number) => {
      // Handle the alpha value
      const edge = [
        circle.x + circle.translateX - circle.size, // distance from left edge
        canvasSize.current.w - circle.x - circle.translateX - circle.size, // distance from right edge
        circle.y + circle.translateY - circle.size, // distance from top edge
        canvasSize.current.h - circle.y - circle.translateY - circle.size, // distance from bottom edge
      ]
      const closestEdge = edge.reduce((a, b) => Math.min(a, b))
      const remapClosestEdge = Number.parseFloat(remapValue(closestEdge, 0, 20, 0, 1).toFixed(2))
      if (remapClosestEdge > 1) {
        circle.alpha += 0.02
        if (circle.alpha > circle.targetAlpha) {
          circle.alpha = circle.targetAlpha
        }
      } else {
        circle.alpha = circle.targetAlpha * remapClosestEdge
      }
      circle.x += circle.dx // Use circle.dx directly
      circle.y += circle.dy // Use circle.dy directly
      circle.translateX += (mouse.current.x / (staticity / circle.magnetism) - circle.translateX) / ease
      circle.translateY += (mouse.current.y / (staticity / circle.magnetism) - circle.translateY) / ease

      // Modulo operations to wrap particles around the canvas
      if (circle.x > canvasSize.current.w + circle.size) circle.x = -circle.size;
      if (circle.x < -circle.size) circle.x = canvasSize.current.w + circle.size;
      if (circle.y > canvasSize.current.h + circle.size) circle.y = -circle.size;
      if (circle.y < -circle.size) circle.y = canvasSize.current.h + circle.size;


      drawCircle(circle, true)

      // Particle removal/recreation logic seems unnecessary if wrapping
      // if (
      //   circle.x < -circle.size ||
      //   circle.x > canvasSize.current.w + circle.size ||
      //   circle.y < -circle.size ||
      //   circle.y > canvasSize.current.h + circle.size
      // ) {
      //   circles.current.splice(i, 1)
      //   const newCircle = circleParams()
      //   circles.current.push(newCircle) // Push the new circle back into the array
      // }
    })
    rafID.current = window.requestAnimationFrame(animate)
  }

  return (
    <div className={cn("absolute inset-0 -z-10", className)} ref={canvasContainerRef} aria-hidden="true" {...props}> {/* Ensure absolute positioning and z-index */}
      <canvas ref={canvasRef} className="size-full" />
    </div>
  )
}
