import { type ReactNode } from "react";

interface PanelProps {
  children: ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
  elevated?: boolean;
  bordered?: boolean;
  interactive?: boolean;
  className?: string;
}

const paddingClasses: Record<NonNullable<PanelProps["padding"]>, string> = {
  none: "",
  sm: "p-2",
  md: "p-3",
  lg: "p-4",
};

export function Panel({
  children,
  padding = "md",
  elevated = false,
  bordered = true,
  interactive = false,
  className = "",
}: PanelProps) {
  return (
    <div
      className={[
        "rounded-lg",
        elevated ? "bg-panel-elev" : "bg-panel",
        bordered ? "border border-border" : "",
        interactive ? "hover:border-navy-700 transition-colors duration-base cursor-pointer" : "",
        paddingClasses[padding],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </div>
  );
}
