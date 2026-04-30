import { Link, useLocation } from "react-router-dom";
import Button from "../common/Button";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <header className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-600">Visitor Management System</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-stone-900">
          {location.pathname === "/dashboard" ? "Operations Dashboard" : "Workflow Console"}
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="rounded-2xl border border-stone-200 bg-white px-4 py-2 text-sm">
          <div className="font-semibold text-stone-900">{user?.full_name}</div>
          <div className="text-stone-500">{user?.email}</div>
        </div>
        <Link to="/notifications" className="btn-secondary hidden md:inline-flex">
          Notifications
        </Link>
        <Link to="/requests/new" className="btn-primary hidden md:inline-flex">
          New Request
        </Link>
        <Button variant="secondary" onClick={logout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
