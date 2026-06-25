import type { Config } from "tailwindcss";

/**
 * FloraAI design tokens.
 * Colors resolve to CSS variables (declared in globals.css) so the same scale
 * can be re-themed (e.g. dark mode) without touching component code.
 */
const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Channel-triplet CSS vars (declared in globals.css) so Tailwind opacity
        // modifiers (bg-leaf/10, ring-leaf/60, …) work AND dark mode can retheme.
        forest: "rgb(var(--forest) / <alpha-value>)",
        sage: "rgb(var(--sage) / <alpha-value>)",
        leaf: "rgb(var(--leaf) / <alpha-value>)",
        ivory: "rgb(var(--ivory) / <alpha-value>)",
        surface: "rgb(var(--surface) / <alpha-value>)",
        ink: "rgb(var(--ink) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)",
        success: "rgb(var(--success) / <alpha-value>)",
        warning: "rgb(var(--warning) / <alpha-value>)",
        danger: "rgb(var(--danger) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      fontSize: {
        // Editorial scale — confident headings, comfortable body.
        "display-lg": ["clamp(2.75rem, 6vw, 4.5rem)", { lineHeight: "1.04", letterSpacing: "-0.025em" }],
        "display": ["clamp(2.25rem, 4.2vw, 3.25rem)", { lineHeight: "1.08", letterSpacing: "-0.02em" }],
        "title": ["1.6rem", { lineHeight: "1.2", letterSpacing: "-0.015em" }],
      },
      borderRadius: {
        sm: "8px",
        DEFAULT: "12px",
        lg: "16px",
        xl: "22px",
        "2xl": "28px",
      },
      boxShadow: {
        xs: "0 1px 2px rgba(27, 67, 50, 0.04)",
        sm: "0 1px 3px rgba(27, 67, 50, 0.06), 0 1px 2px rgba(27, 67, 50, 0.04)",
        md: "0 4px 16px -4px rgba(27, 67, 50, 0.08), 0 2px 6px -2px rgba(27, 67, 50, 0.05)",
        lg: "0 18px 40px -12px rgba(27, 67, 50, 0.14), 0 6px 14px -6px rgba(27, 67, 50, 0.08)",
        glow: "0 0 0 1px rgba(82, 183, 136, 0.25), 0 10px 30px -10px rgba(82, 183, 136, 0.35)",
      },
      maxWidth: {
        content: "1180px",
        prose: "68ch",
      },
      transitionTimingFunction: {
        organic: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s var(--ease-organic) both",
      },
    },
  },
  plugins: [],
};

export default config;
