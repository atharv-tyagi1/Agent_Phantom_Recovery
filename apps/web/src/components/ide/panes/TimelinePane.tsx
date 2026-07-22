"use client";

import { useExecution, SessionEvent } from "@/contexts/execution-context";

function TimelineRow({ event, index }: { event: SessionEvent; index: number }) {
  if (event.type === "state_change") {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", padding: "0.375rem 0" }}>
        <div style={{ width: 24, flexShrink: 0, display: "flex", justifyContent: "center" }}>
          <span style={{ fontSize: "0.75rem" }}>
            {event.status === "COMPLETED" ? "✅" : event.status === "FAILED" ? "❌" : "→"}
          </span>
        </div>
        <span style={{ fontSize: "0.7rem", color: "rgba(139,92,246,0.7)", fontFamily: "var(--font-mono)", fontWeight: 600 }}>
          {event.status}
        </span>
        {event.timestamp && (
          <span style={{ marginLeft: "auto", fontSize: "0.65rem", color: "rgba(255,255,255,0.2)", fontFamily: "var(--font-mono)" }}>
            {new Date(event.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  if (event.type === "global_review_audit") {
    return (
      <div style={{
        display: "flex", alignItems: "flex-start", gap: "0.625rem",
        padding: "0.5rem 0.625rem", borderRadius: "0.625rem", margin: "0.25rem 0",
        background: event.approved ? "rgba(52,211,153,0.06)" : "rgba(251,146,60,0.06)",
        border: `1px solid ${event.approved ? "rgba(52,211,153,0.15)" : "rgba(251,146,60,0.15)"}`,
      }}>
        <span style={{ flexShrink: 0, fontSize: "0.8rem" }}>{event.approved ? "✅" : "🔄"}</span>
        <div>
          <div style={{ fontSize: "0.7rem", fontWeight: 600, color: event.approved ? "#34d399" : "#fb923c" }}>
            GLM 5.2 Review — {event.approved ? "Approved" : "Rejected"}
          </div>
          {event.quality_score != null && (
            <div style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.3)", marginTop: "0.125rem" }}>
              {(event.quality_score * 100).toFixed(0)}% quality score
            </div>
          )}
          {!event.approved && event.actionable_fix && (
            <div style={{ fontSize: "0.65rem", color: "#67e8f9", marginTop: "0.375rem", fontFamily: "var(--font-mono)" }}>
              Fix: {event.actionable_fix.slice(0, 80)}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (event.type === "thought") {
    return (
      <div style={{ display: "flex", alignItems: "flex-start", gap: "0.625rem", padding: "0.3rem 0" }}>
        <div style={{ width: 24, flexShrink: 0, display: "flex", justifyContent: "center" }}>
          <span style={{ fontSize: "0.6rem", color: "rgba(255,255,255,0.2)", fontFamily: "var(--font-mono)", marginTop: "0.15rem" }}>
            {String(event.step ?? index).padStart(2, "0")}
          </span>
        </div>
        <p style={{
          fontSize: "0.7rem", color: "#64748b", lineHeight: 1.5, flex: 1,
          overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
        }}>
          {event.content}
        </p>
      </div>
    );
  }

  if (event.type === "tool_observation") {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", padding: "0.3rem 0" }}>
        <div style={{ width: 24, flexShrink: 0, display: "flex", justifyContent: "center" }}>
          <span style={{ fontSize: "0.625rem", color: event.success ? "#34d399" : "#fb7185" }}>
            {event.success ? "▶" : "✗"}
          </span>
        </div>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "#22d3ee" }}>{event.tool_name}</span>
        <span style={{ fontSize: "0.65rem", color: event.success ? "#34d399" : "#fb7185" }}>
          {event.success ? "ok" : "err"}
        </span>
        {event.timestamp && (
          <span style={{ marginLeft: "auto", fontSize: "0.65rem", color: "rgba(255,255,255,0.15)", fontFamily: "var(--font-mono)" }}>
            {new Date(event.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  return null;
}

export function TimelinePane({ projectId }: { projectId: string }) {
  const { sessionEvents, snapshot } = useExecution();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#050508" }}>
      {/* Header */}
      <div className="ide-pane-header">
        <span style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          📋 Timeline
        </span>
        {snapshot && (
          <span style={{ marginLeft: "auto", fontSize: "0.7rem", color: "rgba(255,255,255,0.2)", fontFamily: "var(--font-mono)" }}>
            {snapshot.current_step} / {snapshot.max_steps}
          </span>
        )}
      </div>

      {/* Steps */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem" }}>
        {sessionEvents.length === 0 ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", paddingTop: "2rem", color: "rgba(255,255,255,0.2)" }}>
            <span style={{ fontSize: "1.5rem" }}>📋</span>
            <p style={{ fontSize: "0.75rem" }}>No execution steps yet</p>
          </div>
        ) : (
          <div style={{ position: "relative" }}>
            {/* Vertical line */}
            <div style={{
              position: "absolute", left: 11, top: 16, bottom: 16, width: 1,
              background: "rgba(255,255,255,0.05)",
            }} />
            <div>
              {sessionEvents.map((ev, i) => (
                <TimelineRow key={i} event={ev} index={i} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Checkpoints footer */}
      {snapshot?.checkpoint_hashes && snapshot.checkpoint_hashes.length > 0 && (
        <div style={{
          padding: "0.5rem 0.75rem", borderTop: "1px solid rgba(255,255,255,0.05)", flexShrink: 0,
        }}>
          <div style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.2)", marginBottom: "0.375rem" }}>Git Checkpoints</div>
          {snapshot.checkpoint_hashes.map((hash, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.65rem" }}>
              <span style={{ color: "rgba(255,255,255,0.15)" }}>●</span>
              <span style={{ fontFamily: "var(--font-mono)", color: "#64748b" }}>{hash.slice(0, 8)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
