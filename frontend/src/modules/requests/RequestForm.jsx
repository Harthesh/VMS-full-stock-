import { useMemo, useState } from "react";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import FormField from "../../components/common/FormField";
import SelectField from "../../components/common/SelectField";
import { visitorTypeOptions } from "../../utils/constants";

const baseState = {
  visitor_type: "supplier",
  visit_date: "",
  visit_time: "",
  department_id: "",
  host_user_id: "",
  visitor_name: "",
  company_name: "",
  mobile: "",
  email: "",
  id_proof_type: "",
  id_proof_number: "",
  purpose: "",
  requires_security_clearance: false,
  requires_it_access: false,
  requires_hospitality: false,
  remarks: "",
  hospitality: {
    meal_required: false,
    transport_required: false,
    meeting_room: "",
    escort_needed: false,
    vip_notes: "",
    remarks: "",
  },
  panel_member_user_ids: [],
};

export default function RequestForm({ initialValues, departments, users, onSubmit, submitting, title, submitError = "" }) {
  const [values, setValues] = useState(initialValues ? mapInitialValues(initialValues) : baseState);
  const [errors, setErrors] = useState({});

  const departmentOptions = useMemo(
    () => departments.map((department) => ({ value: String(department.id), label: `${department.code} · ${department.name}` })),
    [departments],
  );

  const userOptions = useMemo(
    () => users.map((user) => ({ value: String(user.id), label: `${user.full_name} · ${user.email}` })),
    [users],
  );

  function updateField(name, value) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  function updateHospitality(name, value) {
    setValues((current) => ({
      ...current,
      hospitality: {
        ...current.hospitality,
        [name]: value,
      },
    }));
  }

  function validate() {
    const nextErrors = {};
    ["visitor_type", "visit_date", "visitor_name", "mobile", "purpose"].forEach((field) => {
      if (!values[field]) nextErrors[field] = "Required";
    });
    if ((values.visitor_type === "customer" || values.visitor_type === "vip_customer") && !values.host_user_id) {
      nextErrors.host_user_id = "Host user is required";
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (!validate()) return;
    onSubmit(normalizePayload(values));
  }

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <Card title={title} subtitle="Capture visit details, approvals, and logistics requirements in one flow.">
        {submitError && <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{submitError}</div>}
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <SelectField
            label="Visitor Type"
            value={values.visitor_type}
            options={visitorTypeOptions}
            onChange={(event) => updateField("visitor_type", event.target.value)}
            error={errors.visitor_type}
          />
          <FormField
            label="Visit Date"
            type="date"
            value={values.visit_date}
            onChange={(event) => updateField("visit_date", event.target.value)}
            error={errors.visit_date}
          />
          <FormField
            label="Visit Time"
            type="time"
            value={values.visit_time}
            onChange={(event) => updateField("visit_time", event.target.value)}
          />
          <SelectField
            label="Department"
            value={values.department_id}
            options={departmentOptions}
            onChange={(event) => updateField("department_id", event.target.value)}
          />
          <SelectField
            label="Host User"
            value={values.host_user_id}
            options={userOptions}
            onChange={(event) => updateField("host_user_id", event.target.value)}
            error={errors.host_user_id}
          />
          <FormField
            label="Visitor Name"
            value={values.visitor_name}
            onChange={(event) => updateField("visitor_name", event.target.value)}
            error={errors.visitor_name}
          />
          {values.visitor_type !== "candidate" && (
            <FormField
              label="Company Name"
              value={values.company_name}
              onChange={(event) => updateField("company_name", event.target.value)}
            />
          )}
          <FormField
            label="Mobile"
            value={values.mobile}
            onChange={(event) => updateField("mobile", event.target.value)}
            error={errors.mobile}
          />
          <FormField
            label="Email"
            type="email"
            value={values.email}
            onChange={(event) => updateField("email", event.target.value)}
          />
          <FormField
            label="ID Proof Type"
            value={values.id_proof_type}
            onChange={(event) => updateField("id_proof_type", event.target.value)}
          />
          <FormField
            label="ID Proof Number"
            value={values.id_proof_number}
            onChange={(event) => updateField("id_proof_number", event.target.value)}
          />
          <div className="md:col-span-2 xl:col-span-3">
            <FormField
              label="Purpose"
              textarea
              value={values.purpose}
              onChange={(event) => updateField("purpose", event.target.value)}
              error={errors.purpose}
            />
          </div>
          <div className="grid gap-3 md:col-span-2 xl:col-span-3 md:grid-cols-3">
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.requires_security_clearance}
                onChange={(event) => updateField("requires_security_clearance", event.target.checked)}
              />
              Requires security clearance
            </label>
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.requires_it_access}
                onChange={(event) => updateField("requires_it_access", event.target.checked)}
              />
              Requires IT access
            </label>
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.requires_hospitality}
                onChange={(event) => updateField("requires_hospitality", event.target.checked)}
              />
              Requires hospitality/logistics
            </label>
          </div>
          <div className="md:col-span-2 xl:col-span-3">
            <FormField
              label="Remarks"
              textarea
              value={values.remarks}
              onChange={(event) => updateField("remarks", event.target.value)}
            />
          </div>
        </div>
      </Card>

      {values.requires_hospitality && (
        <Card title="Hospitality / Logistics" subtitle="Optional support for meals, transport, escorting, and VIP handling.">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.hospitality.meal_required}
                onChange={(event) => updateHospitality("meal_required", event.target.checked)}
              />
              Meal required
            </label>
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.hospitality.transport_required}
                onChange={(event) => updateHospitality("transport_required", event.target.checked)}
              />
              Transport required
            </label>
            <FormField
              label="Meeting Room"
              value={values.hospitality.meeting_room}
              onChange={(event) => updateHospitality("meeting_room", event.target.value)}
            />
            <label className="panel-muted flex items-center gap-3 px-4 py-3 text-sm">
              <input
                type="checkbox"
                checked={values.hospitality.escort_needed}
                onChange={(event) => updateHospitality("escort_needed", event.target.checked)}
              />
              Escort needed
            </label>
            <div className="md:col-span-2">
              <FormField
                label="VIP Notes"
                textarea
                value={values.hospitality.vip_notes}
                onChange={(event) => updateHospitality("vip_notes", event.target.value)}
              />
            </div>
          </div>
        </Card>
      )}

      <div className="flex justify-end">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving..." : "Save Request"}
        </Button>
      </div>
    </form>
  );
}

function mapInitialValues(data) {
  return {
    ...baseState,
    ...data,
    visit_date: data.visit_date || "",
    visit_time: data.visit_time || "",
    department_id: data.department?.id ? String(data.department.id) : "",
    host_user_id: data.host_user?.id ? String(data.host_user.id) : "",
    hospitality: {
      ...baseState.hospitality,
      ...(data.hospitality_request || {}),
    },
  };
}

function normalizePayload(values) {
  return {
    ...values,
    visit_time: emptyToNull(values.visit_time),
    department_id: values.department_id ? Number(values.department_id) : null,
    host_user_id: values.host_user_id ? Number(values.host_user_id) : null,
    company_name: emptyToNull(values.company_name),
    email: emptyToNull(values.email),
    id_proof_type: emptyToNull(values.id_proof_type),
    id_proof_number: emptyToNull(values.id_proof_number),
    remarks: emptyToNull(values.remarks),
    hospitality: values.requires_hospitality
      ? {
          ...values.hospitality,
          meeting_room: emptyToNull(values.hospitality.meeting_room),
          vip_notes: emptyToNull(values.hospitality.vip_notes),
          remarks: emptyToNull(values.hospitality.remarks),
        }
      : null,
  };
}

function emptyToNull(value) {
  return typeof value === "string" && value.trim() === "" ? null : value;
}
