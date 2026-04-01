import apiClient from "./client";

export async function fetchRequests() {
  const { data } = await apiClient.get("/visitor-requests");
  return data;
}

export async function fetchRequest(id) {
  const { data } = await apiClient.get(`/visitor-requests/${id}`);
  return data;
}

export async function createRequest(payload) {
  const { data } = await apiClient.post("/visitor-requests", payload);
  return data;
}

export async function updateRequest(id, payload) {
  const { data } = await apiClient.patch(`/visitor-requests/${id}`, payload);
  return data;
}

export async function submitRequest(id) {
  const { data } = await apiClient.post(`/visitor-requests/${id}/submit`);
  return data;
}

export async function cancelRequest(id, message) {
  const { data } = await apiClient.post(`/visitor-requests/${id}/cancel`, { message });
  return data;
}

