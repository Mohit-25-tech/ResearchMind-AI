import { Loader2 } from "lucide-react";

interface LoadingProps {
  /** Text to display below the spinner, e.g. "Uploading...", "Thinking..." */
  text?: string;
  /** Size of the spinner icon in pixels */
  size?: number;
}

export default function Loading({ text = "Loading...", size = 20 }: LoadingProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <Loader2
        size={size}
        className="animate-spin text-accent"
      />
      <p className="text-sm text-text-secondary">{text}</p>
    </div>
  );
}
