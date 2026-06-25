import { FileText } from "lucide-react";
import type { Citation } from "@/lib/types";
import { humanize } from "@/lib/utils";

export function Citations({ items }: { items: Citation[] }) {
  if (!items.length) return null;
  // De-duplicate by source for a clean reference list.
  const sources = Array.from(new Set(items.map((c) => c.source)));

  return (
    <div className="rounded-lg border border-line bg-leaf/[0.025] p-4">
      <p className="mb-3 flex items-center gap-1.5 text-[0.74rem] font-medium uppercase tracking-[0.12em] text-muted">
        <FileText className="h-3.5 w-3.5" /> Grounded in {sources.length} source
        {sources.length > 1 ? "s" : ""}
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s) => (
          <span
            key={s}
            className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 text-[0.76rem] text-ink/75"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-leaf" />
            {humanize(s.replace(/\.md$/, ""))}
          </span>
        ))}
      </div>
    </div>
  );
}
