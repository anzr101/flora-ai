import { cn } from "@/lib/utils";

type Tone = "neutral" | "leaf" | "success" | "warning" | "danger";

const tones: Record<Tone, string> = {
  neutral: "bg-forest/[0.06] text-forest border-forest/10",
  leaf: "bg-leaf/10 text-forest border-leaf/20",
  success: "bg-success/10 text-success border-success/20",
  warning: "bg-warning/15 text-[#8a6d1f] border-warning/30",
  danger: "bg-danger/10 text-danger border-danger/20",
};

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[0.74rem] font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
