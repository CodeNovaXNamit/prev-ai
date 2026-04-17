"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/api";

type Message = {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  source?: string;
};

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content:
        "Hello. I'm PrivAI, your local-first assistant. Ask about notes, tasks, or privacy controls.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("prevai-chat");

    if (stored) {
      setMessages(JSON.parse(stored) as Message[]);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem("prevai-chat", JSON.stringify(messages));
  }, [messages]);

  const submitMessage = () => {
    if (!input.trim()) {
      return;
    }

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: input.trim(),
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsThinking(true);
    setError(null);

    apiRequest<{ response: string; source: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message: userMessage.content }),
    })
      .then((payload) => {
        setMessages((current) => [
          ...current,
          {
            id: Date.now() + 1,
            role: "assistant",
            content: payload.response,
            source: payload.source,
          },
        ]);
      })
      .catch((requestError: Error) => {
        setError(requestError.message);
      })
      .finally(() => {
        setIsThinking(false);
      });
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-hidden">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-[85%] rounded-[24px] px-4 py-3 ${
              message.role === "assistant"
                ? "bg-white/5 text-text"
                : "ml-auto bg-gradient-to-r from-[var(--accent)]/80 to-[var(--info)]/80 text-white"
            }`}
          >
            <div className="mb-1 text-xs uppercase tracking-[0.22em] text-white/60">
              {message.role}
            </div>
            <div className="leading-7">{message.content}</div>
            {message.source && (
              <div className="mt-2 text-[11px] uppercase tracking-[0.18em] text-[var(--info)]">
                {message.source}
              </div>
            )}
          </div>
        ))}

        {isThinking && (
          <div className="max-w-[70%] rounded-[24px] bg-white/5 px-4 py-3 text-text">
            <div className="mb-1 text-xs uppercase tracking-[0.22em] text-white/60">
              assistant
            </div>
            <div className="flex items-center gap-2">
              <span>AI is thinking</span>
              <span className="inline-flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--info)] [animation-delay:0ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--info)] [animation-delay:120ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--info)] [animation-delay:240ms]" />
              </span>
            </div>
          </div>
        )}
      </div>

      {error && <div className="mt-4 text-sm text-rose-300">{error}</div>}

      <div className="mt-6 flex flex-col gap-3 rounded-[24px] border border-white/10 bg-black/10 p-4 sm:flex-row">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              submitMessage();
            }
          }}
          placeholder="Ask PrivAI anything..."
          className="w-full rounded-2xl border border-white/10 bg-transparent px-4 py-3 text-base text-text outline-none placeholder:text-white/35"
        />
        <Button onClick={submitMessage} className="sm:min-w-32">
          Send
        </Button>
      </div>
    </div>
  );
}
