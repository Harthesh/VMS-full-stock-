import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Card from "../components/common/Card";
import LoadingSpinner from "../components/common/LoadingSpinner";
import StatusBadge from "../components/common/StatusBadge";
import Table from "../components/common/Table";
import { fetchRequests } from "../api/requests";
import { formatDate, formatVisitorType } from "../utils/format";

export default function MyRequestsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading requests..." />;

  const columns = [
    { key: "request_no", label: "Request No." },
    { key: "visitor_name", label: "Visitor" },
    { key: "visitor_type", label: "Type", render: (row) => formatVisitorType(row.visitor_type) },
    { key: "visit_date", label: "Visit Date", render: (row) => formatDate(row.visit_date) },
    { key: "status", label: "Status", render: (row) => <StatusBadge status={row.status} /> },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div className="flex gap-3">
          <Link className="font-semibold text-brand-600" to={`/requests/${row.id}`}>
            View
          </Link>
          {row.status === "draft" || row.status === "sent_back" ? (
            <Link className="font-semibold text-stone-700" to={`/requests/${row.id}/edit`}>
              Edit
            </Link>
          ) : null}
        </div>
      ),
    },
  ];

  return (
    <Card title="My Requests" subtitle="All visitor requests visible for your current role scope.">
      <Table columns={columns} rows={rows} />
    </Card>
  );
}

