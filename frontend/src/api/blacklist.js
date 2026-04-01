import apiClient from "./client";

export async function fetchBlacklist(params = {}) {
  const { data } = await apiClient.get("/blacklist", { params });
  return data;
}

export async function createBlacklistEntry(payload) {
  const { data } = await apiClient.post("/blacklist", payload);
  return data;
}

export async function updateBlacklistEntry(id, payload) {
  const { data } = await apiClient.patch(`/blacklist/${id}`, payload);
  return data;
}

