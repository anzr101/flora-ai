"use client";

import { AlertTriangle, ScanEye } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Meter } from "@/components/ui/Meter";
import type { SpeciesPrediction } from "@/lib/types";
import { humanize, pct } from "@/lib/utils";

export function SpeciesResult({ data }: { data: SpeciesPrediction }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="eyebrow">
            <ScanEye className="h-3.5 w-3.5" /> Identified
          </span>
          <div className="mt-2 flex items-center gap-3">
            <span className="font-display text-[2rem] leading-none text-forest">
              {humanize(data.label)}
            </span>
            <Badge tone={data.low_confidence ? "warning" : "leaf"}>
              {pct(data.confidence, 0)} confidence
            </Badge>
          </div>
        </div>
        <span className="font-mono text-[0.72rem] text-muted">{data.model_version}</span>
      </div>

      {data.low_confidence && (
        <div className="flex gap-3 rounded-lg border border-warning/30 bg-warning/[0.08] p-3.5">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[#8a6d1f]" />
          <p className="text-[0.84rem] leading-relaxed text-ink/80">
            <span className="font-medium">Low confidence.</span> The image looks
            out-of-distribution for the model. The system abstains rather than
            asserting a label — treat the species as uncertain.
          </p>
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
