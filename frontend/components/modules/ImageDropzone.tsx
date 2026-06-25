"use client";

import { useCallback, useRef, useState } from "react";
import { ImagePlus, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function ImageDropzone({
  file,
  onChange,
  className,
}: {
  file: File | null;
  onChange: (file: File | null) => void;
  className?: string;
}) {
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handle = useCallback(
    (f: File | null) => {
      if (preview) URL.revokeObjectURL(preview);
      if (f && f.type.startsWith("image/")) {
        setPreview(URL.createObjectURL(f));
        onChange(f);
      } else {
        setPreview(null);
        onChange(null);
      }
    },
    [onChange, preview],
  );

  return (
    <div className={className}>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => handle(e.target.files?.[0] ?? null)}
      />
      {preview ? (
        <div className="group relative overflow-hidden rounded-lg border border-line">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={preview} alt="Selected plant" className="h-64 w-full object-cover" />
          <button
            type="button"
            onClick={() => handle(null)}
            className="focus-ring absolute right-3 top-3 inline-flex h-8 w-8 items-center justify-center rounded-full bg-ink/55 text-white backdrop-blur transition hover:bg-ink/75"
            aria-label="Remove image"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handle(e.dataTransfer.files?.[0] ?? null);
          }}
          className={cn(
            "focus-ring flex h-64 w-full flex-col items-center justify-center gap-3 rounded-lg border border-dashed bg-leaf/[0.02] text-center transition-colors",
            dragging ? "border-leaf bg-leaf/[0.06]" : "border-line hover:border-leaf/50",
          )}
        >
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-leaf/10 text-leaf">
            <ImagePlus className="h-5 w-5" />
          </span>
          <span className="text-[0.9rem] font-medium text-ink/85">
            Drop a leaf photo, or click to browse
          </span>
          <span className="text-[0.78rem] text-muted">JPG or PNG · analysed locally by the vision model</span>
        </button>
      )}
    </div>
  );
}
