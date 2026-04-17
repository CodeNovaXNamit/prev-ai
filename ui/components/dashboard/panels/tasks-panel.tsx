"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Task, apiRequest } from "@/lib/api";

export function TasksPanel() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskInput, setTaskInput] = useState("");
  const [priority, setPriority] = useState("medium");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refreshTasks().finally(() => setIsLoading(false));
  }, []);

  const refreshTasks = async () => {
    try {
      setError(null);
      setTasks(await apiRequest<Task[]>("/tasks"));
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  };

  const completion = Math.round(
    (tasks.filter((task) => task.completed).length / Math.max(tasks.length, 1)) * 100,
  );

  const addTask = () => {
    if (!taskInput.trim()) {
      return;
    }

    apiRequest<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: taskInput.trim(),
        description: "",
        priority,
        completed: false,
      }),
    })
      .then((created) => {
        setTasks((current) => [created, ...current]);
        setTaskInput("");
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-black/10 p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="text-sm muted">Task completion</div>
            <div className="mt-1 text-3xl font-semibold">{completion}%</div>
          </div>
          <div className="h-16 w-16 rounded-full border-4 border-white/10 p-1">
            <div
              className="flex h-full w-full items-center justify-center rounded-full bg-[var(--accent-soft)] text-sm font-semibold"
            >
              {completion}
            </div>
          </div>
        </div>
        <div className="mt-4 h-2 rounded-full bg-white/10">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--info)]"
            style={{ width: `${completion}%` }}
          />
        </div>
      </div>

      <div className="flex flex-col gap-3 rounded-[28px] border border-white/10 bg-black/10 p-4 sm:flex-row">
        <input
          value={taskInput}
          onChange={(event) => setTaskInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              addTask();
            }
          }}
          placeholder="Add a task..."
          className="w-full rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <select
          value={priority}
          onChange={(event) => setPriority(event.target.value)}
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <Button onClick={addTask}>Add Task</Button>
      </div>

      {error && <div className="text-sm text-rose-300">{error}</div>}
      {isLoading && <div className="text-sm muted">Loading tasks...</div>}

      <div className="space-y-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="flex items-center justify-between rounded-[24px] border border-white/10 bg-white/5 px-4 py-4"
          >
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() =>
                  apiRequest<Task>(`/tasks/${task.id}`, {
                    method: "PATCH",
                    body: JSON.stringify({ completed: !task.completed }),
                  })
                    .then((updated) =>
                      setTasks((current) =>
                        current.map((item) => (item.id === task.id ? updated : item)),
                      ),
                    )
                    .catch((requestError) => setError((requestError as Error).message))
                }
                className="h-5 w-5 rounded border-white/10 accent-[var(--accent)]"
              />
              <div>
                <span className={task.completed ? "line-through opacity-50" : ""}>
                  {task.title}
                </span>
                <div className="text-sm muted">
                  {task.priority} priority {task.due_date ? `| due ${task.due_date}` : ""}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() =>
                apiRequest<{ deleted: boolean }>(`/tasks/${task.id}`, { method: "DELETE" })
                  .then(() =>
                    setTasks((current) => current.filter((item) => item.id !== task.id)),
                  )
                  .catch((requestError) => setError((requestError as Error).message))
              }
              className="rounded-full border border-white/10 px-3 py-1 text-sm hover:bg-white/5"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
