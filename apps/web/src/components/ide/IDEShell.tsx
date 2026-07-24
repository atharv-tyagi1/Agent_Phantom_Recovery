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
import { reposApi } from "@/lib/api";

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

  // Import Repo Modal state
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [gitUrl, setGitUrl] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  const PrimaryComponent = paneComponents[primaryPane];
  const SecondaryComponent = paneComponents[secondaryPane];

  const allPanes: PaneId[] = ["chat", "code", "terminal", "browser", "memory", "timeline"];

  const handleImportGitUrl = async () => {
    if (!gitUrl.trim()) return;
    setIsImporting(true);
    setImportStatus("Cloning and indexing repository AST...");
    try {
      const res = await reposApi.importGitUrl(projectId, gitUrl);
      setImportStatus(`Success! Imported ${res.data.full_name} to ${res.data.local_path}`);
      setTimeout(() => {
        setIsImportModalOpen(false);
        setGitUrl("");
        setImportStatus(null);
      }, 2000);
    } catch (err: any) {
      setImportStatus(`Import failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsImporting(false);
    }
  };

  const handleUploadZip = async () => {
    if (!selectedFile) return;
    setIsImporting(true);
    setImportStatus("Extracting ZIP archive and indexing AST symbols...");
    try {
      const res = await reposApi.uploadCodebaseZip(projectId, selectedFile);
      setImportStatus(`Success! Uploaded and indexed ${res.data.name}`);
      setTimeout(() => {
        setIsImportModalOpen(false);
        setSelectedFile(null);
        setImportStatus(null);
      }, 2000);
    } catch (err: any) {
      setImportStatus(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsImporting(false);
    }
  };

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

            {/* Import Repository / Upload ZIP Button */}
            <button
              onClick={() => setIsImportModalOpen(true)}
              className="text-xs px-3 py-1 rounded font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400 border border-amber-400/50 flex items-center gap-1.5 shadow-sm transition-all">
              <span>🔗 Connect Repo / Upload ZIP</span>
            </button>

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

      {/* Import Repository / Upload ZIP Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0f172a] border border-amber-500/30 rounded-xl p-6 max-w-lg w-full text-slate-100 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-amber-400 flex items-center gap-2">
                <span>🔗 Connect GitHub Repo or Upload ZIP</span>
              </h3>
              <button
                onClick={() => setIsImportModalOpen(false)}
                className="text-gray-400 hover:text-white font-mono text-sm">
                ✕
              </button>
            </div>

            {/* Option 1: Direct GitHub URL */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-300">Option 1: Import GitHub Repository by URL</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="https://github.com/username/repository.git"
                  value={gitUrl}
                  onChange={(e) => setGitUrl(e.target.value)}
                  className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white placeholder-gray-500 outline-none focus:border-amber-500 font-mono"
                />
                <button
                  onClick={handleImportGitUrl}
                  disabled={isImporting || !gitUrl.trim()}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold rounded text-xs transition-all">
                  Import & Index
                </button>
              </div>
            </div>

            <div className="relative flex items-center justify-center my-2">
              <div className="border-t border-gray-800 w-full" />
              <span className="bg-[#0f172a] px-3 text-[10px] text-gray-500 font-mono uppercase">OR</span>
            </div>

            {/* Option 2: Upload ZIP */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-300">Option 2: Upload Codebase ZIP Archive</label>
              <div className="flex gap-2 items-center">
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-1.5 text-xs text-gray-300 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:bg-amber-500/20 file:text-amber-400 hover:file:bg-amber-500/30"
                />
                <button
                  onClick={handleUploadZip}
                  disabled={isImporting || !selectedFile}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold rounded text-xs transition-all">
                  Upload ZIP
                </button>
              </div>
            </div>

            <div className="relative flex items-center justify-center my-2">
              <div className="border-t border-gray-800 w-full" />
              <span className="bg-[#0f172a] px-3 text-[10px] text-gray-500 font-mono uppercase">OR</span>
            </div>

            {/* Option 3: Full GitHub App / OAuth Onboarding */}
            <div className="p-3 bg-gray-900/60 rounded border border-gray-800 flex items-center justify-between text-xs">
              <div>
                <span className="font-semibold text-gray-200 block">Full GitHub OAuth & App Integration</span>
                <span className="text-gray-400 text-[11px]">Install App for PRs, Check Runs, and Webhooks</span>
              </div>
              <a
                href="/onboarding"
                className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-amber-400 border border-amber-500/30 rounded font-semibold transition-all">
                Launch Wizard 🚀
              </a>
            </div>

            {/* Status notification */}
            {importStatus && (
              <div className="p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono">
                {importStatus}
              </div>
            )}
          </div>
        </div>
      )}
    </ExecutionProvider>
  );
}
