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
    <div className="max-w-2xl">
      <span className="eyebrow">
        <span className="h-px w-7 bg-moss/50" />
        {eyebrow}
      </span>
      <h1 className="mt-5 font-display text-[clamp(2.2rem,4.5vw,3.4rem)] font-normal leading-[1.05] tracking-[-0.02em] text-forest">
        {title}
      </h1>
      <p className="mt-5 text-[1.05rem] leading-relaxed text-muted">{description}</p>
    </div>
  );
}
