import apiClient from "./client";

export async function fetchInvitations(params = {}) {
  const { data } = await apiClient.get("/invitations", { params });
  return data;
}

export async function createInvitation(payload) {
  const { data } = await apiClient.post("/invitations", payload);
  return data;
}

export async function cancelInvitation(id) {
  const { data } = await apiClient.delete(`/invitations/${id}`);
  return data;
}

export async function resendInvitation(id) {
  const { data } = await apiClient.post(`/invitations/${id}/resend`);
  return data;
}

export async function fetchPublicInvitation(token) {
  const { data } = await apiClient.get(`/public/invitations/${token}`);
  return data;
}

export async function submitPublicInvitation(token, payload) {
  const { data } = await apiClient.post(`/public/invitations/${token}/submit`, payload);
  return data;
}
