"use client";

import { useState, useRef, useEffect } from "react";
import { useExecution, SessionEvent } from "@/contexts/execution-context";

function EventBubble({ event }: { event: SessionEvent }) {
  if (event.type === "thought") {
    return (
      <div className="flex gap-2.5 py-1.5">
        <div className="w-6 h-6 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center text-xs"
          style={{ background: "rgba(139,92,246,0.25)", border: "1px solid rgba(139,92,246,0.3)" }}>
          👁
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold mb-1" style={{ color: "#a78bfa" }}>Reasoning</div>
          <div className="text-sm leading-relaxed rounded-xl rounded-tl-sm p-3"
            style={{ background: "rgba(139,92,246,0.08)", border: "1px solid rgba(139,92,246,0.15)", color: "#cbd5e1" }}>
            {event.content}
          </div>
        </div>
      </div>
    );
  }

  if (event.type === "tool_observation") {
    return (
      <div className="flex gap-2.5 py-1.5">
        <div className="w-6 h-6 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center text-xs"
          style={{ background: "rgba(34,211,238,0.15)", border: "1px solid rgba(34,211,238,0.25)" }}>
          ⚙️
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono font-semibold" style={{ color: "#22d3ee" }}>{event.tool_name}</span>
            <span className="text-xs px-1.5 py-0.5 rounded-full font-medium"
              style={{
                background: event.success ? "rgba(52,211,153,0.15)" : "rgba(251,113,133,0.15)",
                color: event.success ? "#34d399" : "#fb7185",
                border: `1px solid ${event.success ? "rgba(52,211,153,0.25)" : "rgba(251,113,133,0.25)"}`,
              }}>
              {event.success ? "✓ ok" : "✗ err"}
            </span>
          </div>
          {event.output && (
            <pre className="text-xs rounded-xl p-3 overflow-auto max-h-28 whitespace-pre-wrap"
              style={{ background: "#0d0d14", border: "1px solid rgba(255,255,255,0.07)", color: "#94a3b8", fontFamily: "var(--font-mono)" }}>
              {event.output.slice(0, 500)}{event.output.length > 500 ? "…" : ""}
            </pre>
          )}
          {event.error && (
            <pre className="text-xs mt-1.5 rounded-xl p-3 whitespace-pre-wrap"
              style={{ background: "rgba(251,113,133,0.05)", border: "1px solid rgba(251,113,133,0.2)", color: "#fb7185", fontFamily: "var(--font-mono)" }}>
              {event.error}
            </pre>
          )}
        </div>
      </div>
    );
  }

  if (event.type === "global_review_audit") {
    return (
      <div className="my-2 rounded-2xl p-4"
        style={{
          background: event.approved ? "rgba(52,211,153,0.06)" : "rgba(251,146,60,0.06)",
          border: `1px solid ${event.approved ? "rgba(52,211,153,0.2)" : "rgba(251,146,60,0.2)"}`,
        }}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm">{event.approved ? "✅" : "🔄"}</span>
          <span className="text-sm font-bold" style={{ color: event.approved ? "#34d399" : "#fb923c" }}>
            GLM 5.2 Audit — {event.approved ? "Approved" : "Rejected"}
          </span>
          {event.quality_score != null && (
            <span className="ml-auto text-xs font-mono" style={{ color: "rgba(255,255,255,0.4)" }}>
              {(event.quality_score * 100).toFixed(0)}% quality
            </span>
          )}
        </div>
        {event.summary && (
          <p className="text-sm" style={{ color: "#94a3b8" }}>{event.summary}</p>
        )}
        {!event.approved && event.rejection_reason && (
          <div className="mt-2 text-xs rounded-xl px-3 py-2"
            style={{ background: "rgba(251,146,60,0.1)", border: "1px solid rgba(251,146,60,0.2)", color: "#fdba74" }}>
            <div className="font-semibold mb-1">Rejection Reason:</div>
            <div>{event.rejection_reason}</div>
          </div>
        )}
        {!event.approved && event.actionable_fix && (
          <div className="mt-2 text-xs rounded-xl px-3 py-2"
            style={{ background: "rgba(34,211,238,0.08)", border: "1px solid rgba(34,211,238,0.2)", color: "#67e8f9", fontFamily: "var(--font-mono)" }}>
            <div className="font-semibold mb-1" style={{ fontFamily: "var(--font-sans)" }}>Actionable Fix:</div>
            <div>{event.actionable_fix}</div>
          </div>
        )}
      </div>
    );
  }

  if (event.type === "state_change") {
    return (
      <div className="flex items-center gap-3 py-1">
        <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.05)" }} />
        <span className="text-xs font-mono font-medium" style={{ color: "rgba(255,255,255,0.2)", flexShrink: 0 }}>
          → {event.status}
        </span>
        <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.05)" }} />
      </div>
    );
  }

  return null;
}

export function ChatPane({ projectId }: { projectId: string }) {
  const { sessionEvents, startExecution, isRunning, resetExecution } = useExecution();
  const [input, setInput] = useState("");
  const [userMessages, setUserMessages] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [sessionEvents.length, userMessages.length]);

  const handleSubmit = async () => {
    if (!input.trim() || isRunning) return;
    const prompt = input.trim();
    setUserMessages((p) => [...p, prompt]);
    setInput("");
    try {
      await startExecution(projectId, prompt);
    } catch (e) {
      console.error("Execution failed:", e);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#050508" }}>
      {/* Header */}
      <div className="ide-pane-header">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(255,255,255,0.35)" }}>
          💬 Chat
        </span>
        {sessionEvents.length > 0 && (
          <button
            onClick={resetExecution}
            className="ml-auto text-xs transition-colors"
            style={{ color: "rgba(255,255,255,0.2)" }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.5)")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.2)")}>
            Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem 1rem" }}>
        {userMessages.length === 0 && sessionEvents.length === 0 && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", gap: "1rem", paddingTop: "3rem", paddingBottom: "3rem" }}>
            <div style={{
              width: 64, height: 64, borderRadius: "1.25rem",
              background: "linear-gradient(135deg, rgba(139,92,246,0.15), rgba(6,182,212,0.1))",
              border: "1px solid rgba(139,92,246,0.2)",
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2rem",
            }}>👻</div>
            <div style={{ textAlign: "center" }}>
              <p style={{ color: "#e2e8f0", fontWeight: 600, marginBottom: "0.25rem" }}>Agent Phantom IDE</p>
              <p style={{ color: "rgba(255,255,255,0.35)", fontSize: "0.8rem", lineHeight: 1.6 }}>
                Describe a task below — the agent will plan,<br />investigate, and execute autonomously.
              </p>
            </div>
          </div>
        )}

        {userMessages.map((msg, i) => (
          <div key={`u${i}`} style={{ display: "flex", justifyContent: "flex-end", padding: "0.375rem 0" }}>
            <div className="chat-bubble-user" style={{ maxWidth: "75%" }}>
              <p style={{ fontSize: "0.875rem", color: "#e2e8f0" }}>{msg}</p>
            </div>
          </div>
        ))}

        {sessionEvents.map((ev, i) => (
          <EventBubble key={i} event={ev} />
        ))}

        {isRunning && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0" }}>
            {[0, 150, 300].map((delay) => (
              <span key={delay} style={{
                width: 6, height: 6, borderRadius: "50%", background: "#a78bfa",
                animation: `phantom-ping 1.2s ${delay}ms ease-in-out infinite`,
                display: "inline-block",
              }} />
            ))}
            <span style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.3)" }}>Agent thinking…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: "0.625rem 0.75rem 0.75rem", flexShrink: 0 }}>
        <div style={{
          display: "flex", gap: "0.5rem", alignItems: "flex-end",
          background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: "1rem", padding: "0.625rem 0.75rem",
          transition: "border-color 0.2s",
        }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
            }}
            placeholder="Describe a task for Agent Phantom…"
            disabled={isRunning}
            rows={2}
            style={{
              flex: 1, background: "transparent", border: "none", outline: "none",
              color: "#e2e8f0", fontSize: "0.875rem", resize: "none",
              fontFamily: "var(--font-sans)", lineHeight: 1.5,
              opacity: isRunning ? 0.4 : 1,
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={isRunning || !input.trim()}
            style={{
              padding: "0.5rem 1rem", borderRadius: "0.75rem", border: "none",
              background: isRunning || !input.trim()
                ? "rgba(255,255,255,0.08)"
                : "linear-gradient(135deg, #7c3aed, #0891b2)",
              color: isRunning || !input.trim() ? "rgba(255,255,255,0.25)" : "white",
              fontSize: "0.8rem", fontWeight: 600, cursor: isRunning || !input.trim() ? "not-allowed" : "pointer",
              transition: "all 0.2s", whiteSpace: "nowrap", flexShrink: 0,
              fontFamily: "var(--font-sans)",
            }}>
            {isRunning ? "Running…" : "Run ↵"}
          </button>
        </div>
        <p style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.2)", marginTop: "0.25rem", marginLeft: "0.25rem" }}>
          ↵ submit · Shift+↵ new line
        </p>
      </div>
    </div>
  );
}
