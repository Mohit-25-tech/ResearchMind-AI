import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorMessageProps {
  /** The error message to display */
  message: string;
  /** Optional retry callback — shows a Retry button when provided */
  onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className="flex items-center gap-2 rounded-lg bg-error-subtle px-4 py-2.5">
        <AlertCircle size={16} className="text-error shrink-0" />
        <p className="text-sm text-error">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm
                     text-text-secondary hover:text-text-primary hover:bg-surface-elevated
                     transition-colors cursor-pointer"
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
}
