import { formatStatus } from "../../utils/format";

const colorMap = {
  draft: "bg-stone-200 text-stone-700",
  scheduled: "bg-sky-100 text-sky-700",
  approved: "bg-emerald-100 text-emerald-700",
  checked_in: "bg-brand-100 text-brand-700",
  checked_out: "bg-stone-100 text-stone-700",
  rejected: "bg-red-100 text-red-700",
  sent_back: "bg-amber-100 text-amber-700",
  cancelled: "bg-stone-300 text-stone-700",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${colorMap[status] || "bg-stone-200 text-stone-700"}`}>
      {formatStatus(status)}
    </span>
  );
}

