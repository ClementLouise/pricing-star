import { forwardRef, useEffect, useRef, useState } from "react";

type Format = "currency" | "percentage" | "integer" | "decimal";

interface NumberInputProps {
  label?: string;
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  format?: Format;
  precision?: number;
  min?: number;
  max?: number;
  step?: number;
  error?: string;
  helper?: string;
  disabled?: boolean;
  placeholder?: string;
}

function displayValue(raw: number | null | undefined, format: Format, precision: number): string {
  if (raw == null) return "";
  if (format === "currency") return raw.toFixed(precision);
  if (format === "percentage") return (raw * 100).toFixed(precision);
  return raw.toFixed(precision);
}

function parseRaw(str: string, format: Format): number | null {
  const cleaned = str.replace(/[^0-9.-]/g, "");
  if (cleaned === "" || cleaned === "-") return null;
  const n = parseFloat(cleaned);
  if (isNaN(n)) return null;
  if (format === "percentage") return n / 100;
  return n;
}

const prefixMap: Partial<Record<Format, string>> = { currency: "$" };
const suffixMap: Partial<Record<Format, string>> = { percentage: "%" };

export const NumberInput = forwardRef<HTMLInputElement, NumberInputProps>(
  (
    {
      label,
      value,
      onChange,
      format = "decimal",
      precision = 0,
      min,
      max,
      step,
      error,
      helper,
      disabled,
      placeholder,
    },
    ref,
  ) => {
    const [text, setText] = useState(() => displayValue(value, format, precision));
    const dirty = useRef(false);

    useEffect(() => {
      if (!dirty.current) {
        setText(displayValue(value, format, precision));
      }
    }, [value, format, precision]);

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
      dirty.current = true;
      setText(e.target.value);
      const parsed = parseRaw(e.target.value, format);
      onChange(parsed);
    }

    function handleBlur() {
      dirty.current = false;
      setText(displayValue(value, format, precision));
    }

    const pfx = prefixMap[format];
    const sfx = suffixMap[format];
    const inputId = label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-text-secondary uppercase tracking-wide">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {pfx && <span className="absolute left-3 text-sm text-text-tertiary pointer-events-none">{pfx}</span>}
          <input
            ref={ref}
            id={inputId}
            type="text"
            inputMode="decimal"
            value={text}
            placeholder={placeholder}
            disabled={disabled}
            min={min}
            max={max}
            step={step}
            onChange={handleChange}
            onBlur={handleBlur}
            className={[
              "w-full h-9 rounded border bg-panel text-sm text-text-primary text-right font-mono tabular-nums",
              "border-border placeholder:text-text-tertiary",
              "focus:outline-none focus:border-gold-500 focus:ring-1 focus:ring-gold-500",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              error ? "border-danger" : "",
              pfx ? "pl-7" : "pl-3",
              sfx ? "pr-7" : "pr-3",
            ]
              .filter(Boolean)
              .join(" ")}
          />
          {sfx && <span className="absolute right-3 text-xs text-text-tertiary pointer-events-none">{sfx}</span>}
        </div>
        {error && <p className="text-xs text-danger">{error}</p>}
        {helper && !error && <p className="text-xs text-text-tertiary">{helper}</p>}
      </div>
    );
  },
);
NumberInput.displayName = "NumberInput";
