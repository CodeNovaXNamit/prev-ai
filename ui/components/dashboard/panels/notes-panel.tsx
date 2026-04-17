"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Note, apiRequest } from "@/lib/api";

export function NotesPanel() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<Note[]>("/notes")
      .then((payload) => setNotes(payload))
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  const addNote = () => {
    if (!title.trim() || !body.trim()) {
      return;
    }

    apiRequest<Note>("/notes", {
      method: "POST",
      body: JSON.stringify({
        title: title.trim(),
        note_text: body.trim(),
      }),
    })
      .then((created) => {
        setNotes((current) => [created, ...current]);
        setTitle("");
        setBody("");
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 rounded-[28px] border border-white/10 bg-black/10 p-4">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Note title"
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <textarea
          value={body}
          onChange={(event) => setBody(event.target.value)}
          placeholder="Write a secure note..."
          rows={4}
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <div className="flex justify-end">
          <Button onClick={addNote}>Create Note</Button>
        </div>
      </div>

      {error && <div className="text-sm text-rose-300">{error}</div>}

      <div className="grid gap-4 lg:grid-cols-2">
        {notes.map((note) => (
          <div
            key={note.id}
            className="rounded-[28px] border border-white/10 bg-white/5 p-5"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-xl font-semibold">{note.title}</h4>
                <p className="mt-3 leading-7 muted">{note.note_text}</p>
                {note.summary && (
                  <div className="mt-4 rounded-2xl border border-white/10 bg-black/10 p-4 text-sm">
                    {note.summary}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() =>
                  apiRequest<{ deleted: boolean }>(`/notes/${note.id}`, { method: "DELETE" })
                    .then(() =>
                      setNotes((current) => current.filter((item) => item.id !== note.id)),
                    )
                    .catch((requestError) => setError((requestError as Error).message))
                }
                className="rounded-full border border-white/10 px-3 py-1 text-sm hover:bg-white/5"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
