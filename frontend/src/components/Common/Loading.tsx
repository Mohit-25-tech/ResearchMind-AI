import { Loader2 } from "lucide-react";

interface LoadingProps {
  text?: string;
  size?: number;
}

export default function Loading({ text = "Loading...", size = 16 }: LoadingProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-8">
      <Loader2 size={size} className="animate-spin text-text-muted" />
      <p className="text-[11px] text-text-muted">{text}</p>
    </div>
  );
}
