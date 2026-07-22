"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
} from "react";
import { tasksApi, executionsApi } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────
export type ExecutionStatus =
  | "INITIALIZING"
  | "PLANNING"
  | "INVESTIGATING"
  | "EXECUTING"
  | "VERIFYING"
  | "REVIEWING"
  | "RE_PLANNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "IDLE";

export interface SessionEvent {
  type: string;
  step?: number;
  content?: string;
  tool_name?: string;
  success?: boolean;
  output?: string;
  error?: string;
  approved?: boolean;
  quality_score?: number;
  rejection_reason?: string;
  actionable_fix?: string;
  summary?: string;
  status?: string;
  timestamp?: string;
}

export interface ExecutionSnapshot {
  execution_id: string;
  task_id: string;
  status: ExecutionStatus;
  current_step: number;
  max_steps: number;
  modified_files: string[];
  rejection_count: number;
  quality_score?: number;
  working_memory?: Record<string, unknown>;
  checkpoint_hashes?: string[];
}

interface ExecutionContextValue {
  snapshot: ExecutionSnapshot | null;
  sessionEvents: SessionEvent[];
  wsStatus: "connected" | "disconnected";
  isRunning: boolean;
  startExecution: (projectId: string, taskPrompt: string) => Promise<void>;
  resetExecution: () => void;
}

// ── Context ───────────────────────────────────────────────────────────────────
const ExecutionContext = createContext<ExecutionContextValue | null>(null);

export function ExecutionProvider({
  children,
  projectId,
}: {
  children: React.ReactNode;
  projectId: string;
}) {
  const [snapshot, setSnapshot] = useState<ExecutionSnapshot | null>(null);
  const [sessionEvents, setSessionEvents] = useState<SessionEvent[]>([]);
  const [wsStatus, setWsStatus] = useState<"connected" | "disconnected">("disconnected");
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = useCallback((executionId: string) => {
    const wsUrl =
      (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
        /^http/,
        "ws"
      ) + `/ws/executions/${executionId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("connected");
    };

    ws.onmessage = (evt) => {
      try {
        const event: SessionEvent = JSON.parse(evt.data);
        setSessionEvents((prev) => [...prev, event]);

        // Update snapshot based on state_change events
        if (event.type === "state_change" && event.status) {
          setSnapshot((prev) =>
            prev ? { ...prev, status: event.status as ExecutionStatus } : prev
          );
        }

        // Detect terminal state
        if (
          event.type === "stream_end" ||
          ["COMPLETED", "FAILED", "CANCELLED"].includes(event.status || "")
        ) {
          setIsRunning(false);
        }

        // Track quality score from audit events
        if (event.type === "global_review_audit" && event.quality_score != null) {
          setSnapshot((prev) =>
            prev ? { ...prev, quality_score: event.quality_score } : prev
          );
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setWsStatus("disconnected");
      setIsRunning(false);
    };

    ws.onerror = () => {
      setWsStatus("disconnected");
    };
  }, []);

  const startExecution = useCallback(
    async (projId: string, taskPrompt: string) => {
      setIsRunning(true);
      setSessionEvents([]);
      setSnapshot(null);

      // 1. Create a task
      const taskRes = await tasksApi.create(projId, {
        title: taskPrompt.slice(0, 80),
        description: taskPrompt,
      });
      const task = taskRes.data;

      // 2. Create an execution
      const execRes = await executionsApi.create(task.id);
      const execution = execRes.data;

      // 3. Set initial snapshot
      setSnapshot({
        execution_id: execution.id,
        task_id: task.id,
        status: "INITIALIZING",
        current_step: 0,
        max_steps: 15,
        modified_files: [],
        rejection_count: 0,
      });

      // 4. Connect WebSocket stream
      connectWebSocket(execution.id);
    },
    [connectWebSocket]
  );

  const resetExecution = useCallback(() => {
    wsRef.current?.close();
    setSnapshot(null);
    setSessionEvents([]);
    setIsRunning(false);
    setWsStatus("disconnected");
  }, []);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  return (
    <ExecutionContext.Provider
      value={{ snapshot, sessionEvents, wsStatus, isRunning, startExecution, resetExecution }}
    >
      {children}
    </ExecutionContext.Provider>
  );
}

export function useExecution(): ExecutionContextValue {
  const ctx = useContext(ExecutionContext);
  if (!ctx) throw new Error("useExecution must be used within ExecutionProvider");
  return ctx;
}
