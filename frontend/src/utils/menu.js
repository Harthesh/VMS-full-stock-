const menuItems = [
  { label: "Dashboard", path: "/dashboard", roles: [] },
  { label: "My Requests", path: "/requests", roles: [] },
  { label: "Create Request", path: "/requests/new", roles: ["employee", "hr", "bd_sales", "admin"] },
  { label: "Invitations", path: "/invitations", roles: ["employee", "hr", "bd_sales", "manager", "hod", "admin"] },
  { label: "Pending Approvals", path: "/approvals", roles: ["manager", "hod", "ceo_office", "security", "it", "bd_sales", "admin"] },
  { label: "Gate Scan", path: "/gate/scan", roles: ["gatekeeper", "security", "admin"] },
  { label: "Gate Check-In", path: "/gate/check-in", roles: ["gatekeeper", "security", "admin"] },
  { label: "Gate Check-Out", path: "/gate/check-out", roles: ["gatekeeper", "security", "admin"] },
  { label: "Blacklist", path: "/blacklist", roles: ["security", "gatekeeper", "admin"] },
  { label: "Hospitality", path: "/hospitality", roles: ["admin", "hr", "manager", "hod"] },
  { label: "Emergency", path: "/emergency", roles: ["security", "admin", "gatekeeper", "hr"] },
  { label: "Notifications", path: "/notifications", roles: [] },
  { label: "Users", path: "/admin/users", roles: ["admin"] },
  { label: "Roles", path: "/admin/roles", roles: ["admin"] },
  { label: "Audit Logs", path: "/admin/audit-logs", roles: ["admin"] },
  { label: "Settings", path: "/settings", roles: ["admin"] },
  { label: "Reports", path: "/reports", roles: ["admin", "security", "hr", "bd_sales", "manager", "hod"] },
];

export function getVisibleMenuItems(roleKeys) {
  if (roleKeys.includes("admin")) {
    return menuItems;
  }
  return menuItems.filter((item) => item.roles.length === 0 || item.roles.some((role) => roleKeys.includes(role)));
}
