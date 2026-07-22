"use client";

import { useState } from "react";
import { useExecution } from "@/contexts/execution-context";
import { useMemory } from "@/hooks/useMemory";

type Tab = "session" | "working" | "project" | "experience";

const tabs: { id: Tab; icon: string; label: string }[] = [
  { id: "session",    icon: "🕐", label: "Session" },
  { id: "working",    icon: "⚡", label: "Working" },
  { id: "project",    icon: "📁", label: "Project" },
  { id: "experience", icon: "💡", label: "Experience" },
];

export function MemoryPane({ projectId }: { projectId: string }) {
  const [activeTab, setActiveTab] = useState<Tab>("session");
  const { snapshot, sessionEvents } = useExecution();
  const { projectFacts, loading } = useMemory(snapshot?.execution_id, projectId);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#050508" }}>
      {/* Header */}
      <div className="ide-pane-header">
        <span style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          🧠 Memory
        </span>
      </div>

      {/* Tabs */}
      <div style={{
        display: "flex", gap: "0.25rem", padding: "0.5rem 0.75rem",
        borderBottom: "1px solid rgba(255,255,255,0.06)", flexShrink: 0,
      }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: "0.25rem 0.625rem", borderRadius: "0.5rem", fontSize: "0.7rem",
              fontWeight: 500, cursor: "pointer", border: "none", fontFamily: "var(--font-sans)",
              background: activeTab === t.id ? "rgba(139,92,246,0.15)" : "transparent",
              color: activeTab === t.id ? "#a78bfa" : "rgba(255,255,255,0.3)",
              outline: activeTab === t.id ? "1px solid rgba(139,92,246,0.25)" : "none",
              transition: "all 0.15s",
            }}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem" }}>
        {activeTab === "session" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {sessionEvents.length === 0 ? (
              <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem", fontStyle: "italic" }}>No session events yet</p>
            ) : (
              sessionEvents.map((ev, i) => (
                <div key={i} style={{
                  background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "0.75rem", padding: "0.5rem 0.75rem",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                    <span style={{ color: "#a78bfa", fontFamily: "var(--font-mono)", fontSize: "0.7rem", fontWeight: 600 }}>{ev.type}</span>
                    {ev.step != null && <span style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.7rem" }}>step {ev.step}</span>}
                  </div>
                  {(ev.content || ev.output || ev.summary) && (
                    <p style={{ color: "#94a3b8", fontSize: "0.7rem", lineHeight: 1.5, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>
                      {ev.content || ev.output || ev.summary}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "working" && (
          <div>
            {!snapshot || !snapshot.working_memory || Object.keys(snapshot.working_memory).length === 0 ? (
              <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem", fontStyle: "italic" }}>Working memory empty</p>
            ) : (
              <pre style={{
                fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "#94a3b8",
                background: "#0d0d14", borderRadius: "0.75rem", padding: "0.75rem",
                border: "1px solid rgba(255,255,255,0.07)", whiteSpace: "pre-wrap", wordBreak: "break-all",
              }}>
                {JSON.stringify(snapshot.working_memory, null, 2)}
              </pre>
            )}
          </div>
        )}

        {activeTab === "project" && (
          <div>
            {loading ? (
              <p style={{ color: "#a78bfa", fontSize: "0.75rem", animation: "phantom-ping 1s ease-in-out infinite" }}>Loading…</p>
            ) : Object.keys(projectFacts).length === 0 ? (
              <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem", fontStyle: "italic" }}>No project facts stored yet</p>
            ) : (
              Object.entries(projectFacts).map(([k, v]) => (
                <div key={k} style={{
                  display: "flex", justifyContent: "space-between", gap: "0.75rem",
                  padding: "0.5rem 0", borderBottom: "1px solid rgba(255,255,255,0.05)",
                  fontSize: "0.75rem",
                }}>
                  <span style={{ color: "#a78bfa", fontFamily: "var(--font-mono)" }}>{k}</span>
                  <span style={{ color: "#94a3b8", textAlign: "right" }}>{JSON.stringify(v)}</span>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "experience" && (
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem", fontStyle: "italic" }}>
            Past solutions stored in DB after successful executions
          </p>
        )}
      </div>
    </div>
  );
}
