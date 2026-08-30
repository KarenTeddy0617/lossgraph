import { apiRequest } from "./client";

export interface Transaction {
  id: number;
  transaction_code: string;
  amount: number;
  currency?: string;
  is_abuse: boolean;
}

export function getTransactions(): Promise<Transaction[]> {
  const token = localStorage.getItem("access_token");

  return apiRequest<Transaction[]>("/transactions/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getTransaction(
  transactionId: number
): Promise<Transaction> {
  const token = localStorage.getItem("access_token");

  return apiRequest<Transaction>(
    `/transactions/${transactionId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

export interface TransactionRisk {
  transaction_id: number;
  transaction_code: string;
  risk_score: number;
  risk_percentage: number;
  prediction: "ABUSE" | "NORMAL";
}

export function getTransactionRisk(
  transactionId: number
): Promise<TransactionRisk> {
  const token = localStorage.getItem("access_token");

  return apiRequest<TransactionRisk>(
    `/transactions/${transactionId}/risk`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}