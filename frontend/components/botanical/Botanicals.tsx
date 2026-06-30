/**
 * Hand-crafted botanical line-art (inline SVG, currentColor strokes).
 * Used as decorative, breathing accents throughout the sanctuary. Drawn — not
 * stock imagery — so it reads as intentional and stays crisp at any size.
 */
import { cn } from "@/lib/utils";

type Props = { className?: string; strokeWidth?: number };

/** A fern frond — central midrib with tapering leaflet pairs (generated). */
export function Frond({ className, strokeWidth = 1.4 }: Props) {
  const N = 13;
  const midrib: [number, number][] = [];
  for (let i = 0; i <= 40; i++) {
    const t = i / 40;
    const y = 300 - t * 286;
    const x = 60 + 16 * Math.sin(t * Math.PI * 0.9); // gentle bow
    midrib.push([x, y]);
  }
  const ribPath =
    "M" + midrib.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" L");

  const leaflets: string[] = [];
  for (let i = 1; i <= N; i++) {
    const t = i / (N + 1);
    const y = 300 - t * 286;
    const x = 60 + 16 * Math.sin(t * Math.PI * 0.9);
    const len = 40 * (1 - t) + 8;
    const lift = 18 * (1 - t) + 6;
    // right + left leaflet as gentle quadratic curves
    leaflets.push(`M${x},${y} Q${x + len * 0.6},${y - lift * 0.4} ${x + len},${y - lift}`);
    leaflets.push(`M${x},${y} Q${x - len * 0.6},${y - lift * 0.4} ${x - len},${y - lift}`);
  }

  return (
    <svg viewBox="0 0 120 320" fill="none" className={cn("h-full w-full", className)} aria-hidden="true">
      <path d={ribPath} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" />
      {leaflets.map((d, i) => (
        <path key={i} d={d} stroke="currentColor" strokeWidth={strokeWidth * 0.8} strokeLinecap="round" opacity={0.92} />
      ))}
    </svg>
  );
}

/** A single elegant leaf with midrib and side veins. */
export function LeafVein({ className, strokeWidth = 1.4 }: Props) {
  return (
    <svg viewBox="0 0 100 140" fill="none" className={cn("h-full w-full", className)} aria-hidden="true">
      <path
        d="M50 6 C78 42 80 96 50 134 C20 96 22 42 50 6 Z"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        className="fill-leaf/[0.06]"
      />
      <path d="M50 16 L50 126" stroke="currentColor" strokeWidth={strokeWidth * 0.85} strokeLinecap="round" />
      {[28, 48, 68, 88].map((y, i) => {
        const spread = 22 - i * 3.5;
        return (
          <g key={y} opacity={0.7}>
            <path d={`M50 ${y} Q${50 + spread * 0.5} ${y + 4} ${50 + spread} ${y + 14}`} stroke="currentColor" strokeWidth={strokeWidth * 0.7} strokeLinecap="round" />
            <path d={`M50 ${y} Q${50 - spread * 0.5} ${y + 4} ${50 - spread} ${y + 14}`} stroke="currentColor" strokeWidth={strokeWidth * 0.7} strokeLinecap="round" />
          </g>
        );
      })}
    </svg>
  );
}

/** A eucalyptus-like sprig — round leaves paired along a curving stem. */
export function Sprig({ className, strokeWidth = 1.4 }: Props) {
  const stem: [number, number][] = [];
  for (let i = 0; i <= 30; i++) {
    const t = i / 30;
    const x = 20 + t * 150;
    const y = 70 + 34 * Math.sin(t * Math.PI);
    stem.push([x, y]);
  }
  const stemPath = "M" + stem.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" L");
  const leaves: { cx: number; cy: number; rot: number }[] = [];
  for (let i = 1; i <= 7; i++) {
    const t = i / 8;
    const x = 20 + t * 150;
    const y = 70 + 34 * Math.sin(t * Math.PI);
    const dydx = Math.cos(t * Math.PI);
    const ang = (Math.atan2(34 * dydx * (Math.PI / 8), 5) * 180) / Math.PI;
    leaves.push({ cx: x, cy: y - 14, rot: ang - 30 });
    leaves.push({ cx: x, cy: y + 14, rot: ang + 30 + 180 });
  }
  return (
    <svg viewBox="0 0 190 140" fill="none" className={cn("h-full w-full", className)} aria-hidden="true">
      <path d={stemPath} stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" />
      {leaves.map((l, i) => (
        <ellipse
          key={i}
          cx={l.cx}
          cy={l.cy}
          rx="11"
          ry="6.5"
          transform={`rotate(${l.rot} ${l.cx} ${l.cy})`}
          stroke="currentColor"
          strokeWidth={strokeWidth * 0.8}
          className="fill-leaf/[0.05]"
        />
      ))}
    </svg>
  );
}
