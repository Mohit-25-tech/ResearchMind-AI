import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  subtitle?: string;
}

export default function EmptyState({ icon, title, subtitle }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center gap-2 py-10 px-4 text-center"
    >
      <div className="text-text-faint">{icon}</div>
      <h3 className="text-xs font-medium text-text-muted">{title}</h3>
      {subtitle && (
        <p className="text-[11px] text-text-faint">{subtitle}</p>
      )}
    </motion.div>
  );
}
