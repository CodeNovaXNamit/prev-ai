"use client";

import { useEffect, useState } from "react";

import { Note, apiRequest } from "@/lib/api";
import { WorkspaceShell } from "@/components/app/workspace-shell";

export function SummariesView() {
  const [title, setTitle] = useState("");
  const [noteText, setNoteText] = useState("");
  const [notes, setNotes] = useState<Note[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadNotes = () => {
    apiRequest<Note[]>("/summaries")
      .then(setNotes)
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadNotes();
  }, []);

  const summarize = async () => {
    if (!noteText.trim() || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const created = await apiRequest<Note>("/summarize", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim() || "Untitled local note",
          note_text: noteText.trim(),
        }),
      });
      setTitle("");
      setNoteText("");
      setSuccess(`Generated summary for "${created.title}".`);
      loadNotes();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <WorkspaceShell
      title="Notes"
      description="Summarize notes through the local model and review saved summaries alongside the original source text stored on your device."
      actions={
        <>
          <button type="button" className="button button-secondary" onClick={loadNotes}>
            Refresh
          </button>
          <button type="button" className="button button-primary" onClick={() => void summarize()} disabled={loading}>
            {loading ? "Summarizing..." : "Generate summary"}
          </button>
        </>
      }
    >
      {success ? (
        <div className="feedback-banner micro-pulse">
          <div>
            <strong className="success-text">Summary saved</strong>
            <span>{success}</span>
          </div>
        </div>
      ) : null}
      {error ? (
        <div className="feedback-banner feedback-banner-error">
          <div>
            <strong className="error-text">Summary failed</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : null}
      <section className="app-card reveal stagger-1">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Summary composer</span>
            <h2>Send text to the local model</h2>
          </div>
          <span className="status-chip">
            <span className="status-dot" />
            {notes.length} notes stored
          </span>
        </div>

        <div className={`quick-form ${loading ? "busy-state" : ""}`}>
          <div className="surface-input">
            <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Note title" />
          </div>
          <div className="surface-textarea">
            <textarea
              value={noteText}
              onChange={(event) => setNoteText(event.target.value)}
              placeholder="Paste lecture notes, meeting notes, or research text"
            />
          </div>
        </div>
      </section>

      <section className="app-card reveal stagger-2">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Saved outputs</span>
            <h2>Local note summaries</h2>
          </div>
        </div>

        <div className="notes-stack">
          {notes.length === 0 ? <div className="empty-state">No summaries saved yet.</div> : null}
          {notes.map((note) => (
            <article key={note.id} className="note-entry">
              <h3>{note.title}</h3>
              <div className="note-summary-box">
                <strong>Summary</strong>
                <p>{note.summary || "No summary returned."}</p>
              </div>
              <div className="note-original-box">
                <strong>Original note</strong>
                <p>{note.note_text}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
