import { useEffect, useState } from "react";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import FormField from "../../components/common/FormField";
import SelectField from "../../components/common/SelectField";

const actionOptions = [
  { value: "block", label: "Block" },
  { value: "alert", label: "Alert" },
  { value: "allow_with_warning", label: "Allow with Warning" },
];

const emptyState = {
  visitor_name: "",
  mobile: "",
  email: "",
  id_proof_type: "",
  id_proof_number: "",
  reason: "",
  action_type: "block",
  is_active: true,
};

export default function BlacklistForm({ initialValues, onSubmit, submitting }) {
  const [values, setValues] = useState(emptyState);

  useEffect(() => {
    setValues(initialValues || emptyState);
  }, [initialValues]);

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <Card title={initialValues ? "Edit Blacklist Record" : "Add Blacklist Record"} subtitle="Security controls used during scan and gate check-in.">
      <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
        <FormField label="Visitor Name" value={values.visitor_name} onChange={(event) => setValues((current) => ({ ...current, visitor_name: event.target.value }))} />
        <FormField label="Mobile" value={values.mobile || ""} onChange={(event) => setValues((current) => ({ ...current, mobile: event.target.value }))} />
        <FormField label="Email" type="email" value={values.email || ""} onChange={(event) => setValues((current) => ({ ...current, email: event.target.value }))} />
        <FormField label="ID Proof Type" value={values.id_proof_type || ""} onChange={(event) => setValues((current) => ({ ...current, id_proof_type: event.target.value }))} />
        <FormField label="ID Proof Number" value={values.id_proof_number || ""} onChange={(event) => setValues((current) => ({ ...current, id_proof_number: event.target.value }))} />
        <SelectField label="Action" value={values.action_type} options={actionOptions} onChange={(event) => setValues((current) => ({ ...current, action_type: event.target.value }))} />
        <div className="md:col-span-2">
          <FormField label="Reason" textarea value={values.reason} onChange={(event) => setValues((current) => ({ ...current, reason: event.target.value }))} />
        </div>
        <label className="panel-muted md:col-span-2 flex items-center gap-3 px-4 py-3 text-sm">
          <input type="checkbox" checked={values.is_active} onChange={(event) => setValues((current) => ({ ...current, is_active: event.target.checked }))} />
          Record is active
        </label>
        <div className="md:col-span-2 flex justify-end">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Saving..." : "Save Record"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

