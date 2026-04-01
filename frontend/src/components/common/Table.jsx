export default function Table({ columns, rows, emptyText = "No records found" }) {
  if (!rows.length) {
    return <div className="panel-muted p-8 text-center text-sm text-stone-500">{emptyText}</div>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200 bg-white">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-stone-50 text-xs uppercase tracking-[0.18em] text-stone-500">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-4 py-3 font-semibold">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={row.id || index} className="border-t border-stone-100">
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-3 align-top text-stone-700">
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

