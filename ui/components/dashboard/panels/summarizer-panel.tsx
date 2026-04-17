"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Note, apiRequest } from "@/lib/api";

export function SummarizerPanel() {
  const [input, setInput] = useState("");
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [history, setHistory] = useState<Note[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<Note[]>("/notes")
      .then((payload) => setHistory(payload.filter((note) => note.summary)))
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  const handleSummarize = () => {
    if (!input.trim()) {
      return;
    }

    apiRequest<Note>("/summarize", {
      method: "POST",
      body: JSON.stringify({
        title,
        note_text: input.trim(),
      }),
    })
      .then((payload) => {
        setSummary(payload.summary ?? "");
        setHistory((current) => [payload, ...current.filter((item) => item.id !== payload.id)]);
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <div className="rounded-[28px] border border-white/10 bg-black/10 p-5">
        <div className="mb-4 text-sm uppercase tracking-[0.22em] text-[var(--info)]">
          Input text
        </div>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Summary title"
          className="mb-4 w-full rounded-[24px] border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={13}
          placeholder="Paste text to summarize..."
          className="w-full rounded-[24px] border border-white/10 bg-transparent px-4 py-4 outline-none placeholder:text-white/35"
        />
        <div className="mt-4 flex justify-end">
          <Button onClick={handleSummarize}>Generate Summary</Button>
        </div>
      </div>

      <div className="rounded-[28px] border border-white/10 bg-white/5 p-5">
        <div className="mb-4 text-sm uppercase tracking-[0.22em] text-[var(--accent)]">
          Local summary
        </div>
        <div className="rounded-[24px] border border-white/10 bg-black/10 p-5">
          <p className="text-lg leading-8">
            {summary || "Generate a summary to see the local model output here."}
          </p>
        </div>
        {error && <div className="mt-4 text-sm text-rose-300">{error}</div>}
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          {["Clarity", "Compression", "Privacy"].map((item, index) => (
            <div
              key={item}
              className="rounded-2xl border border-white/10 bg-black/10 p-4"
            >
              <div className="text-sm muted">{item}</div>
              <div className="mt-2 text-2xl font-semibold">{92 - index * 4}%</div>
            </div>
          ))}
        </div>
        <div className="mt-5 space-y-3">
          {history.slice(0, 3).map((item) => (
            <div key={item.id} className="rounded-2xl border border-white/10 bg-black/10 p-4">
              <div className="text-sm uppercase tracking-[0.18em] text-[var(--info)]">
                {item.title}
              </div>
              <div className="mt-2 text-sm muted">{item.summary}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
