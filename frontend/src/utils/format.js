import { roleLabels, statusLabels, visitorTypeOptions } from "./constants";

export function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleDateString();
}

export function formatDateTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

export function formatStatus(status) {
  return statusLabels[status] || status;
}

export function formatRole(roleKey) {
  return roleLabels[roleKey] || roleKey;
}

export function formatVisitorType(visitorType) {
  return visitorTypeOptions.find((item) => item.value === visitorType)?.label || visitorType;
}

