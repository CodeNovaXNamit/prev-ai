"use client";

import { useEffect, useState } from "react";

import { Task, apiRequest } from "@/lib/api";

export function TasksView() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);

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
    apiRequest<Task>(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    })
      .then((updated) =>
        setTasks((current) =>
          current
            .map((item) => (item.id === task.id ? updated : item))
            .sort((a, b) => Number(a.completed) - Number(b.completed) || new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()),
        ),
      )
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusyTaskId(null));
  };

  const deleteTask = (taskId: string) => {
    setBusyTaskId(taskId);
    setError(null);
    apiRequest<{ deleted: boolean }>(`/tasks/${taskId}`, { method: "DELETE" })
      .then(() => setTasks((current) => current.filter((item) => item.id !== taskId)))
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setBusyTaskId(null));
  };

  const pendingTasks = tasks.filter((task) => !task.completed);
  const doneTasks = tasks.filter((task) => task.completed);

  return (
    <section className="stack-lg">
      <div className="panel">
        <div className="row-between">
          <div>
            <h1 className="page-title">Tasks</h1>
            <p className="page-copy">
              Keep your work in one simple checklist. Tick a task when it is done, or say it in chat.
            </p>
          </div>
          <button type="button" className="button-secondary" onClick={loadTasks}>
            Refresh
          </button>
        </div>
      </div>
      {error && <div className="error-text">{error}</div>}
      {tasks.length === 0 && (
        <div className="panel muted-text">
          No tasks yet. Add one from chat, then come back here to tick it off.
        </div>
      )}
      {tasks.length > 0 && (
        <div className="grid-two task-groups">
          <div className="panel stack-md">
            <div className="task-group-header">
              <div className="item-title">To do</div>
              <div className="task-count">{pendingTasks.length}</div>
            </div>
            {pendingTasks.length === 0 && <div className="muted-text">Nothing pending right now.</div>}
            {pendingTasks.map((task) => (
              <div key={task.id} className="task-card">
                <label className="task-main">
                  <input
                    type="checkbox"
                    className="task-check"
                    checked={task.completed}
                    disabled={busyTaskId === task.id}
                    onChange={(event) => setTaskCompleted(task, event.target.checked)}
                  />
                  <div className="task-copy">
                    <div className="task-title">{task.title}</div>
                    <div className="task-note">{task.description || "Saved from chat"}</div>
                  </div>
                </label>
                <div className="task-actions">
                  <div className="task-time">
                    {task.due_date ? `Due ${task.due_date}` : `Updated ${new Date(task.updated_at).toLocaleDateString()}`}
                  </div>
                  <button
                    type="button"
                    className="button-secondary"
                    disabled={busyTaskId === task.id}
                    onClick={() => deleteTask(task.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="panel stack-md">
            <div className="task-group-header">
              <div className="item-title">Completed</div>
              <div className="task-count">{doneTasks.length}</div>
            </div>
            {doneTasks.length === 0 && <div className="muted-text">Completed tasks will appear here.</div>}
            {doneTasks.map((task) => (
              <div key={task.id} className="task-card task-card-done">
                <label className="task-main">
                  <input
                    type="checkbox"
                    className="task-check"
                    checked={task.completed}
                    disabled={busyTaskId === task.id}
                    onChange={(event) => setTaskCompleted(task, event.target.checked)}
                  />
                  <div className="task-copy">
                    <div className="task-title task-title-done">{task.title}</div>
                    <div className="task-note">{task.description || "Saved from chat"}</div>
                  </div>
                </label>
                <div className="task-time">
                  Finished. Updated {new Date(task.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
