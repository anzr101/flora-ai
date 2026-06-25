"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { pct } from "@/lib/utils";

/** A calm horizontal confidence/probability meter with an animated fill. */
export function Meter({
  value,
  label,
  valueLabel,
  tone = "leaf",
  className,
}: {
  value: number; // 0..1
  label?: string;
  valueLabel?: string;
  tone?: "leaf" | "forest" | "success" | "warning" | "danger" | "muted";
  className?: string;
}) {
  const toneClass = {
    leaf: "bg-leaf",
    forest: "bg-forest",
    success: "bg-success",
    warning: "bg-warning",
    danger: "bg-danger",
    muted: "bg-muted/50",
  }[tone];

  return (
    <div className={cn("w-full", className)}>
      {(label || valueLabel) && (
        <div className="mb-1.5 flex items-center justify-between text-[0.8rem]">
          {label && <span className="text-ink/80">{label}</span>}
          <span className="font-mono text-[0.78rem] tabular-nums text-muted">
            {valueLabel ?? pct(value, 1)}
          </span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-forest/[0.07]">
        <motion.div
          className={cn("h-full rounded-full", toneClass)}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(0, Math.min(1, value)) * 100}%` }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
    </div>
  );
}
