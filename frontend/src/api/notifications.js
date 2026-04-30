import apiClient from "./client";

export async function fetchNotifications() {
  const { data } = await apiClient.get("/notifications");
  return data;
}

export async function markNotificationRead(id) {
  const { data } = await apiClient.post(`/notifications/${id}/read`);
  return data;
}

