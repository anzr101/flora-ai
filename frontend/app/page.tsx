"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Frond, LeafVein, Sprig } from "@/components/botanical/Botanicals";
import { fadeUp, riseBlur, stagger, staggerSlow, inViewOnce, easeOutExpo } from "@/lib/motion";

const CHAPTERS = [
  {
    no: "i",
    kicker: "The eye",
    title: "It recognises what it sees",
    body: "Photograph any plant — a windowsill monstera, a wild fern, a herb from the garden. A vision model trained across the tree of life names the species from the leaf alone, returning its botanical name with a quiet measure of certainty.",
    href: "/vision",
    cta: "Identify a plant",
    art: "leaf" as const,
  },
  {
    no: "ii",
    kicker: "The reading",
    title: "It senses how a plant is faring",
    body: "Light, water, warmth, soil. From the conditions a plant lives in, a model reads its wellbeing — and, gently, explains which of those conditions are tipping it toward stress, so you know what to change.",
    href: "/health",
    cta: "Read its wellbeing",
    art: "sprig" as const,
  },
  {
    no: "iii",
    kicker: "The companion",
    title: "It reasons, and answers with care",
    body: "Ask anything. A patient companion draws on a curated body of botanical knowledge, cites where each answer comes from, and weaves the vision and wellbeing readings into one clear, kind recommendation.",
    href: "/assistant",
    cta: "Meet the companion",
    art: "frond" as const,
  },
];

const QUIET_METRICS = [
  { v: "450k", l: "species recognised" },
  { v: "0.72", l: "wellbeing macro-F1" },
  { v: "every", l: "answer cited" },
];

export default function HomePage() {
  const reduce = useReducedMotion();

  return (
    <>
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative">
        <div className="container-flora grid items-center gap-14 py-24 md:py-32 lg:grid-cols-[1.05fr_0.95fr]">
          <motion.div variants={staggerSlow} initial="hidden" animate="show">
            <motion.span variants={fadeUp} className="eyebrow">
              <span className="h-px w-7 bg-moss/50" />
              The botanical conservatory
            </motion.span>

            <motion.h1
              variants={riseBlur}
              className="mt-7 font-display text-[clamp(2.9rem,6.5vw,5rem)] font-normal leading-[1.02] tracking-[-0.025em] text-forest"
            >
              Tend to what
              <br />
              <span className="text-gradient italic">quietly grows.</span>
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="mt-8 max-w-xl text-[1.12rem] leading-relaxed text-muted"
            >
              FloraAI is a calm sanctuary for plant intelligence — a vision that
              recognises, a sense for wellbeing, and a companion that reasons.
              Step away from the noise and understand the living things in your care.
            </motion.p>

            <motion.div variants={fadeUp} className="mt-10 flex flex-wrap items-center gap-3.5">
              <Link href="/diagnose">
                <Button size="lg">
                  Diagnose a plant <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/assistant">
                <Button size="lg" variant="outline">
                  Meet the companion
                </Button>
              </Link>
            </motion.div>

            <motion.div
              variants={fadeUp}
              className="mt-12 flex flex-wrap items-center gap-x-7 gap-y-2 text-[0.84rem] text-muted"
            >
              {["Recognises any plant", "Explains its reasoning", "Cites its sources"].map((t) => (
                <span key={t} className="flex items-center gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-leaf" /> {t}
                </span>
              ))}
            </motion.div>
          </motion.div>

          {/* Hero visual — a botanical "specimen plate", floating and breathing. */}
          <motion.div
            initial={{ opacity: 0, y: 26, filter: "blur(8px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ duration: 1.1, ease: easeOutExpo, delay: 0.2 }}
            className="relative mx-auto w-full max-w-md"
          >
            <div
              className="absolute inset-0 -z-10 rounded-[3rem] blur-3xl"
              style={{ background: "radial-gradient(circle at 50% 40%, rgb(var(--dawn) / 0.5), transparent 65%)" }}
            />
            <div className={reduce ? "" : "animate-float-soft"}>
              <SpecimenPlate />
            </div>
          </motion.div>
        </div>

        {/* breathing scroll cue */}
        <div className="container-flora hidden pb-6 md:block">
          <span className="flex items-center gap-3 text-[0.72rem] uppercase tracking-[0.2em] text-moss/70">
            <span className="relative block h-10 w-px overflow-hidden bg-line">
              <span className={`absolute inset-x-0 top-0 h-4 bg-moss ${reduce ? "" : "animate-[float-soft_2.4s_ease-in-out_infinite]"}`} />
            </span>
            Wander in
          </span>
        </div>
      </section>

      {/* ── Intention line ────────────────────────────────────────────── */}
      <section className="relative py-16 md:py-24">
        <div className="container-narrow text-center">
          <FlourishDivider />
          <motion.p
            variants={riseBlur}
            initial="hidden"
            whileInView="show"
            viewport={inViewOnce}
            className="mx-auto mt-10 max-w-2xl font-display text-[clamp(1.6rem,3.2vw,2.4rem)] font-normal italic leading-[1.3] tracking-[-0.01em] text-forest"
          >
            Away from the hustle and the noise — a slower, kinder way to
            understand what you grow.
          </motion.p>
          <FlourishDivider className="mt-10" />
        </div>
      </section>

      {/* ── The three intelligences — an editorial journey ────────────── */}
      <section className="relative py-10 md:py-16">
        <div className="container-flora">
          <motion.div
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={inViewOnce}
            className="mb-20 max-w-xl"
          >
            <span className="eyebrow"><span className="h-px w-7 bg-moss/50" /> Three quiet intelligences</span>
            <h2 className="mt-5 font-display text-[clamp(2rem,4vw,3rem)] font-normal leading-[1.08] tracking-[-0.02em] text-forest">
              One garden, tended by three hands
            </h2>
          </motion.div>

          <div className="space-y-24 md:space-y-32">
            {CHAPTERS.map((c, i) => (
              <Chapter key={c.no} chapter={c} flip={i % 2 === 1} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Quiet metrics ─────────────────────────────────────────────── */}
      <section className="relative py-20 md:py-28">
        <div className="container-narrow">
          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={inViewOnce}
            className="flex flex-col items-stretch justify-center gap-px overflow-hidden rounded-[28px] border border-line/70 bg-surface/60 backdrop-blur-md sm:flex-row"
          >
            {QUIET_METRICS.map((m) => (
              <motion.div key={m.l} variants={fadeUp} className="flex-1 px-8 py-10 text-center">
                <div className="font-display text-[2.6rem] font-normal leading-none text-forest">{m.v}</div>
                <div className="mt-3 text-[0.82rem] uppercase tracking-[0.16em] text-moss">{m.l}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Closing invitation ────────────────────────────────────────── */}
      <section className="relative pb-12">
        <div className="container-flora">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={inViewOnce}
            transition={{ duration: 0.9, ease: easeOutExpo }}
            className="grain relative overflow-hidden rounded-[42px] border border-line/60 px-8 py-20 text-center md:px-16 md:py-28"
            style={{ background: "linear-gradient(160deg, rgb(var(--surface) / 0.9), rgb(var(--mist) / 0.7))" }}
          >
            <div className="pointer-events-none absolute -left-16 -top-10 h-72 w-52 text-forest/[0.06]">
              <div className="animate-sway h-full w-full"><Frond /></div>
            </div>
            <div className="pointer-events-none absolute -bottom-16 -right-12 h-72 w-52 -scale-x-100 text-moss/[0.07]">
              <div className="animate-sway h-full w-full [animation-delay:1.5s]"><Frond /></div>
            </div>

            <div className="relative z-10">
              <span className="eyebrow justify-center"><span className="h-px w-7 bg-moss/50" /> An open invitation</span>
              <h2 className="mx-auto mt-6 max-w-2xl font-display text-[clamp(2.2rem,4.5vw,3.4rem)] font-normal leading-[1.07] tracking-[-0.02em] text-forest">
                Step into the conservatory
              </h2>
              <p className="mx-auto mt-6 max-w-lg text-[1.02rem] leading-relaxed text-muted">
                Bring a photo, a few conditions, a question. Leave with a calm,
                grounded understanding of the plant in your care.
              </p>
              <div className="mt-10 flex justify-center">
                <Link href="/diagnose">
                  <Button size="lg">
                    Begin a diagnosis <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  );
}

/* ── Pieces ──────────────────────────────────────────────────────────── */

function SpecimenPlate() {
  return (
    <div className="relative rounded-[2.4rem] border border-line/70 bg-surface/80 p-7 shadow-lift backdrop-blur-xl">
      <div className="flex items-center justify-between text-[0.7rem] uppercase tracking-[0.2em] text-moss">
        <span>Specimen</span>
        <span className="font-mono tracking-tight">no. 01</span>
      </div>
      <div className="relative mt-3 flex h-72 items-center justify-center rounded-[1.6rem] border border-line/60 bg-gradient-to-b from-mist/40 to-surface/40">
        <div className="animate-sway h-60 w-44 text-forest/80">
          <LeafVein strokeWidth={1.3} />
        </div>
        <span className="absolute bottom-4 left-5 font-display text-[1.05rem] italic text-forest">
          Monstera deliciosa
        </span>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-[0.78rem] text-muted">Identified · 97% certain</span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-leaf/10 px-2.5 py-1 text-[0.72rem] font-medium text-forest">
          <span className="h-1.5 w-1.5 rounded-full bg-leaf" /> thriving
        </span>
      </div>
    </div>
  );
}

function Chapter({
  chapter,
  flip,
}: {
  chapter: (typeof CHAPTERS)[number];
  flip: boolean;
}) {
  const Art = chapter.art === "leaf" ? LeafVein : chapter.art === "sprig" ? Sprig : Frond;
  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      whileInView="show"
      viewport={inViewOnce}
      className={`grid items-center gap-10 md:grid-cols-2 md:gap-16 ${flip ? "md:[direction:rtl]" : ""}`}
    >
      <motion.div variants={fadeUp} className="md:[direction:ltr]">
        <div className="flex items-baseline gap-4">
          <span className="font-display text-[2.4rem] italic leading-none text-leaf/40">{chapter.no}</span>
          <span className="eyebrow">{chapter.kicker}</span>
        </div>
        <h3 className="mt-4 font-display text-[clamp(1.7rem,3vw,2.4rem)] font-normal leading-[1.1] tracking-[-0.015em] text-forest">
          {chapter.title}
        </h3>
        <p className="mt-5 max-w-md text-[1rem] leading-relaxed text-muted">{chapter.body}</p>
        <Link
          href={chapter.href}
          className="group mt-7 inline-flex items-center gap-1.5 text-[0.9rem] font-medium text-forest"
        >
          {chapter.cta}
          <ArrowUpRight className="h-4 w-4 transition-transform duration-300 ease-organic group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </Link>
      </motion.div>

      <motion.div variants={riseBlur} className="md:[direction:ltr]">
        <div className="relative mx-auto flex aspect-[5/4] max-w-md items-center justify-center rounded-[2.2rem] border border-line/60 bg-surface/50 backdrop-blur-md">
          <div
            className="absolute inset-0 -z-10 rounded-[2.2rem] blur-2xl"
            style={{ background: "radial-gradient(circle at 50% 50%, rgb(var(--sage) / 0.28), transparent 70%)" }}
          />
          <div className="animate-sway h-3/4 w-3/4 text-forest/70">
            <Art strokeWidth={1.3} />
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function FlourishDivider({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center justify-center gap-3 text-moss/50 ${className}`}>
      <span className="h-px w-12 bg-current" />
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true" className="text-leaf">
        <path d="M12 3C8 7 7 11 12 21C17 11 16 7 12 3Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" className="fill-leaf/10" />
        <path d="M12 7V18" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" />
      </svg>
      <span className="h-px w-12 bg-current" />
    </div>
  );
}
