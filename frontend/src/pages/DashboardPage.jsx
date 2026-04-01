import { useEffect, useState } from "react";
import Card from "../components/common/Card";
import LoadError from "../components/common/LoadError";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatCard from "../components/common/StatCard";
import { fetchDashboardSummary } from "../api/dashboard";
import { formatRole, formatVisitorType } from "../utils/format";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardSummary()
      .then(setSummary)
      .catch((apiError) => setError(apiError.response?.data?.detail || "Unable to load dashboard data right now."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;
  if (error || !summary) {
    return <LoadError title="Dashboard unavailable" message={error || "Unable to load dashboard data right now."} />;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Requests Today" value={summary.total_requests_today} />
        <StatCard label="Pending Approvals" value={summary.pending_approvals} tone="accent" />
        <StatCard label="Approved Today" value={summary.approved_visitors_today} tone="neutral" />
        <StatCard label="Checked-In Now" value={summary.checked_in_visitors_now} />
        <StatCard label="Checked-Out Today" value={summary.checked_out_visitors_today} tone="accent" />
        <StatCard label="Blacklist Alerts" value={summary.blacklisted_visitors_detected} tone="neutral" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <Card title="Request Trend" subtitle="Daily intake across the last seven days.">
          <div className="flex min-h-56 items-end gap-3">
            {summary.trend_chart.map((point) => (
              <div key={point.date} className="flex flex-1 flex-col items-center gap-2">
                <div
                  className="w-full rounded-t-2xl bg-gradient-to-t from-brand-600 to-accent-500"
                  style={{ height: `${Math.max(point.count * 16, 12)}px` }}
                />
                <div className="text-xs text-stone-500">{point.date.slice(5)}</div>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Approval Pending by Role" subtitle="Current active steps grouped by responsible role.">
          <div className="space-y-3">
            {Object.entries(summary.approval_pending_by_role).map(([role, count]) => (
              <div key={role} className="flex items-center justify-between rounded-xl border border-stone-200 px-4 py-3">
                <span className="text-sm font-medium text-stone-700">{formatRole(role)}</span>
                <span className="rounded-full bg-stone-900 px-3 py-1 text-xs font-semibold text-white">{count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Visitor Mix" subtitle="Overall request volume by visitor type.">
          <div className="space-y-3">
            {Object.entries(summary.visitor_count_by_type).map(([visitorType, count]) => (
              <div key={visitorType}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium text-stone-700">{formatVisitorType(visitorType)}</span>
                  <span className="text-stone-500">{count}</span>
                </div>
                <div className="h-3 rounded-full bg-stone-100">
                  <div className="h-3 rounded-full bg-brand-600" style={{ width: `${Math.max(count * 10, 8)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Operations Notes" subtitle="Recommended operational usage for this build.">
          <ul className="space-y-3 text-sm text-stone-600">
            <li>Use Pending Approvals for role-driven transitions. Backend rules enforce the next valid state.</li>
            <li>Use Gate Scan for QR/manual lookup before check-in to validate blacklist and approval status.</li>
            <li>Use Badge Preview once approval is complete to print a compact gate badge with QR.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
