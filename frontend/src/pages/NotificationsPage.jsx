import { useEffect, useState } from "react";
import { fetchNotifications, markNotificationRead } from "../api/notifications";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Table from "../components/common/Table";
import { formatDateTime } from "../utils/format";

export default function NotificationsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  function loadNotifications() {
    fetchNotifications()
      .then(setRows)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadNotifications();
  }, []);

  async function handleMarkRead(id) {
    await markNotificationRead(id);
    loadNotifications();
  }

  if (loading) return <LoadingSpinner label="Loading notifications..." />;

  return (
    <Card title="Notifications" subtitle="System event feed for submissions, approvals, and gate movements.">
      <Table
        rows={rows}
        columns={[
          { key: "title", label: "Title" },
          { key: "message", label: "Message" },
          { key: "event_type", label: "Event" },
          { key: "status", label: "Status" },
          { key: "created_at", label: "Created", render: (row) => formatDateTime(row.created_at) },
          {
            key: "action",
            label: "Action",
            render: (row) =>
              row.status === "read" ? (
                <span className="text-sm text-stone-500">Read</span>
              ) : (
                <Button variant="secondary" onClick={() => handleMarkRead(row.id)}>
                  Mark Read
                </Button>
              ),
          },
        ]}
      />
    </Card>
  );
}

