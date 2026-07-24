"use client";

export function BentoGrid() {
  return (
    <section className="py-20 px-6 md:px-10 max-w-[1440px] mx-auto border-t border-[#524533]/20 hex-pattern" id="systems">
      <h2 className="text-3xl font-bold text-[#e5e2e1] mb-12 text-center reveal active">Core Capabilities</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[240px]">
        {/* Planning */}
        <div className="glass-panel p-6 rounded-lg flex flex-col justify-between hover:glow-amber-hover transition-all reveal active md:col-span-2 group cursor-default">
          <div>
            <div className="flex justify-between items-start mb-4">
              <span className="material-symbols-outlined text-4xl text-[#ffb000] group-hover:scale-110 transition-transform">
                schema
              </span>
              <span className="font-mono text-xs text-[#9f8e78] px-2 py-1 bg-[#201f1f] rounded border border-[#524533]/30">
                SYS_01
              </span>
            </div>
            <h3 className="text-xl font-bold text-[#e5e2e1] mb-2">Multi-Step Planning</h3>
            <p className="text-[#d7c4ac] text-sm leading-relaxed font-sans">
              Breaks down complex codebase issues into discrete, verifiable steps before writing a single line of code. Generates a strategic architectural blueprint for recovery.
            </p>
          </div>
        </div>

        {/* Memory */}
        <div className="glass-panel p-6 rounded-lg flex flex-col justify-between hover:glow-amber-hover transition-all reveal active group cursor-default">
          <div>
            <div className="flex justify-between items-start mb-4">
              <span className="material-symbols-outlined text-4xl text-[#45d79c] group-hover:scale-110 transition-transform">
                memory
              </span>
              <span className="font-mono text-xs text-[#9f8e78] px-2 py-1 bg-[#201f1f] rounded border border-[#524533]/30">
                MEM_Core
              </span>
            </div>
            <h3 className="text-xl font-bold text-[#e5e2e1] mb-2">Persistent Context</h3>
            <p className="text-[#d7c4ac] text-sm leading-relaxed font-sans">
              Retains repository knowledge, user rules, and past verified fix embeddings across multi-step execution sessions.
            </p>
          </div>
        </div>

        {/* Analysis */}
        <div className="glass-panel p-6 rounded-lg flex flex-col justify-between hover:glow-amber-hover transition-all reveal active group cursor-default">
          <div>
            <div className="flex justify-between items-start mb-4">
              <span className="material-symbols-outlined text-4xl text-[#adc6ff] group-hover:scale-110 transition-transform">
                analytics
              </span>
              <span className="font-mono text-xs text-[#9f8e78] px-2 py-1 bg-[#201f1f] rounded border border-[#524533]/30">
                AST_RAG
              </span>
            </div>
            <h3 className="text-xl font-bold text-[#e5e2e1] mb-2">Deep Static Analysis</h3>
            <p className="text-[#d7c4ac] text-sm leading-relaxed font-sans">
              Tree-sitter AST parsing traces variables, symbols, and call graphs across multiple files to identify root cause flaws.
            </p>
          </div>
        </div>

        {/* Execution */}
        <div className="glass-panel p-6 rounded-lg flex flex-col justify-between hover:glow-amber-hover transition-all reveal active md:col-span-2 group cursor-default">
          <div>
            <div className="flex justify-between items-start mb-4">
              <span className="material-symbols-outlined text-4xl text-[#ffb000] group-hover:scale-110 transition-transform">
                terminal
              </span>
              <div className="flex gap-2">
                <span className="w-2 h-2 rounded-full bg-[#ffb4ab] animate-ping" />
                <span className="w-2 h-2 rounded-full bg-[#ffb000]" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-[#e5e2e1] mb-2">Autonomous Execution &amp; Verification</h3>
            <p className="text-[#d7c4ac] text-sm leading-relaxed font-sans">
              Writes candidate patches, runs local tests in a sandboxed terminal environment, and iteratively self-corrects via GLM 5.2 audits until the verification loop passes cleanly.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
