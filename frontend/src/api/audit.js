import apiClient from "./client";

export async function fetchAuditLogs() {
  const { data } = await apiClient.get("/audit-logs");
  return data;
}

