"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { WaveIcon } from "@/components/ui/icons";
import { AnalyticsPayload, apiRequest } from "@/lib/api";

const fallbackAnalytics: AnalyticsPayload = {
  sessions: 0,
  tasks_completed_percent: 0,
  saved_notes: 0,
  scheduled_events: 0,
  weekly_activity: [0, 0, 0, 0, 0, 0, 0],
  completion_series: [0, 0, 0, 0, 0, 0, 0],
  timeline: [{ title: "Awaiting backend data", time: "00:00", status: "idle" }],
  preferred_feature: "chat",
};

function buildPath(data: number[]) {
  const width = 320;
  const height = 120;
  const step = width / (data.length - 1);

  return data
    .map((value, index) => {
      const x = index * step;
      const y = height - (value / 100) * height;
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}

export function AnalyticsPanel({
  initialData,
}: {
  initialData?: AnalyticsPayload | null;
}) {
  const [analytics, setAnalytics] = useState<AnalyticsPayload>(initialData ?? fallbackAnalytics);

  useEffect(() => {
    if (initialData) {
      setAnalytics(initialData);
    }
  }, [initialData]);

  useEffect(() => {
    apiRequest<AnalyticsPayload>("/analytics")
      .then((payload) => setAnalytics(payload))
      .catch(() => {
        // Keep fallback analytics visible if the backend is offline.
      });
  }, []);

  const usagePath = buildPath(analytics.weekly_activity);
  const completionPath = buildPath(analytics.completion_series);

  return (
    <div className="space-y-6">
      <Card className="p-5">
        <div className="text-sm uppercase tracking-[0.22em] text-[var(--info)]">
          Usage stats
        </div>
        <div className="mt-5 grid grid-cols-2 gap-4">
          {[
            { label: "Sessions", value: analytics.sessions.toString() },
            { label: "Tasks done", value: `${analytics.tasks_completed_percent}%` },
            { label: "Notes saved", value: analytics.saved_notes.toString() },
            { label: "Events", value: analytics.scheduled_events.toString() },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-[24px] border border-white/10 bg-white/5 p-4"
            >
              <div className="text-sm muted">{stat.label}</div>
              <div className="mt-2 text-2xl font-semibold">{stat.value}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm uppercase tracking-[0.22em] text-[var(--accent)]">
              AI usage graph
            </div>
            <div className="mt-1 text-xl font-semibold">Weekly activity</div>
          </div>
          <div className="text-sm text-emerald-400">{analytics.preferred_feature}</div>
        </div>
        <div className="mt-6 rounded-[24px] border border-white/10 bg-black/10 p-4">
          <svg viewBox="0 0 320 140" className="h-40 w-full">
            <defs>
              <linearGradient id="usageLine" x1="0%" x2="100%" y1="0%" y2="0%">
                <stop offset="0%" stopColor="var(--info)" />
                <stop offset="100%" stopColor="var(--accent)" />
              </linearGradient>
            </defs>
            {[0, 1, 2, 3].map((line) => (
              <line
                key={line}
                x1="0"
                x2="320"
                y1={20 + line * 30}
                y2={20 + line * 30}
                stroke="rgba(255,255,255,0.08)"
                strokeDasharray="4 6"
              />
            ))}
            <path d={`${usagePath} L 320 140 L 0 140 Z`} fill="url(#usageArea)" />
            <defs>
              <linearGradient id="usageArea" x1="0%" x2="0%" y1="0%" y2="100%">
                <stop offset="0%" stopColor="rgba(73,180,255,0.28)" />
                <stop offset="100%" stopColor="rgba(73,180,255,0.02)" />
              </linearGradient>
            </defs>
            <path
              d={usagePath}
              fill="none"
              stroke="url(#usageLine)"
              strokeWidth="4"
              strokeLinecap="round"
            />
            {analytics.weekly_activity.map((value, index) => {
              const x = index * (320 / (analytics.weekly_activity.length - 1));
              const y = 120 - (value / 100) * 120;
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="4.5"
                  fill="var(--bg)"
                  stroke="var(--accent)"
                  strokeWidth="3"
                />
              );
            })}
          </svg>
          <div className="mt-3 flex justify-between text-xs muted">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
              <span key={day}>{day}</span>
            ))}
          </div>
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm uppercase tracking-[0.22em] text-[var(--info)]">
              Tracker intelligence
            </div>
            <div className="mt-1 text-xl font-semibold">Completion and momentum</div>
          </div>
          <WaveIcon className="h-6 w-6 text-[var(--info)]" />
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/5 p-4">
            <div className="text-sm muted">Task completion arc</div>
            <svg viewBox="0 0 320 140" className="mt-3 h-32 w-full">
              <path
                d={completionPath}
                fill="none"
                stroke="rgba(255,255,255,0.14)"
                strokeWidth="10"
                strokeLinecap="round"
              />
              <path
                d={completionPath}
                fill="none"
                stroke="url(#completionLine)"
                strokeWidth="6"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="completionLine" x1="0%" x2="100%" y1="0%" y2="0%">
                  <stop offset="0%" stopColor="var(--accent)" />
                  <stop offset="100%" stopColor="var(--info)" />
                </linearGradient>
              </defs>
            </svg>
            <div className="mt-2 flex justify-between text-xs muted">
              <span>Focused sprint</span>
              <span>91% peak</span>
            </div>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/5 p-4">
            <div className="text-sm muted">System tracker</div>
            <div className="mt-4 space-y-4">
              {[
                { label: "Private context sync", value: Math.min(100, analytics.sessions * 10) },
                { label: "Task orchestration", value: analytics.tasks_completed_percent },
                { label: "Summary pipeline", value: Math.min(100, analytics.saved_notes * 12) },
              ].map((item) => (
                <div key={item.label}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span>{item.label}</span>
                    <span className="text-[var(--info)]">{item.value}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-black/20">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--info)]"
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-5">
        <div className="text-sm uppercase tracking-[0.22em] text-[var(--info)]">
          Timeline tracker
        </div>
        <div className="mt-5 space-y-4">
          {analytics.timeline.map((item) => (
            <div key={item.title} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className="mt-1 h-3 w-3 rounded-full bg-[var(--accent)]" />
                <div className="h-full w-px bg-white/10" />
              </div>
              <div className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="text-sm muted">{item.time}</div>
                  <div className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[var(--info)]">
                    {item.status}
                  </div>
                </div>
                <div className="mt-2 font-medium">{item.title}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
