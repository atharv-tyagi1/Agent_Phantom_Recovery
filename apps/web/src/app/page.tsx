import Link from "next/link";

const features = [
  {
    icon: "🧠",
    title: "Multi-Model Architecture",
    desc: "Kimi K3 for planning, Nemotron Ultra for verification, GLM 5.2 as an adversarial global reviewer that rejects weak outputs and forces self-correction.",
    gradient: "from-violet-500/20 to-purple-500/5",
    border: "border-violet-500/20",
  },
  {
    icon: "🔁",
    title: "Closed-Loop Execution",
    desc: "Goal → Plan → Investigate → Execute → Verify → Audit. If the GLM 5.2 reviewer rejects the output, it feeds back an actionable fix and replans automatically.",
    gradient: "from-cyan-500/20 to-blue-500/5",
    border: "border-cyan-500/20",
  },
  {
    icon: "👁️",
    title: "Vision & OCR",
    desc: "Kimi K3 handles high-level UI visual reasoning. NVIDIA Nemotron-OCR-v2 extracts pixel-perfect text from images, terminal logs, PDFs, and screenshots.",
    gradient: "from-emerald-500/20 to-teal-500/5",
    border: "border-emerald-500/20",
  },
  {
    icon: "📦",
    title: "Repository Intelligence",
    desc: "AST parsing, dependency graphs, call-chain analysis, and semantic vector search turn your codebase into high-signal context — not raw token noise.",
    gradient: "from-amber-500/20 to-orange-500/5",
    border: "border-amber-500/20",
  },
  {
    icon: "🧩",
    title: "Multi-Tier Memory",
    desc: "Working, Session, Project, and Experience memory keep the agent contextually grounded across steps, preventing drift and repeated mistakes.",
    gradient: "from-rose-500/20 to-pink-500/5",
    border: "border-rose-500/20",
  },
  {
    icon: "⚡",
    title: "Tool-Driven Execution",
    desc: "Terminal, Filesystem, Git, Browser, GitHub, and Nemotron OCR — all sandboxed and orchestrated by the execution controller with checkpoint rollback.",
    gradient: "from-violet-500/20 to-indigo-500/5",
    border: "border-indigo-500/20",
  },
];

const stats = [
  { value: "9", label: "Phase Architecture" },
  { value: "3", label: "LLM Models" },
  { value: "6", label: "Tool Integrations" },
  { value: "4", label: "Memory Tiers" },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#050508] text-slate-100 overflow-x-hidden">
      {/* ── Background orbs ──────────────────────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="blob-drift absolute top-[-20%] left-[-10%] w-[700px] h-[700px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)" }} />
        <div className="blob-drift-2 absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%)" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)" }} />
      </div>

      {/* ── Grid overlay ─────────────────────────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }} />

      {/* ── Navbar ───────────────────────────────────────────────────────── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center glow-violet"
            style={{ background: "linear-gradient(135deg, #7c3aed, #0891b2)" }}>
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z" />
            </svg>
          </div>
          <span className="text-white font-bold tracking-tight text-lg">Agent Phantom</span>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm text-slate-400">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login"
            className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/signup"
            className="gradient-btn px-5 py-2 rounded-xl text-sm font-semibold text-white">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative z-10 flex flex-col items-center text-center px-6 pt-24 pb-20 max-w-5xl mx-auto">
        {/* Badge */}
        <div className="animate-float-up inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-8 glass"
          style={{ borderColor: "rgba(139,92,246,0.3)", color: "#a78bfa" }}>
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 status-ping inline-block" />
          Autonomous Engineering Agent · Phase 8 Complete
        </div>

        {/* Headline */}
        <h1 className="animate-float-up-1 text-5xl md:text-7xl font-black tracking-tight leading-[1.05] mb-6">
          <span className="text-white">The AI Agent That</span>
          <br />
          <span className="gradient-text">Thinks, Acts & Audits</span>
          <br />
          <span className="text-white">Itself.</span>
        </h1>

        {/* Subheading */}
        <p className="animate-float-up-2 text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          Agent Phantom is a long-horizon autonomous coding system with a closed-loop execution model, 
          multi-model LLMs, repository intelligence, and a GLM 5.2 global reviewer that forces self-correction.
        </p>

        {/* CTA Buttons */}
        <div className="animate-float-up-3 flex flex-col sm:flex-row gap-4 items-center mb-16">
          <Link href="/signup"
            className="gradient-btn px-8 py-3.5 rounded-2xl text-base font-bold text-white shadow-2xl">
            Launch IDE →
          </Link>
          <Link href="/login"
            className="px-8 py-3.5 rounded-2xl text-base font-semibold glass glass-hover text-slate-300">
            Sign In
          </Link>
        </div>

        {/* Stats */}
        <div className="animate-float-up-4 grid grid-cols-2 md:grid-cols-4 gap-px glass rounded-2xl overflow-hidden w-full max-w-2xl">
          {stats.map((s) => (
            <div key={s.label} className="flex flex-col items-center py-5 px-4"
              style={{ background: "rgba(255,255,255,0.03)" }}>
              <span className="text-3xl font-black gradient-text">{s.value}</span>
              <span className="text-xs text-slate-500 mt-1">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── IDE Preview Mockup ───────────────────────────────────────────── */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        <div className="relative rounded-2xl overflow-hidden glass"
          style={{ border: "1px solid rgba(139,92,246,0.25)", boxShadow: "0 40px 80px -20px rgba(0,0,0,0.6), 0 0 80px rgba(139,92,246,0.1)" }}>

          {/* Fake window chrome */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.07]"
            style={{ background: "#0d0d14" }}>
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/70" />
              <div className="w-3 h-3 rounded-full bg-amber-500/70" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/70" />
            </div>
            <div className="flex-1 flex items-center justify-center">
              <div className="px-6 py-0.5 rounded-full text-xs text-slate-500 glass" style={{ fontSize: "0.7rem" }}>
                agent-phantom — Antigravity IDE
              </div>
            </div>
          </div>

          {/* Fake IDE layout */}
          <div className="flex h-[440px]" style={{ background: "#050508" }}>
            {/* Fake sidebar */}
            <div className="w-12 flex flex-col items-center py-3 gap-2 border-r border-white/[0.07]"
              style={{ background: "#0d0d14" }}>
              <div className="w-8 h-8 rounded-xl flex items-center justify-center mb-2"
                style={{ background: "linear-gradient(135deg, #7c3aed, #0891b2)" }}>
                <span className="text-xs">👻</span>
              </div>
              {["💬", "📄", "⌨️", "🌐", "🧠", "📋"].map((icon, i) => (
                <div key={i}
                  className={`w-9 h-9 rounded-lg flex items-center justify-center text-sm cursor-default ${i === 0 ? "bg-violet-500/20" : ""}`}
                  style={{ color: i === 0 ? "#a78bfa" : "rgba(255,255,255,0.25)" }}>
                  {icon}
                </div>
              ))}
            </div>

            {/* Fake left pane — Chat */}
            <div className="flex-1 flex flex-col border-r border-white/[0.07]">
              <div className="px-3 py-2 border-b border-white/[0.07] flex items-center gap-2" style={{ background: "#0d0d14" }}>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Chat</span>
              </div>
              <div className="flex-1 overflow-hidden p-3 flex flex-col gap-3">
                <div className="flex gap-2">
                  <div className="w-5 h-5 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center" style={{ background: "rgba(139,92,246,0.3)" }}>
                    <span style={{ fontSize: "9px" }}>👁</span>
                  </div>
                  <div className="chat-bubble-agent">
                    <p className="text-xs text-slate-300 leading-relaxed">Analyzing codebase… found 3 potential vulnerabilities in <span className="text-violet-400 font-mono">auth/validate.py</span></p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="w-5 h-5 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center" style={{ background: "rgba(34,211,238,0.2)" }}>
                    <span style={{ fontSize: "9px" }}>⚙️</span>
                  </div>
                  <div style={{ background: "rgba(34,211,238,0.08)", border: "1px solid rgba(34,211,238,0.2)", borderRadius: "0.75rem", borderTopLeftRadius: "0.15rem", padding: "0.5rem 0.75rem" }}>
                    <p className="text-[10px] text-slate-400 font-mono">terminal → pytest tests/test_auth.py</p>
                    <p className="text-[10px] text-emerald-400 mt-1">✓ 14/14 passed · 2.3s</p>
                  </div>
                </div>
                <div style={{ background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.25)", borderRadius: "0.75rem", padding: "0.75rem" }}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs">✅</span>
                    <span className="text-xs font-semibold text-emerald-400">GLM 5.2 Audit — Approved</span>
                    <span className="ml-auto text-[10px] font-mono text-slate-500">94% quality</span>
                  </div>
                  <p className="text-[10px] text-slate-400">All vulnerabilities patched and tests passing. Execution complete.</p>
                </div>
              </div>
              {/* Fake input */}
              <div className="p-3 border-t border-white/[0.07]">
                <div className="flex gap-2 rounded-xl px-3 py-2 glass">
                  <span className="text-[11px] text-slate-600 flex-1">Describe a task for Agent Phantom…</span>
                  <div className="px-3 py-1 rounded-lg text-[11px] font-semibold text-white" style={{ background: "linear-gradient(135deg, #7c3aed, #0891b2)" }}>Run</div>
                </div>
              </div>
            </div>

            {/* Fake right pane — Code */}
            <div className="flex-1 flex flex-col">
              <div className="px-3 py-2 border-b border-white/[0.07] flex items-center gap-2" style={{ background: "#0d0d14" }}>
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Code</span>
                <div className="px-2 py-0.5 rounded text-[10px] font-mono" style={{ background: "rgba(139,92,246,0.15)", color: "#a78bfa", border: "1px solid rgba(139,92,246,0.3)" }}>validate.py</div>
              </div>
              <div className="flex-1 overflow-hidden p-3 font-mono text-[10px] leading-5" style={{ color: "#7c8fa6" }}>
                <div><span style={{ color: "#569cd6" }}>def</span> <span style={{ color: "#dcdcaa" }}>validate_token</span><span style={{ color: "#d4d4d4" }}>(token: str) -&gt; </span><span style={{ color: "#4ec9b0" }}>bool</span><span style={{ color: "#d4d4d4" }}>:</span></div>
                <div className="pl-4"><span style={{ color: "#6a9955" }}># Validate JWT expiration and signature</span></div>
                <div className="pl-4"><span style={{ color: "#569cd6" }}>try</span><span style={{ color: "#d4d4d4" }}>:</span></div>
                <div className="pl-8"><span style={{ color: "#9cdcfe" }}>payload</span> <span style={{ color: "#d4d4d4" }}>=</span> <span style={{ color: "#4ec9b0" }}>jwt</span><span style={{ color: "#d4d4d4" }}>.</span><span style={{ color: "#dcdcaa" }}>decode</span><span style={{ color: "#d4d4d4" }}>(token)</span></div>
                <div className="pl-8"><span style={{ color: "#569cd6" }}>if</span> <span style={{ color: "#9cdcfe" }}>payload</span><span style={{ color: "#d4d4d4" }}>[</span><span style={{ color: "#ce9178" }}>&apos;exp&apos;</span><span style={{ color: "#d4d4d4" }}>]</span> <span style={{ color: "#d4d4d4" }}>&lt;</span> <span style={{ color: "#4ec9b0" }}>time</span><span style={{ color: "#d4d4d4" }}>.</span><span style={{ color: "#dcdcaa" }}>time</span><span style={{ color: "#d4d4d4" }}>()</span><span style={{ color: "#d4d4d4" }}>:</span></div>
                <div className="pl-12"><span style={{ color: "#c586c0" }}>return</span> <span style={{ color: "#569cd6" }}>False</span></div>
                <div className="pl-8"><span style={{ color: "#c586c0" }}>return</span> <span style={{ color: "#569cd6" }}>True</span></div>
                <div className="pl-4"><span style={{ color: "#569cd6" }}>except</span> <span style={{ color: "#4ec9b0" }}>jwt</span><span style={{ color: "#d4d4d4" }}>.</span><span style={{ color: "#4ec9b0" }}>InvalidTokenError</span><span style={{ color: "#d4d4d4" }}>:</span></div>
                <div className="pl-8"><span style={{ color: "#c586c0" }}>return</span> <span style={{ color: "#569cd6" }}>False</span></div>
              </div>
            </div>
          </div>

          {/* Fake statusbar */}
          <div className="flex items-center justify-between px-3 h-6 border-t border-white/[0.07] font-mono"
            style={{ background: "#0d0d14", fontSize: "0.65rem", color: "rgba(255,255,255,0.3)" }}>
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
              <span className="text-emerald-400">COMPLETED</span>
              <span>Step 8 / 15</span>
            </div>
            <div className="flex items-center gap-3">
              <span>GLM 5.2 Score</span>
              <span className="text-emerald-400 font-semibold">94%</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
              <span className="text-emerald-400">Live</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────── */}
      <section id="features" className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
            Built for <span className="gradient-text">real engineering</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Every component is designed for long-horizon autonomous tasks, not toy demos.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title}
              className={`glass glass-hover relative rounded-2xl p-6 overflow-hidden group`}
              style={{ borderColor: f.border.replace("border-", "").replace("/20", "") }}>
              <div className={`absolute inset-0 bg-gradient-to-br ${f.gradient} opacity-40 group-hover:opacity-60 transition-opacity`} />
              <div className="relative z-10">
                <span className="text-3xl mb-4 block">{f.icon}</span>
                <h3 className="text-white font-semibold mb-2">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Architecture Banner ───────────────────────────────────────────── */}
      <section id="architecture" className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        <div className="glass rounded-3xl p-8 md:p-12 text-center relative overflow-hidden"
          style={{ border: "1px solid rgba(139,92,246,0.2)" }}>
          <div className="absolute inset-0 opacity-30"
            style={{ background: "radial-gradient(ellipse at center, rgba(139,92,246,0.15) 0%, transparent 70%)" }} />
          <div className="relative z-10">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Goal → Plan → Investigate → Execute → Verify → <span className="gradient-text">Audit</span>
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto mb-8">
              The GLM 5.2 Global Reviewer acts as an unbiased final auditor. If it rejects the output with a quality score below threshold, 
              it generates an actionable fix and the agent re-plans — automatically.
            </p>
            <Link href="/signup"
              className="gradient-btn inline-flex items-center gap-2 px-8 py-4 rounded-2xl text-base font-bold text-white">
              Open the IDE →
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-white/[0.06] py-8 text-center text-slate-600 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-5 h-5 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #7c3aed, #0891b2)" }}>
            <span style={{ fontSize: "8px" }}>👻</span>
          </div>
          <span className="text-slate-400 font-semibold">Agent Phantom</span>
        </div>
        <p>Autonomous engineering for complex problem-solving, bug fixing, and codebase recovery.</p>
      </footer>
    </main>
  );
}
