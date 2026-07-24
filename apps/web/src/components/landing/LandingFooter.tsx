"use client";

import Link from "next/link";

export function LandingFooter() {
  return (
    <footer className="w-full py-8 bg-[#0e0e0e] border-t border-[#524533]/20 px-6 md:px-10 max-w-[1440px] mx-auto relative z-40">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        <div>
          <div className="text-xl font-black text-[#e5e2e1] mb-1 tracking-tighter flex items-center gap-2">
            <span>👻</span>
            <span>PHANTOM RECOVERY</span>
          </div>
          <div className="font-mono text-[11px] uppercase tracking-widest text-[#45d79c]">
            © 2026 AGENT PHANTOM RECOVERY. ALL RIGHTS RESERVED.
          </div>
        </div>

        <div className="flex flex-wrap gap-6 md:justify-end items-center font-mono text-xs uppercase tracking-widest text-[#d7c4ac]">
          <Link className="hover:text-[#6ffbbe] transition-colors" href="/dashboard">
            Dashboard
          </Link>
          <Link className="hover:text-[#6ffbbe] transition-colors" href="/ide/demo-project">
            Antigravity IDE
          </Link>
          <a className="hover:text-[#6ffbbe] transition-colors" href="#architecture">
            Architecture
          </a>
          <span className="text-[#ffb000] font-bold">● System Online</span>
        </div>
      </div>
    </footer>
  );
}
