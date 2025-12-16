import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Button } from "./button"

const emptyStateVariants = cva(
  "flex flex-col items-center justify-center text-center",
  {
    variants: {
      size: {
        sm: "py-8 px-4",
        md: "py-12 px-6",
        lg: "py-16 px-8",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
)

export interface EmptyStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof emptyStateVariants> {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick?: () => void
    href?: string
  }
  secondaryAction?: {
    label: string
    onClick?: () => void
    href?: string
  }
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({
    className,
    size,
    icon,
    title,
    description,
    action,
    secondaryAction,
    ...props
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(emptyStateVariants({ size, className }))}
        {...props}
      >
        {/* Icon */}
        {icon && (
          <div className="mb-4 text-6xl opacity-50" aria-hidden="true">
            {icon}
          </div>
        )}

        {/* Title */}
        <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
          {title}
        </h3>

        {/* Description */}
        {description && (
          <p className="text-slate-600 dark:text-slate-400 max-w-md mb-6">
            {description}
          </p>
        )}

        {/* Actions */}
        {(action || secondaryAction) && (
          <div className="flex flex-col sm:flex-row gap-3 items-center justify-center">
            {action && (
              action.href ? (
                <Button asChild variant="primary" size="lg">
                  <a href={action.href}>{action.label}</a>
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="lg"
                  onClick={action.onClick}
                >
                  {action.label}
                </Button>
              )
            )}

            {secondaryAction && (
              secondaryAction.href ? (
                <Button asChild variant="outline" size="lg">
                  <a href={secondaryAction.href}>{secondaryAction.label}</a>
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="lg"
                  onClick={secondaryAction.onClick}
                >
                  {secondaryAction.label}
                </Button>
              )
            )}
          </div>
        )}
      </div>
    )
  }
)
EmptyState.displayName = "EmptyState"

export { EmptyState }
