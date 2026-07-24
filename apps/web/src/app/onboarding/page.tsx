"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { workspacesApi, githubAppApi, projectsApi, monitoringApi } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [workspaceName, setWorkspaceName] = useState("My Recovery Workspace");
  const [workspaceId, setWorkspaceId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [installationId, setInstallationId] = useState<number | null>(null);
  const [repos, setRepos] = useState<any[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<any | null>(null);
  const [monitoringMode, setMonitoringMode] = useState("auto_investigate");
  const [loading, setLoading] = useState(false);

  // Step 1: Create Workspace
  const handleCreateWorkspace = async () => {
    setLoading(true);
    try {
      const wsRes = await workspacesApi.create({ name: workspaceName });
      const wsId = wsRes.data.id;
      setWorkspaceId(wsId);

      const projRes = await projectsApi.create({ name: `${workspaceName} Default Project` });
      setProjectId(projRes.data.id);

      setStep(2);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Install GitHub App
  const handleInstallApp = async () => {
    try {
      const res = await githubAppApi.getInstallUrl(workspaceId);
      if (res.data?.url) {
        window.open(res.data.url, "_blank");
      }
      // Demo mock installation id for setup
      setInstallationId(999888);
      setStep(3);
    } catch (e) {
      console.error(e);
      setInstallationId(999888);
      setStep(3);
    }
  };

  // Step 3: Fetch Installation Repos
  useEffect(() => {
    if (step === 3 && installationId) {
      githubAppApi.getInstallationRepos(installationId)
        .then((res) => {
          setRepos(res.data || []);
          if (res.data?.length > 0) {
            setSelectedRepo(res.data[0]);
          }
        })
        .catch((err) => console.error(err));
    }
  }, [step, installationId]);

  // Step 4: Connect & Launch
  const handleCompleteOnboarding = async () => {
    setLoading(true);
    try {
      if (selectedRepo && installationId) {
        const connRes = await githubAppApi.connectRepo(installationId, {
          project_id: projectId,
          github_repo_id: selectedRepo.id,
          name: selectedRepo.name,
          full_name: selectedRepo.full_name || selectedRepo.name,
          git_url: selectedRepo.html_url || "https://github.com/agent-phantom/demo-repo",
          default_branch: selectedRepo.default_branch || "main"
        });

        const repoId = connRes.data.repository_id;
        await monitoringApi.update(repoId, { mode: monitoringMode });
      }
      router.push(`/ide/${projectId || "demo-project"}`);
    } catch (e) {
      console.error(e);
      router.push(`/ide/demo-project`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-[#e5e2e1] flex flex-col items-center justify-center p-6">
      <div className="glass-panel w-full max-w-2xl p-8 rounded-2xl border border-[#ffb000]/30 shadow-2xl relative overflow-hidden">
        {/* Progress Bar */}
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-[#524533]/30 font-mono text-xs text-[#d7c4ac]">
          <span className={step >= 1 ? "text-[#ffb000] font-bold" : ""}>1. Workspace</span>
          <span>→</span>
          <span className={step >= 2 ? "text-[#ffb000] font-bold" : ""}>2. GitHub App</span>
          <span>→</span>
          <span className={step >= 3 ? "text-[#ffb000] font-bold" : ""}>3. Choose Repo</span>
          <span>→</span>
          <span className={step >= 4 ? "text-[#ffb000] font-bold" : ""}>4. Launch IDE</span>
        </div>

        {/* STEP 1 */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-[#e5e2e1] mb-2">Create Workspace</h2>
              <p className="text-xs text-[#d7c4ac]">Workspaces house your repositories, policy controls, and team members.</p>
            </div>
            <div>
              <label className="block text-xs font-mono text-[#d7c4ac] mb-2">WORKSPACE NAME</label>
              <input
                type="text"
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                className="w-full bg-[#131313] border border-[#524533]/40 rounded p-3 text-sm text-[#e5e2e1] focus:border-[#ffb000] outline-none"
              />
            </div>
            <button
              onClick={handleCreateWorkspace}
              disabled={loading}
              className="w-full bg-[#ffb000] text-[#6a4700] p-3 rounded font-mono font-bold text-xs uppercase tracking-wider glow-amber hover:bg-[#ffddaf] transition-all cursor-pointer"
            >
              {loading ? "Creating..." : "Continue →"}
            </button>
          </div>
        )}

        {/* STEP 2 */}
        {step === 2 && (
          <div className="space-y-6 text-center">
            <div className="w-16 h-16 bg-[#ffb000]/10 border border-[#ffb000]/30 rounded-full flex items-center justify-center mx-auto text-3xl">
              ⚙️
            </div>
            <div>
              <h2 className="text-2xl font-bold text-[#e5e2e1] mb-2">Install Agent Phantom GitHub App</h2>
              <p className="text-xs text-[#d7c4ac] max-w-md mx-auto">
                Automation Layer require installation permissions for webhooks, push events, checks, and PR creation.
              </p>
            </div>
            <div className="p-4 bg-[#1c1b1b] rounded-lg text-left text-xs font-mono text-[#d7c4ac] space-y-2">
              <div className="text-[#45d79c]">✔ Webhooks &amp; Push Monitoring</div>
              <div className="text-[#45d79c]">✔ Automatic Code Recovery &amp; Checks</div>
              <div className="text-[#45d79c]">✔ Automated Pull Request Creation</div>
            </div>
            <button
              onClick={handleInstallApp}
              className="w-full bg-[#ffb000] text-[#6a4700] p-3 rounded font-mono font-bold text-xs uppercase tracking-wider glow-amber hover:bg-[#ffddaf] transition-all cursor-pointer"
            >
              Install GitHub App &amp; Continue →
            </button>
          </div>
        )}

        {/* STEP 3 */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-[#e5e2e1] mb-2">Select Repository &amp; Monitoring Mode</h2>
              <p className="text-xs text-[#d7c4ac]">Choose repository and set your autonomous recovery trigger policy.</p>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#d7c4ac] mb-2">REPOSITORY</label>
              <select
                onChange={(e) => {
                  const r = repos.find((repo) => repo.id === Number(e.target.value));
                  if (r) setSelectedRepo(r);
                }}
                className="w-full bg-[#131313] border border-[#524533]/40 rounded p-3 text-sm text-[#e5e2e1] focus:border-[#ffb000] outline-none"
              >
                {repos.map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.full_name || repo.name} ({repo.default_branch || "main"})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#d7c4ac] mb-2">AUTOMATION MODE</label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: "auto_investigate", title: "Auto Investigate", desc: "Scan diffs & run verifier" },
                  { id: "auto_fix", title: "Auto Fix", desc: "Apply verified code patches" },
                  { id: "auto_pr", title: "Auto PR", desc: "Open PR on completion" },
                  { id: "suggest", title: "Suggest Only", desc: "Generate report only" },
                ].map((m) => (
                  <div
                    key={m.id}
                    onClick={() => setMonitoringMode(m.id)}
                    className={`p-3 rounded border cursor-pointer transition-all ${
                      monitoringMode === m.id
                        ? "border-[#ffb000] bg-[#ffb000]/10 text-[#ffb000]"
                        : "border-[#524533]/30 bg-[#131313] text-[#d7c4ac]"
                    }`}
                  >
                    <div className="font-bold text-xs">{m.title}</div>
                    <div className="text-[10px] opacity-80">{m.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleCompleteOnboarding}
              disabled={loading}
              className="w-full bg-[#ffb000] text-[#6a4700] p-3 rounded font-mono font-bold text-xs uppercase tracking-wider glow-amber hover:bg-[#ffddaf] transition-all cursor-pointer"
            >
              {loading ? "Initializing..." : "Launch Antigravity IDE Workspace →"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
