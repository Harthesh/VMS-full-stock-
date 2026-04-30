import apiClient from "./client";

export async function fetchVisitorSummary(params = {}) {
  const { data } = await apiClient.get("/reports/visitor-summary", { params });
  return data;
}

export async function fetchDailyGateMovement(params = {}) {
  const { data } = await apiClient.get("/reports/daily-gate-movement", { params });
  return data;
}

export async function fetchPendingApprovalReport(params = {}) {
  const { data } = await apiClient.get("/reports/pending-approvals", { params });
  return data;
}

export async function fetchBlacklistAlertReport(params = {}) {
  const { data } = await apiClient.get("/reports/blacklist-alerts", { params });
  return data;
}

export async function fetchVisitorTypeSummary(params = {}) {
  const { data } = await apiClient.get("/reports/visitor-type-summary", { params });
  return data;
}

