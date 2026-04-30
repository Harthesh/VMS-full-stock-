import { NavLink } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import { getVisibleMenuItems } from "../../utils/menu";

export default function Sidebar() {
  const { user } = useAuth();
  const roleKeys = user?.roles?.map((role) => role.key) || [];
  const items = getVisibleMenuItems(roleKeys);
  const roleNames = (user?.roles ?? []).map((role) => role.name).join(", ");

  return (
    <aside className="panel sticky top-4 h-fit p-4">
      <div className="rounded-2xl bg-brand-600 px-4 py-5 text-white">
        <div className="text-xs uppercase tracking-[0.2em] text-white/70">Access Scope</div>
        <div className="mt-2 text-lg font-semibold">{roleNames || "User"}</div>
      </div>
      <nav className="mt-4 space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive ? "bg-stone-900 text-white" : "text-stone-600 hover:bg-stone-100 hover:text-stone-900"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
