import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const cardVariants = cva(
  "rounded-xl border transition-all duration-300",
  {
    variants: {
      variant: {
        // Default light card
        default: "bg-white border-slate-200 dark:bg-slate-800 dark:border-slate-700",

        // Elevated card with shadow
        elevated: "bg-white border-slate-200 shadow-lg hover:shadow-xl dark:bg-slate-800 dark:border-slate-700",

        // Glassmorphism effect
        glass: "bg-white/50 backdrop-blur-sm border-slate-200/50 dark:bg-slate-800/50 dark:border-slate-700/50",

        // Gradient background
        gradient: "bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200 dark:from-slate-800 dark:to-slate-900 dark:border-slate-700",

        // Interactive card (hoverable)
        interactive: "bg-white border-slate-200 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10 cursor-pointer dark:bg-slate-800 dark:border-slate-700 dark:hover:border-purple-500/50",

        // Outline only
        outline: "bg-transparent border-slate-300 dark:border-slate-600",

        // Genre-specific cards
        gospel: "bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200 dark:from-purple-950/20 dark:to-pink-950/20 dark:border-purple-800/30",
        jazz: "bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200 dark:from-blue-950/20 dark:to-cyan-950/20 dark:border-blue-800/30",
        blues: "bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200 dark:from-indigo-950/20 dark:to-purple-950/20 dark:border-indigo-800/30",
        neosoul: "bg-gradient-to-br from-pink-50 to-rose-50 border-pink-200 dark:from-pink-950/20 dark:to-rose-950/20 dark:border-pink-800/30",
      },
      padding: {
        none: "p-0",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      }
    },
    defaultVariants: {
      variant: "default",
      padding: "md",
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, padding, className }))}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & { as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" }
>(({ className, as: Comp = "h3", ...props }, ref) => (
  <Comp
    ref={ref as any}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight text-slate-900 dark:text-slate-100",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-slate-600 dark:text-slate-400", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
