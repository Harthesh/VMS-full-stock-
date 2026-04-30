import apiClient from "./client";

export async function fetchEmergencyEvents(params = {}) {
  const { data } = await apiClient.get("/emergency/events", { params });
  return data;
}

export async function fetchEmergencyEvent(id) {
  const { data } = await apiClient.get(`/emergency/events/${id}`);
  return data;
}

export async function triggerEmergencyEvent(payload) {
  const { data } = await apiClient.post("/emergency/events", payload);
  return data;
}

export async function resolveEmergencyEvent(id, payload = {}) {
  const { data } = await apiClient.post(`/emergency/events/${id}/resolve`, payload);
  return data;
}

export async function updateMuster(musterId, payload) {
  const { data } = await apiClient.patch(`/emergency/musters/${musterId}`, payload);
  return data;
}

export async function fetchEventSummary(id) {
  const { data } = await apiClient.get(`/emergency/events/${id}/summary`);
  return data;
}
