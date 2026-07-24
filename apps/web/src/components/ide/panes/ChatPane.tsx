"use client";

import { useState, useRef, useEffect } from "react";
import { useExecution, SessionEvent } from "@/contexts/execution-context";

function EventBubble({ event }: { event: SessionEvent }) {
  if (event.type === "thought") {
    return (
      <div className="flex gap-3 py-2">
        <div className="w-7 h-7 rounded-lg flex-shrink-0 mt-0.5 flex items-center justify-center text-xs font-bold bg-amber-500/20 border border-amber-500/30 text-amber-400">
          👁
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-mono font-semibold text-amber-400 mb-1">Agent Reasoning (Kimi K3)</div>
          <div className="chat-bubble-agent text-xs text-gray-200 leading-relaxed font-sans">
            {event.content}
          </div>
        </div>
      </div>
    );
  }

  if (event.type === "tool_observation") {
    return (
      <div className="flex gap-3 py-2">
        <div className="w-7 h-7 rounded-lg flex-shrink-0 mt-0.5 flex items-center justify-center text-xs font-bold bg-blue-500/20 border border-blue-500/30 text-blue-400">
          ⚙️
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono font-bold text-blue-400">{event.tool_name}</span>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
              event.success
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
            }`}>
              {event.success ? "✓ SUCCESS" : "✗ ERROR"}
            </span>
          </div>
          {event.output && (
            <pre className="text-xs rounded-lg p-3 bg-[#0d1322] border border-white/[0.08] text-gray-300 font-mono overflow-auto max-h-32 whitespace-pre-wrap">
              {event.output.slice(0, 600)}{event.output.length > 600 ? "…" : ""}
            </pre>
          )}
          {event.error && (
            <pre className="text-xs mt-1.5 rounded-lg p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono whitespace-pre-wrap">
              {event.error}
            </pre>
          )}
        </div>
      </div>
    );
  }

  if (event.type === "global_review_audit") {
    return (
      <div className={`my-3 rounded-xl p-4 border ${
        event.approved
          ? "bg-emerald-500/10 border-emerald-500/30"
          : "bg-orange-500/10 border-orange-500/30"
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm">{event.approved ? "✅" : "🔄"}</span>
            <span className={`text-xs font-bold ${event.approved ? "text-emerald-400" : "text-orange-400"}`}>
              GLM 5.2 Global Review Audit — {event.approved ? "Approved" : "Rejected & Reset"}
            </span>
          </div>
          {event.quality_score != null && (
            <span className="text-xs font-mono font-bold text-gray-400">
              {(event.quality_score * 100).toFixed(0)}% quality
            </span>
          )}
        </div>
        {event.summary && (
          <p className="text-xs text-gray-300 mb-2">{event.summary}</p>
        )}
        {!event.approved && event.rejection_reason && (
          <div className="mt-2 text-xs rounded-lg p-2.5 bg-orange-500/15 border border-orange-500/30 text-orange-300">
            <span className="font-bold block mb-0.5">Rejection Reason:</span>
            <span>{event.rejection_reason}</span>
          </div>
        )}
        {!event.approved && event.actionable_fix && (
          <div className="mt-2 text-xs rounded-lg p-2.5 bg-blue-500/15 border border-blue-500/30 text-blue-300 font-mono">
            <span className="font-bold block mb-0.5 font-sans">Actionable Fix:</span>
            <span>{event.actionable_fix}</span>
          </div>
        )}
      </div>
    );
  }

  if (event.type === "state_change") {
    return (
      <div className="flex items-center gap-3 py-1 my-1">
        <div className="h-px flex-1 bg-white/[0.08]" />
        <span className="text-[10px] font-mono font-bold text-gray-400 px-2 py-0.5 rounded bg-gray-800 border border-white/[0.08]">
          STATE → {event.status}
        </span>
        <div className="h-px flex-1 bg-white/[0.08]" />
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
      console.error("Execution error:", e);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0b0f19]">
      {/* Pane Header */}
      <div className="ide-pane-header justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-gray-300 font-mono uppercase tracking-wider">
            💬 Chat & Reasoning
          </span>
          <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            Kimi K3 + GLM 5.2
          </span>
        </div>
        {sessionEvents.length > 0 && (
          <button
            onClick={resetExecution}
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors font-mono">
            Clear Stream
          </button>
        )}
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {userMessages.length === 0 && sessionEvents.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-3xl shadow-lg shadow-amber-500/10">
              👻
            </div>
            <div>
              <h3 className="text-white font-bold text-base mb-1">Agent Phantom Controller</h3>
              <p className="text-gray-400 text-xs max-w-sm leading-relaxed">
                Enter an engineering goal below. The agent will plan, execute tools, verify assertions, and run GLM 5.2 global audits autonomously.
              </p>
            </div>
          </div>
        )}

        {userMessages.map((msg, i) => (
          <div key={`u${i}`} className="flex justify-end py-1">
            <div className="chat-bubble-user max-w-[85%]">
              <p className="text-xs text-white">{msg}</p>
            </div>
          </div>
        ))}

        {sessionEvents.map((ev, i) => (
          <EventBubble key={i} event={ev} />
        ))}

        {isRunning && (
          <div className="flex items-center gap-2 py-3 text-xs text-amber-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-amber-400 status-ping" />
            Agent processing task pipeline…
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Box */}
      <div className="p-3 border-t border-white/[0.08] bg-[#111827]">
        <div className="flex gap-2 items-end bg-[#0b0f19] border border-white/[0.1] rounded-xl p-3 focus-within:border-amber-500/50 transition-colors">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder="Describe an engineering task for Agent Phantom…"
            disabled={isRunning}
            rows={2}
            className="flex-1 bg-transparent text-xs text-gray-100 placeholder-gray-500 outline-none resize-none disabled:opacity-40 font-sans"
          />
          <button
            onClick={handleSubmit}
            disabled={isRunning || !input.trim()}
            className="gradient-btn px-4 py-2 rounded-lg text-xs font-bold text-slate-950 disabled:opacity-40 disabled:cursor-not-allowed shrink-0">
            {isRunning ? "Running…" : "Run Execution ↵"}
          </button>
        </div>
        <div className="text-[10px] font-mono text-gray-500 mt-1.5 ml-1">
          ↵ Submit · Shift+↵ New line
        </div>
      </div>
    </div>
  );
}
