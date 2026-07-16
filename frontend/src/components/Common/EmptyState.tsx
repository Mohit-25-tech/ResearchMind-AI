import type { ReactNode } from "react";

interface EmptyStateProps {
  /** Icon element to display above the title */
  icon: ReactNode;
  /** Main heading */
  title: string;
  /** Secondary description text */
  subtitle?: string;
}

export default function EmptyState({ icon, title, subtitle }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 px-4 text-center">
      <div className="text-text-muted">{icon}</div>
      <h3 className="text-sm font-medium text-text-secondary">{title}</h3>
      {subtitle && (
        <p className="text-xs text-text-muted">{subtitle}</p>
      )}
    </div>
  );
}
