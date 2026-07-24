"use client";

import { useExecution, SessionEvent } from "@/contexts/execution-context";

function TimelineRow({ event, index }: { event: SessionEvent; index: number }) {
  if (event.type === "state_change") {
    return (
      <div className="flex items-center gap-3 py-2">
        <div className="w-6 flex justify-center text-amber-400 font-bold text-xs font-mono">
          →
        </div>
        <span className="text-xs font-mono font-bold text-amber-400">
          STATE: {event.status}
        </span>
        {event.timestamp && (
          <span className="ml-auto text-[10px] font-mono text-gray-500">
            {new Date(event.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  if (event.type === "global_review_audit") {
    return (
      <div className={`p-3 rounded-lg my-1 border ${
        event.approved ? "bg-emerald-500/10 border-emerald-500/30" : "bg-orange-500/10 border-orange-500/30"
      }`}>
        <div className="flex items-center justify-between text-xs font-bold font-mono">
          <span className={event.approved ? "text-emerald-400" : "text-orange-400"}>
            {event.approved ? "✅ GLM 5.2 Approved" : "🔄 GLM 5.2 Re-Plan Audit"}
          </span>
          {event.quality_score != null && (
            <span className="text-gray-400">{(event.quality_score * 100).toFixed(0)}% Score</span>
          )}
        </div>
      </div>
    );
  }

  if (event.type === "thought") {
    return (
      <div className="flex items-start gap-3 py-1.5">
        <div className="w-6 text-center text-gray-500 font-mono text-[10px] pt-0.5">
          {String(event.step ?? index).padStart(2, "0")}
        </div>
        <p className="text-xs text-gray-300 flex-1 leading-relaxed font-sans line-clamp-2">
          {event.content}
        </p>
      </div>
    );
  }

  if (event.type === "tool_observation") {
    return (
      <div className="flex items-center gap-3 py-1">
        <div className={`w-6 text-center text-xs font-bold ${event.success ? "text-emerald-400" : "text-rose-400"}`}>
          {event.success ? "▶" : "✗"}
        </div>
        <span className="font-mono text-xs text-blue-400 font-bold">{event.tool_name}</span>
        <span className={`text-[10px] font-mono font-bold ${event.success ? "text-emerald-400" : "text-rose-400"}`}>
          {event.success ? "ok" : "err"}
        </span>
      </div>
    );
  }

  return null;
}

export function TimelinePane({ projectId }: { projectId: string }) {
  const { sessionEvents, snapshot } = useExecution();

  return (
    <div className="flex flex-col h-full bg-[#0b0f19]">
      <div className="ide-pane-header justify-between">
        <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
          📋 Execution Step Timeline
        </span>
        {snapshot && (
          <span className="text-xs font-mono text-gray-500">
            Step {snapshot.current_step}/{snapshot.max_steps}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {sessionEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 gap-2 text-gray-500">
            <span className="text-2xl">📋</span>
            <p className="text-xs font-mono">No step progression logged yet</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sessionEvents.map((ev, i) => (
              <TimelineRow key={i} event={ev} index={i} />
            ))}
          </div>
        )}
      </div>

      {snapshot?.checkpoint_hashes && snapshot.checkpoint_hashes.length > 0 && (
        <div className="p-3 border-t border-white/[0.08] bg-[#111827]">
          <div className="text-[10px] font-mono font-bold text-gray-400 uppercase tracking-wider mb-2">
            Git Checkpoint Rollback History
          </div>
          <div className="space-y-1">
            {snapshot.checkpoint_hashes.map((hash, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono">
                <span className="text-amber-400">●</span>
                <span className="text-gray-300 font-bold">{hash.slice(0, 8)}</span>
                <span className="text-gray-500 text-[10px]">Checkpoint #{i + 1}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
