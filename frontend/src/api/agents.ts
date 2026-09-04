import { apiRequest } from "./client";

export interface AgentInvestigation {
  transaction_id: number;
  verdict: "NORMAL" | "REVIEW" | "ABUSE";
  confidence: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  summary: string;
  reasons: string[];
  recommended_action:
    | "ALLOW"
    | "MONITOR"
    | "MANUAL_REVIEW"
    | "BLOCK";

  evidence: {
    transaction: {
      id: number;
      transaction_code: string;
      merchant_id: number;
      customer_id: number;
      amount: number;
      status: string;
      refund_status: string;
      chargeback: boolean;
      created_at: string;
    };

    ml_risk: number;

    graph_analysis: {
      graph_score: number;
      graph_risk_level: string;
      features: Record<string, number>;
    };

    refunds: Array<{
      id: number;
      amount: number;
      reason: string;
      status: string;
      created_at: string;
    }>;

    cluster: {
      in_cluster: boolean;
      cluster_id?: number;
      cluster_code?: string;
      risk_score?: number;
      member_count?: number;
      exposure_amount?: number;
    };
  };

  tools_used: string[];
}

export function analyzeTransaction(
  transactionId: number
): Promise<AgentInvestigation> {
  return apiRequest<AgentInvestigation>(
    `/agent/analyze/${transactionId}`
  );
}