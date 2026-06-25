import { cn } from "@/lib/utils";

/** Organic loading indicator — a gentle rotating arc, never flashy. */
export function Spinner({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={cn("h-5 w-5 animate-spin text-leaf", className)}
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.2" strokeWidth="2.5" />
      <path
        d="M21 12a9 9 0 0 0-9-9"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function LoadingDots({ label }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-2 text-muted">
      <span className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 animate-bounce rounded-full bg-leaf"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </span>
      {label && <span className="text-[0.85rem]">{label}</span>}
    </span>
  );
}
