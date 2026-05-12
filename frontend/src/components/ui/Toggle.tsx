interface ToggleProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export function Toggle({ label, description, checked, onChange, disabled = false }: ToggleProps) {
  return (
    <label className={["flex items-start gap-3 cursor-pointer", disabled ? "opacity-50 cursor-not-allowed" : ""].join(" ")}>
      <button
        role="switch"
        aria-checked={checked}
        type="button"
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={[
          "relative shrink-0 w-10 h-6 rounded-full border transition-colors duration-fast mt-0.5",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
          checked ? "bg-gold-500 border-gold-500" : "bg-border border-border",
        ].join(" ")}
      >
        <span
          className={[
            "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-panel-elev border border-border shadow transition-transform duration-fast",
            checked ? "translate-x-4" : "translate-x-0",
          ].join(" ")}
        />
      </button>
      <div>
        <p className="text-sm font-medium text-text-primary">{label}</p>
        {description && <p className="text-xs text-text-secondary mt-0.5">{description}</p>}
      </div>
    </label>
  );
}
