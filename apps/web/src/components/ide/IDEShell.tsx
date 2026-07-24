"use client";

import { useState } from "react";
import { IDESidebar } from "./IDESidebar";
import { StatusBar } from "./StatusBar";
import { ChatPane } from "./panes/ChatPane";
import { CodePane } from "./panes/CodePane";
import { TerminalPane } from "./panes/TerminalPane";
import { BrowserPane } from "./panes/BrowserPane";
import { MemoryPane } from "./panes/MemoryPane";
import { TimelinePane } from "./panes/TimelinePane";
import { ExecutionProvider } from "@/contexts/execution-context";

type PaneId = "chat" | "code" | "terminal" | "browser" | "memory" | "timeline";

interface IDEShellProps {
  projectId: string;
  projectName?: string;
}

const paneComponents: Record<PaneId, React.ComponentType<{ projectId: string }>> = {
  chat: ChatPane,
  code: CodePane,
  terminal: TerminalPane,
  browser: BrowserPane,
  memory: MemoryPane,
  timeline: TimelinePane,
};

const paneLabels: Record<PaneId, string> = {
  chat: "Chat & Reasoning",
  code: "Monaco Code",
  terminal: "Terminal Stream",
  browser: "Browser Preview",
  memory: "Multi-Tier Memory",
  timeline: "Execution Timeline",
};

export function IDEShell({ projectId, projectName = "Agent Phantom" }: IDEShellProps) {
  const [primaryPane, setPrimaryPane] = useState<PaneId>("chat");
  const [secondaryPane, setSecondaryPane] = useState<PaneId>("code");
  const [showSecondary, setShowSecondary] = useState(true);

  const PrimaryComponent = paneComponents[primaryPane];
  const SecondaryComponent = paneComponents[secondaryPane];

  const allPanes: PaneId[] = ["chat", "code", "terminal", "browser", "memory", "timeline"];

  return (
    <ExecutionProvider projectId={projectId}>
      <div className="ide-root">
        {/* Sidebar */}
        <IDESidebar
          activePane={primaryPane}
          onPaneChange={(pane) => {
            if (pane === primaryPane) return;
            setSecondaryPane(primaryPane);
            setPrimaryPane(pane);
          }}
          projectName={projectName}
        />

        {/* Main Workspace Area */}
        <div className="ide-main">
          {/* Topbar */}
          <header className="ide-topbar">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-xs flex-1 min-w-0 font-medium">
              <span className="text-amber-400 font-bold tracking-tight text-sm">Agent Phantom</span>
              <span className="text-gray-600">/</span>
              <span className="text-gray-300 font-mono truncate">{projectName}</span>
              <span className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Closed-Loop Engine
              </span>
            </div>

            {/* View Pill Indicators */}
            <div className="hidden md:flex items-center gap-1.5 text-xs font-mono">
              <span className="px-2.5 py-1 rounded text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                {paneLabels[primaryPane]}
              </span>
              {showSecondary && (
                <>
                  <span className="text-gray-600">↔</span>
                  <span className="px-2.5 py-1 rounded text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/30">
                    {paneLabels[secondaryPane]}
                  </span>
                </>
              )}
            </div>

            {/* Pane Controls */}
            <div className="flex items-center gap-2">
              <select
                value={secondaryPane}
                onChange={(e) => setSecondaryPane(e.target.value as PaneId)}
                className="text-xs rounded px-2.5 py-1 text-gray-200 outline-none cursor-pointer bg-gray-800/80 border border-white/[0.1] font-mono">
                {allPanes.map((p) => (
                  <option key={p} value={p} className="bg-[#111827]">
                    {paneLabels[p]}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setShowSecondary((s) => !s)}
                className={`text-xs px-3 py-1 rounded font-semibold transition-all ${
                  showSecondary
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                    : "bg-gray-800 text-gray-400 border border-white/[0.1]"
                }`}>
                {showSecondary ? "⊟ Split View" : "⊞ Split View"}
              </button>
            </div>
          </header>

          {/* Pane Workspace Area */}
          <div className="ide-pane-area">
            {/* Primary Pane */}
            <div className="ide-pane" style={{ width: showSecondary ? "50%" : "100%" }}>
              <PrimaryComponent projectId={projectId} />
            </div>

            {/* Divider + Secondary Pane */}
            {showSecondary && (
              <>
                <div className="ide-pane-divider" />
                <div className="ide-pane" style={{ width: "50%" }}>
                  <SecondaryComponent projectId={projectId} />
                </div>
              </>
            )}
          </div>

          {/* Status Bar */}
          <StatusBar />
        </div>
      </div>
    </ExecutionProvider>
  );
}
