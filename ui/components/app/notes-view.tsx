"use client";

import { useEffect, useState } from "react";

import { Note, apiRequest } from "@/lib/api";
import { WorkspaceShell } from "@/components/app/workspace-shell";

export function NotesView() {
  const [title, setTitle] = useState("");
  const [noteText, setNoteText] = useState("");
  const [notes, setNotes] = useState<Note[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadNotes = () => {
    apiRequest<Note[]>("/notes")
      .then((payload) => {
        setNotes(payload);
        setError(null);
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadNotes();
  }, []);

  const createNote = async () => {
    if (!title.trim() || !noteText.trim() || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const created = await apiRequest<Note>("/notes", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          note_text: noteText.trim(),
        }),
      });

      setNotes((current) => [created, ...current]);
      setTitle("");
      setNoteText("");
      setSuccess(`Saved "${created.title}" locally.`);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const deleteNote = async (id: string) => {
    setError(null);
    setSuccess(null);
    try {
      await apiRequest<{ deleted: boolean }>(`/notes/${id}`, { method: "DELETE" });
      setNotes((current) => current.filter((item) => item.id !== id));
      setSuccess("Note deleted.");
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  };

  return (
    <WorkspaceShell
      title="Notes"
      description="Create and manage private notes stored through the local backend without leaving the new workspace."
      actions={
        <>
          <button type="button" className="button button-secondary" onClick={loadNotes}>
            Refresh
          </button>
          <button type="button" className="button button-primary" onClick={() => void createNote()} disabled={loading}>
            {loading ? "Saving..." : "Create note"}
          </button>
        </>
      }
    >
      {success ? (
        <div className="feedback-banner micro-pulse">
          <div>
            <strong className="success-text">Notes updated</strong>
            <span>{success}</span>
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="feedback-banner feedback-banner-error">
          <div>
            <strong className="error-text">Notes request failed</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : null}

      <section className="app-card reveal stagger-1">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Note composer</span>
            <h2>Write secure local notes</h2>
          </div>
          <span className="status-chip">
            <span className="status-dot" />
            {notes.length} saved notes
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
              placeholder="Write a private note, meeting log, or research draft"
            />
          </div>
        </div>
      </section>

      <section className="app-card reveal stagger-2">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Saved notes</span>
            <h2>Private local storage</h2>
          </div>
        </div>

        <div className="notes-stack">
          {notes.length === 0 ? <div className="empty-state">No notes saved yet.</div> : null}
          {notes.map((note) => (
            <article key={note.id} className="note-entry">
              <div className="row-between">
                <div>
                  <h3>{note.title}</h3>
                  <span className="muted-text">Stored on your local stack</span>
                </div>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={() => void deleteNote(note.id)}
                >
                  Delete
                </button>
              </div>
              <div className="note-original-box">
                <strong>Note body</strong>
                <p>{note.note_text}</p>
              </div>
              {note.summary ? (
                <div className="note-summary-box">
                  <strong>Attached summary</strong>
                  <p>{note.summary}</p>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
