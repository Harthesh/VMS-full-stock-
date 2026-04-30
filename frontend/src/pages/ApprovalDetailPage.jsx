import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Card from "../components/common/Card";
import LoadError from "../components/common/LoadError";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatusBadge from "../components/common/StatusBadge";
import VisitorQrCard from "../components/common/VisitorQrCard";
import { submitApprovalAction } from "../api/approvals";
import { fetchRequest } from "../api/requests";
import ApprovalActionPanel from "../modules/approvals/ApprovalActionPanel";
import RequestTimeline from "../modules/requests/RequestTimeline";
import { formatDate, formatVisitorType } from "../utils/format";

export default function ApprovalDetailPage() {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRequest(id)
      .then(setRequest)
      .catch((apiError) => setError(apiError.response?.data?.detail || "Unable to load this approval request."))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(payload) {
    setSubmitting(true);
    try {
      const updated = await submitApprovalAction(id, payload);
      setRequest(updated);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingSpinner label="Loading approval detail..." />;
  if (error || !request) {
    return <LoadError title="Approval unavailable" message={error || "Unable to load this approval request."} />;
  }

  return (
    <div className="space-y-6">
      <Card title={`${request.request_no} · ${request.visitor_name}`} subtitle={`${formatVisitorType(request.visitor_type)} · ${formatDate(request.visit_date)}`}>
        <div className="flex flex-wrap gap-3">
          <StatusBadge status={request.status} />
          <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-stone-600">
            Level {request.current_approval_level}
          </div>
        </div>
        <div className="mt-5 rounded-2xl bg-stone-50 p-4 text-sm text-stone-700">{request.purpose}</div>
      </Card>
      <VisitorQrCard request={request} />
      <ApprovalActionPanel onSubmit={handleSubmit} submitting={submitting} />
      <RequestTimeline request={request} />
    </div>
  );
}
