import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getTransaction,
  getTransactionRisk,
  type Transaction,
  type TransactionRisk,
} from "../api/transactions";

import {
  analyzeTransaction,
  type AgentInvestigation,
} from "../api/agents";

function TransactionDetail() {
  const { transactionId } = useParams();
  const navigate = useNavigate();

  const [transaction, setTransaction] =
    useState<Transaction | null>(null);

  const [risk, setRisk] =
    useState<TransactionRisk | null>(null);

  const [agent, setAgent] =
    useState<AgentInvestigation | null>(null);

  const [loading, setLoading] = useState(true);
  const [riskLoading, setRiskLoading] = useState(false);
  const [agentLoading, setAgentLoading] = useState(false);

  const [error, setError] = useState("");
  const [agentError, setAgentError] = useState("");

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

  async function investigateTransaction() {
    if (!transactionId) return;

    setAgentLoading(true);
    setAgentError("");

    try {
      const result = await analyzeTransaction(
        Number(transactionId)
      );

      setAgent(result);
    } catch (err) {
      console.error(err);
      setAgentError(
        "Unable to complete AI investigation."
      );
    } finally {
      setAgentLoading(false);
    }
  }

  function getRiskClass(
    riskLevel: AgentInvestigation["risk_level"]
  ) {
    switch (riskLevel) {
      case "CRITICAL":
        return "risk-critical";

      case "HIGH":
        return "risk-high";

      case "MEDIUM":
        return "risk-medium";

      default:
        return "risk-low";
    }
  }

  function getVerdictClass(
    verdict: AgentInvestigation["verdict"]
  ) {
    switch (verdict) {
      case "ABUSE":
        return "status-abuse";

      case "REVIEW":
        return "status-review";

      default:
        return "status-normal";
    }
  }

  if (loading) {
    return (
      <main className="main-content">
        Loading...
      </main>
    );
  }

  if (!transaction) {
    return (
      <main className="main-content">
        <p>
          {error || "Transaction not found."}
        </p>

        <button
          onClick={() =>
            navigate("/transactions")
          }
        >
          Back to Transactions
        </button>
      </main>
    );
  }

  return (
    <main className="main-content">

      <button
        onClick={() =>
          navigate("/transactions")
        }
      >
        ← Back to Transactions
      </button>

      <h1>Transaction Details</h1>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {/* Transaction Information */}

      <div className="detail-card">

        <h2>
          {transaction.transaction_code}
        </h2>

        <p>
          <strong>ID:</strong>{" "}
          {transaction.id}
        </p>

        <p>
          <strong>Amount:</strong>{" "}
          ₹
          {Number(
            transaction.amount
          ).toLocaleString("en-IN")}
        </p>

        <p>
          <strong>Known Abuse:</strong>{" "}
          {transaction.is_abuse
            ? "Yes"
            : "No"}
        </p>

      </div>

      {/* ML Risk */}

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
              <strong>
                Risk Score:
              </strong>{" "}
              {risk.risk_percentage}%
            </p>

            <p>
              <strong>
                Prediction:
              </strong>{" "}
              {risk.prediction}
            </p>
          </>
        )}

      </div>

      {/* AI Investigation */}

      <div className="detail-card agent-card">

        <div className="agent-header">

          <div>
            <h2>
              AI Investigation
            </h2>

            <p>
              LossGraph AI analyzes ML,
              graph, refund and cluster
              evidence.
            </p>
          </div>

          {!agent && (
            <button
              onClick={
                investigateTransaction
              }
              disabled={agentLoading}
            >
              {agentLoading
                ? "Investigating..."
                : "Investigate Transaction"}
            </button>
          )}

        </div>

        {agentError && (
          <p className="error">
            {agentError}
          </p>
        )}

        {agent && (
          <div className="agent-results">

            {/* Verdict */}

            <div className="agent-summary-grid">

              <div>
                <span>Verdict</span>

                <strong
                  className={getVerdictClass(
                    agent.verdict
                  )}
                >
                  {agent.verdict}
                </strong>
              </div>

              <div>
                <span>Confidence</span>

                <strong>
                  {(
                    agent.confidence * 100
                  ).toFixed(1)}
                  %
                </strong>
              </div>

              <div>
                <span>Risk Level</span>

                <strong
                  className={getRiskClass(
                    agent.risk_level
                  )}
                >
                  {agent.risk_level}
                </strong>
              </div>

              <div>
                <span>Recommended Action</span>

                <strong>
                  {agent.recommended_action}
                </strong>
              </div>

            </div>

            {/* Summary */}

            <div className="agent-section">

              <h3>
                Investigation Summary
              </h3>

              <p>
                {agent.summary}
              </p>

            </div>

            {/* Reasons */}

            <div className="agent-section">

              <h3>
                Evidence & Reasons
              </h3>

              <ul className="agent-reasons">

                {agent.reasons.map(
                  (reason, index) => (
                    <li key={index}>
                      {reason}
                    </li>
                  )
                )}

              </ul>

            </div>

            {/* ML + Graph */}

            <div className="agent-section">

              <h3>
                Risk Signals
              </h3>

              <div className="signal-grid">

                <div>
                  <span>
                    ML Risk
                  </span>

                  <strong>
                    {(
                      agent.evidence.ml_risk *
                      100
                    ).toFixed(2)}
                    %
                  </strong>
                </div>

                <div>
                  <span>
                    Graph Risk
                  </span>

                  <strong>
                    {(
                      agent.evidence
                        .graph_analysis
                        .graph_score *
                      100
                    ).toFixed(2)}
                    %
                  </strong>
                </div>

                <div>
                  <span>
                    Graph Level
                  </span>

                  <strong>
                    {
                      agent.evidence
                        .graph_analysis
                        .graph_risk_level
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Cluster
                  </span>

                  <strong>
                    {agent.evidence.cluster
                      .in_cluster
                      ? "Detected"
                      : "None"}
                  </strong>
                </div>

              </div>

            </div>

            {/* Cluster */}

            {agent.evidence.cluster
              .in_cluster && (
              <div className="agent-section">

                <h3>
                  Abuse Cluster
                </h3>

                <p>
                  <strong>
                    Cluster:
                  </strong>{" "}
                  {
                    agent.evidence
                      .cluster
                      .cluster_code
                  }
                </p>

                <p>
                  <strong>
                    Members:
                  </strong>{" "}
                  {
                    agent.evidence
                      .cluster
                      .member_count
                  }
                </p>

                <p>
                  <strong>
                    Exposure:
                  </strong>{" "}
                  ₹
                  {Number(
                    agent.evidence
                      .cluster
                      .exposure_amount || 0
                  ).toLocaleString(
                    "en-IN",
                    {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    }
                  )}
                </p>

              </div>
            )}

          </div>
        )}

      </div>

    </main>
  );
}

export default TransactionDetail;