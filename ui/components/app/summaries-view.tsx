"use client";

import { useEffect, useState } from "react";

import { Note, apiRequest } from "@/lib/api";

export function SummariesView() {
  const [summaries, setSummaries] = useState<Note[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<Note[]>("/summaries")
      .then(setSummaries)
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  return (
    <section className="stack-lg">
      <div className="panel">
        <h1 className="page-title">Summaries</h1>
        <p className="page-copy">This page shows every summarized note saved in the backend so far.</p>
      </div>
      {error && <div className="error-text">{error}</div>}
      <div className="stack-md">
        {summaries.length === 0 && <div className="panel muted-text">No summaries saved yet.</div>}
        {summaries.map((note) => (
          <div key={note.id} className="panel stack-sm">
            <div className="item-title">{note.title}</div>
            <div className="summary-box">{note.summary}</div>
            <div className="muted-text">{note.note_text}</div>
            <div className="meta-row">
              <span>saved</span>
              <span>{new Date(note.updated_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
