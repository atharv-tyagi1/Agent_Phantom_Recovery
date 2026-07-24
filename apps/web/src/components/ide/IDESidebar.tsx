"use client";

import { useExecution } from "@/contexts/execution-context";

type PaneId = "chat" | "code" | "terminal" | "browser" | "memory" | "timeline";

const panes: { id: PaneId; icon: string; label: string }[] = [
  { id: "chat",     icon: "💬", label: "Chat & Reasoning" },
  { id: "code",     icon: "📄", label: "Monaco Code" },
  { id: "terminal", icon: "⌨️", label: "Terminal Stream" },
  { id: "browser",  icon: "🌐", label: "Browser Preview" },
  { id: "memory",   icon: "🧠", label: "Multi-Tier Memory" },
  { id: "timeline", icon: "📋", label: "Execution Timeline" },
];

interface IDESidebarProps {
  activePane: PaneId;
  onPaneChange: (pane: PaneId) => void;
  projectName?: string;
}

export function IDESidebar({ activePane, onPaneChange }: IDESidebarProps) {
  const { snapshot } = useExecution();
  const status = snapshot?.status;

  return (
    <div className="ide-sidebar">
      {/* Brand Logo */}
      <div className="w-9 h-9 rounded-lg flex items-center justify-center mb-3 text-slate-950 font-bold text-base shadow-md shadow-amber-500/20 cursor-pointer"
        style={{ background: "linear-gradient(135deg, #f59e0b, #d97706)" }}>
        👻
      </div>

      {/* Pane Buttons */}
      <div className="w-full px-2 flex flex-col gap-1">
        {panes.map((p) => (
          <button
            key={p.id}
            onClick={() => onPaneChange(p.id)}
            title={p.label}
            className={`sidebar-btn ${activePane === p.id ? "active" : ""}`}>
            <span>{p.icon}</span>
            {activePane === p.id && (
              <span className="absolute left-0 w-0.5 h-5 rounded-r bg-amber-500" />
            )}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      {/* Status Dot */}
      <div
        title={`Status: ${status ?? "IDLE"}`}
        className={`w-2.5 h-2.5 rounded-full mb-3 ${
          status === "COMPLETED" ? "bg-emerald-400" :
          status === "FAILED"    ? "bg-rose-500" :
          ["PLANNING","EXECUTING","REVIEWING","VERIFYING","INVESTIGATING"].includes(status ?? "") ? "bg-amber-400 status-ping" :
          "bg-gray-600"
        }`}
      />
    </div>
  );
}
