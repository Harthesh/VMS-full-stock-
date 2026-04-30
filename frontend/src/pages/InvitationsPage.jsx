import { useEffect, useState } from "react";
import Card from "../components/common/Card";
import Table from "../components/common/Table";
import {
  cancelInvitation,
  createInvitation,
  fetchInvitations,
  resendInvitation,
} from "../api/invitations";

const VISITOR_TYPES = [
  { value: "customer", label: "Customer" },
  { value: "vip_customer", label: "VIP Customer" },
  { value: "supplier", label: "Supplier" },
  { value: "candidate", label: "Candidate" },
  { value: "contractor", label: "Contractor" },
];

const statusColor = {
  pending: "bg-amber-100 text-amber-700",
  used: "bg-emerald-100 text-emerald-700",
  expired: "bg-stone-200 text-stone-700",
  cancelled: "bg-red-100 text-red-700",
};

function CreateForm({ onSubmit, busy }) {
  const [form, setForm] = useState({
    visitor_name: "",
    visitor_email: "",
    visitor_mobile: "",
    company_name: "",
    visitor_type: "customer",
    visit_date: "",
    visit_time: "",
    purpose: "",
    expires_in_days: 7,
  });

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function submit(e) {
    e.preventDefault();
    if (!form.visitor_name || !form.visit_date || !form.purpose) return;
    const payload = { ...form };
    if (!payload.visit_time) delete payload.visit_time;
    if (!payload.visitor_email) delete payload.visitor_email;
    payload.expires_in_days = Number(payload.expires_in_days) || 7;
    onSubmit(payload);
  }

  return (
    <form onSubmit={submit} className="grid gap-3 md:grid-cols-2">
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Visitor name *
        </label>
        <input
          required
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visitor_name}
          onChange={(e) => update("visitor_name", e.target.value)}
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Visitor email
        </label>
        <input
          type="email"
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visitor_email}
          onChange={(e) => update("visitor_email", e.target.value)}
          placeholder="visitor@example.com"
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Mobile
        </label>
        <input
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visitor_mobile}
          onChange={(e) => update("visitor_mobile", e.target.value)}
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Company
        </label>
        <input
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.company_name}
          onChange={(e) => update("company_name", e.target.value)}
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Visitor type
        </label>
        <select
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visitor_type}
          onChange={(e) => update("visitor_type", e.target.value)}
        >
          {VISITOR_TYPES.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Expires in (days)
        </label>
        <input
          type="number"
          min={1}
          max={60}
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.expires_in_days}
          onChange={(e) => update("expires_in_days", e.target.value)}
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Visit date *
        </label>
        <input
          type="date"
          required
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visit_date}
          onChange={(e) => update("visit_date", e.target.value)}
        />
      </div>
      <div>
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Visit time
        </label>
        <input
          type="time"
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.visit_time}
          onChange={(e) => update("visit_time", e.target.value)}
        />
      </div>
      <div className="md:col-span-2">
        <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
          Purpose *
        </label>
        <input
          required
          className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
          value={form.purpose}
          onChange={(e) => update("purpose", e.target.value)}
          placeholder="Why is this visitor coming?"
        />
      </div>
      <div className="md:col-span-2 flex justify-end">
        <button
          type="submit"
          disabled={busy}
          className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {busy ? "Sending…" : "Send Invitation"}
        </button>
      </div>
    </form>
  );
}

export default function InvitationsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchInvitations({ only_mine: false });
      setRows(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(form) {
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const inv = await createInvitation(form);
      const link = `${window.location.origin}/invite/${inv.token}`;
      setInfo(`Invitation sent — public link: ${link}`);
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleCancel(row) {
    if (!window.confirm(`Cancel invitation for ${row.visitor_name}?`)) return;
    setBusy(true);
    try {
      await cancelInvitation(row.id);
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleResend(row) {
    setBusy(true);
    try {
      await resendInvitation(row.id);
      setInfo(`Invitation email resent to ${row.visitor_email || "visitor"}`);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  function copyLink(token) {
    const link = `${window.location.origin}/invite/${token}`;
    navigator.clipboard?.writeText(link);
    setInfo(`Copied ${link}`);
  }

  return (
    <div className="space-y-6">
      <Card
        title="Send Visitor Invitation"
        subtitle="Pre-register a visitor by sending them a one-time link to complete their details. The submission auto-creates a Visitor Request and starts the approval flow."
      >
        <CreateForm onSubmit={handleCreate} busy={busy} />
      </Card>

      {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
      {info && <div className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800 break-all">{info}</div>}

      <Card title="Invitations" subtitle={loading ? "Loading…" : `${rows.length} invitation(s)`}>
        <Table
          rows={rows}
          emptyText="No invitations yet."
          columns={[
            {
              key: "visitor",
              label: "Visitor",
              render: (r) => (
                <div>
                  <div className="font-medium text-stone-900">{r.visitor_name}</div>
                  <div className="text-xs text-stone-500">
                    {r.visitor_email || "—"} · {r.visitor_mobile || "—"}
                  </div>
                </div>
              ),
            },
            { key: "company_name", label: "Company", render: (r) => r.company_name || "—" },
            { key: "visit_date", label: "Visit" , render: (r) => `${r.visit_date}${r.visit_time ? " " + r.visit_time.slice(0,5) : ""}` },
            { key: "visitor_type", label: "Type" },
            {
              key: "status",
              label: "Status",
              render: (r) => (
                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusColor[r.status] || "bg-stone-200 text-stone-700"}`}>
                  {r.status}
                </span>
              ),
            },
            {
              key: "expires",
              label: "Expires",
              render: (r) => new Date(r.expires_at).toLocaleString(),
            },
            {
              key: "host",
              label: "Host",
              render: (r) => r.host?.full_name || "—",
            },
            {
              key: "actions",
              label: "Actions",
              render: (r) => (
                <div className="flex flex-wrap gap-2">
                  <button
                    className="text-xs font-semibold text-brand-600"
                    onClick={() => copyLink(r.token)}
                  >
                    Copy link
                  </button>
                  {r.status === "pending" && (
                    <>
                      <button
                        className="text-xs font-semibold text-stone-600"
                        onClick={() => handleResend(r)}
                        disabled={busy}
                      >
                        Resend
                      </button>
                      <button
                        className="text-xs font-semibold text-red-600"
                        onClick={() => handleCancel(r)}
                        disabled={busy}
                      >
                        Cancel
                      </button>
                    </>
                  )}
                  {r.visitor_request_id && (
                    <a
                      className="text-xs font-semibold text-emerald-700"
                      href={`/requests/${r.visitor_request_id}`}
                    >
                      View request
                    </a>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
