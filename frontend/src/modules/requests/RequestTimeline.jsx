import Card from "../../components/common/Card";
import StatusBadge from "../../components/common/StatusBadge";
import { formatDateTime, formatRole } from "../../utils/format";

export default function RequestTimeline({ request }) {
  return (
    <Card title="Approval Timeline" subtitle="Workflow stages and action history captured from the backend engine.">
      <div className="grid gap-5 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.16em] text-stone-500">Steps</h3>
          <div className="space-y-3">
            {request.approval_steps?.length ? (
              request.approval_steps.map((step) => (
                <div key={step.id} className="panel-muted p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-stone-900">{step.step_name}</div>
                      <div className="text-sm text-stone-500">{formatRole(step.role_key)}</div>
                    </div>
                    <StatusBadge status={step.status} />
                  </div>
                  {step.remarks && <div className="mt-2 text-sm text-stone-600">{step.remarks}</div>}
                </div>
              ))
            ) : (
              <div className="panel-muted p-4 text-sm text-stone-500">No approval steps generated for this request.</div>
            )}
          </div>
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.16em] text-stone-500">Actions</h3>
          <div className="space-y-3">
            {request.approval_actions?.length ? (
              request.approval_actions.map((action) => (
                <div key={action.id} className="panel-muted p-4">
                  <div className="font-semibold capitalize text-stone-900">{action.action.replaceAll("_", " ")}</div>
                  <div className="mt-1 text-sm text-stone-500">
                    {action.action_by?.full_name || "System"} · {formatDateTime(action.created_at)}
                  </div>
                  {action.remarks && <div className="mt-2 text-sm text-stone-700">{action.remarks}</div>}
                </div>
              ))
            ) : (
              <div className="panel-muted p-4 text-sm text-stone-500">No actions recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

