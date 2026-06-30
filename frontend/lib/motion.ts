// Shared motion vocabulary for FloraAI. Calm, organic easing — nothing snappy.

export const easeOutExpo = [0.16, 1, 0.3, 1] as const;
export const easeCalm = [0.22, 1, 0.36, 1] as const;

export const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: easeOutExpo } },
};

export const fadeIn = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.9, ease: easeCalm } },
};

export const riseBlur = {
  hidden: { opacity: 0, y: 24, filter: "blur(6px)" },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.9, ease: easeOutExpo },
  },
};

// Parent that staggers children — the highest-impact "expensive" cue.
export const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.09, delayChildren: 0.08 } },
};

export const staggerSlow = {
  hidden: {},
  show: { transition: { staggerChildren: 0.14, delayChildren: 0.12 } },
};

// Viewport defaults so sections reveal once, a touch before entering view.
export const inViewOnce = { once: true, margin: "-80px" } as const;
