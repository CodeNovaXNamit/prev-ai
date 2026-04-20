"use client";

import { useEffect, useState } from "react";

import { Task, apiRequest } from "@/lib/api";
import { formatRelativeDate } from "@/components/app/format";
import { WorkspaceShell } from "@/components/app/workspace-shell";

export function TasksView() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadTasks = () => {
    apiRequest<Task[]>("/tasks")
      .then(setTasks)
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const setTaskCompleted = (task: Task, completed: boolean) => {
    setBusyTaskId(task.id);
    setError(null);
    setSuccess(null);
    apiRequest<Task>(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    })
      .then((updated) =>
        setTasks((current) =>
          current
            .map((item) => (item.id === task.id ? updated : item))
            .sort(
              (a, b) =>
                Number(a.completed) - Number(b.completed) ||
                new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
            ),
        ),
      )
      .then(() => setSuccess(completed ? `Completed "${task.title}".` : `Reopened "${task.title}".`))
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusyTaskId(null));
  };

  const deleteTask = (taskId: string) => {
    setBusyTaskId(taskId);
    setError(null);
    setSuccess(null);
    apiRequest<{ deleted: boolean }>(`/tasks/${taskId}`, { method: "DELETE" })
      .then(() => {
        const removed = tasks.find((item) => item.id === taskId);
        setTasks((current) => current.filter((item) => item.id !== taskId));
        setSuccess(removed ? `Deleted "${removed.title}".` : "Task deleted.");
      })
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusyTaskId(null));
  };

  const pendingTasks = tasks.filter((task) => !task.completed);
  const doneTasks = tasks.filter((task) => task.completed);

  return (
    <WorkspaceShell
      title="Tasks"
      description="Keep your work in one simple checklist. Tick a task when it is done, or let PrivAI create it from natural language in chat."
      actions={
        <button type="button" className="button button-secondary" onClick={loadTasks}>
          Refresh
        </button>
      }
    >
      {success ? (
        <div className="feedback-banner micro-pulse">
          <div>
            <strong className="success-text">Task updated</strong>
            <span>{success}</span>
          </div>
        </div>
      ) : null}
      {error ? (
        <div className="feedback-banner feedback-banner-error">
          <div>
            <strong className="error-text">Task action failed</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : null}
      <section className="workspace-grid workspace-grid-two reveal stagger-1">
        <div className="app-card">
          <div className="list-card-header">
            <div>
              <span className="eyebrow">To do</span>
              <h2>Pending tasks</h2>
            </div>
            <span className="count-badge">{pendingTasks.length}</span>
          </div>

          <div className="task-list">
            {pendingTasks.length === 0 ? (
              <div className="empty-state">No pending tasks. Create one from chat or the event workflow.</div>
            ) : null}
            {pendingTasks.map((task) => (
              <article key={task.id} className={`task-card ${busyTaskId === task.id ? "busy-state" : ""}`}>
                <label className="task-row">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    disabled={busyTaskId === task.id}
                    onChange={(event) => setTaskCompleted(task, event.target.checked)}
                  />
                  <div>
                    <strong>{task.title}</strong>
                    <span className="task-note">{task.description || "Saved from chat"}</span>
                  </div>
                </label>
                <div className="row-between">
                  <p>{formatRelativeDate(task.due_date)}</p>
                  <button
                    type="button"
                    className="button button-secondary"
                    disabled={busyTaskId === task.id}
                    onClick={() => deleteTask(task.id)}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="app-card">
          <div className="list-card-header">
            <div>
              <span className="eyebrow">Completed</span>
              <h2>Done</h2>
            </div>
            <span className="count-badge">{doneTasks.length}</span>
          </div>
          <div className="task-list">
            {doneTasks.length === 0 ? <div className="empty-state">Completed tasks will appear here.</div> : null}
            {doneTasks.map((task) => (
              <article key={task.id} className={`task-card task-card-complete ${busyTaskId === task.id ? "busy-state" : ""}`}>
                <label className="task-row">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    disabled={busyTaskId === task.id}
                    onChange={(event) => setTaskCompleted(task, event.target.checked)}
                  />
                  <div>
                    <strong>{task.title}</strong>
                    <span className="task-note">{task.description || "Saved from chat"}</span>
                  </div>
                </label>
                <p>Updated {formatRelativeDate(task.updated_at)}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </WorkspaceShell>
  );
}
