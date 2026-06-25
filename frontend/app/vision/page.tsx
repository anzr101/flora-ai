"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Info, ScanEye } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { ImageDropzone } from "@/components/modules/ImageDropzone";
import { SpeciesResult } from "@/components/modules/SpeciesResult";
import { identifySpecies } from "@/lib/api";
import type { SpeciesPrediction } from "@/lib/types";

// Houseplants the zero-shot identifier recognises (open-vocabulary — extendable).
const SUPPORTED_SPECIES = [
  "Monstera deliciosa", "Snake plant", "Golden pothos", "Peace lily",
  "Fiddle-leaf fig", "Rubber plant", "ZZ plant", "Spider plant",
  "Aloe vera", "Jade plant", "Boston fern", "Calathea",
  "Philodendron", "English ivy", "Chinese evergreen", "Orchid",
];

export default function VisionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<SpeciesPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onIdentify() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await identifySpecies(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Identification failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-flora py-14 md:py-20">
      <PageHeader
        eyebrow="Module 02 · Deep Learning"
        title="Visual identification"
        description="Upload a plant photo and the vision model identifies the species. It reports calibrated confidence and abstains when the image is unclear rather than guessing."
      />

      <div className="mt-12 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <Card className="p-7">
          <h2 className="mb-5 flex items-center gap-2 text-[1rem] font-semibold text-ink">
            <ScanEye className="h-4 w-4 text-leaf" /> Image
          </h2>
          <ImageDropzone file={file} onChange={(f) => { setFile(f); setResult(null); }} />
          <Button
            size="lg"
            className="mt-6 w-full"
            onClick={onIdentify}
            disabled={!file || loading}
          >
            {loading ? <Spinner className="h-4 w-4 text-ivory" /> : "Identify species"}
          </Button>
          {error && <p className="mt-3 text-[0.84rem] text-danger">{error}</p>}

          <div className="mt-5 rounded-lg border border-line bg-leaf/[0.03] p-4">
            <p className="flex items-center gap-1.5 text-[0.74rem] font-medium uppercase tracking-[0.12em] text-muted">
              <Info className="h-3.5 w-3.5" /> How identification works
            </p>
            <p className="mt-2 text-[0.82rem] leading-relaxed text-ink/75">
              This uses <strong>CLIP zero-shot</strong> recognition — your photo is
              matched against text descriptions of each plant, so it works on
              <strong> real photos with no training data</strong>. It's
              open-vocabulary: new species are added with a sentence, not a
              retraining run. Currently recognises {SUPPORTED_SPECIES.length} common
              houseplants.
            </p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {SUPPORTED_SPECIES.slice(0, 8).map((c) => (
                <span
                  key={c}
                  className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 text-[0.74rem] text-ink/70"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-leaf" />
                  {c}
                </span>
              ))}
              <span className="inline-flex items-center rounded-full border border-line bg-surface px-2.5 py-1 text-[0.74rem] text-muted">
                +{SUPPORTED_SPECIES.length - 8} more
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-7">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              >
                <SpeciesResult data={result} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                exit={{ opacity: 0 }}
                className="flex h-full min-h-[20rem] flex-col items-center justify-center text-center"
              >
                <span className="flex h-14 w-14 items-center justify-center rounded-full bg-leaf/10 text-leaf">
                  <ScanEye className="h-6 w-6" />
                </span>
                <p className="mt-4 text-[0.95rem] font-medium text-ink/80">Awaiting an image</p>
                <p className="mt-1.5 max-w-xs text-[0.86rem] text-muted">
                  Upload a leaf photo to see the predicted species and the model's
                  confidence across its top candidates.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </div>
    </div>
  );
}
