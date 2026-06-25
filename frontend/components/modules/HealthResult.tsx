"use client";

import { motion } from "framer-motion";
import { Activity, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Meter } from "@/components/ui/Meter";
import type { HealthPrediction, RiskLabel } from "@/lib/types";
import { cn, humanize, pct } from "@/lib/utils";

const RISK_META: Record<RiskLabel, { tone: "success" | "warning" | "danger"; label: string }> = {
  healthy: { tone: "success", label: "Healthy" },
  at_risk: { tone: "warning", label: "At risk" },
  diseased: { tone: "danger", label: "Diseased" },
};

export function HealthResult({ data }: { data: HealthPrediction }) {
  const meta = RISK_META[data.risk_label];
  const ordered: RiskLabel[] = ["healthy", "at_risk", "diseased"];

  return (
    <div className="space-y-7">
      {/* Headline verdict */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="eyebrow">
            <Activity className="h-3.5 w-3.5" /> Predicted status
          </span>
          <div className="mt-2 flex items-center gap-3">
            <span className="font-display text-[2.4rem] leading-none text-forest">
              {meta.label}
            </span>
            <Badge tone={meta.tone}>risk {pct(data.risk_score, 0)}</Badge>
          </div>
        </div>
        <span className="font-mono text-[0.72rem] text-muted">{data.model_version}</span>
      </div>

      {/* Class probabilities */}
      <div>
        <p className="mb-3 text-[0.8rem] font-medium uppercase tracking-[0.12em] text-muted">
          Class probabilities
        </p>
        <div className="space-y-3.5">
          {ordered.map((cls) => (
            <Meter
              key={cls}
              label={RISK_META[cls].label}
              value={data.class_probabilities[cls] ?? 0}
              tone={cls === data.risk_label ? RISK_META[cls].tone : "muted"}
            />
          ))}
        </div>
      </div>

      {/* SHAP local drivers */}
      {data.top_drivers.length > 0 && (
        <div>
          <p className="mb-1 text-[0.8rem] font-medium uppercase tracking-[0.12em] text-muted">
            Why this prediction
          </p>
          <p className="mb-3 text-[0.82rem] text-muted">
            Top factors for <em>this</em> plant (local SHAP). Green factors pushed
            toward a healthier outcome; amber pushed toward risk.
          </p>
          <ul className="space-y-2.5">
            {data.top_drivers.map((d, i) => {
              const [name, val] = Object.entries(d)[0];
              const positive = val > 0; // pushes toward predicted (worse) class
              const magnitude = Math.min(Math.abs(val) / 2.5, 1);
              return (
                <li key={i} className="flex items-center gap-3">
                  <span className="w-44 shrink-0 truncate text-[0.85rem] text-ink/85">
                    {humanize(name)}
                  </span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-forest/[0.06]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${magnitude * 100}%` }}
                      transition={{ duration: 0.8, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                      className={cn("h-full rounded-full", positive ? "bg-warning" : "bg-success")}
                    />
                  </div>
                  <span
                    className={cn(
                      "flex w-14 shrink-0 items-center justify-end gap-0.5 font-mono text-[0.74rem] tabular-nums",
                      positive ? "text-[#8a6d1f]" : "text-success",
                    )}
                  >
                    {positive ? (
                      <ArrowUpRight className="h-3 w-3" />
                    ) : (
                      <ArrowDownRight className="h-3 w-3" />
                    )}
                    {val.toFixed(2)}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
