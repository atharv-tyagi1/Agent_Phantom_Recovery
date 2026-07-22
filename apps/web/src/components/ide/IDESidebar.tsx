"use client";

import { useExecution } from "@/contexts/execution-context";

type PaneId = "chat" | "code" | "terminal" | "browser" | "memory" | "timeline";

const panes: { id: PaneId; icon: string; label: string }[] = [
  { id: "chat",     icon: "💬", label: "Chat" },
  { id: "code",     icon: "📄", label: "Code" },
  { id: "terminal", icon: "⌨️", label: "Terminal" },
  { id: "browser",  icon: "🌐", label: "Browser" },
  { id: "memory",   icon: "🧠", label: "Memory" },
  { id: "timeline", icon: "📋", label: "Timeline" },
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
      {/* Logo */}
      <div className="w-9 h-9 rounded-xl flex items-center justify-center mb-3 glow-violet"
        style={{ background: "linear-gradient(135deg, #7c3aed, #0891b2)", flexShrink: 0 }}>
        <svg className="w-[18px] h-[18px]" style={{ color: "white" }} fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
        </svg>
      </div>

      <div className="w-full px-2 flex flex-col gap-0.5">
        {panes.map((p) => (
          <button
            key={p.id}
            onClick={() => onPaneChange(p.id)}
            title={p.label}
            className={`sidebar-btn ${activePane === p.id ? "active" : ""}`}>
            <span>{p.icon}</span>
            {/* Active indicator bar */}
            {activePane === p.id && (
              <span className="absolute left-0 w-0.5 h-5 rounded-r-full"
                style={{ background: "#a78bfa" }} />
            )}
          </button>
        ))}
      </div>

      <div style={{ flex: 1 }} />

      {/* Status dot */}
      <div
        title={`Execution: ${status ?? "IDLE"}`}
        className={`w-2 h-2 rounded-full mb-2 ${
          status === "COMPLETED" ? "bg-emerald-400" :
          status === "FAILED"    ? "" :
          ["PLANNING","EXECUTING","REVIEWING","VERIFYING"].includes(status ?? "") ? "status-ping" :
          ""
        }`}
        style={{
          background: status === "COMPLETED" ? "#34d399" :
                      status === "FAILED"    ? "#fb7185" :
                      ["PLANNING","EXECUTING","REVIEWING","VERIFYING"].includes(status ?? "") ? "#a78bfa" :
                      "rgba(255,255,255,0.15)"
        }}
      />
    </div>
  );
}
