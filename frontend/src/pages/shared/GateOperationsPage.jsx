import { useState } from "react";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import StatusBadge from "../../components/common/StatusBadge";
import { checkInVisitor, checkOutVisitor, lookupVisitor } from "../../api/gate";
import GateSearchPanel from "../../modules/gate/GateSearchPanel";
import { formatDate, formatVisitorType } from "../../utils/format";

export default function GateOperationsPage({ mode }) {
  const [result, setResult] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [feedbackTone, setFeedbackTone] = useState("success");
  const [submitting, setSubmitting] = useState(false);

  async function handleSearch(values) {
    setFeedback("");
    setFeedbackTone("success");
    try {
      const data = await lookupVisitor(values);
      setResult(data);
    } catch (apiError) {
      setResult(null);
      setFeedbackTone("error");
      setFeedback(apiError.response?.data?.detail || "Unable to find a matching visitor request.");
    }
  }

  async function handleAction(actionType) {
    if (!result) return;
    setSubmitting(true);
    setFeedback("");
    setFeedbackTone("success");
    try {
      const payload = { gate_entry_point: "Main Gate", remarks: mode === "scan" ? "Processed after QR scan" : "" };
      if (actionType === "check-in") {
        await checkInVisitor(result.request.id, payload);
        setFeedback("Visitor checked in successfully.");
      } else if (actionType === "check-out") {
        await checkOutVisitor(result.request.id, payload);
        setFeedback("Visitor checked out successfully.");
      }
      const refreshed = await lookupVisitor({ request_no: result.request.request_no });
      setResult(refreshed);
    } catch (apiError) {
      setFeedbackTone("error");
      setFeedback(apiError.response?.data?.detail || "Unable to complete gate action.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <GateSearchPanel mode={mode} onSearch={handleSearch} />
      {feedback && (
        <div
          className={`rounded-2xl px-4 py-3 text-sm ${
            feedbackTone === "error" ? "border border-red-200 bg-red-50 text-red-700" : "bg-brand-50 text-brand-700"
          }`}
        >
          {feedback}
        </div>
      )}
      {result && (
        <Card title={`${result.request.request_no} · ${result.request.visitor_name}`} subtitle={`${formatVisitorType(result.request.visitor_type)} · ${formatDate(result.request.visit_date)}`}>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Detail label="Status" value={<StatusBadge status={result.request.status} />} />
            <Detail label="Host" value={result.host?.full_name || "-"} />
            <Detail label="Badge" value={result.badge?.badge_no || result.request.badge_no || "-"} />
            <Detail label="QR Value" value={result.badge?.qr_code_value || result.request.qr_code_value || "-"} />
            <Detail label="ID Verification" value={result.request.is_id_verified ? "Verified" : "Pending"} />
            <Detail label="Visitor Email" value={result.request.email || "-"} />
            <Detail label="Mobile" value={result.request.mobile || "-"} />
            <Detail label="Check-In" value={result.request.check_in_time ? "Completed" : "Pending"} />
            <Detail label="Check-Out" value={result.request.check_out_time ? "Completed" : "Pending"} />
          </div>
          {(result.blacklist_action || result.blacklist_reason) && (
            <div className="mt-5 rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              {result.blacklist_action?.replaceAll("_", " ")}: {result.blacklist_reason}
            </div>
          )}
          <div className="mt-5 flex flex-wrap justify-end gap-3">
            {mode !== "check-out" && (
              <Button onClick={() => handleAction("check-in")} disabled={submitting || !result.can_check_in}>
                {submitting ? "Processing..." : "Check In"}
              </Button>
            )}
            {mode !== "check-in" && (
              <Button variant="secondary" onClick={() => handleAction("check-out")} disabled={submitting || !result.can_check_out}>
                {submitting ? "Processing..." : "Check Out"}
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">{label}</div>
      <div className="mt-2 text-sm font-medium text-stone-800">{value}</div>
    </div>
  );
}
