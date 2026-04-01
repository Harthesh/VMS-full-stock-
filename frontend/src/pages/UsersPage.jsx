import { useEffect, useMemo, useState } from "react";
import { createUser, fetchDepartments, fetchRoles, fetchUsers, updateUser } from "../api/admin";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import FormField from "../components/common/FormField";
import SelectField from "../components/common/SelectField";
import Table from "../components/common/Table";

const blankUser = {
  full_name: "",
  email: "",
  mobile: "",
  password: "",
  department_id: "",
  role_ids: [],
  employee_code: "",
  is_active: true,
};

export default function UsersPage() {
  const [rows, setRows] = useState([]);
  const [roles, setRoles] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [values, setValues] = useState(blankUser);
  const [editingId, setEditingId] = useState(null);

  function loadData() {
    Promise.all([fetchUsers(), fetchRoles(), fetchDepartments()]).then(([users, roleData, departmentData]) => {
      setRows(users);
      setRoles(roleData);
      setDepartments(departmentData);
    });
  }

  useEffect(() => {
    loadData();
  }, []);

  const roleOptions = useMemo(() => roles.map((role) => ({ value: String(role.id), label: role.name })), [roles]);
  const departmentOptions = useMemo(
    () => departments.map((department) => ({ value: String(department.id), label: department.name })),
    [departments],
  );

  async function handleSubmit(event) {
    event.preventDefault();
    const payload = {
      ...values,
      department_id: values.department_id ? Number(values.department_id) : null,
      role_ids: values.role_ids.map(Number),
    };
    if (editingId) {
      await updateUser(editingId, payload);
    } else {
      await createUser(payload);
    }
    setValues(blankUser);
    setEditingId(null);
    loadData();
  }

  return (
    <div className="space-y-6">
      <Card title="User Management" subtitle="Create and maintain application users and role assignments.">
        <form className="grid gap-4 md:grid-cols-2 xl:grid-cols-3" onSubmit={handleSubmit}>
          <FormField label="Full Name" value={values.full_name} onChange={(event) => setValues((current) => ({ ...current, full_name: event.target.value }))} />
          <FormField label="Email" type="email" value={values.email} onChange={(event) => setValues((current) => ({ ...current, email: event.target.value }))} />
          <FormField label="Mobile" value={values.mobile} onChange={(event) => setValues((current) => ({ ...current, mobile: event.target.value }))} />
          <FormField label="Employee Code" value={values.employee_code} onChange={(event) => setValues((current) => ({ ...current, employee_code: event.target.value }))} />
          <FormField label="Password" type="password" value={values.password} onChange={(event) => setValues((current) => ({ ...current, password: event.target.value }))} />
          <SelectField label="Department" value={values.department_id} options={departmentOptions} onChange={(event) => setValues((current) => ({ ...current, department_id: event.target.value }))} />
          <div className="xl:col-span-2">
            <span className="label">Roles</span>
            <div className="grid gap-2 md:grid-cols-2">
              {roleOptions.map((role) => (
                <label key={role.value} className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
                  <input
                    type="checkbox"
                    checked={values.role_ids.includes(role.value)}
                    onChange={(event) =>
                      setValues((current) => ({
                        ...current,
                        role_ids: event.target.checked
                          ? [...current.role_ids, role.value]
                          : current.role_ids.filter((value) => value !== role.value),
                      }))
                    }
                  />
                  {role.label}
                </label>
              ))}
            </div>
          </div>
          <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
            <input type="checkbox" checked={values.is_active} onChange={(event) => setValues((current) => ({ ...current, is_active: event.target.checked }))} />
            User is active
          </label>
          <div className="xl:col-span-3 flex justify-end">
            <Button type="submit">{editingId ? "Update User" : "Create User"}</Button>
          </div>
        </form>
      </Card>

      <Card title="Users" subtitle="Current user directory and role assignments.">
        <Table
          rows={rows}
          columns={[
            { key: "full_name", label: "Name" },
            { key: "email", label: "Email" },
            { key: "department", label: "Department", render: (row) => row.department?.name || "-" },
            { key: "roles", label: "Roles", render: (row) => row.roles.map((role) => role.name).join(", ") },
            {
              key: "edit",
              label: "Edit",
              render: (row) => (
                <button
                  className="font-semibold text-brand-600"
                  onClick={() => {
                    setEditingId(row.id);
                    setValues({
                      full_name: row.full_name,
                      email: row.email,
                      mobile: row.mobile || "",
                      password: "",
                      department_id: row.department?.id ? String(row.department.id) : "",
                      role_ids: row.roles.map((role) => String(role.id)),
                      employee_code: row.employee_code || "",
                      is_active: row.is_active,
                    });
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
