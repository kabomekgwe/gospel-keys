/**
 * Toast Notification Component
 * Lightweight toast system for user feedback
 */

import { cva, type VariantProps } from 'class-variance-authority';
import { X } from 'lucide-react';
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

// Toast Variants
const toastVariants = cva(
  'pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-lg border p-4 shadow-lg transition-all',
  {
    variants: {
      variant: {
        default: 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700',
        success: 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900',
        error: 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900',
        warning: 'bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-900',
        info: 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

// Toast Types
export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: Toast = { ...toast, id };

    setToasts((prev) => [...prev, newToast]);

    // Auto-remove after duration (default 5s)
    const duration = toast.duration ?? 5000;
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

interface ToastContainerProps {
  toasts: Toast[];
  removeToast: (id: string) => void;
}

function ToastContainer({ toasts, removeToast }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-4 sm:p-6">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

interface ToastItemProps {
  toast: Toast;
  onClose: () => void;
}

function ToastItem({ toast, onClose }: ToastItemProps) {
  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
    default: '',
  };

  const icon = iconMap[toast.variant || 'default'];

  return (
    <div className={toastVariants({ variant: toast.variant })}>
      {icon && (
        <div
          className={`flex size-5 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
            toast.variant === 'success'
              ? 'bg-green-500 text-white'
              : toast.variant === 'error'
                ? 'bg-red-500 text-white'
                : toast.variant === 'warning'
                  ? 'bg-yellow-500 text-white'
                  : toast.variant === 'info'
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-500 text-white'
          }`}
        >
          {icon}
        </div>
      )}
      <div className="flex-1">
        <p className="font-semibold text-sm text-slate-900 dark:text-white">{toast.title}</p>
        {toast.description && (
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{toast.description}</p>
        )}
      </div>
      <button
        onClick={onClose}
        className="shrink-0 rounded-md p-1 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        aria-label="Close"
      >
        <X className="size-4 text-slate-500 dark:text-slate-400" />
      </button>
    </div>
  );
}
