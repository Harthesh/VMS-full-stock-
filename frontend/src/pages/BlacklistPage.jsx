import { useEffect, useState } from "react";
import BlacklistForm from "../modules/blacklist/BlacklistForm";
import { createBlacklistEntry, fetchBlacklist, updateBlacklistEntry } from "../api/blacklist";
import Card from "../components/common/Card";
import Table from "../components/common/Table";
import StatusBadge from "../components/common/StatusBadge";

export default function BlacklistPage() {
  const [rows, setRows] = useState([]);
  const [editing, setEditing] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function loadRows() {
    fetchBlacklist().then(setRows);
  }

  useEffect(() => {
    loadRows();
  }, []);

  async function handleSubmit(payload) {
    setSubmitting(true);
    try {
      if (editing?.id) {
        await updateBlacklistEntry(editing.id, payload);
      } else {
        await createBlacklistEntry(payload);
      }
      setEditing(null);
      loadRows();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <BlacklistForm initialValues={editing} onSubmit={handleSubmit} submitting={submitting} />
      <Card title="Blacklist Records" subtitle="Searchable visitor watchlist used during scan and check-in.">
        <Table
          rows={rows}
          columns={[
            { key: "visitor_name", label: "Visitor" },
            { key: "mobile", label: "Mobile" },
            { key: "id_proof_number", label: "ID Proof" },
            { key: "action_type", label: "Action", render: (row) => <StatusBadge status={row.action_type} /> },
            { key: "reason", label: "Reason" },
            {
              key: "edit",
              label: "Edit",
              render: (row) => (
                <button className="font-semibold text-brand-600" onClick={() => setEditing(row)}>
                  Edit
                </button>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}

