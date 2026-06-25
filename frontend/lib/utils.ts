import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind classes with conflict resolution. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a 0–1 probability as a percentage string. */
export function pct(value: number, digits = 0): string {
  return `${(value * 100).toFixed(digits)}%`;
}

/** Title-case a snake_case feature/label name for display. */
export function humanize(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\bpct\b/gi, "%")
    .replace(/\bph\b/gi, "pH")
    .replace(/\bc\b/gi, "(°C)")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
