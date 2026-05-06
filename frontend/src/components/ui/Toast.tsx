import { createContext, type ReactNode, useCallback, useContext, useState } from "react";
import { createPortal } from "react-dom";

type ToastVariant = "success" | "error" | "warning" | "info";

interface ToastMessage {
  id: number;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  success: (msg: string) => void;
  error: (msg: string) => void;
  warning: (msg: string) => void;
  info: (msg: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const variantClasses: Record<ToastVariant, string> = {
  success: "bg-success border-success/30 text-white",
  error: "bg-danger border-danger/30 text-white",
  warning: "bg-warning border-warning/30 text-white",
  info: "bg-info border-info/30 text-white",
};

const icons: Record<ToastVariant, string> = {
  success: "✓",
  error: "✕",
  warning: "⚠",
  info: "ℹ",
};

let nextId = 1;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const add = useCallback((variant: ToastVariant, message: string) => {
    const id = nextId++;
    setToasts((prev) => [...prev, { id, variant, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000);
  }, []);

  const ctx: ToastContextValue = {
    success: (msg) => add("success", msg),
    error: (msg) => add("error", msg),
    warning: (msg) => add("warning", msg),
    info: (msg) => add("info", msg),
  };

  return (
    <ToastContext.Provider value={ctx}>
      {children}
      {createPortal(
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
          {toasts.map((t) => (
            <div
              key={t.id}
              role="alert"
              className={[
                "flex items-center gap-2 px-3 py-2 rounded border shadow-lg text-sm pointer-events-auto",
                "animate-in slide-in-from-right-4",
                variantClasses[t.variant],
              ].join(" ")}
            >
              <span>{icons[t.variant]}</span>
              <span>{t.message}</span>
            </div>
          ))}
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
}
