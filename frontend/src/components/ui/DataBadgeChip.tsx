import { Info } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";
import type { DataBadge } from "@/types/api";
import { PROVIDER_MODE_DOT, PROVIDER_MODE_LABEL } from "@/lib/risk";
import { formatDateTime, formatRelativeTime } from "@/lib/format";

/** Every value on this dashboard that matters is expected to carry one of
 * these. It is intentionally impossible to render a KPI without also
 * rendering where it came from and how fresh it is. */
export function DataBadgeChip({ badge, compact = false }: { badge: DataBadge; compact?: boolean }) {
  return (
    <Tooltip.Provider delayDuration={150}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button
            type="button"
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-canvas-raised/60 px-2.5 py-1 text-[11px] font-mono text-ink-muted hover:border-border-strong transition-colors"
          >
            <span className={`h-1.5 w-1.5 rounded-full ${PROVIDER_MODE_DOT[badge.mode]} ${badge.mode === "live" ? "animate-pulse-dot" : ""}`} />
            {PROVIDER_MODE_LABEL[badge.mode]}
            {!compact && badge.observed_at && <span className="text-ink-faint">· {formatRelativeTime(badge.observed_at)}</span>}
            <Info size={11} className="text-ink-faint" />
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            side="top"
            sideOffset={6}
            className="z-50 max-w-xs rounded-lg border border-border-strong bg-canvas-raised px-3 py-2.5 text-xs text-ink shadow-glass"
          >
            <div className="space-y-1">
              <div className="font-semibold text-ink">{badge.source || "Unknown source"}</div>
              <div className="text-ink-muted">{badge.message}</div>
              {badge.observed_at && <div className="text-ink-faint">Observed: {formatDateTime(badge.observed_at)}</div>}
              {badge.confidence !== null && badge.confidence !== undefined && (
                <div className="text-ink-faint">Confidence: {Math.round(badge.confidence * 100)}%</div>
              )}
            </div>
            <Tooltip.Arrow className="fill-canvas-raised" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
