import apiClient from "./client";

export async function lookupVisitor(payload) {
  const { data } = await apiClient.post("/gate/lookup", payload);
  return data;
}

export async function checkInVisitor(requestId, payload) {
  const { data } = await apiClient.post(`/gate/${requestId}/check-in`, payload);
  return data;
}

export async function checkOutVisitor(requestId, payload) {
  const { data } = await apiClient.post(`/gate/${requestId}/check-out`, payload);
  return data;
}

