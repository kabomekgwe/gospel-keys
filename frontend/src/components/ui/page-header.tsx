import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const pageHeaderVariants = cva(
  "flex flex-col gap-2",
  {
    variants: {
      spacing: {
        sm: "mb-4",
        md: "mb-6",
        lg: "mb-8",
        xl: "mb-12",
      },
    },
    defaultVariants: {
      spacing: "lg",
    },
  }
)

export interface PageHeaderProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof pageHeaderVariants> {
  title: string
  description?: string
  badge?: React.ReactNode
  actions?: React.ReactNode
}

const PageHeader = React.forwardRef<HTMLDivElement, PageHeaderProps>(
  ({ className, spacing, title, description, badge, actions, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(pageHeaderVariants({ spacing, className }))}
        {...props}
      >
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100">
                {title}
              </h1>
              {badge && <div>{badge}</div>}
            </div>
            {description && (
              <p className="text-base text-slate-600 dark:text-slate-400 max-w-3xl">
                {description}
              </p>
            )}
          </div>
          {actions && (
            <div className="flex items-center gap-2">
              {actions}
            </div>
          )}
        </div>
      </div>
    )
  }
)
PageHeader.displayName = "PageHeader"

// Sub-components for more flexible composition
const PageHeaderTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h1
    ref={ref}
    className={cn(
      "text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100",
      className
    )}
    {...props}
  />
))
PageHeaderTitle.displayName = "PageHeaderTitle"

const PageHeaderDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn(
      "text-base text-slate-600 dark:text-slate-400 max-w-3xl",
      className
    )}
    {...props}
  />
))
PageHeaderDescription.displayName = "PageHeaderDescription"

export { PageHeader, PageHeaderTitle, PageHeaderDescription }
