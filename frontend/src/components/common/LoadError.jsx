import Card from "./Card";

export default function LoadError({ title = "Unable to load page", message = "Something went wrong while loading this screen." }) {
  return (
    <Card title={title} subtitle="The page could not be rendered successfully.">
      <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{message}</div>
    </Card>
  );
}
