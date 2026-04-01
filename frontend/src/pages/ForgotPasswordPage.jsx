import { Link } from "react-router-dom";
import Card from "../components/common/Card";

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card title="Forgot Password" subtitle="Email reset flow is intentionally left as an integration placeholder.">
        <p className="text-sm text-stone-600">
          Wire this page to your SMTP provider or identity platform. The backend already has a notification service layer that can
          be extended for reset tokens and email delivery.
        </p>
        <Link to="/login" className="mt-4 inline-flex text-sm font-semibold text-brand-600">
          Back to login
        </Link>
      </Card>
    </div>
  );
}

