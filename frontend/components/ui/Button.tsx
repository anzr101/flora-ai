"use client";

import { forwardRef } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variants: Record<Variant, string> = {
  // Subtle top-lit gradient + inner highlight for a premium, tactile feel.
  primary:
    "bg-gradient-to-b from-[rgb(34_82_61)] to-forest text-ivory shadow-md hover:shadow-lg hover:brightness-[1.06] active:translate-y-px [box-shadow:inset_0_1px_0_0_rgb(255_255_255_/_0.08),0_4px_16px_-4px_rgb(27_67_50_/_0.3)]",
  secondary:
    "bg-gradient-to-b from-[rgb(96_198_152)] to-leaf text-white shadow-sm hover:shadow-md hover:brightness-[1.05] active:translate-y-px",
  outline:
    "border border-line bg-surface/80 text-ink backdrop-blur-sm hover:border-leaf/50 hover:bg-leaf/[0.05] hover:shadow-sm",
  ghost: "text-ink/80 hover:bg-forest/[0.05] hover:text-forest",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3.5 text-[0.85rem] gap-1.5 rounded-sm",
  md: "h-11 px-5 text-[0.92rem] gap-2 rounded",
  lg: "h-[3.25rem] px-7 text-[0.98rem] gap-2.5 rounded-lg",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "focus-ring inline-flex select-none items-center justify-center font-medium transition-all duration-200 ease-organic disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
