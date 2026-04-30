import { Link } from "react-router-dom";
import Card from "../components/common/Card";
import LoginForm from "../modules/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <div className="grid w-full max-w-5xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[2rem] bg-stone-900 p-8 text-white shadow-soft">
          <p className="text-xs uppercase tracking-[0.24em] text-white/60">Production Workflow</p>
          <h1 className="mt-4 font-display text-5xl font-semibold leading-tight">
            Control every visitor movement from request to exit.
          </h1>
          <p className="mt-6 max-w-xl text-base text-white/72">
            Unified approvals, blacklist checks, gate operations, badge generation, and operational reporting for suppliers,
            candidates, contractors, customers, and VIP guests.
          </p>
        </div>
        <Card title="Sign In" subtitle="Use your assigned application credentials.">
          <LoginForm />
          <Link className="mt-4 inline-block text-sm font-medium text-brand-600" to="/forgot-password">
            Forgot password?
          </Link>
        </Card>
      </div>
    </div>
  );
}

