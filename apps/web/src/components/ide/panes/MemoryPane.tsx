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
    <div className="flex flex-col h-full bg-[#0b0f19]">
      <div className="ide-pane-header">
        <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
          🧠 Multi-Tier Memory Store
        </span>
      </div>

      <div className="flex gap-1.5 p-2 border-b border-white/[0.08] bg-[#111827] overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-3 py-1 rounded text-xs font-mono font-semibold transition-all ${
              activeTab === t.id
                ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.05]"
            }`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4 font-mono text-xs">
        {activeTab === "session" && (
          <div className="space-y-2">
            {sessionEvents.length === 0 ? (
              <p className="text-gray-500 italic">No session events recorded yet</p>
            ) : (
              sessionEvents.map((ev, i) => (
                <div key={i} className="p-3 rounded-lg bg-[#111827] border border-white/[0.08]">
                  <div className="flex items-center justify-between text-amber-400 font-bold mb-1">
                    <span>{ev.type}</span>
                    {ev.step != null && <span className="text-gray-500">step {ev.step}</span>}
                  </div>
                  {(ev.content || ev.output || ev.summary) && (
                    <p className="text-gray-300 font-sans leading-relaxed line-clamp-2">
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
              <p className="text-gray-500 italic">Working memory (transient state) empty</p>
            ) : (
              <pre className="p-3 rounded-lg bg-[#111827] border border-white/[0.08] text-gray-300 whitespace-pre-wrap">
                {JSON.stringify(snapshot.working_memory, null, 2)}
              </pre>
            )}
          </div>
        )}

        {activeTab === "project" && (
          <div>
            {loading ? (
              <p className="text-amber-400 status-ping">Fetching project facts…</p>
            ) : Object.keys(projectFacts).length === 0 ? (
              <p className="text-gray-500 italic">No project facts stored in DB yet</p>
            ) : (
              Object.entries(projectFacts).map(([k, v]) => (
                <div key={k} className="flex justify-between p-2.5 border-b border-white/[0.06]">
                  <span className="text-amber-400 font-bold">{k}</span>
                  <span className="text-gray-300">{JSON.stringify(v)}</span>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "experience" && (
          <p className="text-gray-500 italic">
            Past verified solution embeddings retrieved from vector database after successful executions
          </p>
        )}
      </div>
    </div>
  );
}
