"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { ProtectedRoute } from "@/components/protected-route";
import { projectsApi } from "@/lib/api";
import Link from "next/link";

interface Project {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
}

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    projectsApi
      .list()
      .then((res) => setProjects(res.data ?? []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false));
  }, []);

  const createProject = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const res = await projectsApi.create({ name: newName.trim(), description: newDesc.trim() });
      const project = res.data;
      setProjects((p) => [project, ...p]);
      setNewName("");
      setNewDesc("");
      setShowCreate(false);
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#0b0f19] text-gray-100 font-sans">
        {/* Header */}
        <header className="border-b border-white/[0.08] bg-[#111827]">
          <div className="max-w-7xl mx-auto flex items-center justify-between px-8 py-4">
            <div className="flex items-center gap-3">
              <Link href="/" className="w-9 h-9 rounded-lg flex items-center justify-center font-bold text-slate-950 shadow-md shadow-amber-500/20"
                style={{ background: "linear-gradient(135deg, #f59e0b, #d97706)" }}>
                👻
              </Link>
              <div>
                <span className="text-white font-bold text-base tracking-tight block">Agent Phantom</span>
                <span className="text-[10px] font-mono text-gray-400">Engineering Workspaces</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-gray-400 text-xs font-mono hidden sm:inline-block">{user?.email}</span>
              <button
                onClick={signOut}
                className="px-3.5 py-1.5 rounded text-xs font-semibold text-gray-300 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.1] transition-all font-mono">
                Sign Out
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard Main Content */}
        <main className="max-w-6xl mx-auto px-8 py-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
            <div>
              <h1 className="text-2xl font-extrabold text-white tracking-tight mb-1">
                Workspace Projects
              </h1>
              <p className="text-gray-400 text-sm">
                Select an engineering recovery target to launch the Antigravity IDE.
              </p>
            </div>

            <button
              onClick={() => setShowCreate((v) => !v)}
              className="gradient-btn px-5 py-2.5 rounded-lg text-xs font-bold text-slate-950 shadow-lg shrink-0">
              + Create Project
            </button>
          </div>

          {/* New Project Form */}
          {showCreate && (
            <div className="mb-8 glass-bright rounded-xl p-5 border border-amber-500/30">
              <h3 className="text-sm font-bold text-white mb-3">Create Engineering Project</h3>
              <div className="space-y-3 max-w-xl">
                <input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Project title (e.g., E-Commerce Auth Recovery)…"
                  className="w-full bg-[#0b0f19] border border-white/[0.1] rounded-lg px-4 py-2.5 text-xs text-white placeholder-gray-500 outline-none focus:border-amber-500 transition-all font-sans"
                />
                <input
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Target repository or description…"
                  className="w-full bg-[#0b0f19] border border-white/[0.1] rounded-lg px-4 py-2.5 text-xs text-white placeholder-gray-500 outline-none focus:border-amber-500 transition-all font-sans"
                />
                <div className="flex gap-2">
                  <button
                    onClick={createProject}
                    disabled={creating || !newName.trim()}
                    className="gradient-btn px-4 py-2 rounded-lg text-xs font-bold text-slate-950 disabled:opacity-40">
                    {creating ? "Creating…" : "Save Project"}
                  </button>
                  <button
                    onClick={() => setShowCreate(false)}
                    className="px-4 py-2 rounded-lg text-xs font-medium text-gray-400 bg-white/[0.05] border border-white/[0.1]">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Projects Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-36 rounded-xl bg-white/[0.03] border border-white/[0.08] status-ping" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center border border-dashed border-white/[0.1] rounded-2xl bg-[#111827]/40">
              <span className="text-4xl mb-3">📂</span>
              <h3 className="text-white font-bold text-sm mb-1">No Projects Found</h3>
              <p className="text-gray-400 text-xs mb-4">Create your first target project to launch the IDE workspace.</p>
              <button
                onClick={() => router.push("/ide/demo-project")}
                className="gradient-btn px-5 py-2.5 rounded-lg text-xs font-bold text-slate-950">
                Open Demo Workspace →
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {projects.map((p) => (
                <div
                  key={p.id}
                  onClick={() => router.push(`/ide/${p.id}`)}
                  className="glass glass-hover rounded-xl p-5 border border-white/[0.08] flex flex-col justify-between cursor-pointer group">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-sm">
                        📁
                      </span>
                      <span className="text-[10px] font-mono text-gray-500">ID: {p.id.slice(0, 8)}</span>
                    </div>
                    <h3 className="text-white font-bold text-sm mb-1 group-hover:text-amber-400 transition-colors">
                      {p.name}
                    </h3>
                    <p className="text-gray-400 text-xs line-clamp-2 leading-relaxed">
                      {p.description || "Autonomous engineering recovery workspace target."}
                    </p>
                  </div>

                  <button className="w-full mt-5 py-2 rounded text-xs font-bold font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30 group-hover:bg-amber-500 group-hover:text-slate-950 transition-all">
                    Launch IDE Workspace →
                  </button>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
