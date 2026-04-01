export default function FormField({ label, error, textarea = false, ...props }) {
  const Component = textarea ? "textarea" : "input";
  return (
    <label className="block">
      <span className="label">{label}</span>
      <Component className={`field ${textarea ? "min-h-24 resize-y" : ""}`} {...props} />
      {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
    </label>
  );
}

