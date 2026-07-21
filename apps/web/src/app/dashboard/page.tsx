"use client";

import { useAuth } from "@/contexts/auth-context";
import { ProtectedRoute } from "@/components/protected-route";

export default function DashboardPage() {
  const { user, signOut } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen relative overflow-hidden bg-neutral-950">
        {/* Background blobs */}
        <div className="absolute top-[-10%] left-[10%] w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[5%] w-[350px] h-[350px] rounded-full bg-cyan-500/10 blur-[80px]" />

        {/* Top bar */}
        <header className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-cyan-400 flex items-center justify-center shadow-md shadow-violet-500/20">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
                />
              </svg>
            </div>
            <span className="text-white font-semibold tracking-tight text-lg">
              Agent Phantom
            </span>
          </div>

          <button
            onClick={signOut}
            className="px-4 py-2 rounded-lg text-sm font-medium text-neutral-300 bg-white/[0.05] border border-white/[0.08] hover:bg-white/[0.08] hover:text-white transition-all"
          >
            Sign Out
          </button>
        </header>

        {/* Main content */}
        <main className="relative z-10 max-w-4xl mx-auto px-8 py-12">
          <h1 className="text-3xl font-semibold text-white tracking-tight mb-2">
            Welcome back
          </h1>
          <p className="text-neutral-400 mb-10">
            Your autonomous recovery workspace is ready.
          </p>

          {/* User info card */}
          <div className="backdrop-blur-xl bg-white/[0.04] border border-white/[0.08] rounded-2xl p-6 shadow-xl">
            <h2 className="text-sm font-medium text-neutral-400 uppercase tracking-wider mb-4">
              Your Profile
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-white/[0.04]">
                <span className="text-neutral-500 text-sm">Email</span>
                <span className="text-white text-sm font-medium">
                  {user?.email}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-white/[0.04]">
                <span className="text-neutral-500 text-sm">User ID</span>
                <span className="text-neutral-300 text-sm font-mono">
                  {user?.id?.slice(0, 8)}…
                </span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-neutral-500 text-sm">Status</span>
                <span className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Authenticated
                </span>
              </div>
            </div>
          </div>

          {/* Placeholder cards for future workspace panes */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            {[
              {
                title: "Projects",
                desc: "Manage recovery targets",
                icon: "📂",
              },
              {
                title: "Executions",
                desc: "Monitor agent runs",
                icon: "⚡",
              },
              { title: "Memory", desc: "Browse agent memory", icon: "🧠" },
            ].map((card) => (
              <div
                key={card.title}
                className="backdrop-blur-xl bg-white/[0.03] border border-white/[0.06] rounded-xl p-5 hover:bg-white/[0.05] hover:border-white/[0.1] transition-all cursor-pointer group"
              >
                <span className="text-2xl mb-3 block">{card.icon}</span>
                <h3 className="text-white font-medium group-hover:text-violet-300 transition-colors">
                  {card.title}
                </h3>
                <p className="text-neutral-500 text-sm mt-1">{card.desc}</p>
              </div>
            ))}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
