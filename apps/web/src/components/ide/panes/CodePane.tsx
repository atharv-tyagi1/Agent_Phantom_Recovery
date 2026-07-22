"use client";

import { useState, useEffect } from "react";
import { useExecution } from "@/contexts/execution-context";
import dynamic from "next/dynamic";

// Monaco Editor lazy-loaded (client-only)
const MonacoEditor = dynamic(() => import("@monaco-editor/react").then(m => m.default), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center">
      <span className="text-neutral-600 text-sm animate-pulse">Loading editor…</span>
    </div>
  ),
});

interface CodePaneProps {
  projectId: string;
}

export function CodePane({ projectId }: CodePaneProps) {
  const { snapshot } = useExecution();
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const modifiedFiles = snapshot?.modified_files ?? [];

  // Auto-select first file when it becomes available
  useEffect(() => {
    if (modifiedFiles.length > 0 && !selectedFile) {
      setSelectedFile(modifiedFiles[0]);
    }
  }, [modifiedFiles, selectedFile]);

  const loadFile = async (filePath: string) => {
    setSelectedFile(filePath);
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/tools/filesystem/read`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: filePath }),
        }
      );
      const data = await res.json();
      setFileContent(data.content || "// Unable to load file content");
    } catch {
      setFileContent(`// Could not load: ${filePath}`);
    } finally {
      setLoading(false);
    }
  };

  const getLanguage = (path: string) => {
    const ext = path.split(".").pop()?.toLowerCase();
    const map: Record<string, string> = {
      ts: "typescript", tsx: "typescript", js: "javascript", jsx: "javascript",
      py: "python", rs: "rust", go: "go", java: "java", css: "css",
      json: "json", yaml: "yaml", yml: "yaml", md: "markdown", sh: "shell",
      html: "html", xml: "xml", sql: "sql",
    };
    return map[ext ?? ""] ?? "plaintext";
  };

  return (
    <div className="flex flex-col h-full bg-neutral-950/50">
      {/* Pane Header */}
      <div className="flex items-center px-3 h-10 border-b border-white/[0.05] shrink-0 gap-1 overflow-x-auto">
        <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider shrink-0 mr-2">Code</span>
        {modifiedFiles.length === 0 && (
          <span className="text-xs text-neutral-600 italic">No files modified yet</span>
        )}
        {modifiedFiles.map((file) => {
          const name = file.split(/[\\/]/).pop() ?? file;
          return (
            <button
              key={file}
              onClick={() => loadFile(file)}
              className={`shrink-0 px-3 py-1 rounded-md text-xs font-mono transition-all ${
                selectedFile === file
                  ? "bg-violet-600/20 text-violet-300 border border-violet-500/30"
                  : "text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.04]"
              }`}
            >
              {name}
            </button>
          );
        })}
      </div>

      {/* Editor */}
      {selectedFile ? (
        <div className="flex-1 min-h-0">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <span className="text-neutral-600 text-sm animate-pulse">Loading file…</span>
            </div>
          ) : (
            <MonacoEditor
              value={fileContent}
              language={getLanguage(selectedFile)}
              theme="vs-dark"
              options={{
                readOnly: true,
                minimap: { enabled: false },
                fontSize: 13,
                lineHeight: 22,
                scrollBeyondLastLine: false,
                padding: { top: 12 },
                fontFamily: "var(--font-geist-mono), 'JetBrains Mono', monospace",
                renderLineHighlight: "gutter",
              }}
            />
          )}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <span className="text-4xl mb-3 block">📄</span>
            <p className="text-neutral-600 text-sm">Files modified by the agent will appear here</p>
          </div>
        </div>
      )}
    </div>
  );
}
