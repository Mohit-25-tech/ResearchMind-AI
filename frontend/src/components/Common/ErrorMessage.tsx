import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-6">
      <div className="flex items-center gap-1.5 rounded-md bg-error-subtle px-3 py-2">
        <AlertCircle size={13} className="text-error shrink-0" />
        <p className="text-xs text-error">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1 rounded-md px-2.5 py-1 text-xs
                     text-text-muted hover:text-text-secondary hover:bg-surface-elevated
                     transition-colors cursor-pointer"
        >
          <RefreshCw size={11} />
          Retry
        </button>
      )}
    </div>
  );
}
