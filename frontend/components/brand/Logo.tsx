import { cn } from "@/lib/utils";

/**
 * FloraAI mark — a minimal, single-stroke leaf with a subtle midrib.
 * Drawn as inline SVG (not an icon font / emoji) so it stays crisp and on-brand.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      className={cn("h-7 w-7", className)}
      aria-hidden="true"
    >
      <path
        d="M26 6C13 6 6 13.5 6 25c0 .55.45 1 1 1 11.5 0 19-7 19-20 0-.55-.45-1-1-1Z"
        className="fill-leaf/15 stroke-forest"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M9 23C14 16 18.5 12.5 24 9"
        className="stroke-forest"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 text-[1.05rem] font-semibold tracking-tight text-forest",
        className,
      )}
    >
      <LogoMark />
      <span>
        Flora<span className="text-leaf">AI</span>
      </span>
    </span>
  );
}
