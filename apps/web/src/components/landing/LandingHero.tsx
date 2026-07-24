"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";

export function LandingHero() {
  const router = useRouter();

  const handleGitHubSignIn = async () => {
    try {
      const res = await authApi.getGitHubLoginUrl();
      if (res.data?.url) {
        window.location.href = res.data.url;
      }
    } catch (e) {
      console.error("Failed to get GitHub OAuth URL:", e);
      router.push("/dashboard");
    }
  };

  return (
    <section className="relative min-h-[85vh] flex flex-col justify-center items-center px-6 md:px-10 overflow-hidden border-b border-[#524533]/20 hex-pattern pt-16">
      <div className="relative z-10 max-w-4xl mx-auto text-center reveal active">
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#ffb000]/30 bg-[#ffb000]/10 text-[#ffb000] font-mono text-xs mb-8 font-semibold">
          <span className="w-2 h-2 rounded-full bg-[#ffb000] animate-pulse" />
          SYSTEM ONLINE. READY FOR INJECTION.
        </div>

        {/* Display Headline */}
        <h1 className="text-4xl sm:text-6xl md:text-[72px] md:leading-[1.1] font-bold text-[#e5e2e1] mb-6 tracking-tight drop-shadow-2xl">
          Autonomous Engineering. <br />
          <span className="text-[#ffb000]">Verified Recovery.</span>
        </h1>

        {/* Subtitle */}
        <p className="text-base md:text-lg text-[#d7c4ac] max-w-2xl mx-auto mb-10 leading-relaxed font-sans">
          Agent Phantom is a long-horizon autonomous system that investigates, fixes, and verifies code with mission-critical precision. Elevate your engineering pipeline beyond standard autocomplete.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={handleGitHubSignIn}
            className="w-full sm:w-auto bg-[#ffb000] text-[#6a4700] font-mono text-xs uppercase tracking-widest px-8 py-4 rounded hover:bg-[#ffddaf] active:scale-95 transition-all glow-amber font-bold flex items-center justify-center gap-3 shadow-xl cursor-pointer">
            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            <span>Sign in with GitHub</span>
          </button>
          <a
            href="#architecture"
            className="w-full sm:w-auto glass-panel text-[#adc6ff] hover:text-[#d8e2ff] hover:glow-amber-hover font-mono text-xs uppercase tracking-widest px-8 py-4 rounded transition-all flex items-center justify-center gap-2">
            <span className="material-symbols-outlined text-lg">hub</span>
            View Architecture
          </a>
        </div>
      </div>
    </section>
  );
}
