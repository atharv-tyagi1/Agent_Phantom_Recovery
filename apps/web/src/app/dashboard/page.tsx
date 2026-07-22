"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { ProtectedRoute } from "@/components/protected-route";
import { projectsApi } from "@/lib/api";

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
      <div className="min-h-screen relative overflow-hidden bg-neutral-950">
        {/* Background blobs */}
        <div className="absolute top-[-10%] left-[10%] w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[5%] w-[350px] h-[350px] rounded-full bg-cyan-500/10 blur-[80px] pointer-events-none" />

        {/* Top bar */}
        <header className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-violet-500/30">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z" />
              </svg>
            </div>
            <span className="text-white font-semibold tracking-tight text-lg">Agent Phantom</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-neutral-500 text-sm hidden sm:block">{user?.email}</span>
            <button
              onClick={signOut}
              className="px-4 py-2 rounded-lg text-sm font-medium text-neutral-300 bg-white/[0.05] border border-white/[0.08] hover:bg-white/[0.08] hover:text-white transition-all"
            >
              Sign Out
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="relative z-10 max-w-5xl mx-auto px-8 py-12">
          {/* Hero */}
          <div className="mb-10">
            <h1 className="text-3xl font-semibold text-white tracking-tight mb-2">
              Welcome back
            </h1>
            <p className="text-neutral-400">
              Select a project to open in the Antigravity IDE, or create a new one.
            </p>
          </div>

          {/* Create Project Button */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-medium text-neutral-400 uppercase tracking-wider">
              Your Projects
            </h2>
            <button
              onClick={() => setShowCreate((v) => !v)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-sm font-medium transition-all shadow-lg shadow-violet-500/20"
            >
              <span>+</span> New Project
            </button>
          </div>

          {/* Create Form */}
          {showCreate && (
            <div className="mb-6 backdrop-blur-xl bg-white/[0.04] border border-white/[0.08] rounded-2xl p-5 shadow-xl">
              <h3 className="text-sm font-semibold text-white mb-4">New Project</h3>
              <div className="space-y-3">
                <input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Project name…"
                  className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white placeholder-neutral-600 outline-none focus:ring-1 focus:ring-violet-500/50 transition-all"
                />
                <input
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Description (optional)…"
                  className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white placeholder-neutral-600 outline-none focus:ring-1 focus:ring-violet-500/50 transition-all"
                />
                <div className="flex gap-3">
                  <button
                    onClick={createProject}
                    disabled={creating || !newName.trim()}
                    className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-all"
                  >
                    {creating ? "Creating…" : "Create"}
                  </button>
                  <button
                    onClick={() => setShowCreate(false)}
                    className="px-5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-neutral-400 text-sm hover:text-white transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Project Cards */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-40 rounded-2xl bg-white/[0.02] border border-white/[0.05] animate-pulse" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <span className="text-5xl">👻</span>
              <div className="text-center">
                <p className="text-white font-medium">No projects yet</p>
                <p className="text-neutral-500 text-sm mt-1">Create your first project to get started</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="group backdrop-blur-xl bg-white/[0.03] border border-white/[0.06] rounded-2xl p-5 hover:bg-white/[0.05] hover:border-white/[0.1] hover:shadow-lg hover:shadow-violet-500/5 transition-all cursor-pointer"
                  onClick={() => router.push(`/ide/${project.id}`)}
                >
                  {/* Icon */}
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600/20 to-cyan-500/20 border border-white/[0.07] flex items-center justify-center mb-4">
                    <span className="text-lg">📂</span>
                  </div>

                  <h3 className="text-white font-semibold group-hover:text-violet-300 transition-colors text-sm mb-1 line-clamp-1">
                    {project.name}
                  </h3>
                  {project.description && (
                    <p className="text-neutral-500 text-xs line-clamp-2 mb-4">{project.description}</p>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/ide/${project.id}`);
                    }}
                    className="w-full mt-auto py-2 rounded-xl bg-white/[0.04] border border-white/[0.07] text-xs font-medium text-neutral-400 group-hover:bg-violet-600/20 group-hover:border-violet-500/30 group-hover:text-violet-300 transition-all"
                  >
                    Open in IDE →
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
