import Link from "next/link";
import { Wordmark } from "@/components/brand/Logo";
import { LeafVein } from "@/components/botanical/Botanicals";

export function SiteFooter() {
  return (
    <footer className="relative mt-32 overflow-hidden border-t border-line/60">
      {/* A single quiet leaf, breathing, in the corner. */}
      <div className="animate-sway pointer-events-none absolute -right-6 top-6 h-40 w-28 text-forest/[0.05]">
        <LeafVein />
      </div>

      <div className="container-flora grid gap-12 py-16 md:grid-cols-[1.5fr_1fr_1fr]">
        <div className="max-w-xs">
          <Wordmark />
          <p className="mt-5 text-[0.92rem] leading-relaxed text-muted">
            A quiet place to understand the living things in your care — where
            machine learning, vision, and patient reasoning tend the garden together.
          </p>
        </div>

        <div>
          <h4 className="text-[0.74rem] font-medium uppercase tracking-[0.18em] text-moss">
            The garden
          </h4>
          <ul className="mt-5 space-y-3 text-[0.9rem] text-muted">
            <li><Link className="transition-colors hover:text-forest" href="/diagnose">Diagnose a plant</Link></li>
            <li><Link className="transition-colors hover:text-forest" href="/vision">Identify a species</Link></li>
            <li><Link className="transition-colors hover:text-forest" href="/health">Read its wellbeing</Link></li>
            <li><Link className="transition-colors hover:text-forest" href="/assistant">Ask the companion</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-[0.74rem] font-medium uppercase tracking-[0.18em] text-moss">
            Tended by
          </h4>
          <ul className="mt-5 space-y-3 text-[0.9rem] text-muted">
            <li>Classical ML · scikit-learn</li>
            <li>Vision · BioCLIP</li>
            <li>Reasoning · Claude + retrieval</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-line/60">
        <div className="container-flora flex flex-col items-center justify-between gap-3 py-6 text-[0.78rem] text-muted sm:flex-row">
          <span>© 2026 FloraAI — grown with care.</span>
          <span className="font-mono text-[0.72rem] tracking-tight">ml · vision · companion · gateway</span>
        </div>
      </div>
    </footer>
  );
}
