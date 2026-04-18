"use client";

import { useState } from "react";

import { apiRequest, ChatResponse } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  source?: string;
};

export function HomeChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Ask me something. I can save tasks, and I can remember personal details like your name, city, or favorites for future chats.",
    },
  ]);
  const [value, setValue] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pendingTasks, setPendingTasks] = useState<string[]>([]);
  const [pendingEvents, setPendingEvents] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const trimmed = value.trim();
    if (!trimmed || loading) {
      return;
    }

    setMessages((current) => [...current, { id: `${Date.now()}`, role: "user", text: trimmed }]);
    setValue("");
    setError(null);
    setPendingTasks([]);
    setPendingEvents([]);
    setLoading(true);

    try {
      const payload = await apiRequest<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ message: trimmed }),
      });
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-reply`,
          role: "assistant",
          text: payload.response,
          source: payload.source,
        },
      ]);
      setPendingTasks(payload.created_tasks.map((task) => task.title));
      setPendingEvents(payload.created_events.map((event) => event.title));
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="stack-lg">
      <div className="panel">
        <h1 className="page-title">Home</h1>
        <p className="page-copy">
          Chat with the model and upload files for your local workflow. Tasks and personal details
          can be saved locally from chat.
        </p>
      </div>

      <div className="panel stack-md">
        <label className="upload-row">
          <input
            type="file"
            multiple
            className="hidden-input"
            onChange={(event) =>
              setFiles(Array.from(event.target.files ?? []).map((file) => file.name))
            }
          />
          <span className="button-secondary">Upload Files</span>
          <span className="muted-text">
            {files.length ? files.join(", ") : "No files selected"}
          </span>
        </label>

        <div className="chat-box">
          {messages.map((message) => (
            <div
              key={message.id}
              className={message.role === "user" ? "bubble bubble-user" : "bubble"}
            >
              <div className="bubble-role">{message.role}</div>
              <div>{message.text}</div>
              {message.source && <div className="bubble-meta">{message.source}</div>}
            </div>
          ))}
          {loading && <div className="muted-text">Thinking...</div>}
        </div>

        {pendingTasks.length > 0 && (
          <div className="notice">
            Saved to tasks: {pendingTasks.join(", ")}
          </div>
        )}
        {pendingEvents.length > 0 && (
          <div className="notice">
            Saved to schedule: {pendingEvents.join(", ")}
          </div>
        )}
        {error && <div className="error-text">{error}</div>}

        <div className="composer">
          <input
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void sendMessage();
              }
            }}
            placeholder="Type a message"
            className="text-input"
          />
          <button type="button" onClick={() => void sendMessage()} className="button-primary">
            Send
          </button>
        </div>
      </div>
    </section>
  );
}
