"use client";

import { useEffect, useState } from "react";

import { AnalyticsPanel } from "@/components/dashboard/panels/analytics-panel";
import { ChatPanel } from "@/components/dashboard/panels/chat-panel";
import { NotesPanel } from "@/components/dashboard/panels/notes-panel";
import { PrivacyPanel } from "@/components/dashboard/panels/privacy-panel";
import { SchedulePanel } from "@/components/dashboard/panels/schedule-panel";
import { SummarizerPanel } from "@/components/dashboard/panels/summarizer-panel";
import { TasksPanel } from "@/components/dashboard/panels/tasks-panel";
import { UploadPanel } from "@/components/dashboard/panels/upload-panel";
import { Sidebar } from "@/components/layout/sidebar";
import { Card } from "@/components/ui/card";
import { AnalyticsPayload, apiRequest } from "@/lib/api";

export type PanelKey =
  | "chat"
  | "notes"
  | "tasks"
  | "schedule"
  | "summarizer"
  | "privacy";

const panelMap: Record<PanelKey, { title: string; description: string }> = {
  chat: {
    title: "Chat Assistant",
    description: "Live local-first chat routed through FastAPI and your Ollama Phi-3 runtime.",
  },
  notes: {
    title: "Notes",
    description: "Create encrypted notes that stay protected at rest in MySQL.",
  },
  tasks: {
    title: "Tasks",
    description: "Manage tasks in real time with encrypted persistence and completion tracking.",
  },
  schedule: {
    title: "Schedule",
    description: "Plan events, deadlines, and meetings in the same private workspace.",
  },
  summarizer: {
    title: "Summarizer",
    description: "Send notes to your local Phi-3 workflow and archive the generated summaries.",
  },
  privacy: {
    title: "Privacy Settings",
    description: "Inspect runtime privacy guarantees, model connectivity, and storage configuration.",
  },
};

export function DashboardShell() {
  const [activePanel, setActivePanel] = useState<PanelKey>("chat");
  const [analytics, setAnalytics] = useState<AnalyticsPayload | null>(null);

  useEffect(() => {
    let cancelled = false;

    apiRequest<AnalyticsPayload>("/analytics")
      .then((payload) => {
        if (cancelled) {
          return;
        }
        setAnalytics(payload);
        if (
          payload.preferred_feature === "schedule" ||
          payload.preferred_feature === "tasks" ||
          payload.preferred_feature === "notes" ||
          payload.preferred_feature === "summarizer" ||
          payload.preferred_feature === "privacy" ||
          payload.preferred_feature === "chat"
        ) {
          setActivePanel(payload.preferred_feature);
        }
      })
      .catch(() => {
        // Keep the dashboard usable even if analytics isn't reachable yet.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section id="dashboard" className="section-shell pt-24">
      <div className="mb-10 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 text-sm uppercase tracking-[0.28em] text-[var(--info)]">
            Interactive dashboard
          </div>
          <h2 className="section-title" style={{ fontFamily: "var(--font-heading)" }}>
            Responsive encrypted workspace
          </h2>
          <p className="mt-4 text-lg muted">
            The new UI now runs against your backend instead of mock browser state,
            with local chat, tasks, notes, schedules, summaries, and behavior analytics.
          </p>
        </div>

        <Card className="flex items-center gap-4 px-5 py-4">
          <div className="h-3 w-3 rounded-full bg-emerald-400" />
          <div>
            <div className="text-sm muted">Local mode status</div>
            <div className="font-semibold">
              {analytics ? `Preferred flow: ${analytics.preferred_feature}` : "Active and secured"}
            </div>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[260px_minmax(0,1fr)_360px]">
        <Sidebar activePanel={activePanel} onSelect={setActivePanel} />

        <div className="min-w-0">
          <Card className="min-h-[720px] p-5 sm:p-6">
            <div className="mb-6 border-b border-white/10 pb-5">
              <div className="text-sm uppercase tracking-[0.24em] text-[var(--accent)]">
                {panelMap[activePanel].title}
              </div>
              <h3 className="mt-2 text-2xl font-semibold">
                {panelMap[activePanel].description}
              </h3>
            </div>

            {activePanel === "chat" && (
              <>
                <UploadPanel />
                <ChatPanel />
              </>
            )}
            {activePanel === "notes" && <NotesPanel />}
            {activePanel === "tasks" && <TasksPanel />}
            {activePanel === "schedule" && <SchedulePanel />}
            {activePanel === "summarizer" && <SummarizerPanel />}
            {activePanel === "privacy" && <PrivacyPanel />}
          </Card>
        </div>

        <AnalyticsPanel initialData={analytics} />
      </div>
    </section>
  );
}
