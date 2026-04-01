import { useState } from "react";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import FormField from "../../components/common/FormField";
import QrScannerPanel from "./QrScannerPanel";

export default function GateSearchPanel({ onSearch, mode }) {
  const [values, setValues] = useState({
    qr_code_value: "",
    request_no: "",
    visitor_name: "",
    mobile: "",
  });

  function handleSubmit(event) {
    event.preventDefault();
    onSearch(values);
  }

  async function handleDetected(qrCodeValue) {
    const nextValues = {
      qr_code_value: qrCodeValue,
      request_no: "",
      visitor_name: "",
      mobile: "",
    };
    setValues(nextValues);
    await onSearch(nextValues);
  }

  return (
    <Card
      title={mode === "scan" ? "Gate QR / Manual Search" : mode === "check-in" ? "Gate Check-In Search" : "Gate Check-Out Search"}
      subtitle="Look up a visitor by QR, request number, name, or mobile before taking gate action."
    >
      <div className="space-y-5">
        <QrScannerPanel onDetected={handleDetected} autoStart={mode === "scan"} />
        <form className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" onSubmit={handleSubmit}>
        <FormField
          label="QR Value"
          value={values.qr_code_value}
          onChange={(event) => setValues((current) => ({ ...current, qr_code_value: event.target.value }))}
        />
        <FormField
          label="Request Number"
          value={values.request_no}
          onChange={(event) => setValues((current) => ({ ...current, request_no: event.target.value }))}
        />
        <FormField
          label="Visitor Name"
          value={values.visitor_name}
          onChange={(event) => setValues((current) => ({ ...current, visitor_name: event.target.value }))}
        />
        <FormField
          label="Mobile"
          value={values.mobile}
          onChange={(event) => setValues((current) => ({ ...current, mobile: event.target.value }))}
        />
        <div className="md:col-span-2 xl:col-span-4 flex justify-end">
          <Button type="submit">Search</Button>
        </div>
        </form>
      </div>
    </Card>
  );
}
