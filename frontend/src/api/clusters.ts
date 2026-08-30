import { apiRequest } from "./client";

export interface AbuseCluster {
  merchant_id: number;
  member_count: number;
  risk_score: number;
  risk_percentage: number;
  exposure_amount: number;
  transaction_ids: number[];
  transaction_codes: string[];
}

export async function getClusters(): Promise<AbuseCluster[]> {
  return apiRequest<AbuseCluster[]>("/clusters/");
}