export const visitorTypeOptions = [
  { value: "supplier", label: "Supplier" },
  { value: "candidate", label: "Candidate" },
  { value: "contractor", label: "Contractor / Partner" },
  { value: "customer", label: "Customer" },
  { value: "vip_customer", label: "VIP Customer" },
];

export const approvalActionOptions = [
  { value: "approve", label: "Approve" },
  { value: "reject", label: "Reject" },
  { value: "send_back", label: "Send Back" },
];

export const roleLabels = {
  employee: "Employee",
  hr: "HR",
  bd_sales: "BD / Sales",
  manager: "Manager",
  hod: "HOD",
  ceo_office: "CEO Office",
  security: "Security",
  it: "IT",
  gatekeeper: "Gatekeeper",
  admin: "Admin",
};

export const statusLabels = {
  draft: "Draft",
  scheduled: "Scheduled",
  pending_manager_approval: "Pending Manager Approval",
  pending_hod_approval: "Pending HOD Approval",
  pending_ceo_office_approval: "Pending CEO Office Approval",
  pending_security_clearance: "Pending Security Clearance",
  pending_it_approval: "Pending IT Approval",
  pending_logistics_confirmation: "Pending Logistics Confirmation",
  approved: "Approved",
  rejected: "Rejected",
  sent_back: "Sent Back",
  cancelled: "Cancelled",
  checked_in: "Checked In",
  checked_out: "Checked Out",
};

