import { useState } from "react";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import SelectField from "../../components/common/SelectField";
import FormField from "../../components/common/FormField";
import { approvalActionOptions } from "../../utils/constants";

export default function ApprovalActionPanel({ onSubmit, submitting }) {
  const [values, setValues] = useState({ action: "approve", remarks: "" });

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <Card title="Approval Action" subtitle="Backend-enforced workflow transition with remark capture.">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <SelectField
          label="Action"
          value={values.action}
          options={approvalActionOptions}
          onChange={(event) => setValues((current) => ({ ...current, action: event.target.value }))}
        />
        <FormField
          label="Remarks"
          textarea
          value={values.remarks}
          onChange={(event) => setValues((current) => ({ ...current, remarks: event.target.value }))}
        />
        <Button type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit Action"}
        </Button>
      </form>
    </Card>
  );
}

