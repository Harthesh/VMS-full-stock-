import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import LoadError from "../components/common/LoadError";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatusBadge from "../components/common/StatusBadge";
import VisitorQrCard from "../components/common/VisitorQrCard";
import { cancelRequest, fetchRequest, submitRequest } from "../api/requests";
import useAuth from "../hooks/useAuth";
import RequestTimeline from "../modules/requests/RequestTimeline";
import { formatDate, formatDateTime, formatVisitorType } from "../utils/format";

export default function RequestDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRequest(id)
      .then(setRequest)
      .catch((apiError) => setError(apiError.response?.data?.detail || "Unable to load this request."))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmitRequest() {
    setSubmitting(true);
    try {
      const updated = await submitRequest(id);
      setRequest(updated);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCancel() {
    const remarks = window.prompt("Enter cancellation remarks", "Cancelled by requester");
    if (!remarks) return;
    setSubmitting(true);
    try {
      const updated = await cancelRequest(id, remarks);
      setRequest(updated);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingSpinner label="Loading request..." />;
  if (error || !request) return <LoadError title="Request unavailable" message={error || "Unable to load this request."} />;

  const roleKeys = user?.roles?.map((role) => role.key) || [];
  const canSubmit = request.status === "draft" || request.status === "sent_back";
  const canEdit = canSubmit;
  const canPrintBadge = Boolean(request.badge?.badge_no || request.badge_no || request.qr_code_value);

  return (
    <div className="space-y-6">
      <Card
        title={`${request.request_no} · ${request.visitor_name}`}
        subtitle={`${formatVisitorType(request.visitor_type)} visit scheduled for ${formatDate(request.visit_date)}`}
        action={
          <div className="flex flex-wrap gap-3">
            <StatusBadge status={request.status} />
            {canEdit && (
              <Link className="btn-secondary" to={`/requests/${request.id}/edit`}>
                Edit Draft
              </Link>
            )}
            {canSubmit && (
              <Button onClick={handleSubmitRequest} disabled={submitting}>
                {submitting ? "Submitting..." : "Submit"}
              </Button>
            )}
            {!["checked_in", "checked_out", "cancelled"].includes(request.status) && (
              <Button variant="danger" onClick={handleCancel} disabled={submitting}>
                Cancel
              </Button>
            )}
            {canPrintBadge && (
              <Link className="btn-secondary" to={`/badge/${request.id}`}>
                Badge Preview
              </Link>
            )}
            {roleKeys.some((role) => ["manager", "hod", "ceo_office", "security", "it", "bd_sales", "admin"].includes(role)) && (
              <Link className="btn-secondary" to={`/approvals/${request.id}`}>
                Approval View
              </Link>
            )}
          </div>
        }
      >
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <Detail label="Company" value={request.company_name} />
          <Detail label="Mobile" value={request.mobile} />
          <Detail label="Email" value={request.email} />
          <Detail label="Host" value={request.host_user?.full_name} />
          <Detail label="Department" value={request.department?.name} />
          <Detail label="Security Clearance" value={request.requires_security_clearance ? "Yes" : "No"} />
          <Detail label="IT Access" value={request.requires_it_access ? "Yes" : "No"} />
          <Detail label="Hospitality" value={request.requires_hospitality ? "Yes" : "No"} />
          <Detail label="Badge No." value={request.badge?.badge_no || request.badge_no} />
          <Detail label="Check-In" value={formatDateTime(request.check_in_time)} />
          <Detail label="Check-Out" value={formatDateTime(request.check_out_time)} />
          <Detail label="ID Verified" value={request.is_id_verified ? "Verified" : "Pending"} />
        </div>
        <div className="mt-5 rounded-2xl bg-stone-50 p-4 text-sm text-stone-700">{request.purpose}</div>
      </Card>

      {request.hospitality_request && (
        <Card title="Hospitality" subtitle="Operational logistics attached to this visit.">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <Detail label="Meal" value={request.hospitality_request.meal_required ? "Required" : "Not required"} />
            <Detail label="Transport" value={request.hospitality_request.transport_required ? "Required" : "Not required"} />
            <Detail label="Meeting Room" value={request.hospitality_request.meeting_room} />
            <Detail label="Escort" value={request.hospitality_request.escort_needed ? "Required" : "Not required"} />
            <Detail label="Logistics Status" value={request.hospitality_request.logistics_status} />
            <Detail label="VIP Notes" value={request.hospitality_request.vip_notes} />
          </div>
        </Card>
      )}

      <VisitorQrCard request={request} />

      <RequestTimeline request={request} />
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">{label}</div>
      <div className="mt-2 text-sm font-medium text-stone-800">{value || "-"}</div>
    </div>
  );
}
