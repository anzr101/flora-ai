export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="max-w-prose">
      <span className="eyebrow">
        <span className="h-1 w-1 rounded-full bg-leaf" />
        {eyebrow}
      </span>
      <h1 className="mt-4 font-display text-display tracking-tight text-forest">
        {title}
      </h1>
      <p className="mt-4 text-[1.05rem] leading-relaxed text-muted">
        {description}
      </p>
    </div>
  );
}
