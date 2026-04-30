import { useEffect, useMemo, useState } from "react";
import Card from "../components/common/Card";
import Table from "../components/common/Table";
import {
  fetchEmergencyEvent,
  fetchEmergencyEvents,
  resolveEmergencyEvent,
  triggerEmergencyEvent,
  updateMuster,
} from "../api/emergency";

const EVENT_TYPES = [
  { value: "fire", label: "Fire" },
  { value: "medical", label: "Medical" },
  { value: "security", label: "Security" },
  { value: "disaster", label: "Disaster" },
  { value: "other", label: "Other" },
];

const SEVERITIES = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const MUSTER_STATUSES = [
  { value: "pending", label: "Pending" },
  { value: "accounted_for", label: "Accounted for" },
  { value: "unaccounted", label: "Unaccounted" },
  { value: "evacuated", label: "Evacuated" },
];

const severityColor = {
  low: "bg-emerald-100 text-emerald-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

const eventStatusColor = {
  active: "bg-red-100 text-red-700",
  contained: "bg-amber-100 text-amber-700",
  resolved: "bg-emerald-100 text-emerald-700",
};

const musterColor = {
  pending: "bg-amber-100 text-amber-700",
  accounted_for: "bg-emerald-100 text-emerald-700",
  unaccounted: "bg-red-100 text-red-700",
  evacuated: "bg-sky-100 text-sky-700",
};

function TriggerForm({ onSubmit, busy }) {
  const [form, setForm] = useState({
    event_type: "fire",
    severity: "high",
    title: "",
    description: "",
    location: "",
  });

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function submit(e) {
    e.preventDefault();
    if (!form.title.trim()) return;
    onSubmit(form);
    setForm({ event_type: "fire", severity: "high", title: "", description: "", location: "" });
  }

  return (
    <form onSubmit={submit} className="grid gap-3 md:grid-cols-2">
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Event Type
        </label>
        <select
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.event_type}
          onChange={(e) => update("event_type", e.target.value)}
        >
          {EVENT_TYPES.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Severity
        </label>
        <select
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.severity}
          onChange={(e) => update("severity", e.target.value)}
        >
          {SEVERITIES.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
      <div className="md:col-span-2">
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Title</label>
        <input
          required
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.title}
          onChange={(e) => update("title", e.target.value)}
          placeholder="e.g. Smoke detected — Block A"
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Location</label>
        <input
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.location}
          onChange={(e) => update("location", e.target.value)}
          placeholder="Block A, 2nd floor"
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Description
        </label>
        <input
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          placeholder="More detail (optional)"
        />
      </div>
      <div className="md:col-span-2 flex justify-end">
        <button
          type="submit"
          disabled={busy}
          className="rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
        >
          {busy ? "Triggering…" : "🚨 Trigger Emergency"}
        </button>
      </div>
    </form>
  );
}

function MusterTable({ musters, onChange, busy }) {
  if (!musters?.length) {
    return (
      <div className="panel-muted p-6 text-center text-sm text-stone-500">
        No visitors were on campus when this event was triggered.
      </div>
    );
  }
  return (
    <Table
      rows={musters}
      columns={[
        { key: "visitor_name_snapshot", label: "Visitor" },
        { key: "host_name_snapshot", label: "Host", render: (r) => r.host_name_snapshot || "—" },
        {
          key: "status",
          label: "Status",
          render: (r) => (
            <span
              className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                musterColor[r.status] || "bg-stone-200 text-stone-700"
              }`}
            >
              {r.status.replace("_", " ")}
            </span>
          ),
        },
        {
          key: "actions",
          label: "Update",
          render: (r) => (
            <select
              className="rounded-xl border border-stone-200 px-2 py-1 text-xs"
              value={r.status}
              disabled={busy}
              onChange={(e) => onChange(r.id, e.target.value)}
            >
              {MUSTER_STATUSES.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          ),
        },
      ]}
    />
  );
}

export default function EmergencyPage() {
  const [events, setEvents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function loadEvents() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEmergencyEvents();
      setEvents(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadEvent(id) {
    if (!id) {
      setSelected(null);
      return;
    }
    try {
      const data = await fetchEmergencyEvent(id);
      setSelected(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  useEffect(() => {
    loadEvent(selectedId);
  }, [selectedId]);

  async function handleTrigger(form) {
    setBusy(true);
    setError(null);
    try {
      const created = await triggerEmergencyEvent(form);
      await loadEvents();
      setSelectedId(created.id);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleResolve() {
    if (!selected) return;
    if (!window.confirm(`Resolve event ${selected.event_no}?`)) return;
    setBusy(true);
    try {
      await resolveEmergencyEvent(selected.id);
      await loadEvents();
      await loadEvent(selected.id);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleMusterChange(musterId, status) {
    setBusy(true);
    try {
      await updateMuster(musterId, { status });
      await loadEvent(selected.id);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  const counts = useMemo(() => {
    if (!selected?.musters) return null;
    const out = { pending: 0, accounted_for: 0, unaccounted: 0, evacuated: 0 };
    selected.musters.forEach((m) => {
      out[m.status] = (out[m.status] || 0) + 1;
    });
    return out;
  }, [selected]);

  return (
    <div className="space-y-6">
      <Card
        title="Trigger Emergency"
        subtitle="Logs an event, snapshots all currently checked-in visitors into a muster list, and notifies security/admin."
      >
        <TriggerForm onSubmit={handleTrigger} busy={busy} />
      </Card>

      {error && (
        <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <Card title="Events" subtitle={loading ? "Loading…" : `${events.length} event(s) total`}>
        <Table
          rows={events}
          emptyText="No emergency events have been triggered."
          columns={[
            { key: "event_no", label: "Event No" },
            { key: "event_type", label: "Type" },
            {
              key: "severity",
              label: "Severity",
              render: (r) => (
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                    severityColor[r.severity] || "bg-stone-200 text-stone-700"
                  }`}
                >
                  {r.severity}
                </span>
              ),
            },
            {
              key: "status",
              label: "Status",
              render: (r) => (
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                    eventStatusColor[r.status] || "bg-stone-200 text-stone-700"
                  }`}
                >
                  {r.status}
                </span>
              ),
            },
            { key: "title", label: "Title" },
            { key: "location", label: "Location", render: (r) => r.location || "—" },
            {
              key: "triggered_at",
              label: "Triggered",
              render: (r) => new Date(r.triggered_at).toLocaleString(),
            },
            {
              key: "open",
              label: "Open",
              render: (r) => (
                <button
                  className="font-semibold text-brand-600"
                  onClick={() => setSelectedId(r.id)}
                >
                  View
                </button>
              ),
            },
          ]}
        />
      </Card>

      {selected && (
        <Card
          title={`${selected.event_no} — ${selected.title}`}
          subtitle={`${selected.event_type.toUpperCase()} • ${selected.severity} severity • status: ${selected.status}`}
          action={
            selected.status !== "resolved" ? (
              <button
                onClick={handleResolve}
                disabled={busy}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                Resolve
              </button>
            ) : null
          }
        >
          {counts && (
            <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
              {MUSTER_STATUSES.map((o) => (
                <div key={o.value} className="rounded-2xl border border-stone-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-[0.2em] text-stone-500">{o.label}</div>
                  <div className="mt-2 text-2xl font-semibold text-stone-900">
                    {counts[o.value] || 0}
                  </div>
                </div>
              ))}
            </div>
          )}
          {selected.description && (
            <p className="mb-3 text-sm text-stone-600">
              <strong>Description:</strong> {selected.description}
            </p>
          )}
          {selected.location && (
            <p className="mb-3 text-sm text-stone-600">
              <strong>Location:</strong> {selected.location}
            </p>
          )}
          <h3 className="mb-2 mt-4 font-display text-lg font-semibold text-stone-900">
            Evacuation Muster ({selected.musters?.length || 0})
          </h3>
          <MusterTable
            musters={selected.musters}
            onChange={handleMusterChange}
            busy={busy}
          />
          {selected.resolution_notes && (
            <p className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              <strong>Resolution:</strong> {selected.resolution_notes}
            </p>
          )}
        </Card>
      )}
    </div>
  );
}
