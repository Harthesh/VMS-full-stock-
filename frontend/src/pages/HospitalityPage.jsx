import { useEffect, useMemo, useState } from "react";
import Card from "../components/common/Card";
import Table from "../components/common/Table";
import StatusBadge from "../components/common/StatusBadge";
import { fetchHospitality, updateHospitality } from "../api/hospitality";

const STATUS_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In Progress" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
];

const statusBadgeColor = {
  pending: "bg-amber-100 text-amber-700",
  in_progress: "bg-sky-100 text-sky-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-stone-300 text-stone-700",
};

function ServiceTags({ row }) {
  const tags = [];
  if (row.meal_required) tags.push("Meal");
  if (row.transport_required) tags.push("Transport");
  if (row.escort_needed) tags.push("Escort");
  if (row.meeting_room) tags.push(`Room: ${row.meeting_room}`);
  if (!tags.length) return <span className="text-stone-400">—</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((t) => (
        <span key={t} className="rounded-full bg-stone-100 px-2 py-0.5 text-xs text-stone-700">
          {t}
        </span>
      ))}
    </div>
  );
}

export default function HospitalityPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [savingId, setSavingId] = useState(null);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const data = await fetchHospitality(params);
      setRows(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  async function changeStatus(row, nextStatus) {
    setSavingId(row.id);
    try {
      const updated = await updateHospitality(row.id, { logistics_status: nextStatus });
      setRows((prev) => prev.map((r) => (r.id === row.id ? updated : r)));
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setSavingId(null);
    }
  }

  const counts = useMemo(() => {
    const out = { pending: 0, in_progress: 0, completed: 0, cancelled: 0 };
    rows.forEach((r) => {
      out[r.logistics_status] = (out[r.logistics_status] || 0) + 1;
    });
    return out;
  }, [rows]);

  return (
    <div className="space-y-6">
      <Card
        title="Hospitality Requests"
        subtitle="Coordinate meals, transport, escorts, and meeting room logistics for incoming visitors."
        action={
          <select
            className="rounded-xl border border-stone-200 px-3 py-2 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        }
      >
        <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          {STATUS_OPTIONS.map((o) => (
            <div key={o.value} className="rounded-2xl border border-stone-200 bg-white p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-stone-500">{o.label}</div>
              <div className="mt-2 text-2xl font-semibold text-stone-900">{counts[o.value] || 0}</div>
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        {loading ? (
          <div className="panel-muted p-8 text-center text-sm text-stone-500">Loading…</div>
        ) : (
          <Table
            rows={rows}
            emptyText="No hospitality requests found."
            columns={[
              {
                key: "request",
                label: "Request",
                render: (r) => (
                  <div>
                    <div className="font-semibold text-stone-900">{r.visitor_request.request_no}</div>
                    <div className="text-xs text-stone-500">
                      {r.visitor_request.visit_date}
                      {r.visitor_request.visit_time ? ` ${r.visitor_request.visit_time.slice(0, 5)}` : ""}
                    </div>
                  </div>
                ),
              },
              {
                key: "visitor",
                label: "Visitor",
                render: (r) => (
                  <div>
                    <div className="font-medium text-stone-900">{r.visitor_request.visitor_name}</div>
                    <div className="text-xs text-stone-500">{r.visitor_request.company_name || "—"}</div>
                  </div>
                ),
              },
              {
                key: "host",
                label: "Host",
                render: (r) =>
                  r.visitor_request.host_user ? (
                    <div>
                      <div>{r.visitor_request.host_user.full_name}</div>
                      <div className="text-xs text-stone-500">{r.visitor_request.host_user.email}</div>
                    </div>
                  ) : (
                    <span className="text-stone-400">—</span>
                  ),
              },
              { key: "services", label: "Services", render: (r) => <ServiceTags row={r} /> },
              {
                key: "request_status",
                label: "Visit Status",
                render: (r) => <StatusBadge status={r.visitor_request.status} />,
              },
              {
                key: "logistics_status",
                label: "Logistics",
                render: (r) => (
                  <span
                    className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                      statusBadgeColor[r.logistics_status] || "bg-stone-200 text-stone-700"
                    }`}
                  >
                    {r.logistics_status.replace("_", " ")}
                  </span>
                ),
              },
              {
                key: "actions",
                label: "Actions",
                render: (r) => (
                  <select
                    className="rounded-xl border border-stone-200 px-2 py-1 text-xs"
                    value={r.logistics_status}
                    disabled={savingId === r.id}
                    onChange={(e) => changeStatus(r, e.target.value)}
                  >
                    {STATUS_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                ),
              },
            ]}
          />
        )}
      </Card>
    </div>
  );
}
