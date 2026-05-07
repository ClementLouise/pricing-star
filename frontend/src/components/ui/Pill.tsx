import { type ReactNode } from "react";

interface PillProps {
  variant?: "success" | "warning" | "danger" | "info" | "neutral";
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<NonNullable<PillProps["variant"]>, string> = {
  success: "bg-success-light text-success border-success/30",
  warning: "bg-warning-light text-warning border-warning/30",
  danger: "bg-danger-light text-danger border-danger/30",
  info: "bg-info-light text-info border-info/30",
  neutral: "bg-panel-elev text-text-secondary border-border",
};

export function Pill({ variant = "neutral", children, className = "" }: PillProps) {
  return (
    <span
      className={[
        "inline-flex items-center px-1.5 py-0.5 rounded font-mono text-[10px] font-medium border uppercase tracking-wider",
        variantClasses[variant],
        className,
      ].join(" ")}
    >
      {children}
    </span>
  );
}
