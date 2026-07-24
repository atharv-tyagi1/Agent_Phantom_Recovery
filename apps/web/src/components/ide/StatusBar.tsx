"use client";

import { useExecution } from "@/contexts/execution-context";

const statusStyle: Record<string, { color: string; bg: string }> = {
  IDLE:          { color: "#9ca3af", bg: "transparent" },
  INITIALIZING:  { color: "#60a5fa", bg: "rgba(96,165,250,0.1)" },
  PLANNING:      { color: "#fbbf24", bg: "rgba(251,191,36,0.15)" },
  INVESTIGATING: { color: "#f59e0b", bg: "rgba(245,158,11,0.15)" },
  EXECUTING:     { color: "#3b82f6", bg: "rgba(59,130,246,0.15)" },
  VERIFYING:     { color: "#10b981", bg: "rgba(16,185,129,0.15)" },
  REVIEWING:     { color: "#8b5cf6", bg: "rgba(139,92,246,0.15)" },
  RE_PLANNING:   { color: "#f97316", bg: "rgba(249,115,22,0.15)" },
  COMPLETED:     { color: "#10b981", bg: "rgba(16,185,129,0.15)" },
  FAILED:        { color: "#fb7185", bg: "rgba(251,113,133,0.15)" },
  CANCELLED:     { color: "#9ca3af", bg: "transparent" },
};

export function StatusBar() {
  const { snapshot, wsStatus } = useExecution();
  const status = snapshot?.status ?? "IDLE";
  const style = statusStyle[status] ?? statusStyle.IDLE;
  const qualityScore = snapshot?.quality_score;

  return (
    <div className="ide-statusbar">
      {/* Execution status badge */}
      <div className="flex items-center gap-1.5 px-2 py-0.5 rounded font-bold font-mono"
        style={{ background: style.bg, border: `1px solid ${style.color}40`, color: style.color }}>
        <span
          className={["PLANNING","EXECUTING","REVIEWING","VERIFYING","INVESTIGATING"].includes(status) ? "status-ping" : ""}
          style={{ width: 6, height: 6, borderRadius: "50%", background: style.color, display: "inline-block" }} />
        <span>{status}</span>
      </div>

      {/* Step Counter */}
      {snapshot && (
        <span className="text-gray-400 font-mono">
          Step {snapshot.current_step}/{snapshot.max_steps}
        </span>
      )}

      {/* Rejection count */}
      {snapshot && snapshot.rejection_count > 0 && (
        <span className="text-orange-400 font-mono font-semibold">
          ↩ {snapshot.rejection_count} re-plan{snapshot.rejection_count > 1 ? "s" : ""}
        </span>
      )}

      <div className="flex-1" />

      {/* GLM 5.2 Quality Score */}
      {qualityScore != null && (
        <div className="flex items-center gap-1.5 font-mono text-gray-400">
          <span>GLM 5.2 Score:</span>
          <span className="font-bold" style={{
            color: qualityScore >= 0.8 ? "#10b981" : qualityScore >= 0.5 ? "#f59e0b" : "#fb7185"
          }}>
            {(qualityScore * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {/* WebSocket indicator */}
      <div className="flex items-center gap-1.5 font-mono">
        <span style={{
          width: 6, height: 6, borderRadius: "50%", display: "inline-block",
          background: wsStatus === "connected" ? "#10b981" : "#fb7185"
        }} />
        <span style={{ color: wsStatus === "connected" ? "#10b981" : "#fb7185" }}>
          {wsStatus === "connected" ? "Live Stream" : "Offline"}
        </span>
      </div>
    </div>
  );
}
