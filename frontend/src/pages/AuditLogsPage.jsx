import { useEffect, useState } from "react";
import { fetchAuditLogs } from "../api/audit";
import Card from "../components/common/Card";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Table from "../components/common/Table";
import { formatDateTime } from "../utils/format";

export default function AuditLogsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading audit logs..." />;

  return (
    <Card title="Audit Logs" subtitle="Recent system mutations captured for accountability and troubleshooting.">
      <Table
        rows={rows}
        columns={[
          { key: "entity_type", label: "Entity" },
          { key: "entity_id", label: "Entity ID" },
          { key: "action", label: "Action" },
          {
            key: "details_json",
            label: "Details",
            render: (row) => <pre className="max-w-xs overflow-x-auto text-xs">{JSON.stringify(row.details_json || {}, null, 2)}</pre>,
          },
          { key: "created_at", label: "Created", render: (row) => formatDateTime(row.created_at) },
        ]}
      />
    </Card>
  );
}

