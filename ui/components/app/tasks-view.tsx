"use client";

import { useEffect, useState } from "react";

import { Task, apiRequest } from "@/lib/api";

export function TasksView() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = () => {
    apiRequest<Task[]>("/tasks")
      .then(setTasks)
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadTasks();
  }, []);

  return (
    <section className="stack-lg">
      <div className="panel">
        <div className="row-between">
          <div>
            <h1 className="page-title">Tasks</h1>
            <p className="page-copy">
              Tasks saved from chat or the dashboard appear here. Use refresh to pull the latest local task list.
            </p>
          </div>
          <button type="button" className="button-secondary" onClick={loadTasks}>
            Refresh
          </button>
        </div>
      </div>
      {error && <div className="error-text">{error}</div>}
      <div className="stack-md">
        {tasks.length === 0 && (
          <div className="panel muted-text">
            No tasks saved from chat yet. Meetings and appointments are stored in the schedule, not in tasks.
          </div>
        )}
        {tasks.map((task) => (
          <div key={task.id} className="panel">
            <div className="row-between">
              <div className="item-title">{task.title}</div>
              <div className={task.completed ? "status-ok" : "status-pending"}>
                {task.completed ? "done" : "open"}
              </div>
            </div>
            <div className="muted-text">{task.description || "Captured from chat"}</div>
            <div className="meta-row">
              <span>{task.priority}</span>
              <span>{new Date(task.updated_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
