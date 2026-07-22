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
  chat: "Chat",
  code: "Code",
  terminal: "Terminal",
  browser: "Browser",
  memory: "Memory",
  timeline: "Timeline",
};

export function IDEShell({ projectId, projectName }: IDEShellProps) {
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

        {/* Main Area */}
        <div className="ide-main">
          {/* Top bar */}
          <header className="ide-topbar">
            {/* Breadcrumb */}
            <div className="flex items-center gap-1.5 text-sm flex-1 min-w-0">
              <span className="text-white font-semibold">Agent Phantom</span>
              {projectName && (
                <>
                  <svg className="w-3 h-3 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                  <span className="text-slate-400 text-xs truncate">{projectName}</span>
                </>
              )}
            </div>

            {/* Active pane pill */}
            <div className="hidden sm:flex items-center gap-1 text-xs text-slate-500">
              <span
                className="px-2 py-1 rounded-md text-xs font-medium"
                style={{ background: "rgba(139,92,246,0.15)", color: "#a78bfa", border: "1px solid rgba(139,92,246,0.25)" }}>
                {paneLabels[primaryPane]}
              </span>
              {showSecondary && (
                <>
                  <span className="text-white/20">↕</span>
                  <span
                    className="px-2 py-1 rounded-md text-xs font-medium"
                    style={{ background: "rgba(6,182,212,0.12)", color: "#22d3ee", border: "1px solid rgba(6,182,212,0.2)" }}>
                    {paneLabels[secondaryPane]}
                  </span>
                </>
              )}
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2">
              <select
                value={secondaryPane}
                onChange={(e) => setSecondaryPane(e.target.value as PaneId)}
                className="text-xs rounded-lg px-2 py-1.5 text-slate-300 outline-none cursor-pointer"
                style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", fontFamily: "inherit" }}>
                {allPanes.map((p) => (
                  <option key={p} value={p} style={{ background: "#0d0d14" }}>
                    {paneLabels[p]}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setShowSecondary((s) => !s)}
                className="text-xs px-3 py-1.5 rounded-lg font-medium transition-all"
                style={{
                  background: showSecondary ? "rgba(139,92,246,0.15)" : "rgba(255,255,255,0.05)",
                  border: showSecondary ? "1px solid rgba(139,92,246,0.3)" : "1px solid rgba(255,255,255,0.09)",
                  color: showSecondary ? "#a78bfa" : "#94a3b8",
                }}>
                {showSecondary ? "⊟ Split" : "⊞ Split"}
              </button>
            </div>
          </header>

          {/* Pane Area */}
          <div className="ide-pane-area">
            {/* Primary Pane */}
            <div
              className="ide-pane"
              style={{ width: showSecondary ? "50%" : "100%" }}>
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
