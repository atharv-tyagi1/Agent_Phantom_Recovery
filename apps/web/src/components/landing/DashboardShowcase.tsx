"use client";

import Link from "next/link";

export function DashboardShowcase() {
  return (
    <section className="py-20 px-6 md:px-10 max-w-[1440px] mx-auto reveal" id="terminal">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-[#e5e2e1] mb-3">Mission Control Interface</h2>
        <p className="text-[#d7c4ac] text-sm max-w-xl mx-auto font-sans">
          Real-time telemetry and execution logs streamed directly from the agent&apos;s neural net during recovery operations.
        </p>
      </div>

      <div className="glass-panel p-3 rounded-xl relative group overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-br from-[#ffb000]/5 to-transparent pointer-events-none" />
        
        {/* Window Chrome Header */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-[#524533]/30 mb-2">
          <div className="w-3 h-3 rounded-full bg-[#ffb4ab]" />
          <div className="w-3 h-3 rounded-full bg-[#ffb000]" />
          <div className="w-3 h-3 rounded-full bg-[#45d79c]" />
          <div className="ml-4 font-mono text-xs text-[#d7c4ac] flex-1 text-center opacity-60">
            agent_phantom_recovery.exe — Mission Telemetry Status
          </div>
        </div>

        {/* Live Interactive IDE Preview Container */}
        <div className="relative rounded bg-[#0b0f19] border border-[#524533]/20 overflow-hidden min-h-[380px] p-4 font-mono text-xs flex flex-col justify-between">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Controller status */}
            <div className="md:col-span-5 space-y-3">
              <div className="flex items-center justify-between text-[#ffb000] font-bold text-xs pb-2 border-b border-[#524533]/30">
                <span>SYSTEM AGENT: Kimi K3 + GLM 5.2</span>
                <span className="text-[#45d79c]">● ONLINE</span>
              </div>
              <div className="p-3 rounded bg-[#1c1b1b] border border-[#524533]/30 space-y-2">
                <div className="text-[#adc6ff] text-xs font-bold">▶ STEP 04: CODEBASE INVESTIGATION</div>
                <p className="text-[#d7c4ac] text-[11px] font-sans leading-relaxed">
                  AST Call-graph parsing complete. Identified 3 unhandled exceptions in auth layer.
                </p>
              </div>
              <div className="p-3 rounded bg-[#45d79c]/10 border border-[#45d79c]/30">
                <div className="flex items-center justify-between text-[#45d79c] text-xs font-bold">
                  <span>GLM 5.2 REVIEW AUDIT</span>
                  <span>94% QUALITY</span>
                </div>
                <p className="text-[#d7c4ac] text-[11px] font-sans mt-1">
                  Zero regressions detected. Re-plan count: 0. Verified clean patch.
                </p>
              </div>
            </div>

            {/* Code diff view */}
            <div className="md:col-span-7 bg-[#131313] p-4 rounded border border-[#524533]/30 text-[11px] leading-6 text-[#d7c4ac]">
              <div className="flex items-center justify-between border-b border-[#524533]/30 pb-2 mb-2 text-[#ffb000]">
                <span>auth/validate.py</span>
                <span className="text-[#45d79c]">+12 lines modified</span>
              </div>
              <pre className="overflow-x-auto text-[#d7c4ac]">
{`def validate_session_token(token: str) -> bool:
    # Verified by Agent Phantom Audit Loop
    payload = jwt.decode(token, SECRET_KEY)
    if payload.get("exp") < time.time():
        raise ExpiredSessionError("Session expired")
    return True`}
              </pre>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#524533]/30 flex items-center justify-between">
            <span className="text-[#d7c4ac] text-[11px]">Ready for agent deployment</span>
            <Link
              href="/ide/demo-project"
              className="bg-[#ffb000] text-[#6a4700] px-4 py-1.5 rounded font-mono font-bold text-xs uppercase tracking-wider hover:bg-[#ffddaf] transition-all glow-amber">
              Open Antigravity IDE →
            </Link>
          </div>
        </div>

        {/* Overlay blur accents */}
        <div className="absolute top-1/4 -left-4 w-1 h-32 bg-[#ffb000]/50 blur-sm" />
        <div className="absolute bottom-1/4 -right-4 w-1 h-32 bg-[#45d79c]/50 blur-sm" />
      </div>
    </section>
  );
}
