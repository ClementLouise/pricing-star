import { type ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  size?: "sm" | "md" | "lg";
}

const sizeClasses: Record<NonNullable<ModalProps["size"]>, string> = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
};

export function Modal({ open, onClose, title, children, footer, size = "md" }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 animate-fade-in" onClick={onClose} aria-hidden="true" />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className={[
          "relative w-full bg-panel border border-border rounded-lg shadow-lg animate-scale-in",
          sizeClasses[size],
        ].join(" ")}
      >
        <div className="flex items-center justify-between p-3 border-b border-border">
          <h2 id="modal-title" className="text-sm font-semibold text-text-primary">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="text-text-tertiary hover:text-text-primary transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="p-3">{children}</div>
        {footer && <div className="flex justify-end gap-2 p-3 border-t border-border">{footer}</div>}
      </div>
    </div>,
    document.body,
  );
}
