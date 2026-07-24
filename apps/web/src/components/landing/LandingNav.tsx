"use client";

import Link from "next/link";

export function LandingNav() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-[#131313]/80 backdrop-blur-xl border-b border-[#524533]/30 shadow-sm flex justify-between items-center h-16 px-6 md:px-10 max-w-[1440px] left-0 right-0 mx-auto">
      <Link href="/" className="font-bold text-lg tracking-tighter text-[#ffd597] flex items-center gap-2">
        <span className="w-7 h-7 rounded bg-[#ffb000] text-[#432c00] flex items-center justify-center text-xs font-black shadow-md shadow-[#ffb000]/20">
          👻
        </span>
        <span>PHANTOM RECOVERY</span>
      </Link>

      <div className="hidden md:flex gap-6 items-center">
        <a className="text-[#d7c4ac] hover:text-[#ffd597] transition-colors hover:bg-[#353534]/50 px-3 py-1 rounded text-sm" href="#systems">
          Systems
        </a>
        <a className="text-[#d7c4ac] hover:text-[#ffd597] transition-colors hover:bg-[#353534]/50 px-3 py-1 rounded text-sm" href="#protocols">
          Protocols
        </a>
        <a className="text-[#d7c4ac] hover:text-[#ffd597] transition-colors hover:bg-[#353534]/50 px-3 py-1 rounded text-sm" href="#architecture">
          Architecture
        </a>
        <a className="text-[#ffd597] border-b-2 border-[#ffd597] pb-0.5 px-3 py-1 text-sm font-semibold" href="#terminal">
          Terminal
        </a>
      </div>

      <div className="flex items-center gap-4">
        <Link
          href="/ide/demo-project"
          className="hidden md:flex items-center justify-center p-2 rounded-full hover:bg-[#353534]/50 transition-colors text-[#d7c4ac]"
          title="Open IDE Terminal">
          <span className="material-symbols-outlined text-xl">terminal</span>
        </Link>
        <Link
          href="/dashboard"
          className="hidden md:flex items-center justify-center p-2 rounded-full hover:bg-[#353534]/50 transition-colors text-[#d7c4ac]"
          title="Security & Projects">
          <span className="material-symbols-outlined text-xl">security</span>
        </Link>
        <Link
          href="/ide/demo-project"
          className="bg-[#ffb000] text-[#6a4700] font-mono text-xs uppercase tracking-widest px-4 py-2 rounded shadow-sm hover:bg-[#ffddaf] active:scale-95 transition-all glow-amber font-bold">
          Deploy Agent
        </Link>
      </div>
    </nav>
  );
}
