import Link from "next/link";
import {
  ArrowRight,
  Brain,
  Leaf,
  LineChart,
  MessageSquareText,
  ScanEye,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { Aurora } from "@/components/ui/Aurora";
import { LogoMark } from "@/components/brand/Logo";

const STATS = [
  { v: "0.72", l: "macro-F1", s: "health model" },
  { v: "1.00", l: "hit@4", s: "RAG retrieval" },
  { v: "4", l: "microservices", s: "independently deployed" },
  { v: "100%", l: "cited", s: "grounded answers" },
];

const MODULES = [
  {
    href: "/health",
    icon: LineChart,
    name: "Health Prediction",
    tag: "Classical ML",
    desc: "Predicts a plant's health-risk from environmental and care conditions, with calibrated probabilities and per-prediction SHAP explanations.",
  },
  {
    href: "/vision",
    icon: ScanEye,
    name: "Visual Identification",
    tag: "Deep Learning",
    desc: "Transfer-learned computer vision classifies leaf images, with confidence scoring and honest abstention on out-of-distribution photos.",
  },
  {
    href: "/assistant",
    icon: MessageSquareText,
    name: "Botanical Assistant",
    tag: "Agentic RAG",
    desc: "A reasoning assistant grounded in a curated knowledge base — every answer is cited, and it can call the other models as tools.",
  },
];

const STEPS = [
  { n: "01", t: "Observe", d: "Upload a leaf photo and describe the plant's conditions." },
  { n: "02", t: "Analyse", d: "Vision identifies the species; the ML model scores health risk." },
  { n: "03", t: "Reason", d: "The assistant retrieves knowledge and explains what's happening." },
  { n: "04", t: "Act", d: "You receive one grounded, actionable care recommendation." },
];

export default function HomePage() {
  return (
    <>
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="grain relative overflow-hidden">
        <Aurora />
        <div className="container-flora relative z-10 grid items-center gap-12 py-20 md:py-28 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="animate-fade-up">
            <span className="eyebrow">
              <Sparkles className="h-3.5 w-3.5 text-leaf" />
              Botanical intelligence, 2026
            </span>
            <h1 className="mt-5 font-display text-display-lg text-forest">
              Organic intelligence for{" "}
              <span className="text-gradient italic">living things.</span>
            </h1>
            <p className="mt-6 max-w-xl text-[1.12rem] leading-relaxed text-muted">
              FloraAI is an AI ecosystem for understanding plants — combining
              classical machine learning, computer vision, and grounded reasoning
              into a single, calm interface. Three paradigms, each doing what it
              does best.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link href="/diagnose">
                <Button size="lg">
                  Run a diagnosis <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/assistant">
                <Button size="lg" variant="outline">
                  Ask the assistant
                </Button>
              </Link>
            </div>
            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-[0.82rem] text-muted">
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-leaf" /> No data leakage
              </span>
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-leaf" /> Explainable predictions
              </span>
              <span className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-leaf" /> Cited reasoning
              </span>
            </div>
          </div>

          {/* Visual: layered botanical glass panel */}
          <div className="relative animate-fade-up [animation-delay:120ms]">
            <div className="animate-float-card relative mx-auto aspect-square w-full max-w-md">
              <div className="absolute inset-0 rounded-[2rem] bg-gradient-to-br from-sage/30 via-leaf/10 to-transparent blur-2xl" />
              <Card className="relative h-full overflow-hidden rounded-[2rem] border-leaf/15 bg-surface/80 p-8 shadow-lg backdrop-blur-xl">
                <div className="flex items-center justify-between">
                  <LogoMark className="h-9 w-9" />
                  <span className="font-mono text-[0.7rem] text-muted">live · gateway</span>
                </div>
                <div className="mt-8 space-y-4">
                  <PreviewRow icon={ScanEye} label="Species" value="Monstera deliciosa" meter={0.91} />
                  <PreviewRow icon={LineChart} label="Health" value="At risk" meter={0.62} tone="warning" />
                  <PreviewRow icon={Brain} label="Drivers" value="soil moisture · pH" meter={0.74} />
                </div>
                <div className="mt-8 rounded-lg border border-line bg-ivory/60 p-4">
                  <p className="flex items-center gap-1.5 text-[0.7rem] font-medium uppercase tracking-[0.12em] text-muted">
                    <MessageSquareText className="h-3.5 w-3.5" /> Assistant
                  </p>
                  <p className="mt-2 text-[0.86rem] leading-relaxed text-ink/80">
                    Soil is staying too wet — let the top few centimetres dry and
                    improve drainage to prevent root rot.
                  </p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* ── Credibility strip ─────────────────────────────────────────── */}
      <section className="container-flora">
        <Reveal>
          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line/60 md:grid-cols-4">
            {STATS.map((stat) => (
              <div key={stat.l} className="bg-surface px-6 py-7 text-center sm:py-8">
                <div className="font-display text-[2.2rem] leading-none text-forest">
                  {stat.v}
                </div>
                <div className="mt-2 text-[0.82rem] font-medium text-ink">{stat.l}</div>
                <div className="mt-0.5 text-[0.72rem] text-muted">{stat.s}</div>
              </div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* ── Modules ───────────────────────────────────────────────────── */}
      <section className="container-flora py-12 md:py-20">
        <Reveal>
          <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
            <div className="max-w-prose">
              <span className="eyebrow">
                <Leaf className="h-3.5 w-3.5 text-leaf" /> The ecosystem
              </span>
              <h2 className="mt-4 font-display text-display text-forest">
                Three intelligences, one platform
              </h2>
            </div>
            <p className="max-w-sm text-[0.95rem] leading-relaxed text-muted">
              Rather than forcing one technique everywhere, each module solves the
              problem it is genuinely best suited to.
            </p>
          </div>
        </Reveal>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {MODULES.map((m, i) => (
            <Reveal key={m.href} delay={i * 0.08}>
              <Link href={m.href} className="group block h-full">
                <Card hover className="relative flex h-full flex-col overflow-hidden p-7">
                  {/* Top accent that grows on hover. */}
                  <span className="absolute inset-x-0 top-0 h-0.5 origin-left scale-x-0 bg-gradient-to-r from-leaf to-success transition-transform duration-500 ease-organic group-hover:scale-x-100" />
                  <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-leaf/20 to-sage/20 text-forest ring-1 ring-leaf/10 transition-transform duration-300 ease-organic group-hover:scale-105">
                    <m.icon className="h-5 w-5" />
                  </span>
                  <p className="mt-5 text-[0.72rem] font-medium uppercase tracking-[0.14em] text-leaf">
                    {m.tag}
                  </p>
                  <h3 className="mt-1.5 text-title font-semibold text-ink">{m.name}</h3>
                  <p className="mt-3 flex-1 text-[0.92rem] leading-relaxed text-muted">
                    {m.desc}
                  </p>
                  <span className="mt-6 inline-flex items-center gap-1.5 text-[0.86rem] font-medium text-forest">
                    Explore
                    <ArrowRight className="h-4 w-4 transition-transform duration-300 ease-organic group-hover:translate-x-1" />
                  </span>
                </Card>
              </Link>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section className="container-flora py-12 md:py-20">
        <Reveal>
          <div className="grain relative overflow-hidden rounded-2xl border border-line bg-surface p-8 shadow-sm md:p-12">
            <Aurora className="opacity-70" />
            <div className="relative z-10">
            <span className="eyebrow">
              <Sparkles className="h-3.5 w-3.5 text-leaf" /> The unified flow
            </span>
            <h2 className="mt-4 max-w-xl font-display text-display text-forest">
              From a single photo to a clear recommendation
            </h2>
            <div className="mt-10 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {STEPS.map((s, i) => (
                <Reveal key={s.n} delay={i * 0.08}>
                  <div className="relative">
                    <span className="font-display text-[2rem] text-leaf/40">{s.n}</span>
                    <h3 className="mt-1 text-[1.05rem] font-semibold text-ink">{s.t}</h3>
                    <p className="mt-2 text-[0.88rem] leading-relaxed text-muted">{s.d}</p>
                  </div>
                </Reveal>
              ))}
            </div>
            <div className="mt-10">
              <Link href="/diagnose">
                <Button size="lg">
                  Try the unified diagnosis <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  );
}

function PreviewRow({
  icon: Icon,
  label,
  value,
  meter,
  tone = "leaf",
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  meter: number;
  tone?: "leaf" | "warning";
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-forest/[0.05] text-forest">
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between">
          <span className="text-[0.7rem] uppercase tracking-wide text-muted">{label}</span>
          <span className="truncate pl-2 text-[0.82rem] font-medium text-ink">{value}</span>
        </div>
        <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-forest/[0.07]">
          <div
            className={tone === "warning" ? "h-full rounded-full bg-warning" : "h-full rounded-full bg-leaf"}
            style={{ width: `${meter * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
