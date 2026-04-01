import { useEffect, useMemo, useState } from "react";
import {
  fetchBlacklistAlertReport,
  fetchDailyGateMovement,
  fetchPendingApprovalReport,
  fetchVisitorSummary,
  fetchVisitorTypeSummary,
} from "../api/reports";
import Card from "../components/common/Card";
import FormField from "../components/common/FormField";
import Table from "../components/common/Table";
import { formatDate, formatDateTime, formatVisitorType } from "../utils/format";

export default function ReportsPage() {
  const [visitorSummary, setVisitorSummary] = useState([]);
  const [gateMovement, setGateMovement] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [blacklistAlerts, setBlacklistAlerts] = useState([]);
  const [visitorTypeSummary, setVisitorTypeSummary] = useState([]);
  const [filters, setFilters] = useState({ query: "", status: "", start_date: "", end_date: "" });

  useEffect(() => {
    const params = {
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
    };
    Promise.all([
      fetchVisitorSummary(params),
      fetchDailyGateMovement(params),
      fetchPendingApprovalReport(params),
      fetchBlacklistAlertReport(params),
      fetchVisitorTypeSummary(params),
    ]).then(([visitorData, gateData, approvalData, blacklistData, summaryData]) => {
      setVisitorSummary(visitorData);
      setGateMovement(gateData);
      setPendingApprovals(approvalData);
      setBlacklistAlerts(blacklistData);
      setVisitorTypeSummary(summaryData);
    });
  }, [filters.start_date, filters.end_date]);

  const filteredRows = useMemo(
    () =>
      visitorSummary.filter((row) => {
        const matchesQuery =
          !filters.query ||
          row.request_no.toLowerCase().includes(filters.query.toLowerCase()) ||
          row.visitor_name.toLowerCase().includes(filters.query.toLowerCase());
        const matchesStatus = !filters.status || row.status === filters.status;
        return matchesQuery && matchesStatus;
      }),
    [filters, visitorSummary],
  );

  return (
    <div className="space-y-6">
      <Card title="Reports" subtitle="Export-ready operational reporting surface backed by API data and client-side filters.">
        <div className="grid gap-4 md:grid-cols-4">
          <FormField label="Search" value={filters.query} onChange={(event) => setFilters((current) => ({ ...current, query: event.target.value }))} />
          <FormField label="Status" value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))} placeholder="approved" />
          <FormField label="Start Date" type="date" value={filters.start_date} onChange={(event) => setFilters((current) => ({ ...current, start_date: event.target.value }))} />
          <FormField label="End Date" type="date" value={filters.end_date} onChange={(event) => setFilters((current) => ({ ...current, end_date: event.target.value }))} />
        </div>
      </Card>
      <Card title="Visitor List Report" subtitle="Request registry with date, type, host, and workflow status.">
        <Table
          rows={filteredRows}
          columns={[
            { key: "request_no", label: "Request No." },
            { key: "visitor_name", label: "Visitor" },
            { key: "visitor_type", label: "Type", render: (row) => formatVisitorType(row.visitor_type) },
            { key: "visit_date", label: "Visit Date", render: (row) => formatDate(row.visit_date) },
            { key: "status", label: "Status" },
            { key: "host_name", label: "Host" },
          ]}
        />
      </Card>
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Daily Gate Movement" subtitle="Check-in/check-out activity in the selected period.">
          <Table
            rows={gateMovement}
            columns={[
              { key: "request_no", label: "Request No." },
              { key: "visitor_name", label: "Visitor" },
              { key: "check_in_time", label: "Check-In", render: (row) => formatDateTime(row.check_in_time) },
              { key: "check_out_time", label: "Check-Out", render: (row) => formatDateTime(row.check_out_time) },
              { key: "badge_no", label: "Badge" },
            ]}
          />
        </Card>
        <Card title="Pending Approval Report" subtitle="Requests currently waiting on approval actions.">
          <Table
            rows={pendingApprovals}
            columns={[
              { key: "request_no", label: "Request No." },
              { key: "visitor_name", label: "Visitor" },
              { key: "current_status", label: "Status" },
              { key: "pending_role", label: "Pending Role" },
              { key: "visit_date", label: "Visit Date", render: (row) => formatDate(row.visit_date) },
            ]}
          />
        </Card>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Blacklist Alert Report" subtitle="Gate warnings and blocked entries triggered by watchlist matches.">
          <Table
            rows={blacklistAlerts}
            columns={[
              { key: "request_no", label: "Request No." },
              { key: "visitor_name", label: "Visitor" },
              { key: "action", label: "Action" },
              { key: "remarks", label: "Remarks" },
              { key: "created_at", label: "Created", render: (row) => formatDateTime(row.created_at) },
            ]}
          />
        </Card>
        <Card title="Visitor Type Summary" subtitle="Aggregate volume by visitor category.">
          <Table
            rows={visitorTypeSummary}
            columns={[
              { key: "visitor_type", label: "Type", render: (row) => formatVisitorType(row.visitor_type) },
              { key: "count", label: "Count" },
            ]}
          />
        </Card>
      </div>
    </div>
  );
}
