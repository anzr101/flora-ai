"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Check, ScanEye } from "lucide-react";
import { Meter } from "@/components/ui/Meter";
import type { SpeciesPrediction } from "@/lib/types";
import { humanize, pct } from "@/lib/utils";

/** Animated circular confidence indicator. */
function ConfidenceRing({ value, warn }: { value: number; warn: boolean }) {
  const r = 26;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative h-[68px] w-[68px] shrink-0">
      <svg viewBox="0 0 68 68" className="h-full w-full -rotate-90">
        <circle cx="34" cy="34" r={r} fill="none" strokeWidth="6" className="stroke-forest/10" />
        <motion.circle
          cx="34"
          cy="34"
          r={r}
          fill="none"
          strokeWidth="6"
          strokeLinecap="round"
          className={warn ? "stroke-warning" : "stroke-leaf"}
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c * (1 - value) }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-mono text-[0.82rem] font-medium tabular-nums text-ink">
        {pct(value, 0)}
      </span>
    </div>
  );
}

export function SpeciesResult({ data }: { data: SpeciesPrediction }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <ConfidenceRing value={data.confidence} warn={data.low_confidence} />
          <div>
            <span className="eyebrow">
              <ScanEye className="h-3.5 w-3.5" /> Identified
            </span>
            <div className="mt-1 font-display text-[1.9rem] leading-tight text-forest">
              {humanize(data.label)}
            </div>
          </div>
        </div>
        <span className="hidden font-mono text-[0.7rem] text-muted sm:block">
          {data.model_version}
        </span>
      </div>

      {data.low_confidence ? (
        <div className="flex gap-3 rounded-lg border border-warning/30 bg-warning/[0.08] p-3.5">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[#8a6d1f]" />
          <p className="text-[0.84rem] leading-relaxed text-ink/80">
            <span className="font-medium">Low confidence.</span> The photo is
            ambiguous or outside the recognised set, so the system abstains rather
            than asserting a label — treat this as a guess.
          </p>
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-lg border border-success/20 bg-success/[0.06] px-3.5 py-2.5 text-[0.84rem] text-ink/80">
          <Check className="h-4 w-4 shrink-0 text-success" />
          Confident match — verified against the plant's distinctive features.
        </div>
      )}

      <div>
        <p className="mb-3 text-[0.8rem] font-medium uppercase tracking-[0.12em] text-muted">
          Top candidates
        </p>
        <div className="space-y-3.5">
          {data.top_k.map((item, i) => {
            const [name, conf] = Object.entries(item)[0];
            return (
              <Meter
                key={i}
                label={humanize(name)}
                value={conf}
                tone={i === 0 ? "leaf" : "muted"}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
