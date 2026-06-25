"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { ArrowUp, MessageSquareText, Sparkles } from "lucide-react";
import { Textarea } from "@/components/ui/Field";
import { Button } from "@/components/ui/Button";
import { LoadingDots } from "@/components/ui/Spinner";
import { Markdown } from "@/components/modules/Markdown";
import { Citations } from "@/components/modules/Citations";
import { LogoMark } from "@/components/brand/Logo";
import { chat } from "@/lib/api";
import type { Citation, ChatMessage } from "@/lib/types";

interface Turn extends ChatMessage {
  citations?: Citation[];
  tools?: string[];
}

const SUGGESTIONS = [
  "My monstera has yellow lower leaves and wet soil. What's wrong?",
  "How often should I water a succulent?",
  "Is a peace lily toxic to cats?",
  "How do I treat spider mites?",
];

export default function AssistantPage() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, loading]);

  async function send(message: string) {
    const text = message.trim();
    if (!text || loading) return;
    const history: ChatMessage[] = turns.map(({ role, content }) => ({ role, content }));
    setTurns((t) => [...t, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await chat(text, history);
      setTurns((t) => [
        ...t,
        { role: "assistant", content: res.answer, citations: res.citations, tools: res.tools_used },
      ]);
    } catch (err) {
      setTurns((t) => [
        ...t,
        {
          role: "assistant",
          content: `I couldn't reach the assistant service. ${
            err instanceof Error ? err.message : ""
          }`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const empty = turns.length === 0;

  return (
    <div className="container-flora flex min-h-[calc(100vh-4rem)] max-w-4xl flex-col py-10">
      {/* Header */}
      <div className="mb-6">
        <span className="eyebrow">
          <MessageSquareText className="h-3.5 w-3.5 text-leaf" /> Module 03 · Agentic RAG
        </span>
        <h1 className="mt-3 font-display text-[2.2rem] text-forest">Botanical assistant</h1>
      </div>

      {/* Conversation */}
      <div
        ref={scrollRef}
        className="flex-1 space-y-6 overflow-y-auto rounded-2xl border border-line bg-surface/60 p-6 md:p-8"
      >
        {empty ? (
          <div className="flex h-full min-h-[18rem] flex-col items-center justify-center text-center">
            <LogoMark className="h-10 w-10" />
            <p className="mt-4 text-[1.05rem] font-medium text-ink/85">
              Ask about plant care, grounded in real knowledge
            </p>
            <p className="mt-1.5 max-w-md text-[0.88rem] text-muted">
              Every answer is retrieved from a curated botanical knowledge base and
              cited. The assistant can also reason over the ML and vision models.
            </p>
            <div className="mt-7 grid w-full max-w-xl gap-2.5 sm:grid-cols-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="focus-ring group rounded-lg border border-line bg-surface p-3.5 text-left text-[0.86rem] text-ink/80 transition-all hover:-translate-y-0.5 hover:border-leaf/40 hover:shadow-sm"
                >
                  <Sparkles className="mb-1.5 h-3.5 w-3.5 text-leaf" />
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          turns.map((turn, i) => <ChatBubble key={i} turn={turn} />)
        )}

        {loading && (
          <div className="flex items-start gap-3">
            <Avatar role="assistant" />
            <div className="mt-2">
              <LoadingDots label="Searching the knowledge base…" />
            </div>
          </div>
        )}
      </div>

      {/* Composer */}
      <div className="mt-4">
        <div className="relative rounded-2xl border border-line bg-surface shadow-sm transition-shadow focus-within:shadow-md">
          <Textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(input);
              }
            }}
            placeholder="Ask about watering, light, disease, species…"
            className="max-h-40 min-h-[3.5rem] border-0 bg-transparent py-4 pr-14 hover:border-0 focus-visible:ring-0"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="focus-ring absolute bottom-2.5 right-2.5 inline-flex h-9 w-9 items-center justify-center rounded-lg bg-forest text-ivory transition-all hover:bg-forest/90 disabled:opacity-40"
            aria-label="Send message"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-2 px-1 text-center text-[0.72rem] text-muted">
          Grounded answers with citations · powered by Claude + local retrieval
        </p>
      </div>
    </div>
  );
}

function Avatar({ role }: { role: "user" | "assistant" }) {
  if (role === "assistant") {
    return (
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-leaf/20 bg-leaf/10">
        <LogoMark className="h-5 w-5" />
      </span>
    );
  }
  return (
    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-forest text-[0.78rem] font-medium text-ivory">
      You
    </span>
  );
}

function ChatBubble({ turn }: { turn: Turn }) {
  const isUser = turn.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="flex items-start gap-3"
    >
      <Avatar role={turn.role} />
      <div className="min-w-0 flex-1">
        {isUser ? (
          <p className="inline-block rounded-2xl rounded-tl-sm bg-forest/[0.05] px-4 py-2.5 text-[0.92rem] leading-relaxed text-ink">
            {turn.content}
          </p>
        ) : (
          <div className="space-y-3">
            <div className="rounded-2xl rounded-tl-sm border border-line bg-surface px-4 py-3">
              <Markdown content={turn.content} />
            </div>
            {turn.citations && turn.citations.length > 0 && (
              <Citations items={turn.citations} />
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
