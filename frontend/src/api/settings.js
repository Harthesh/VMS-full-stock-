import apiClient from "./client";

export async function fetchSettings() {
  const { data } = await apiClient.get("/settings");
  return data;
}

export async function updateSetting(key, payload) {
  const { data } = await apiClient.put(`/settings/${key}`, payload);
  return data;
}

