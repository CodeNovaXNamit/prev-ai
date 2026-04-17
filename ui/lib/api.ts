export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Task = {
  id: string;
  title: string;
  description: string;
  due_date: string | null;
  priority: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
};

export type CalendarEvent = {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  location: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type Note = {
  id: string;
  title: string;
  note_text: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
};

export type HealthStatus = {
  app_name: string;
  offline_mode: boolean;
  ollama_available: boolean;
  database_url: string;
  active_model: string;
};

export type ChatResponse = {
  response: string;
  source: string;
  created_tasks: Array<{ id: string; title: string }>;
};

export type AnalyticsPayload = {
  sessions: number;
  tasks_completed_percent: number;
  saved_notes: number;
  scheduled_events: number;
  weekly_activity: number[];
  completion_series: number[];
  timeline: Array<{ title: string; time: string; status: string }>;
  preferred_feature: string;
};

export type SystemCheckResult = {
  name: string;
  status: string;
  detail: string;
};

export type SystemStatusResponse = {
  health: HealthStatus;
  database_connected: boolean;
  total_tasks: number;
  total_summaries: number;
  total_events: number;
  checks: SystemCheckResult[];
  latest_test_results: SystemCheckResult[];
};

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {}
    throw new Error(message);
  }

  return (await response.json()) as T;
}
