import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPublicInvitation, submitPublicInvitation } from "../api/invitations";

const ID_PROOF_TYPES = [
  { value: "", label: "Select" },
  { value: "passport", label: "Passport" },
  { value: "aadhaar", label: "Aadhaar" },
  { value: "pan", label: "PAN" },
  { value: "driving_license", label: "Driving License" },
  { value: "voter_id", label: "Voter ID" },
  { value: "other", label: "Other" },
];

export default function PublicInvitationPage() {
  const { token } = useParams();
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [form, setForm] = useState({
    visitor_name: "",
    visitor_email: "",
    mobile: "",
    company_name: "",
    id_proof_type: "",
    id_proof_number: "",
    purpose: "",
    remarks: "",
  });

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchPublicInvitation(token)
      .then((data) => {
        if (cancelled) return;
        setInvitation(data);
        setForm((prev) => ({
          ...prev,
          visitor_name: data.visitor_name || "",
          visitor_email: data.visitor_email || "",
          mobile: data.visitor_mobile || "",
          company_name: data.company_name || "",
          purpose: data.purpose || "",
        }));
      })
      .catch((err) => setError(err?.response?.data?.detail || err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [token]);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload = { ...form };
      if (!payload.visitor_email) delete payload.visitor_email;
      const result = await submitPublicInvitation(token, payload);
      setSuccess(result);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl p-6 text-center text-stone-500">
        Loading invitation…
      </div>
    );
  }

  if (error && !invitation) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <div className="rounded-2xl bg-red-50 p-6 text-red-700">
          <h1 className="font-display text-xl font-semibold">Invitation Error</h1>
          <p className="mt-2">{error}</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <div className="rounded-2xl bg-emerald-50 p-6 text-emerald-800">
          <h1 className="font-display text-2xl font-semibold">Pre-registration submitted</h1>
          <p className="mt-2">
            Your visit request <strong>{success.request_no}</strong> has been created and is now in
            the approval flow.
          </p>
          <p className="mt-2">
            Status: <strong>{success.status?.replace(/_/g, " ")}</strong>
          </p>
          <p className="mt-2 text-sm">
            You'll receive an email once approved. Please bring a valid ID proof to the gate.
          </p>
        </div>
      </div>
    );
  }

  if (!invitation) return null;

  const isUsable = invitation.status === "pending";

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
        <div className="border-b border-stone-200 pb-4">
          <h1 className="font-display text-2xl font-semibold text-stone-900">
            Visitor Pre-Registration
          </h1>
          <p className="mt-2 text-sm text-stone-600">
            <strong>{invitation.host_name}</strong> ({invitation.host_email}) has invited you for
            a visit on <strong>{invitation.visit_date}</strong>
            {invitation.visit_time ? ` at ${invitation.visit_time.slice(0, 5)}` : ""}.
          </p>
          <p className="mt-1 text-sm text-stone-500">
            Status: <span className="font-semibold">{invitation.status}</span>
          </p>
        </div>

        {!isUsable && (
          <div className="mt-4 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
            This invitation is <strong>{invitation.status}</strong> and cannot be submitted. Please
            contact your host.
          </div>
        )}

        {error && (
          <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Full name *
            </label>
            <input
              required
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.visitor_name}
              onChange={(e) => update("visitor_name", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Email
            </label>
            <input
              type="email"
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.visitor_email}
              onChange={(e) => update("visitor_email", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Mobile *
            </label>
            <input
              required
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.mobile}
              onChange={(e) => update("mobile", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Company
            </label>
            <input
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.company_name}
              onChange={(e) => update("company_name", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              ID proof type
            </label>
            <select
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.id_proof_type}
              onChange={(e) => update("id_proof_type", e.target.value)}
            >
              {ID_PROOF_TYPES.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              ID proof number
            </label>
            <input
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.id_proof_number}
              onChange={(e) => update("id_proof_number", e.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Purpose
            </label>
            <input
              disabled={!isUsable}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.purpose}
              onChange={(e) => update("purpose", e.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">
              Anything else we should know?
            </label>
            <textarea
              disabled={!isUsable}
              rows={3}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              value={form.remarks}
              onChange={(e) => update("remarks", e.target.value)}
            />
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button
              type="submit"
              disabled={!isUsable || submitting}
              className="rounded-xl bg-brand-600 px-6 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {submitting ? "Submitting…" : "Submit Pre-Registration"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
