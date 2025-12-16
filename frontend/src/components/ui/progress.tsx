import * as React from 'react';

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
    value?: number;
    max?: number;
    className?: string;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
    ({ value = 0, max = 100, className = '', ...props }, ref) => {
        const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

        return (
            <div
                ref={ref}
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={max}
                aria-valuenow={value}
                className={`relative w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700 ${className}`}
                {...props}
            >
                <div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300 ease-out"
                    style={{ width: `${percentage}%` }}
                />
            </div>
        );
    }
);

Progress.displayName = 'Progress';

export { Progress };
export type { ProgressProps };
