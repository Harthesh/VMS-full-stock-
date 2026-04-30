export default function StatCard({ label, value, tone = "brand" }) {
  const toneClasses = {
    brand: "from-brand-600/90 to-brand-500/90 text-white",
    accent: "from-accent-700/90 to-accent-500/90 text-white",
    neutral: "from-stone-800/90 to-stone-700/90 text-white",
  };

  return (
    <div className={`rounded-2xl bg-gradient-to-br p-5 shadow-soft ${toneClasses[tone] || toneClasses.brand}`}>
      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">{label}</div>
      <div className="mt-3 text-3xl font-semibold">{value}</div>
    </div>
  );
}

