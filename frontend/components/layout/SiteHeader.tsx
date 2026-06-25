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
  { href: "/health", label: "Health" },
  { href: "/vision", label: "Vision" },
  { href: "/assistant", label: "Assistant" },
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
    <header className="sticky top-0 z-50 border-b border-line/70 bg-ivory/80 backdrop-blur-xl">
      <div className="container-flora flex h-16 items-center justify-between">
        <Link href="/" className="focus-ring rounded-sm" aria-label="FloraAI home">
          <Wordmark />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "focus-ring relative rounded-sm px-3.5 py-2 text-[0.88rem] transition-colors",
                  active ? "text-forest" : "text-muted hover:text-forest",
                )}
              >
                {item.label}
                {active && (
                  <span className="absolute inset-x-3.5 -bottom-px h-px bg-leaf" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <span
            className="hidden items-center gap-2 text-[0.76rem] text-muted sm:inline-flex"
            title={online === null ? "Checking…" : online ? "Platform online" : "Platform offline"}
          >
            <span
              className={cn(
                "h-1.5 w-1.5 rounded-full",
                online === null
                  ? "bg-muted/40"
                  : online
                    ? "bg-success animate-pulse"
                    : "bg-danger",
              )}
            />
            {online === null ? "Connecting" : online ? "Systems online" : "Offline"}
          </span>
          <Link href="/diagnose">
            <Button size="sm">Try the demo</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
