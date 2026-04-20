"use client";

import { useEffect, useRef, useState } from "react";

import { WorkspaceShell } from "@/components/app/workspace-shell";
import { ChatResponse, apiRequest } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  meta: string;
};

const SESSION_STORAGE_KEY = "privai-chat-messages";

const welcomeMessage: Message = {
  id: "welcome",
  role: "assistant",
  text: "Ask me something. I can save tasks, summarize notes, manage events, and keep the workflow fully local.",
  meta: "Local model ready - Phi-3 via Ollama",
};

export function HomeChat() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [value, setValue] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!stored) {
      setMessages([welcomeMessage]);
      return;
    }

    try {
      const parsed = JSON.parse(stored) as Message[];
      setMessages(parsed.length > 0 ? parsed : [welcomeMessage]);
    } catch {
      window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
      setMessages([welcomeMessage]);
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      window.sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  const sendMessage = async () => {
    const trimmed = value.trim();
    if ((!trimmed && files.length === 0) || loading) {
      return;
    }

    const userText = trimmed || `Summarize uploaded file${files.length > 1 ? "s" : ""}`;

    setMessages((current) => [
      ...current,
      { id: `${Date.now()}-user`, role: "user", text: userText, meta: "Queued locally" },
    ]);
    setValue("");
    setError(null);
    setAlerts([]);
    setSuccess(null);
    setLoading(true);

    try {
      if (files.length > 0) {
        const filePayloads = await Promise.all(
          files.map(async (file) => ({
            name: file.name,
            text: await file.text(),
          })),
        );

        const title =
          files.length === 1 ? `Summary of ${files[0].name}` : `Summary of ${files.length} uploaded files`;
        const noteText = [
          trimmed ? `User context:\n${trimmed}` : "User context:\nSummarize the uploaded file content.",
          ...filePayloads.map((file) => `File: ${file.name}\n${file.text.trim() || "No readable text content found."}`),
        ].join("\n\n");

        const summaryRecord = await apiRequest<{ title: string; summary: string | null }>("/summarize", {
          method: "POST",
          body: JSON.stringify({ title, note_text: noteText }),
        });

        setMessages((current) => [
          ...current,
          {
            id: `${Date.now()}-assistant`,
            role: "assistant",
            text: summaryRecord.summary || "Summary saved locally.",
            meta: `Saved in notes - ${summaryRecord.title}`,
          },
        ]);
        setAlerts([`Saved summary: ${summaryRecord.title}`]);
        setSuccess("Summary generated and stored locally.");
        setFiles([]);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        return;
      }

      const payload = await apiRequest<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ message: userText }),
      });

      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          text: payload.response,
          meta: payload.source === "ollama" ? "Generated locally" : `Source - ${payload.source}`,
        },
      ]);

      const nextAlerts = [
        ...payload.created_tasks.map((task) => `Saved task: ${task.title}`),
        ...payload.created_events.map((event) => `Saved event: ${event.title}`),
        ...payload.completed_tasks.map((task) => `Marked completed: ${task.title}`),
      ];
      setAlerts(nextAlerts);
      setSuccess(nextAlerts[0] ?? "Response received from the local assistant.");
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setLoading(false);
      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <WorkspaceShell
      title="Chat"
      description="Chat with the model, upload source notes for summarization, and let PrivAI turn natural language into private local actions."
      actions={
        <>
          <label className="button button-secondary">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
            />
            Upload files
          </label>
          <button type="button" className="button button-primary" onClick={() => void sendMessage()} disabled={loading}>
            {loading ? "Working..." : "Send"}
          </button>
        </>
      }
    >
      <section className="workspace-grid workspace-grid-chat reveal stagger-1">
        <div className="app-card">
          <div className="app-card-heading">
            <div>
              <span className="eyebrow">Local Conversation</span>
              <h2>Offline assistant</h2>
            </div>
            <span className="status-chip">
              <span className="status-dot" />
              Local model pipeline
            </span>
          </div>

          <div className="chat-thread">
            {messages.map((entry) => (
              <article
                key={entry.id}
                className={`chat-bubble ${entry.role === "assistant" ? "chat-bubble-assistant" : "chat-bubble-user"}`}
              >
                <span className="chat-bubble-label">{entry.role === "assistant" ? "Assistant" : "You"}</span>
                <p>{entry.text}</p>
                <span className="chat-bubble-meta">{entry.meta}</span>
              </article>
            ))}
            {loading ? (
              <article className="chat-bubble chat-bubble-assistant">
                <span className="chat-bubble-label">Assistant</span>
                <p>Processing locally...</p>
                <span className="chat-bubble-meta">Waiting for backend response</span>
              </article>
            ) : null}
          </div>

          {files.length > 0 ? (
            <div className="file-chip-row">
              {files.map((file) => (
                <span key={file.name} className="pill">
                  <strong>{file.name}</strong>
                </span>
              ))}
            </div>
          ) : null}

          {success ? (
            <div className="feedback-banner micro-pulse">
              <div>
                <strong className="success-text">Saved locally</strong>
                <span>{success}</span>
              </div>
              <span className="status-live">active</span>
            </div>
          ) : null}

          {error ? (
            <div className="feedback-banner feedback-banner-error">
              <div>
                <strong className="error-text">Request failed</strong>
                <span>{error}</span>
              </div>
            </div>
          ) : null}

          {alerts.length > 0 ? (
            <div className="alerts-stack">
              {alerts.map((alert) => (
                <div key={alert} className="pill">
                  <strong>{alert}</strong>
                </div>
              ))}
            </div>
          ) : null}

          <div className={`chat-composer ${loading ? "busy-state" : ""}`}>
            <label className="button button-secondary">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                hidden
                onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              />
              Upload Files
            </label>
            <div className="chat-input-wrap">
              <input
                className="chat-input"
                type="text"
                value={value}
                onChange={(event) => setValue(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    void sendMessage();
                  }
                }}
                placeholder="Add context or ask a private question"
                aria-label="Chat input"
              />
            </div>
            <button type="button" className="button button-primary" onClick={() => void sendMessage()} disabled={loading}>
              Send
            </button>
          </div>
        </div>

        <aside className="app-card">
          <div className="app-card-heading">
            <div>
              <span className="eyebrow">Capabilities</span>
              <h2>Everything local</h2>
            </div>
          </div>
          <div className="notes-stack">
            <div className="alert-card">
              <strong>Task capture</strong>
              <span className="muted-text">Turn reminders into saved local tasks directly from chat.</span>
            </div>
            <div className="glass-divider" />
            <div className="alert-card">
              <strong>Summaries</strong>
              <span className="muted-text">Upload text files and summarize them through the local model.</span>
            </div>
            <div className="glass-divider" />
            <div className="alert-card">
              <strong>Event creation</strong>
              <span className="muted-text">Meeting-like prompts can be stored as real local events.</span>
            </div>
            <div className="glass-divider" />
            <div className="alert-card">
              <strong>Privacy</strong>
              <span className="muted-text">The UI only talks to your FastAPI backend. Nothing goes to a cloud API.</span>
            </div>
          </div>
        </aside>
      </section>
    </WorkspaceShell>
  );
}
