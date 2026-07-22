"use client";

import { useExecution } from "@/contexts/execution-context";

const statusLabel: Record<string, string> = {
  IDLE: "IDLE", INITIALIZING: "INIT", PLANNING: "PLANNING",
  INVESTIGATING: "ANALYZING", EXECUTING: "EXECUTING",
  VERIFYING: "VERIFYING", REVIEWING: "REVIEWING", RE_PLANNING: "RE-PLAN",
  COMPLETED: "DONE", FAILED: "FAILED", CANCELLED: "CANCELLED",
};

const statusStyle: Record<string, { color: string; bg: string }> = {
  IDLE:          { color: "rgba(255,255,255,0.3)",  bg: "transparent" },
  INITIALIZING:  { color: "#60a5fa", bg: "rgba(96,165,250,0.1)" },
  PLANNING:      { color: "#a78bfa", bg: "rgba(167,139,250,0.1)" },
  INVESTIGATING: { color: "#fbbf24", bg: "rgba(251,191,36,0.1)" },
  EXECUTING:     { color: "#22d3ee", bg: "rgba(34,211,238,0.1)" },
  VERIFYING:     { color: "#34d399", bg: "rgba(52,211,153,0.1)" },
  REVIEWING:     { color: "#c084fc", bg: "rgba(192,132,252,0.1)" },
  RE_PLANNING:   { color: "#fb923c", bg: "rgba(251,146,60,0.1)" },
  COMPLETED:     { color: "#34d399", bg: "rgba(52,211,153,0.1)" },
  FAILED:        { color: "#fb7185", bg: "rgba(251,113,133,0.1)" },
  CANCELLED:     { color: "rgba(255,255,255,0.3)", bg: "transparent" },
};

export function StatusBar() {
  const { snapshot, wsStatus } = useExecution();
  const status = snapshot?.status ?? "IDLE";
  const style = statusStyle[status] ?? statusStyle.IDLE;
  const qualityScore = snapshot?.quality_score;

  return (
    <div className="ide-statusbar">
      {/* Status pill */}
      <div className="flex items-center gap-1.5 px-2 py-0.5 rounded"
        style={{ background: style.bg, border: `1px solid ${style.color}22` }}>
        <span
          className={["PLANNING","EXECUTING","REVIEWING","VERIFYING","INVESTIGATING"].includes(status) ? "status-ping" : ""}
          style={{ width: 5, height: 5, borderRadius: "50%", background: style.color, display: "inline-block", flexShrink: 0 }} />
        <span className="font-semibold" style={{ color: style.color }}>{statusLabel[status] ?? status}</span>
      </div>

      {/* Step counter */}
      {snapshot && (
        <span style={{ color: "rgba(255,255,255,0.25)" }}>
          step {snapshot.current_step}/{snapshot.max_steps}
        </span>
      )}

      {/* Rejection count */}
      {snapshot && snapshot.rejection_count > 0 && (
        <span style={{ color: "#fb923c" }}>
          ↩ {snapshot.rejection_count} re-plan{snapshot.rejection_count > 1 ? "s" : ""}
        </span>
      )}

      <div style={{ flex: 1 }} />

      {/* GLM Score */}
      {qualityScore != null && (
        <div className="flex items-center gap-1" style={{ color: "rgba(255,255,255,0.3)" }}>
          <span>GLM 5.2</span>
          <span style={{
            color: qualityScore >= 0.8 ? "#34d399" : qualityScore >= 0.5 ? "#fbbf24" : "#fb7185",
            fontWeight: 700,
          }}>
            {(qualityScore * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {/* WS Status */}
      <div className="flex items-center gap-1">
        <span style={{ width: 5, height: 5, borderRadius: "50%", display: "inline-block",
          background: wsStatus === "connected" ? "#34d399" : "#fb7185" }} />
        <span style={{ color: wsStatus === "connected" ? "#34d399" : "#fb7185" }}>
          {wsStatus === "connected" ? "Live" : "Offline"}
        </span>
      </div>
    </div>
  );
}
