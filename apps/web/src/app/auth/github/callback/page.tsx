"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authApi } from "@/lib/api";

function GitHubCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setError("No OAuth code received from GitHub.");
      return;
    }

    authApi.githubCallback(code)
      .then((res) => {
        if (res.data?.access_token) {
          localStorage.setItem("phantom_token", res.data.access_token);
          router.push("/onboarding");
        } else {
          setError("Failed to obtain authentication token.");
        }
      })
      .catch((err) => {
        console.error("GitHub OAuth Callback error:", err);
        setError(err.response?.data?.detail || "OAuth Authentication failed.");
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center text-center p-6">
        <div className="glass-panel p-8 rounded-xl max-w-md border border-rose-500/30">
          <div className="text-3xl mb-4">⚠️</div>
          <h1 className="text-xl font-bold text-rose-400 mb-2">Authentication Failed</h1>
          <p className="text-xs text-[#d7c4ac] mb-6 font-mono">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="bg-[#ffb000] text-[#6a4700] px-6 py-2 rounded font-mono font-bold text-xs uppercase tracking-wider glow-amber"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col items-center justify-center text-center p-6">
      <div className="glass-panel p-10 rounded-2xl max-w-md border border-[#ffb000]/30 shadow-2xl flex flex-col items-center">
        <div className="w-12 h-12 rounded-full border-2 border-[#ffb000] border-t-transparent animate-spin mb-6" />
        <h2 className="text-lg font-bold text-[#e5e2e1] mb-2">Signing in with GitHub...</h2>
        <p className="text-xs text-[#d7c4ac] font-mono">Verifying OAuth token &amp; initializing Workspace session</p>
      </div>
    </div>
  );
}

export default function GitHubCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center text-[#e5e2e1]">
        Loading...
      </div>
    }>
      <GitHubCallbackContent />
    </Suspense>
  );
}
