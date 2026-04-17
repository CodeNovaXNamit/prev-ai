"use client";

import { useState } from "react";

import { Card } from "@/components/ui/card";
import { UploadIcon } from "@/components/ui/icons";

type UploadedFile = {
  id: number;
  name: string;
  size: string;
  type: string;
};

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadPanel() {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  return (
    <Card className="mb-6 overflow-hidden p-5">
      <label className="group flex cursor-pointer flex-col rounded-[28px] border border-dashed border-white/15 bg-black/10 p-6 transition hover:border-[var(--info)]/60 hover:bg-white/5">
        <input
          type="file"
          multiple
          className="hidden"
          onChange={(event) => {
            const nextFiles = Array.from(event.target.files ?? []).map((file) => ({
              id: Date.now() + Math.random(),
              name: file.name,
              size: formatBytes(file.size),
              type: file.type || "Unknown type",
            }));

            setFiles((current) => [...nextFiles, ...current].slice(0, 5));
          }}
        />

        <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)] transition group-hover:scale-105">
          <UploadIcon className="h-7 w-7" />
        </div>
        <div className="mt-5 text-xl font-semibold">Upload private files</div>
        <p className="mt-2 max-w-xl leading-7 muted">
          Add PDFs, notes, transcripts, or drafts for a local-first workflow preview.
          Files stay in this browser session to simulate secure on-device processing.
        </p>
        <div className="mt-5 flex flex-wrap gap-3 text-sm">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
            Drag and drop style area
          </span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
            Multi-file ready
          </span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
            Local preview only
          </span>
        </div>
      </label>

      <div className="mt-4 flex flex-wrap gap-3">
        {files.length ? (
          files.map((file) => (
            <div
              key={file.id}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm"
            >
              <span className="font-medium">{file.name}</span>
              <span className="ml-2 muted">{file.size}</span>
            </div>
          ))
        ) : (
          <div className="text-sm muted">
            No files added yet. Upload a file when you want to test the chatbot intake flow.
          </div>
        )}
      </div>
    </Card>
  );
}
