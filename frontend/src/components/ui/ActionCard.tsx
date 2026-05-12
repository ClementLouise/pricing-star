import { type ReactNode } from "react";

interface ActionCardProps {
  icon: ReactNode;
  title: string;
  desc: string;
  shortcut?: string;
  variant?: "default" | "primary";
  onClick: () => void;
}

export function ActionCard({ icon, title, desc, shortcut, variant = "default", onClick }: ActionCardProps) {
  const isPrimary = variant === "primary";
  return (
    <button
      onClick={onClick}
      className={[
        "text-left rounded-md border transition-colors duration-fast min-h-[140px] flex flex-col",
        isPrimary
          ? "bg-text-primary border-text-primary hover:bg-text-primary/85 text-bg"
          : "bg-panel border-border-soft hover:border-gold-500 hover:bg-panel-elev text-text-primary",
      ].join(" ")}
    >
      {/* Header: icon + shortcut */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <span className={isPrimary ? "text-bg/80" : "text-text-tertiary"}>{icon}</span>
        {shortcut && (
          <kbd
            className={[
              "font-mono text-[9px] border rounded px-1 py-0.5",
              isPrimary
                ? "border-bg/20 text-bg/60"
                : "border-border text-text-tertiary",
            ].join(" ")}
          >
            {shortcut}
          </kbd>
        )}
      </div>
      {/* Footer: title + desc */}
      <div className="px-4 pb-4 mt-auto">
        <p className={["text-sm font-semibold mb-1", isPrimary ? "text-bg" : "text-text-primary"].join(" ")}>
          {title}
        </p>
        <p className={["text-xs", isPrimary ? "text-bg/70" : "text-text-secondary"].join(" ")}>
          {desc}
        </p>
      </div>
    </button>
  );
}
