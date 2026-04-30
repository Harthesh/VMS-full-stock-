import { QRCodeSVG } from "qrcode.react";
import Card from "./Card";

export default function VisitorQrCard({ request }) {
  const qrValue = request?.badge?.qr_code_value || request?.qr_code_value;
  const badgeNumber = request?.badge?.badge_no || request?.badge_no;

  if (!qrValue) return null;

  return (
    <Card title="Visitor QR Code" subtitle="This code is generated automatically once the visit is fully approved.">
      <div className="grid gap-6 md:grid-cols-[220px_minmax(0,1fr)] md:items-center">
        <div className="flex justify-center rounded-[2rem] border border-stone-200 bg-white p-6">
          <QRCodeSVG value={qrValue} size={168} />
        </div>
        <div className="space-y-3 text-sm">
          <Info label="QR Value" value={qrValue} />
          <Info label="Badge Number" value={badgeNumber || "-"} />
          <Info label="Visitor Email" value={request?.email || "-"} />
          <Info label="Status" value={request?.status || "-"} />
        </div>
      </div>
    </Card>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white px-4 py-3">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">{label}</div>
      <div className="mt-1 break-all text-sm font-medium text-stone-800">{value}</div>
    </div>
  );
}
