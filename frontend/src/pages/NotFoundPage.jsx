import { Link } from "react-router-dom";
import Card from "../components/common/Card";

export default function NotFoundPage() {
  return (
    <div className="mx-auto mt-24 max-w-lg">
      <Card title="Page Not Found" subtitle="The requested route is not available in this build.">
        <Link className="text-sm font-semibold text-brand-600" to="/dashboard">
          Return to dashboard
        </Link>
      </Card>
    </div>
  );
}
