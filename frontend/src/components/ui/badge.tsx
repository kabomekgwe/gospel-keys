import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        // Status variants
        default: "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100",

        success: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800",

        warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800",

        error: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800",

        info: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800",

        // Curriculum status
        active: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800",

        completed: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800",

        draft: "bg-gray-100 text-gray-800 dark:bg-gray-800/30 dark:text-gray-400 border border-gray-200 dark:border-gray-700",

        // Priority indicators
        overdue: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800",

        new: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800 animate-pulse",

        // Difficulty levels
        beginner: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800",

        intermediate: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 border border-amber-200 dark:border-amber-800",

        advanced: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800",

        // Genre badges
        gospel: "bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 border border-purple-200 dark:from-purple-900/30 dark:to-pink-900/30 dark:text-purple-400 dark:border-purple-800",

        jazz: "bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800 border border-blue-200 dark:from-blue-900/30 dark:to-cyan-900/30 dark:text-blue-400 dark:border-blue-800",

        blues: "bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800 border border-indigo-200 dark:from-indigo-900/30 dark:to-purple-900/30 dark:text-indigo-400 dark:border-indigo-800",

        neosoul: "bg-gradient-to-r from-pink-100 to-rose-100 text-pink-800 border border-pink-200 dark:from-pink-900/30 dark:to-rose-900/30 dark:text-pink-400 dark:border-pink-800",

        // Outline variant
        outline: "text-foreground border border-slate-300 dark:border-slate-600",
      },
      size: {
        sm: "text-[10px] px-2 py-0.5",
        md: "text-xs px-2.5 py-0.5",
        lg: "text-sm px-3 py-1",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
