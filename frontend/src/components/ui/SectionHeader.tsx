interface SectionHeaderProps {
  title: string;
  meta?: string;
}

export function SectionHeader({ title, meta }: SectionHeaderProps) {
  return (
    <div className="flex items-baseline justify-between mb-4">
      <span className="font-mono text-[11px] uppercase tracking-editorial text-text-secondary">
        {title}
      </span>
      {meta && (
        <span className="font-mono text-[10px] text-text-tertiary">{meta}</span>
      )}
    </div>
  );
}
