"use client";

import { useState } from "react";

interface BrowserPaneProps {
  projectId: string;
}

export function BrowserPane({ projectId }: BrowserPaneProps) {
  const [url, setUrl] = useState("about:blank");
  const [inputUrl, setInputUrl] = useState("");

  const navigate = () => {
    let target = inputUrl.trim();
    if (!target) return;
    if (!target.startsWith("http")) target = `https://${target}`;
    setUrl(target);
  };

  return (
    <div className="flex flex-col h-full bg-neutral-950">
      {/* Pane Header */}
      <div className="flex items-center px-4 h-10 border-b border-white/[0.05] shrink-0 gap-2">
        <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider shrink-0">Browser</span>
        <div className="flex-1 flex items-center gap-1 bg-white/[0.04] border border-white/[0.06] rounded-lg px-2">
          <span className="text-neutral-700 text-xs">🌐</span>
          <input
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && navigate()}
            placeholder="Enter URL to preview…"
            className="flex-1 bg-transparent text-xs text-neutral-300 placeholder-neutral-700 outline-none py-1.5"
          />
        </div>
        <button
          onClick={navigate}
          className="shrink-0 px-2.5 py-1 text-xs rounded-md bg-white/[0.05] border border-white/[0.06] text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.08] transition-all"
        >
          Go
        </button>
        {url !== "about:blank" && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="shrink-0 px-2.5 py-1 text-xs rounded-md bg-white/[0.05] border border-white/[0.06] text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.08] transition-all"
          >
            ↗
          </a>
        )}
      </div>

      {/* iframe Preview */}
      {url === "about:blank" ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <span className="text-4xl mb-3 block">🌐</span>
            <p className="text-neutral-600 text-sm">Enter a URL to preview</p>
            <p className="text-neutral-700 text-xs mt-1">Agent-generated previews will load here automatically</p>
          </div>
        </div>
      ) : (
        <iframe
          src={url}
          className="flex-1 w-full border-0"
          sandbox="allow-scripts allow-same-origin allow-forms"
          title="Browser Preview"
        />
      )}
    </div>
  );
}
