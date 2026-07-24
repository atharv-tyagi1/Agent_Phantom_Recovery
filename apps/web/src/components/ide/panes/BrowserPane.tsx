"use client";

import { useState } from "react";

export function BrowserPane({ projectId }: { projectId: string }) {
  const [url, setUrl] = useState("about:blank");
  const [inputUrl, setInputUrl] = useState("http://localhost:3001");

  const navigate = () => {
    let target = inputUrl.trim();
    if (!target) return;
    if (!target.startsWith("http")) target = `https://${target}`;
    setUrl(target);
  };

  return (
    <div className="flex flex-col h-full bg-[#0b0f19]">
      <div className="ide-pane-header gap-2">
        <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider shrink-0">
          🌐 Browser Sandbox
        </span>
        <div className="flex-1 flex items-center gap-1.5 bg-[#111827] border border-white/[0.1] rounded px-2.5 py-1">
          <span className="text-gray-500 text-xs">🔒</span>
          <input
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && navigate()}
            placeholder="Enter preview URL…"
            className="flex-1 bg-transparent text-xs text-gray-200 placeholder-gray-600 outline-none font-mono"
          />
        </div>
        <button
          onClick={navigate}
          className="px-3 py-1 text-xs rounded font-bold font-mono bg-amber-500/20 text-amber-400 border border-amber-500/40 hover:bg-amber-500/30 transition-all">
          Navigate
        </button>
      </div>

      {url === "about:blank" ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-2xl mb-3">
            🌐
          </div>
          <h3 className="text-white font-bold text-sm mb-1">Sandboxed Visual Browser</h3>
          <p className="text-gray-400 text-xs max-w-sm leading-relaxed mb-4">
            Kimi K3 inspects page layout, visual element positions, and visual verification screenshots in real time.
          </p>
          <button
            onClick={() => setUrl(inputUrl)}
            className="gradient-btn px-4 py-2 rounded-lg text-xs font-bold text-slate-950 shadow-md">
            Load Preview →
          </button>
        </div>
      ) : (
        <iframe
          src={url}
          className="flex-1 w-full border-0 bg-white"
          sandbox="allow-scripts allow-same-origin allow-forms"
          title="Browser Preview"
        />
      )}
    </div>
  );
}
