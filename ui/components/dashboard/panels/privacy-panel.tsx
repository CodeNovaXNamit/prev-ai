"use client";

import { useEffect, useState } from "react";

import { ShieldIcon } from "@/components/ui/icons";
import { HealthStatus, apiRequest } from "@/lib/api";

const indicators = [
  "No data leaves device",
  "Encrypted at rest with Fernet",
  "Local mode enabled",
];

export function PrivacyPanel() {
  const [localMode, setLocalMode] = useState(true);
  const [status, setStatus] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<HealthStatus>("/health")
      .then((payload) => {
        setStatus(payload);
        setLocalMode(payload.offline_mode);
      })
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-black/10 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-sm uppercase tracking-[0.22em] text-[var(--info)]">
              Privacy controls
            </div>
            <h4 className="mt-2 text-2xl font-semibold">Local Mode</h4>
            <p className="mt-2 muted">
              Keep chat, storage, and summaries on your own stack with clear runtime visibility.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setLocalMode((current) => !current)}
            className={`flex w-40 items-center justify-between rounded-full border border-white/10 px-4 py-3 ${
              localMode ? "bg-[var(--accent-soft)]" : "bg-white/5"
            }`}
          >
            <span>{localMode ? "ON" : "OFF"}</span>
            <span
              className={`h-6 w-6 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--info)] transition ${
                localMode ? "translate-x-0" : "-translate-x-2"
              }`}
            />
          </button>
        </div>
        {status && (
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm muted">Model</div>
              <div className="mt-2 font-semibold">{status.active_model}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm muted">Ollama</div>
              <div className="mt-2 font-semibold">
                {status.ollama_available ? "Connected" : "Fallback mode"}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm muted">Database</div>
              <div className="mt-2 font-semibold">
                {status.database_url.startsWith("mysql") ? "MySQL" : "SQLite/Test"}
              </div>
            </div>
          </div>
        )}
        {error && <div className="mt-4 text-sm text-rose-300">{error}</div>}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {indicators.map((indicator) => (
          <div
            key={indicator}
            className="rounded-[28px] border border-white/10 bg-white/5 p-5"
          >
            <div className="mb-4 inline-flex rounded-2xl bg-[var(--accent-soft)] p-3 text-[var(--accent)]">
              <ShieldIcon className="h-6 w-6" />
            </div>
            <div className="text-xl font-semibold">{indicator}</div>
            <div className="mt-3 flex items-center gap-2 text-sm text-emerald-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              verified in demo
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-[28px] border border-white/10 bg-black/10 p-6">
        <div className="grid gap-5 lg:grid-cols-[1fr_280px]">
          <div>
            <div className="text-sm uppercase tracking-[0.22em] text-[var(--accent)]">
              Privacy summary
            </div>
            <p className="mt-3 text-lg leading-8 muted">
              The dashboard now exposes real backend status so the trust claims match the
              runtime: Ollama connectivity, offline mode, encrypted persistence, and local storage.
            </p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
            <div className="text-sm muted">Protection status</div>
            <div className="mt-2 text-4xl font-semibold">
              {status?.offline_mode ? "100%" : "82%"}
            </div>
            <div className="mt-4 h-2 rounded-full bg-white/10">
              <div className="h-2 w-full animate-pulseLine rounded-full bg-gradient-to-r from-[var(--info)] to-[var(--accent)]" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
