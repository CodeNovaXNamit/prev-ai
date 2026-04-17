"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { CalendarEvent, apiRequest } from "@/lib/api";

function toLocalDateTime(value: string) {
  if (!value) {
    return "";
  }
  return value.slice(0, 16);
}

export function SchedulePanel() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [title, setTitle] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<CalendarEvent[]>("/events")
      .then((payload) => setEvents(payload))
      .catch((requestError) => setError((requestError as Error).message));
  }, []);

  const saveEvent = () => {
    if (!title.trim() || !startTime || !endTime) {
      return;
    }

    apiRequest<CalendarEvent>("/events", {
      method: "POST",
      body: JSON.stringify({
        title: title.trim(),
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        location,
        notes,
      }),
    })
      .then((created) => {
        setEvents((current) => [...current, created].sort((a, b) => a.start_time.localeCompare(b.start_time)));
        setTitle("");
        setStartTime("");
        setEndTime("");
        setLocation("");
        setNotes("");
      })
      .catch((requestError) => setError((requestError as Error).message));
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 rounded-[28px] border border-white/10 bg-black/10 p-4">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Event title"
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <div className="grid gap-3 md:grid-cols-2">
          <input
            type="datetime-local"
            value={startTime}
            onChange={(event) => setStartTime(event.target.value)}
            className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none"
          />
          <input
            type="datetime-local"
            value={endTime}
            onChange={(event) => setEndTime(event.target.value)}
            className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none"
          />
        </div>
        <input
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          placeholder="Location"
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={4}
          placeholder="Event notes"
          className="rounded-2xl border border-white/10 bg-transparent px-4 py-3 outline-none placeholder:text-white/35"
        />
        <div className="flex justify-end">
          <Button onClick={saveEvent}>Save Event</Button>
        </div>
      </div>

      {error && <div className="text-sm text-rose-300">{error}</div>}

      <div className="space-y-3">
        {events.map((event) => (
          <div
            key={event.id}
            className="flex items-start justify-between rounded-[24px] border border-white/10 bg-white/5 px-4 py-4"
          >
            <div>
              <div className="text-lg font-semibold">{event.title}</div>
              <div className="mt-2 text-sm muted">
                {toLocalDateTime(event.start_time)} to {toLocalDateTime(event.end_time)}
              </div>
              <div className="mt-1 text-sm muted">{event.location}</div>
              {event.notes && <div className="mt-3 text-sm">{event.notes}</div>}
            </div>
            <button
              type="button"
              onClick={() =>
                apiRequest<{ deleted: boolean }>(`/events/${event.id}`, { method: "DELETE" })
                  .then(() =>
                    setEvents((current) => current.filter((item) => item.id !== event.id)),
                  )
                  .catch((requestError) => setError((requestError as Error).message))
              }
              className="rounded-full border border-white/10 px-3 py-1 text-sm hover:bg-white/5"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
