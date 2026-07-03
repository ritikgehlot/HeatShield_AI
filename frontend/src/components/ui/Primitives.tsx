import type { ReactNode } from "react";
import { AlertTriangle, Inbox, RefreshCw } from "lucide-react";

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-surface-hi/60 ${className}`} />;
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }: { icon?: typeof Inbox; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl2 border border-dashed border-border py-14 text-center">
      <Icon className="text-ink-faint" size={28} strokeWidth={1.5} />
      <div>
        <p className="font-display text-base font-medium text-ink">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-ink-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function ErrorState({ title = "Something didn't load", description, onRetry }: { title?: string; description?: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl2 border border-risk-extreme/30 bg-risk-extreme/[0.06] py-14 text-center">
      <AlertTriangle className="text-risk-extreme" size={28} strokeWidth={1.5} />
      <div>
        <p className="font-display text-base font-medium text-ink">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-ink-muted">{description}</p>}
      </div>
      {onRetry && (
        <button onClick={onRetry} className="inline-flex items-center gap-1.5 rounded-lg border border-border-strong px-3 py-1.5 text-sm text-ink hover:bg-surface-hi transition-colors">
          <RefreshCw size={14} /> Try again
        </button>
      )}
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  size = "md",
  disabled,
  type = "button",
  icon: Icon,
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
  disabled?: boolean;
  type?: "button" | "submit";
  icon?: typeof RefreshCw;
  className?: string;
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const sizeClass = size === "sm" ? "px-3 py-1.5 text-sm" : "px-4 py-2.5 text-sm";
  const variantClass = {
    primary: "bg-brand text-white hover:bg-brand-strong shadow-glow-brand",
    secondary: "bg-surface-hi text-ink border border-border-strong hover:bg-surface-hi/70",
    ghost: "text-ink-muted hover:text-ink hover:bg-surface-hi/50",
    danger: "bg-risk-extreme/15 text-risk-extreme border border-risk-extreme/30 hover:bg-risk-extreme/25",
  }[variant];
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${sizeClass} ${variantClass} ${className}`}>
      {Icon && <Icon size={15} />}
      {children}
    </button>
  );
}

export function StatCard({
  label,
  value,
  unit,
  tone = "neutral",
  footnote,
  icon: Icon,
}: {
  label: string;
  value: ReactNode;
  unit?: string;
  tone?: "neutral" | "risk" | "green" | "brand";
  footnote?: ReactNode;
  icon?: typeof Inbox;
}) {
  const toneClass = { neutral: "text-ink", risk: "text-risk-severe", green: "text-green", brand: "text-brand" }[tone];
  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between">
        <p className="mono-tag">{label}</p>
        {Icon && <Icon size={16} className="text-ink-faint" />}
      </div>
      <p className={`mt-2 font-display text-3xl font-semibold ${toneClass}`}>
        {value}
        {unit && <span className="ml-1 text-base font-normal text-ink-faint">{unit}</span>}
      </p>
      {footnote && <div className="mt-1.5 text-xs text-ink-muted">{footnote}</div>}
    </div>
  );
}
