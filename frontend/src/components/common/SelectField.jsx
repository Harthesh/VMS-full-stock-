export default function SelectField({ label, error, options, placeholder = "Select", ...props }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      <select className="field" {...props}>
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
    </label>
  );
}

