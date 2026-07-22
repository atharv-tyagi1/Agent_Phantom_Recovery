import { useState, useEffect, useCallback } from "react";
import { memoryApi } from "@/lib/api";

export interface MemoryData {
  sessionEvents: object[];
  projectFacts: Record<string, unknown>;
  experiences: object[];
  loading: boolean;
}

export function useMemory(executionId?: string, projectId?: string): MemoryData {
  const [sessionEvents, setSessionEvents] = useState<object[]>([]);
  const [projectFacts, setProjectFacts] = useState<Record<string, unknown>>({});
  const [experiences, setExperiences] = useState<object[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchMemory = useCallback(async () => {
    if (!executionId && !projectId) return;
    setLoading(true);
    try {
      if (executionId) {
        const res = await memoryApi.getSession(executionId);
        setSessionEvents(res.data?.events ?? []);
      }
      if (projectId) {
        const res = await memoryApi.getProjectFacts(projectId);
        setProjectFacts(res.data?.facts ?? {});
      }
    } catch {
      // silently fail in development
    } finally {
      setLoading(false);
    }
  }, [executionId, projectId]);

  useEffect(() => {
    fetchMemory();
    const interval = setInterval(fetchMemory, 5000);
    return () => clearInterval(interval);
  }, [fetchMemory]);

  return { sessionEvents, projectFacts, experiences, loading };
}
