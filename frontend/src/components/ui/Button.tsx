import { type ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "link";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  keyboardHint?: string;
}

const variantClasses: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-text-primary text-bg border border-text-primary hover:bg-text-primary/85 active:bg-text-primary/75",
  secondary:
    "bg-panel text-text-primary border border-border hover:border-gold-500 hover:bg-panel-elev",
  ghost: "bg-transparent text-text-secondary border border-transparent hover:bg-panel hover:text-text-primary",
  danger:
    "bg-danger text-white border border-transparent hover:bg-red-700 active:bg-red-800",
  link: "bg-transparent text-info border-none underline-offset-2 hover:underline p-0 h-auto",
};

const sizeClasses: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-7 px-2.5 text-xs",
  md: "h-8 px-3 text-sm",
  lg: "h-10 px-4 text-sm",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", loading = false, disabled, children, keyboardHint, className = "", ...props }, ref) => {
    const isDisabled = disabled || loading;
    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={[
          "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors duration-fast",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
          variantClasses[variant],
          sizeClasses[size],
          isDisabled ? "opacity-50 cursor-not-allowed pointer-events-none" : "cursor-pointer",
          className,
        ].join(" ")}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 000 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z" />
          </svg>
        )}
        {children}
        {keyboardHint && (
          <kbd className="font-mono text-[10px] opacity-60 ml-1 border border-current/20 rounded px-1">
            {keyboardHint}
          </kbd>
        )}
      </button>
    );
  },
);
Button.displayName = "Button";
