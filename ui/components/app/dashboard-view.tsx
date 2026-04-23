"use client";

import { useEffect, useState } from "react";

import {
  AnalyticsPayload,
  CalendarEvent,
  Note,
  SystemStatusResponse,
  Task,
  apiRequest,
} from "@/lib/api";
import { fakeCipher, formatRelativeDate } from "@/components/app/format";
import { WorkspaceShell } from "@/components/app/workspace-shell";

export function DashboardView() {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsPayload | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [summaries, setSummaries] = useState<Note[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    Promise.all([
      apiRequest<SystemStatusResponse>("/system/status"),
      apiRequest<AnalyticsPayload>("/analytics"),
      apiRequest<Task[]>("/tasks"),
      apiRequest<Note[]>("/summaries"),
      apiRequest<CalendarEvent[]>("/events"),
    ])
      .then(([systemStatus, analyticsPayload, taskPayload, summaryPayload, eventPayload]) => {
        setStatus(systemStatus);
        setAnalytics(analyticsPayload);
        setTasks(taskPayload);
        setSummaries(summaryPayload);
        setEvents(eventPayload);
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    load();
  }, []);

  const previewTask = tasks[0]?.title || "No tasks stored yet";
  const previewSummary = summaries[0]?.summary || "No summaries stored yet";
  const previewEvent = events[0]?.title || "No events stored yet";

  return (
    <WorkspaceShell
      title="Dashboard"
      description="Model health, analytics, database connectivity, and a clear view into what the backend is storing for your local assistant."
      actions={
        <button type="button" className="button button-secondary" onClick={load}>
          Refresh
        </button>
      }
    >
      {error ? (
        <div className="feedback-banner feedback-banner-error">
          <div>
            <strong className="error-text">Dashboard load failed</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : null}
      {status ? (
        <>
          <section className="workspace-grid workspace-grid-dashboard-top reveal stagger-1">
            <article className="app-card">
              <div className="app-card-heading">
                <div>
                  <span className="eyebrow">Model</span>
                  <h2>Local runtime</h2>
                </div>
                <span className="status-chip">
                  <span className="status-dot" />
                  {status.health.model_runner_available ? "connected" : "fallback"}
                </span>
              </div>
              <div className="info-rows">
                <div className="info-row">
                  <span>Model</span>
                  <strong>{status.health.active_model}</strong>
                </div>
                <div className="info-row">
                  <span>Database</span>
                  <strong>{status.database_connected ? "connected" : "degraded"}</strong>
                </div>
                <div className="info-row">
                  <span>Mode</span>
                  <strong>{status.health.offline_mode ? "offline-first" : "network-enabled"}</strong>
                </div>
              </div>
            </article>

            <article className="app-card">
              <div className="app-card-heading">
                <div>
                  <span className="eyebrow">Counts</span>
                  <h2>Saved locally</h2>
                </div>
              </div>
              <div className="metric-strip">
                <div className="mini-metric">
                  <strong>{status.total_tasks}</strong>
                  <span>Tasks</span>
                </div>
                <div className="mini-metric">
                  <strong>{status.total_summaries}</strong>
                  <span>Summaries</span>
                </div>
                <div className="mini-metric">
                  <strong>{status.total_events}</strong>
                  <span>Events</span>
                </div>
              </div>
            </article>
          </section>

          <section className="workspace-grid workspace-grid-dashboard-bottom reveal stagger-2">
            <article className="app-card">
              <div className="app-card-heading">
                <div>
                  <span className="eyebrow">Checks</span>
                  <h2>Backend and privacy state</h2>
                </div>
              </div>
              <div className="check-list">
                {status.checks.map((check) => (
                  <div key={check.name} className="check-row">
                    <div>
                      <strong>{check.name}</strong>
                      <p>{check.detail}</p>
                    </div>
                    <span className={check.status === "ok" ? "status-ok" : "status-pending"}>{check.status}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="app-card privacy-preview-card">
              <div className="app-card-heading">
                <div>
                  <span className="eyebrow">Protected payloads</span>
                  <h2>Readable vs stored shape</h2>
                </div>
              </div>
              <div className="privacy-preview-grid">
                <div className="preview-column">
                  <strong>Readable</strong>
                  <code>{previewTask}</code>
                  <code>{previewSummary}</code>
                  <code>{previewEvent}</code>
                </div>
                <div className="preview-column">
                  <strong>Protected preview</strong>
                  <code>{fakeCipher(previewTask)}</code>
                  <code>{fakeCipher(previewSummary)}</code>
                  <code>{fakeCipher(previewEvent)}</code>
                </div>
              </div>
              <span className="muted-text">
                The API returns decrypted values for use in the UI. Encryption-at-rest is verified by backend checks.
              </span>
            </article>
          </section>

          <section className="app-card reveal stagger-3">
            <div className="app-card-heading">
              <div>
                <span className="eyebrow">Activity</span>
                <h2>Usage snapshot</h2>
              </div>
            </div>
            <div className="metric-strip">
              <div className="mini-metric">
                <strong>{analytics?.sessions ?? 0}</strong>
                <span>Sessions</span>
              </div>
              <div className="mini-metric">
                <strong>{analytics?.tasks_completed_percent ?? 0}%</strong>
                <span>Task completion</span>
              </div>
              <div className="mini-metric">
                <strong>{analytics?.preferred_feature ?? "n/a"}</strong>
                <span>Preferred feature</span>
              </div>
            </div>
            <div className="timeline-list">
              {(analytics?.timeline ?? []).map((entry) => (
                <div key={entry.id} className="timeline-item">
                  <div>
                    <strong>{entry.title}</strong>
                    <p className="muted-text">{entry.status}</p>
                  </div>
                  <span>{entry.time}</span>
                </div>
              ))}
              {(analytics?.timeline ?? []).length === 0 ? <div className="empty-state">No analytics timeline available yet.</div> : null}
            </div>
          </section>

          <section className="app-card reveal stagger-4">
            <div className="app-card-heading">
              <div>
                <span className="eyebrow">Latest test results</span>
                <h2>Backend verification</h2>
              </div>
            </div>
            <div className="check-list">
              {status.latest_test_results.map((test) => (
                <div key={test.name} className="check-row">
                  <div>
                    <strong>{test.name}</strong>
                    <p>{test.detail}</p>
                  </div>
                  <span className={test.status === "passed" ? "status-ok" : "status-pending"}>{test.status}</span>
                </div>
              ))}
            </div>
            {events[0] ? (
              <div className="note-summary-box">
                <strong>Next event</strong>
                <p>
                  {events[0].title} - {formatRelativeDate(events[0].start_time)}
                </p>
              </div>
            ) : null}
          </section>
        </>
      ) : (
        <div className="empty-state">Loading dashboard...</div>
      )}
    </WorkspaceShell>
  );
}
