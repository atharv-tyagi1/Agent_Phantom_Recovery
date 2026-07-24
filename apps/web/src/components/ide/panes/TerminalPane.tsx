"use client";

import { useExecution } from "@/contexts/execution-context";
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
      lines.push({ text: `[agent-phantom] State → ${e.status}`, kind: "info" });
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines.length]);

  return (
    <div className="flex flex-col h-full bg-[#0b0f19]">
      <div className="ide-pane-header justify-between">
        <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
          ⌨️ Streaming Terminal Output
        </span>
        <span className="text-[10px] font-mono text-gray-500">xterm.js stream</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-6">
        <div className="text-gray-500 mb-2 border-b border-white/[0.06] pb-1">
          Agent Phantom Exec Terminal Session v1.0
        </div>

        {lines.length === 0 ? (
          <div className="flex items-center gap-2 text-gray-500 mt-2">
            <span className="text-amber-400 font-bold">$</span>
            <span className="w-2 h-4 bg-amber-400 inline-block status-ping" />
            <span className="italic text-gray-600">Awaiting shell tool execution…</span>
          </div>
        ) : (
          lines.map((line, i) => {
            let color = "text-gray-300";
            if (line.kind === "cmd")    color = "text-amber-400 font-bold";
            if (line.kind === "error")  color = "text-rose-400";
            if (line.kind === "info")   color = "text-blue-400";
            return (
              <div key={i} className={`${color} whitespace-pre-wrap break-all`}>
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
