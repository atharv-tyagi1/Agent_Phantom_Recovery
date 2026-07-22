import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Inject Supabase auth token on every request
api.interceptors.request.use(async (config) => {
  if (typeof window !== "undefined") {
    const { createClient } = await import("@/lib/supabase");
    const supabase = createClient();
    const { data } = await supabase.auth.getSession();
    if (data?.session?.access_token) {
      config.headers.Authorization = `Bearer ${data.session.access_token}`;
    }
  }
  return config;
});

// ── Projects ─────────────────────────────────────────────────────────────────
export const projectsApi = {
  list: () => api.get("/projects"),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post("/projects", data),
};

// ── Repositories ──────────────────────────────────────────────────────────────
export const reposApi = {
  list: (projectId: string) => api.get(`/projects/${projectId}/repositories`),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────
export const tasksApi = {
  list: (projectId: string) => api.get(`/projects/${projectId}/tasks`),
  create: (projectId: string, data: { title: string; description?: string }) =>
    api.post(`/projects/${projectId}/tasks`, data),
};

// ── Executions ────────────────────────────────────────────────────────────────
export const executionsApi = {
  create: (taskId: string) =>
    api.post(`/tasks/${taskId}/executions`, {}),
  list: (taskId: string) => api.get(`/tasks/${taskId}/executions`),
  get: (taskId: string, execId: string) =>
    api.get(`/tasks/${taskId}/executions/${execId}`),
};

// ── Memory ────────────────────────────────────────────────────────────────────
export const memoryApi = {
  getSession: (executionId: string) =>
    api.get(`/memory/session/${executionId}`),
  getProjectFacts: (projectId: string) =>
    api.get(`/memory/project/${projectId}/facts`),
  searchExperiences: (tags: string[]) =>
    api.get("/memory/experiences/search", { params: { tags: tags.join(",") } }),
};

// ── Repo Intel ────────────────────────────────────────────────────────────────
export const repoIntelApi = {
  search: (repositoryId: string, query: string) =>
    api.get(`/repo-intel/${repositoryId}/search`, { params: { query } }),
};

export default api;
