import { useEffect, useState } from "react";
import { fetchSettings, updateSetting } from "../api/settings";
import Button from "../components/common/Button";
import Card from "../components/common/Card";
import FormField from "../components/common/FormField";

export default function SettingsPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchSettings().then(setRows);
  }, []);

  async function handleChange(row, value) {
    const updated = await updateSetting(row.key, { value });
    setRows((current) => current.map((item) => (item.key === updated.key ? updated : item)));
  }

  return (
    <Card title="Settings" subtitle="Application-level controls stored in the database.">
      <div className="space-y-4">
        {rows.map((row) => (
          <SettingRow key={row.id} row={row} onSave={handleChange} />
        ))}
      </div>
    </Card>
  );
}

function SettingRow({ row, onSave }) {
  const [value, setValue] = useState(row.value);

  return (
    <div className="panel-muted p-4">
      <div className="mb-2 font-semibold text-stone-900">{row.key}</div>
      <div className="mb-3 text-sm text-stone-500">{row.description || "No description"}</div>
      <div className="flex gap-3">
        <div className="flex-1">
          <FormField label="Value" value={value} onChange={(event) => setValue(event.target.value)} />
        </div>
        <div className="flex items-end">
          <Button onClick={() => onSave(row, value)}>Save</Button>
        </div>
      </div>
    </div>
  );
}

