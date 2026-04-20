"use client";

import { useEffect, useState } from "react";

import { CalendarEvent, apiRequest } from "@/lib/api";
import { formatRelativeDate } from "@/components/app/format";
import { WorkspaceShell } from "@/components/app/workspace-shell";

export function EventsView() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [title, setTitle] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadEvents = () => {
    apiRequest<CalendarEvent[]>("/events")
      .then((payload) => setEvents(payload.sort((a, b) => a.start_time.localeCompare(b.start_time))))
      .catch((requestError) => setError((requestError as Error).message));
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const saveEvent = () => {
    if (!title.trim() || !startTime || !endTime || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

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
        setSuccess(`Saved "${created.title}" to your local schedule.`);
      })
      .catch((requestError) => setError((requestError as Error).message))
      .finally(() => setLoading(false));
  };

  return (
    <WorkspaceShell
      title="Events"
      description="Meetings and appointments saved from chat or entered manually appear here with local-only persistence."
      actions={
        <>
          <button type="button" className="button button-secondary" onClick={loadEvents}>
            Refresh
          </button>
          <button type="button" className="button button-primary" onClick={saveEvent} disabled={loading}>
            {loading ? "Saving..." : "Save event"}
          </button>
        </>
      }
    >
      {success ? (
        <div className="feedback-banner micro-pulse">
          <div>
            <strong className="success-text">Event saved</strong>
            <span>{success}</span>
          </div>
        </div>
      ) : null}
      {error ? (
        <div className="feedback-banner feedback-banner-error">
          <div>
            <strong className="error-text">Event action failed</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : null}

      <section className="app-card reveal stagger-1">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Create event</span>
            <h2>Manual scheduling</h2>
          </div>
        </div>
        <div className={`quick-form ${loading ? "busy-state" : ""}`}>
          <div className="surface-input">
            <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Event title" />
          </div>
          <div className="quick-grid">
            <div className="surface-input">
              <input type="datetime-local" value={startTime} onChange={(event) => setStartTime(event.target.value)} />
            </div>
            <div className="surface-input">
              <input type="datetime-local" value={endTime} onChange={(event) => setEndTime(event.target.value)} />
            </div>
          </div>
          <div className="surface-input">
            <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Location" />
          </div>
          <div className="surface-textarea">
            <textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Event notes" />
          </div>
        </div>
      </section>

      <section className="app-card reveal stagger-2">
        <div className="app-card-heading">
          <div>
            <span className="eyebrow">Saved schedule</span>
            <h2>Upcoming events</h2>
          </div>
        </div>
        <div className="notes-stack">
          {events.length === 0 ? <div className="empty-state">No events saved yet.</div> : null}
          {events.map((event) => (
            <article key={event.id} className="note-entry">
              <div className="row-between">
                <h3>{event.title}</h3>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={() =>
                    apiRequest<{ deleted: boolean }>(`/events/${event.id}`, { method: "DELETE" })
                      .then(() => {
                        setEvents((current) => current.filter((item) => item.id !== event.id));
                        setSuccess(`Deleted "${event.title}".`);
                      })
                      .catch((requestError) => setError((requestError as Error).message))
                  }
                >
                  Delete
                </button>
              </div>
              <div className="note-summary-box">
                <strong>Time</strong>
                <p>
                  {formatRelativeDate(event.start_time)} to {formatRelativeDate(event.end_time)}
                </p>
              </div>
              <div className="note-original-box">
                <strong>Details</strong>
                <p>{event.location || "No location"}</p>
                {event.notes ? <p>{event.notes}</p> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
