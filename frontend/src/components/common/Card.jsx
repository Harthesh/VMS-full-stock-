export default function Card({ title, subtitle, action, children, className = "" }) {
  return (
    <section className={`panel p-5 ${className}`}>
      {(title || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title && <h2 className="font-display text-xl font-semibold text-stone-900">{title}</h2>}
            {subtitle && <p className="mt-1 text-sm text-stone-500">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

