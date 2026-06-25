import Link from "next/link";
import { Wordmark } from "@/components/brand/Logo";

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-line/70">
      <div className="container-flora grid gap-10 py-14 md:grid-cols-[1.4fr_1fr_1fr]">
        <div className="max-w-xs">
          <Wordmark />
          <p className="mt-4 text-[0.88rem] leading-relaxed text-muted">
            Organic intelligence. A botanical AI ecosystem combining classical
            machine learning, computer vision, and grounded reasoning.
          </p>
        </div>

        <div>
          <h4 className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-ink/70">
            Modules
          </h4>
          <ul className="mt-4 space-y-2.5 text-[0.88rem] text-muted">
            <li><Link className="hover:text-forest" href="/health">Health prediction</Link></li>
            <li><Link className="hover:text-forest" href="/vision">Visual identification</Link></li>
            <li><Link className="hover:text-forest" href="/assistant">Botanical assistant</Link></li>
            <li><Link className="hover:text-forest" href="/diagnose">Unified diagnosis</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-ink/70">
            Platform
          </h4>
          <ul className="mt-4 space-y-2.5 text-[0.88rem] text-muted">
            <li><span>Classical ML · scikit-learn</span></li>
            <li><span>Deep learning · PyTorch</span></li>
            <li><span>Agentic RAG · Claude</span></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-line/70">
        <div className="container-flora flex flex-col items-center justify-between gap-3 py-5 text-[0.78rem] text-muted sm:flex-row">
          <span>© 2026 FloraAI. Built as a production-grade AI platform.</span>
          <span className="font-mono text-[0.74rem]">v1.0.0 · ml · dl · agent · gateway</span>
        </div>
      </div>
    </footer>
  );
}
