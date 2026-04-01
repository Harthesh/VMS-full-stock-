import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Card from "../components/common/Card";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatusBadge from "../components/common/StatusBadge";
import Table from "../components/common/Table";
import { fetchPendingApprovals } from "../api/approvals";
import { formatDate, formatVisitorType } from "../utils/format";

export default function PendingApprovalsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingApprovals()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading approvals..." />;

  return (
    <Card title="Pending Approvals" subtitle="Requests waiting on your role or privileged oversight.">
      <Table
        rows={rows}
        columns={[
          { key: "request_no", label: "Request No." },
          { key: "visitor_name", label: "Visitor" },
          { key: "visitor_type", label: "Type", render: (row) => formatVisitorType(row.visitor_type) },
          { key: "visit_date", label: "Visit Date", render: (row) => formatDate(row.visit_date) },
          { key: "status", label: "Status", render: (row) => <StatusBadge status={row.status} /> },
          {
            key: "action",
            label: "Action",
            render: (row) => (
              <Link className="font-semibold text-brand-600" to={`/approvals/${row.id}`}>
                Open
              </Link>
            ),
          },
        ]}
      />
    </Card>
  );
}

