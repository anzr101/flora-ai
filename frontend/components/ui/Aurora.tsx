import { cn } from "@/lib/utils";

/**
 * Decorative aurora backdrop — soft, slow-drifting botanical light.
 * Purely ornamental: absolutely positioned, pointer-events-none, behind content.
 * Calm by design (low opacity, slow motion) — never neon or flashy.
 */
export function Aurora({ className }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}
    >
      <div
        className="absolute -right-[10%] -top-[20%] h-[42rem] w-[42rem] rounded-full opacity-60 blur-[80px]"
        style={{
          background:
            "radial-gradient(circle at 30% 30%, rgb(var(--sage) / 0.55), transparent 60%)",
          animation: "drift-a 16s var(--ease-organic) infinite",
        }}
      />
      <div
        className="absolute -left-[12%] top-[18%] h-[34rem] w-[34rem] rounded-full opacity-50 blur-[80px]"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgb(var(--leaf) / 0.32), transparent 62%)",
          animation: "drift-b 20s var(--ease-organic) infinite",
        }}
      />
      <div
        className="absolute bottom-[-15%] right-[20%] h-[28rem] w-[28rem] rounded-full opacity-40 blur-[90px]"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgb(var(--success) / 0.28), transparent 65%)",
          animation: "drift-a 24s var(--ease-organic) infinite",
        }}
      />
    </div>
  );
}
