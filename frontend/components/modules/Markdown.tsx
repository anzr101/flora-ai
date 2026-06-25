import { Fragment } from "react";

/**
 * Minimal, dependency-free Markdown renderer tuned to the agent's output
 * (headings, bold, ordered/unordered lists, paragraphs). Deliberately small —
 * it covers exactly what the assistant produces, styled to the design system.
 */

function inline(text: string, keyBase: string) {
  // Split on **bold** and `code`, preserving delimiters.
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**")) {
      return (
        <strong key={`${keyBase}-${i}`} className="font-semibold text-ink">
          {p.slice(2, -2)}
        </strong>
      );
    }
    if (p.startsWith("`") && p.endsWith("`")) {
      return (
        <code
          key={`${keyBase}-${i}`}
          className="rounded bg-forest/[0.06] px-1.5 py-0.5 font-mono text-[0.82em] text-forest"
        >
          {p.slice(1, -1)}
        </code>
      );
    }
    return <Fragment key={`${keyBase}-${i}`}>{p}</Fragment>;
  });
}

export function Markdown({ content }: { content: string }) {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: React.ReactNode[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;
  let key = 0;

  const flush = () => {
    if (!list) return;
    const Tag = list.ordered ? "ol" : "ul";
    blocks.push(
      <Tag
        key={key++}
        className={`my-2 space-y-1.5 pl-1 text-[0.92rem] leading-relaxed text-ink/85 ${
          list.ordered ? "list-decimal" : "list-none"
        } ${list.ordered ? "ml-5" : ""}`}
      >
        {list.items.map((it, i) => (
          <li key={i} className="flex gap-2">
            {!list!.ordered && <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-leaf" />}
            <span>{inline(it, `li-${key}-${i}`)}</span>
          </li>
        ))}
      </Tag>,
    );
    list = null;
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) {
      flush();
      continue;
    }
    const heading = line.match(/^(#{2,4})\s+(.*)$/);
    const bullet = line.match(/^[-*]\s+(.*)$/);
    const ordered = line.match(/^\d+\.\s+(.*)$/);

    if (heading) {
      flush();
      blocks.push(
        <h4 key={key++} className="mt-4 text-[0.95rem] font-semibold tracking-tight text-forest">
          {inline(heading[2], `h-${key}`)}
        </h4>,
      );
    } else if (bullet) {
      if (!list || list.ordered) {
        flush();
        list = { ordered: false, items: [] };
      }
      list.items.push(bullet[1]);
    } else if (ordered) {
      if (!list || !list.ordered) {
        flush();
        list = { ordered: true, items: [] };
      }
      list.items.push(ordered[1]);
    } else {
      flush();
      blocks.push(
        <p key={key++} className="my-2 text-[0.92rem] leading-relaxed text-ink/85">
          {inline(line, `p-${key}`)}
        </p>,
      );
    }
  }
  flush();

  return <div className="space-y-0.5">{blocks}</div>;
}
