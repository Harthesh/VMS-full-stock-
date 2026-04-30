import apiClient from "./client";

export async function fetchDashboardSummary() {
  const { data } = await apiClient.get("/dashboard/summary");
  return data;
}

