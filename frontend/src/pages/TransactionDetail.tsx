import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getTransaction,
  getTransactionRisk,
  type Transaction,
  type TransactionRisk,
} from "../api/transactions";

function TransactionDetail() {
  const { transactionId } = useParams();
  const navigate = useNavigate();

  const [transaction, setTransaction] =
    useState<Transaction | null>(null);

  const [risk, setRisk] =
    useState<TransactionRisk | null>(null);

  const [loading, setLoading] = useState(true);
  const [riskLoading, setRiskLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTransaction() {
      try {
        if (!transactionId) return;

        const result = await getTransaction(
          Number(transactionId)
        );

        setTransaction(result);
      } catch (err) {
        console.error(err);
        setError("Unable to load transaction.");
      } finally {
        setLoading(false);
      }
    }

    loadTransaction();
  }, [transactionId]);

  async function calculateRisk() {
    if (!transactionId) return;

    setRiskLoading(true);
    setError("");

    try {
      const result = await getTransactionRisk(
        Number(transactionId)
      );

      setRisk(result);
    } catch (err) {
      console.error(err);
      setError("Unable to calculate transaction risk.");
    } finally {
      setRiskLoading(false);
    }
  }

  if (loading) {
    return <main className="main-content">Loading...</main>;
  }

  if (!transaction) {
    return (
      <main className="main-content">
        <p>{error || "Transaction not found."}</p>
        <button onClick={() => navigate("/transactions")}>
          Back to Transactions
        </button>
      </main>
    );
  }

  return (
    <main className="main-content">
      <button onClick={() => navigate("/transactions")}>
        ← Back to Transactions
      </button>

      <h1>Transaction Details</h1>

      {error && <p className="error">{error}</p>}

      <div className="detail-card">
        <h2>{transaction.transaction_code}</h2>

        <p>
          <strong>ID:</strong> {transaction.id}
        </p>

        <p>
          <strong>Amount:</strong>{" "}
          ₹{Number(transaction.amount).toLocaleString("en-IN")}
        </p>

        <p>
          <strong>Known Abuse:</strong>{" "}
          {transaction.is_abuse ? "Yes" : "No"}
        </p>
      </div>

      <div className="detail-card">
        <h2>ML Risk Assessment</h2>

        {!risk && (
          <button
            onClick={calculateRisk}
            disabled={riskLoading}
          >
            {riskLoading
              ? "Calculating..."
              : "Calculate Risk"}
          </button>
        )}

        {risk && (
          <>
            <p>
              <strong>Risk Score:</strong>{" "}
              {risk.risk_percentage}%
            </p>

            <p>
              <strong>Prediction:</strong>{" "}
              {risk.prediction}
            </p>
          </>
        )}
      </div>
    </main>
  );
}

export default TransactionDetail;