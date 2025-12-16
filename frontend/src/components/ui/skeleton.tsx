import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const skeletonVariants = cva(
  "animate-pulse rounded-md bg-slate-200 dark:bg-slate-700",
  {
    variants: {
      variant: {
        default: "bg-slate-200 dark:bg-slate-700",
        text: "h-4 w-full bg-slate-200 dark:bg-slate-700",
        heading: "h-8 w-3/4 bg-slate-200 dark:bg-slate-700",
        circle: "rounded-full bg-slate-200 dark:bg-slate-700",
        card: "h-48 w-full bg-slate-200 dark:bg-slate-700",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(skeletonVariants({ variant, className }))}
        {...props}
      />
    )
  }
)
Skeleton.displayName = "Skeleton"

// Preset skeleton compositions for common loading states
const SkeletonHeader = () => (
  <div className="space-y-3">
    <Skeleton variant="heading" className="w-1/3" />
    <Skeleton variant="text" className="w-1/2" />
  </div>
)

const SkeletonCard = () => (
  <div className="space-y-3 p-6 border border-slate-200 rounded-xl dark:border-slate-700">
    <div className="flex items-center gap-3">
      <Skeleton variant="circle" className="size-12" />
      <div className="flex-1 space-y-2">
        <Skeleton variant="text" className="w-1/3" />
        <Skeleton variant="text" className="w-1/4 h-3" />
      </div>
    </div>
    <div className="space-y-2">
      <Skeleton variant="text" className="w-full" />
      <Skeleton variant="text" className="w-5/6" />
      <Skeleton variant="text" className="w-4/6" />
    </div>
    <div className="flex gap-2">
      <Skeleton className="h-9 w-24" />
      <Skeleton className="h-9 w-24" />
    </div>
  </div>
)

const SkeletonCurriculumCard = () => (
  <div className="space-y-4 p-6 border border-slate-200 rounded-xl bg-white dark:border-slate-700 dark:bg-slate-800">
    <div className="flex justify-between items-start">
      <div className="flex-1 space-y-2">
        <Skeleton variant="heading" className="w-2/3 h-6" />
        <Skeleton variant="text" className="w-1/2 h-3" />
      </div>
      <Skeleton className="h-6 w-16" />
    </div>
    <div className="space-y-2">
      <Skeleton variant="text" className="w-full h-3" />
      <Skeleton variant="text" className="w-4/5 h-3" />
    </div>
    <div className="flex justify-between text-sm">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-4 w-20" />
    </div>
    <div className="space-y-1">
      <Skeleton className="h-2 w-full rounded-full" />
      <Skeleton className="h-3 w-16" />
    </div>
  </div>
)

const SkeletonExerciseCard = () => (
  <div className="p-6 border border-slate-200 rounded-xl bg-white dark:border-slate-700 dark:bg-slate-800">
    <div className="flex justify-between items-start mb-4">
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
        <Skeleton variant="text" className="w-full h-3" />
        <div className="flex gap-4">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
      <div className="space-y-1 text-right">
        <Skeleton className="h-4 w-24 ml-auto" />
        <Skeleton className="h-3 w-20 ml-auto" />
      </div>
    </div>
  </div>
)

const SkeletonTable = ({ rows = 5 }: { rows?: number }) => (
  <div className="space-y-3">
    <div className="flex gap-3 pb-3 border-b border-slate-200 dark:border-slate-700">
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-4 w-1/4" />
    </div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex gap-3 py-2">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
      </div>
    ))}
  </div>
)

export {
  Skeleton,
  SkeletonHeader,
  SkeletonCard,
  SkeletonCurriculumCard,
  SkeletonExerciseCard,
  SkeletonTable,
}
