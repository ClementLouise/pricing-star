import { type InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "prefix"> {
  label?: string;
  error?: string;
  helper?: string;
  prefix?: string;
  suffix?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helper, prefix, suffix, className = "", id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-text-secondary uppercase tracking-wide">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {prefix && (
            <span className="absolute left-3 text-sm text-text-tertiary pointer-events-none">{prefix}</span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={[
              "w-full h-9 rounded border bg-panel text-sm text-text-primary",
              "border-border placeholder:text-text-tertiary",
              "focus:outline-none focus:border-gold-500 focus:ring-1 focus:ring-gold-500",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              error ? "border-danger" : "",
              prefix ? "pl-7" : "pl-3",
              suffix ? "pr-10" : "pr-3",
              className,
            ]
              .filter(Boolean)
              .join(" ")}
            {...props}
          />
          {suffix && (
            <span className="absolute right-3 text-xs text-text-tertiary pointer-events-none">{suffix}</span>
          )}
        </div>
        {error && <p className="text-xs text-danger">{error}</p>}
        {helper && !error && <p className="text-xs text-text-tertiary">{helper}</p>}
      </div>
    );
  },
);
Input.displayName = "Input";
