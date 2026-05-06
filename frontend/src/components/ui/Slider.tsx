interface SliderProps {
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (value: number) => void;
  formatValue?: (v: number) => string;
  label?: string;
  disabled?: boolean;
}

export function Slider({
  min,
  max,
  step = 1,
  value,
  onChange,
  formatValue,
  label,
  disabled = false,
}: SliderProps) {
  const pct = ((value - min) / (max - min)) * 100;
  const display = formatValue ? formatValue(value) : String(value);

  return (
    <div className="flex flex-col gap-2">
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-secondary">{label}</span>
          <span className="text-sm font-mono font-medium text-text-primary">{display}</span>
        </div>
      )}
      <div className="relative flex items-center h-5">
        <div className="absolute w-full h-1 rounded bg-panel-elev border border-border">
          <div
            className="h-full rounded bg-navy-500 transition-all duration-fast"
            style={{ width: `${pct}%` }}
          />
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute w-full opacity-0 cursor-pointer h-5 disabled:cursor-not-allowed"
          style={{ WebkitAppearance: "none" }}
        />
        <div
          className="absolute w-3.5 h-3.5 rounded-full bg-navy-400 border-2 border-navy-500 shadow pointer-events-none transition-all duration-fast"
          style={{ left: `calc(${pct}% - 7px)` }}
        />
      </div>
      <div className="flex items-center justify-between text-xs text-text-tertiary">
        <span>{formatValue ? formatValue(min) : min}</span>
        <span>{formatValue ? formatValue(max) : max}</span>
      </div>
    </div>
  );
}
