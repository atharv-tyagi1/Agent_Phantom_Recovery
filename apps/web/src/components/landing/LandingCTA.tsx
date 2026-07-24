"use client";

import Link from "next/link";

export function LandingCTA() {
  return (
    <section className="py-24 px-6 md:px-10 text-center relative border-t border-[#524533]/20 bg-[#0e0e0e]">
      <div className="absolute inset-0 bg-gradient-to-t from-[#ffb000]/5 to-transparent pointer-events-none" />
      <div className="relative z-10 max-w-2xl mx-auto reveal active">
        <h2 className="text-3xl md:text-5xl font-bold text-[#e5e2e1] mb-4">Initialize Recovery.</h2>
        <p className="text-[#d7c4ac] text-base mb-8 font-sans">
          Deploy Agent Phantom to secure, refactor, and stabilize your codebase today.
        </p>
        <Link
          href="/ide/demo-project"
          className="inline-block bg-[#ffb000] text-[#6a4700] font-mono text-xs uppercase tracking-widest px-10 py-4 rounded hover:bg-[#ffddaf] active:scale-95 transition-all glow-amber font-bold text-base shadow-xl">
          Begin Deployment
        </Link>
      </div>
    </section>
  );
}
