"use client";

import { ComponentType } from "react";

import { PanelKey } from "@/components/dashboard/dashboard-shell";
import { Card } from "@/components/ui/card";
import {
  ChatIcon,
  NotesIcon,
  SettingsIcon,
  SummaryIcon,
  TaskIcon,
} from "@/components/ui/icons";

const items: Array<{ key: PanelKey; label: string; icon: ComponentType<any> }> = [
  { key: "chat", label: "Chat Assistant", icon: ChatIcon },
  { key: "notes", label: "Notes", icon: NotesIcon },
  { key: "tasks", label: "Tasks", icon: TaskIcon },
  { key: "schedule", label: "Schedule", icon: SummaryIcon },
  { key: "summarizer", label: "Summarizer", icon: SummaryIcon },
  { key: "privacy", label: "Privacy Settings", icon: SettingsIcon },
];

export function Sidebar({
  activePanel,
  onSelect,
}: {
  activePanel: PanelKey;
  onSelect: (panel: PanelKey) => void;
}) {
  return (
    <Card className="h-fit p-4">
      <div className="mb-4 text-sm uppercase tracking-[0.24em] text-[var(--info)]">
        Workspace
      </div>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = item.key === activePanel;

          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onSelect(item.key)}
              className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-left transition ${
                isActive
                  ? "bg-gradient-to-r from-[var(--accent-soft)] to-white/5 text-text"
                  : "bg-transparent text-text/80 hover:bg-white/5"
              }`}
            >
              <span
                className={`rounded-xl p-2 ${
                  isActive ? "bg-white/10 text-[var(--accent)]" : "bg-white/5 text-[var(--info)]"
                }`}
              >
                <Icon className="h-5 w-5" />
              </span>
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </Card>
  );
}
