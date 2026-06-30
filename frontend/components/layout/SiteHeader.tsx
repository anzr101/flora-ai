"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Wordmark } from "@/components/brand/Logo";
import { Button } from "@/components/ui/Button";
import { getPlatformHealth } from "@/lib/api";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/diagnose", label: "Diagnose" },
  { href: "/vision", label: "Identify" },
  { href: "/health", label: "Wellbeing" },
  { href: "/assistant", label: "Companion" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    getPlatformHealth()
      .then(() => active && setOnline(true))
      .catch(() => active && setOnline(false));
    return () => {
      active = false;
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-line/50 bg-ivory/55 backdrop-blur-xl">
      <div className="container-flora flex h-[4.5rem] items-center justify-between">
        <Link href="/" className="focus-ring rounded-full" aria-label="FloraAI home">
          <Wordmark />
        </Link>

        <nav className="hidden items-center rounded-full border border-line/60 bg-surface/50 px-1.5 py-1 backdrop-blur-md md:flex">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "focus-ring rounded-full px-4 py-1.5 text-[0.86rem] transition-colors duration-300",
                  active
                    ? "bg-forest/[0.06] text-forest"
                    : "text-muted hover:text-forest",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-4">
          <span
            className="hidden items-center gap-2 text-[0.74rem] text-moss sm:inline-flex"
            title={online === null ? "Listening…" : online ? "The garden is awake" : "Resting"}
          >
            <span className="relative flex h-2 w-2">
              {online && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-leaf/60" />
              )}
              <span
                className={cn(
                  "relative inline-flex h-2 w-2 rounded-full",
                  online === null ? "bg-muted/40" : online ? "bg-leaf" : "bg-clay",
                )}
              />
            </span>
            {online === null ? "Listening" : online ? "Awake" : "Resting"}
          </span>
          <Link href="/diagnose">
            <Button size="sm">Begin</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
