"use client";

import { useEffect, useState } from "react";

import { CalendarEvent, apiRequest } from "@/lib/api";

function toLocalDateTime(value: string) {
  if (!value) {
    return "";
  }
  return value.slice(0, 16);
}

export function EventsView() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [title, setTitle] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadEvents = () => {
    apiRequest<CalendarEvent[]>("/events")
      .then(setEvents)
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadEvents();
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
    <section className="stack-lg">
      <div className="panel">
        <div className="row-between">
          <div>
            <h1 className="page-title">Events</h1>
            <p className="page-copy">
              Meetings and appointments saved from chat or the dashboard appear here.
            </p>
          </div>
          <button type="button" className="button-secondary" onClick={loadEvents}>
            Refresh
          </button>
        </div>
      </div>

      <div className="panel stack-md">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Event title"
          className="text-input"
        />
        <div className="grid-two">
          <input
            type="datetime-local"
            value={startTime}
            onChange={(event) => setStartTime(event.target.value)}
            className="text-input"
          />
          <input
            type="datetime-local"
            value={endTime}
            onChange={(event) => setEndTime(event.target.value)}
            className="text-input"
          />
        </div>
        <input
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          placeholder="Location"
          className="text-input"
        />
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={4}
          placeholder="Event notes"
          className="text-input"
        />
        <div className="row-between">
          <div className="muted-text">Chat-saved meetings are listed here automatically.</div>
          <button type="button" className="button-primary" onClick={saveEvent}>
            Save Event
          </button>
        </div>
      </div>

      {error && <div className="error-text">{error}</div>}

      <div className="stack-md">
        {events.length === 0 && <div className="panel muted-text">No events saved yet.</div>}
        {events.map((event) => (
          <div key={event.id} className="panel">
            <div className="row-between">
              <div className="item-title">{event.title}</div>
              <button
                type="button"
                className="button-secondary"
                onClick={() =>
                  apiRequest<{ deleted: boolean }>(`/events/${event.id}`, { method: "DELETE" })
                    .then(() => setEvents((current) => current.filter((item) => item.id !== event.id)))
                    .catch((requestError) => setError((requestError as Error).message))
                }
              >
                Delete
              </button>
            </div>
            <div className="muted-text">
              {toLocalDateTime(event.start_time)} to {toLocalDateTime(event.end_time)}
            </div>
            <div className="muted-text">{event.location || "No location"}</div>
            {event.notes && <div>{event.notes}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}
