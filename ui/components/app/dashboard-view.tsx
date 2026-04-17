"use client";

import { useEffect, useState } from "react";

import { SystemStatusResponse, apiRequest } from "@/lib/api";

export function DashboardView() {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<SystemStatusResponse>("/system/status")
      .then(setStatus)
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  return (
    <section className="stack-lg">
      <div className="panel">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-copy">
          Model health, database connectivity, backend checks, and the latest automated test results.
        </p>
      </div>
      {error && <div className="error-text">{error}</div>}
      {status && (
        <>
          <div className="grid-two">
            <div className="panel stack-sm">
              <div className="item-title">Model</div>
              <div className="meta-row">
                <span>{status.health.active_model}</span>
                <span className={status.health.ollama_available ? "status-ok" : "status-pending"}>
                  {status.health.ollama_available ? "connected" : "fallback"}
                </span>
              </div>
              <div className="muted-text">{status.health.database_url}</div>
            </div>
            <div className="panel stack-sm">
              <div className="item-title">Counts</div>
              <div className="meta-row"><span>Tasks</span><span>{status.total_tasks}</span></div>
              <div className="meta-row"><span>Summaries</span><span>{status.total_summaries}</span></div>
              <div className="meta-row"><span>Events</span><span>{status.total_events}</span></div>
            </div>
          </div>

          <div className="panel stack-sm">
            <div className="item-title">System Checks</div>
            {status.checks.map((check) => (
              <div key={check.name} className="row-between">
                <div>
                  <div>{check.name}</div>
                  <div className="muted-text">{check.detail}</div>
                </div>
                <div className={check.status === "ok" ? "status-ok" : "status-pending"}>
                  {check.status}
                </div>
              </div>
            ))}
          </div>

          <div className="panel stack-sm">
            <div className="item-title">Latest Test Results</div>
            {status.latest_test_results.map((test) => (
              <div key={test.name} className="row-between">
                <div>
                  <div>{test.name}</div>
                  <div className="muted-text">{test.detail}</div>
                </div>
                <div className={test.status === "passed" ? "status-ok" : "status-pending"}>
                  {test.status}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
