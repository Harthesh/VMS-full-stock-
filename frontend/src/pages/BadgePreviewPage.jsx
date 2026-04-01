import { QRCodeSVG } from "qrcode.react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Card from "../components/common/Card";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { fetchRequest } from "../api/requests";
import { formatDate, formatVisitorType } from "../utils/format";

export default function BadgePreviewPage() {
  const { id } = useParams();
  const [request, setRequest] = useState(null);

  useEffect(() => {
    fetchRequest(id).then(setRequest);
  }, [id]);

  if (!request) return <LoadingSpinner label="Loading badge..." />;

  const qrValue = request.badge?.qr_code_value || request.qr_code_value;
  const badgeNumber = request.badge?.badge_no || request.badge_no;

  return (
    <Card title="Badge Preview" subtitle="Printable badge structure prepared for future PDF export.">
      <div className="mx-auto max-w-md rounded-[2rem] border border-stone-300 bg-white p-8 shadow-soft">
        <div className="text-center">
          <div className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-600">Visitor Badge</div>
          <div className="mt-2 font-display text-3xl font-semibold text-stone-900">{request.visitor_name}</div>
          <div className="mt-1 text-sm text-stone-500">{formatVisitorType(request.visitor_type)}</div>
        </div>
        <div className="mt-6 flex justify-center">{qrValue ? <QRCodeSVG value={qrValue} size={168} /> : <div>No QR generated</div>}</div>
        <div className="mt-6 grid gap-3 text-sm">
          <Info label="Host" value={request.host_user?.full_name} />
          <Info label="Visit Date" value={formatDate(request.visit_date)} />
          <Info label="Badge No." value={badgeNumber} />
          <Info label="Request No." value={request.request_no} />
        </div>
      </div>
    </Card>
  );
}

function Info({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-stone-200 pb-2">
      <span className="font-semibold text-stone-500">{label}</span>
      <span className="text-stone-900">{value || "-"}</span>
    </div>
  );
}

