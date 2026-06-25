"use client";

import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Input = forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "focus-ring h-11 w-full rounded-sm border border-line bg-surface px-3.5 text-[0.92rem] text-ink placeholder:text-muted/60 transition-colors hover:border-leaf/40",
      className,
    )}
    {...props}
  />
));
Input.displayName = "Input";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "focus-ring w-full resize-none rounded-sm border border-line bg-surface px-3.5 py-3 text-[0.92rem] leading-relaxed text-ink placeholder:text-muted/60 transition-colors hover:border-leaf/40",
      className,
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";

export function Field({
  label,
  hint,
  unit,
  children,
}: {
  label: string;
  hint?: string;
  unit?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-baseline justify-between">
        <span className="text-[0.82rem] font-medium text-ink/90">{label}</span>
        {unit && <span className="text-[0.72rem] text-muted">{unit}</span>}
      </span>
      {children}
      {hint && <span className="mt-1 block text-[0.72rem] text-muted">{hint}</span>}
    </label>
  );
}
