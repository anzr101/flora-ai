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
  // Deep canopy with a soft inner light — tactile, organic, never flat.
  primary:
    "bg-gradient-to-b from-[rgb(34_82_61)] to-forest text-ivory shadow-soft hover:shadow-lift hover:brightness-[1.07] active:translate-y-px [box-shadow:inset_0_1px_0_0_rgb(255_255_255_/_0.1),0_10px_30px_-12px_rgb(20_43_32_/_0.5)]",
  secondary:
    "bg-gradient-to-b from-[rgb(96_198_152)] to-leaf text-white shadow-soft hover:shadow-lift hover:brightness-[1.05] active:translate-y-px",
  outline:
    "border border-forest/15 bg-surface/70 text-forest backdrop-blur-md hover:border-leaf/45 hover:bg-leaf/[0.06] hover:shadow-soft",
  ghost: "text-forest/80 hover:bg-forest/[0.05] hover:text-forest",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-4 text-[0.85rem] gap-1.5 rounded-full",
  md: "h-11 px-5 text-[0.92rem] gap-2 rounded-full",
  lg: "h-[3.35rem] px-8 text-[0.98rem] gap-2.5 rounded-full",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "focus-ring inline-flex select-none items-center justify-center font-medium transition-all duration-300 ease-organic disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
