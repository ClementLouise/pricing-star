import { type ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  width?: string;
}

export function Drawer({ open, onClose, title, children, footer, width = "w-96" }: DrawerProps) {
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
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} aria-hidden="true" />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        className={[
          "relative flex flex-col h-full bg-panel border-l border-border shadow-lg animate-slide-in-right",
          width,
        ].join(" ")}
      >
        <div className="flex items-center justify-between p-3 border-b border-border shrink-0">
          <h2 id="drawer-title" className="text-sm font-semibold text-text-primary">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close drawer"
            className="text-text-tertiary hover:text-text-primary transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3">{children}</div>
        {footer && <div className="flex justify-end gap-2 p-3 border-t border-border shrink-0">{footer}</div>}
      </aside>
    </div>,
    document.body,
  );
}
