import { apiRequest } from "./client";

export interface DashboardOverview {
  total_transactions: number;
  normal_transactions: number;
  abuse_transactions: number;
  abuse_percentage: number;
  abuse_exposure: number;
  high_risk_transactions: number;
  cluster_count: number;
  average_cluster_risk: number;
  average_cluster_risk_percentage: number;
}

export function getDashboardOverview(): Promise<DashboardOverview> {
  const token = localStorage.getItem("access_token");

  return apiRequest<DashboardOverview>("/dashboard/overview", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}