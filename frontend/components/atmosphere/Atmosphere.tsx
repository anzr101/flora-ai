import { Frond, Sprig } from "@/components/botanical/Botanicals";

/**
 * The living backdrop for the whole platform — soft dawn light, drifting mist,
 * and overgrown foliage at the edges, all breathing slowly. Purely decorative,
 * fixed behind content, GPU-cheap (transform/opacity only), and quiet under
 * `prefers-reduced-motion`.
 */
export function Atmosphere() {
  return (
    <div
      aria-hidden="true"
      className="grain pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      style={{ backgroundColor: "rgb(var(--ivory))" }}
    >
      {/* Soft daylight blooms — dawn warmth above, sage light at the sides. */}
      <div
        className="animate-breathe absolute -right-[12%] -top-[18%] h-[55rem] w-[55rem] rounded-full blur-[90px]"
        style={{ background: "radial-gradient(circle at 35% 35%, rgb(var(--dawn) / 0.45), transparent 62%)" }}
      />
      <div
        className="animate-breathe absolute -left-[14%] top-[8%] h-[44rem] w-[44rem] rounded-full blur-[90px] [animation-delay:2s]"
        style={{ background: "radial-gradient(circle at 50% 50%, rgb(var(--sage) / 0.4), transparent 60%)" }}
      />
      <div
        className="animate-breathe absolute bottom-[-16%] left-[26%] h-[40rem] w-[40rem] rounded-full blur-[100px] [animation-delay:4s]"
        style={{ background: "radial-gradient(circle at 50% 50%, rgb(var(--leaf) / 0.22), transparent 65%)" }}
      />

      {/* A horizontal band of mist across the upper third. */}
      <div
        className="absolute inset-x-0 top-[22%] h-48 blur-2xl"
        style={{ background: "linear-gradient(rgb(var(--mist) / 0), rgb(var(--mist) / 0.5), rgb(var(--mist) / 0))" }}
      />

      {/* Overgrown foliage at the edges — canopy silhouettes, blurred & swaying. */}
      <div className="animate-drift absolute -left-24 -top-16 h-[34rem] w-[20rem] text-forest/[0.06] blur-[1.5px]">
        <div className="animate-sway h-full w-full">
          <Frond />
        </div>
      </div>
      <div className="animate-drift-2 absolute -right-28 top-[34%] h-[40rem] w-[22rem] rotate-[18deg] text-moss/[0.07] blur-[1.5px]">
        <div className="animate-sway h-full w-full [animation-delay:1.5s]">
          <Frond />
        </div>
      </div>
      <div className="animate-drift absolute -bottom-10 left-[8%] h-[14rem] w-[28rem] text-forest/[0.06] blur-[1px] [animation-delay:3s]">
        <Sprig />
      </div>
      <div className="animate-drift-2 absolute bottom-[12%] right-[6%] h-[12rem] w-[24rem] -scale-x-100 text-moss/[0.06] blur-[1px]">
        <Sprig />
      </div>

      {/* Gentle vignette to settle the edges. */}
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(120% 90% at 50% 0%, transparent 60%, rgb(var(--canopy) / 0.05))" }}
      />
    </div>
  );
}
