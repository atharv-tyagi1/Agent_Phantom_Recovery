"use client";

import { useExecution, SessionEvent } from "@/contexts/execution-context";
import { useRef, useEffect } from "react";

export function TerminalPane({ projectId }: { projectId: string }) {
  const { sessionEvents } = useExecution();
  const bottomRef = useRef<HTMLDivElement>(null);

  const lines: { text: string; kind: "cmd" | "output" | "error" | "info" }[] = [];
  
  for (const e of sessionEvents) {
    if (e.type === "tool_observation" && (e.tool_name === "terminal" || e.tool_name === "run_command" || e.tool_name === "bash")) {
      if (e.tool_name) lines.push({ text: `$ ${e.tool_name}`, kind: "cmd" });
      if (e.output) lines.push({ text: e.output, kind: e.success ? "output" : "error" });
      if (e.error) lines.push({ text: e.error, kind: "error" });
    }
    if (e.type === "state_change") {
      lines.push({ text: `[phantom] ── ${e.status} ──`, kind: "info" });
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines.length]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#050508" }}>
      {/* Header */}
      <div className="ide-pane-header">
        <span style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          ⌨️ Terminal
        </span>
        <span style={{ marginLeft: "0.5rem", color: "rgba(255,255,255,0.15)", fontSize: "0.7rem" }}>tool output</span>
      </div>

      {/* Output */}
      <div style={{
        flex: 1, overflowY: "auto", padding: "0.75rem 1rem",
        fontFamily: "var(--font-mono)", fontSize: "0.75rem", lineHeight: 1.7,
      }}>
        {/* Prompt header */}
        <div style={{ color: "rgba(255,255,255,0.15)", marginBottom: "0.75rem" }}>
          agent-phantom v1.0 · tool execution stream
        </div>
        
        {lines.length === 0 ? (
          <div style={{ color: "rgba(255,255,255,0.2)" }}>
            <span style={{ color: "#34d399" }}>$</span>
            <span style={{ animation: "phantom-ping 1s ease-in-out infinite", display: "inline-block", marginLeft: "0.375rem" }}>_</span>
            <span style={{ marginLeft: "0.5rem", color: "rgba(255,255,255,0.15)", fontStyle: "italic" }}>awaiting tool execution…</span>
          </div>
        ) : (
          lines.map((line, i) => {
            let color = "#94a3b8";
            if (line.kind === "cmd")    color = "#22d3ee";
            if (line.kind === "error")  color = "#fb7185";
            if (line.kind === "info")   color = "rgba(139,92,246,0.7)";
            return (
              <div key={i} style={{ color, whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
                {line.text}
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
