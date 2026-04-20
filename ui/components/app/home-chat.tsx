"use client";

import { useRef, useState } from "react";

import { apiRequest, ChatResponse } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  source?: string;
};

export function HomeChat() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Ask me something. I can save tasks, and I can remember personal details like your name, city, or favorites for future chats.",
    },
  ]);
  const [value, setValue] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pendingTasks, setPendingTasks] = useState<string[]>([]);
  const [pendingEvents, setPendingEvents] = useState<string[]>([]);
  const [completedTasks, setCompletedTasks] = useState<string[]>([]);
  const [savedSummaryTitle, setSavedSummaryTitle] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const trimmed = value.trim();
    if ((!trimmed && files.length === 0) || loading) {
      return;
    }

    const userText = trimmed || `Summarize uploaded file${files.length > 1 ? "s" : ""}`;
    setMessages((current) => [...current, { id: `${Date.now()}`, role: "user", text: userText }]);
    setValue("");
    setError(null);
    setPendingTasks([]);
    setPendingEvents([]);
    setCompletedTasks([]);
    setSavedSummaryTitle(null);
    setLoading(true);

    try {
      if (files.length > 0) {
        const filePayloads = await Promise.all(
          files.map(async (file) => ({
            name: file.name,
            text: await file.text(),
          })),
        );
        const summaryTitle =
          files.length === 1 ? `Summary of ${files[0].name}` : `Summary of ${files.length} uploaded files`;
        const noteText = [
          trimmed ? `User context:\n${trimmed}` : "User context:\nSummarize the uploaded file content.",
          ...filePayloads.map(
            (file) => `File: ${file.name}\n${file.text.trim() || "No readable text content found."}`,
          ),
        ].join("\n\n");

        const summaryRecord = await apiRequest<{ id: string; title: string; summary: string | null }>("/summarize", {
          method: "POST",
          body: JSON.stringify({
            title: summaryTitle,
            note_text: noteText,
          }),
        });
        setSavedSummaryTitle(summaryTitle);
        setMessages((current) => [
          ...current,
          {
            id: `${Date.now()}-reply`,
            role: "assistant",
            text: summaryRecord.summary || "Summary saved.",
            source: "summary",
          },
        ]);
        setFiles([]);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        setLoading(false);
        return;
      }

      const payload = await apiRequest<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ message: userText }),
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
      setCompletedTasks(payload.completed_tasks.map((task) => task.title));
      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
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
        {completedTasks.length > 0 && (
          <div className="notice">
            Marked completed: {completedTasks.join(", ")}
          </div>
        )}
        {savedSummaryTitle && (
          <div className="notice">
            Saved to summaries: {savedSummaryTitle}
          </div>
        )}
        {error && <div className="error-text">{error}</div>}

        {files.length > 0 && (
          <div className="file-chip-row">
            {files.map((file) => (
              <div key={file.name} className="file-chip">
                {file.name}
              </div>
            ))}
          </div>
        )}

        <div className="composer">
          <label className="button-secondary upload-button">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden-input"
              onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
            />
            Upload Files
          </label>
          <input
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void sendMessage();
              }
            }}
            placeholder="Add context or ask a question"
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
