import apiClient from "./client";

export async function fetchPendingApprovals() {
  const { data } = await apiClient.get("/approvals/pending");
  return data;
}

export async function submitApprovalAction(requestId, payload) {
  const { data } = await apiClient.post(`/approvals/${requestId}/actions`, payload);
  return data;
}

