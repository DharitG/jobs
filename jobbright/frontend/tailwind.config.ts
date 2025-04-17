import type { Config } from "tailwindcss";

const config = {
  darkMode: "class",
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
	],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))", // Use CSS vars for shadcn compatibility
          foreground: "hsl(var(--primary-foreground))",
          // Direct values from design system for custom classes
          500: "#3E6DFF",
          600: "#345BDB",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
          // Direct value from design system
          DEFAULT_RAW: "#E34C4C", // Added for direct use if needed
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
           // Direct value from design system
          DEFAULT_RAW: "#18B26E",
        },
        warning: { // Added warning color
            DEFAULT: "#F8A315",
            // Add foreground if needed, e.g., dark text
        },
        error: { // Added error color (synonym for destructive)
            DEFAULT: "#E34C4C",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Grey palette from design system
        grey: {
          5: "#F7F8FC",  // App background
          20: "#E1E4F0", // Dividers
          40: "#B6BDD4", // Secondary text
          90: "#12172B", // Main text
          // 00: "#FFFFFF" // Base - usually covered by 'background' or direct use
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)", // Default shadcn md
        sm: "calc(var(--radius) - 4px)", // Default shadcn sm
        // Custom radius from design system (can override 'md' or use a new key)
        'design-md': "0.75rem", // 12px
      },
      boxShadow: {
         // Custom shadow from design system
        '1': "0 1px 4px rgba(18,23,43,0.08)",
      },
      fontFamily: {
        // Define fonts from design system
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "Noto Sans", "sans-serif", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"],
        display: ["Satoshi", "Inter", "sans-serif"], // Add Satoshi
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;

export default config;
