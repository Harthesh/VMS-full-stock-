import { useEffect, useState } from "react";
import { createRole, fetchRoles, updateRole } from "../api/admin";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import FormField from "../components/common/FormField";
import Table from "../components/common/Table";

export default function RolesPage() {
  const [rows, setRows] = useState([]);
  const [values, setValues] = useState({ key: "", name: "", description: "" });
  const [editingId, setEditingId] = useState(null);

  function loadRoles() {
    fetchRoles().then(setRows);
  }

  useEffect(() => {
    loadRoles();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (editingId) {
      await updateRole(editingId, { name: values.name, description: values.description });
    } else {
      await createRole(values);
    }
    setValues({ key: "", name: "", description: "" });
    setEditingId(null);
    loadRoles();
  }

  return (
    <div className="space-y-6">
      <Card title="Role Management" subtitle="Maintain workflow and menu roles used by the backend RBAC layer.">
        <form className="grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <FormField label="Role Key" value={values.key} onChange={(event) => setValues((current) => ({ ...current, key: event.target.value }))} disabled={Boolean(editingId)} />
          <FormField label="Role Name" value={values.name} onChange={(event) => setValues((current) => ({ ...current, name: event.target.value }))} />
          <FormField label="Description" value={values.description} onChange={(event) => setValues((current) => ({ ...current, description: event.target.value }))} />
          <div className="md:col-span-3 flex justify-end">
            <Button type="submit">{editingId ? "Update Role" : "Create Role"}</Button>
          </div>
        </form>
      </Card>
      <Card title="Roles" subtitle="Current system roles available for routing, approvals, and menus.">
      <Table
        rows={rows}
        columns={[
          { key: "name", label: "Role" },
          { key: "key", label: "Key" },
          { key: "description", label: "Description" },
          {
            key: "edit",
            label: "Edit",
            render: (row) => (
              <button
                className="font-semibold text-brand-600"
                onClick={() => {
                  setEditingId(row.id);
                  setValues({ key: row.key, name: row.name, description: row.description || "" });
                }}
              >
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
