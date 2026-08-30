
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/client";

interface Cluster {
  merchant_id: number;
  member_count: number;
  risk_score: number;
  risk_percentage: number;
  exposure_amount: number;
  transaction_ids: number[];
  transaction_codes: string[];
}

function ClusterExplorer() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadClusters() {
      try {
        const data = await apiRequest<Cluster[]>("/clusters/");
        setClusters(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load abuse clusters.");
      } finally {
        setLoading(false);
      }
    }

    loadClusters();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <h1>Abuse Clusters</h1>
        <p>Loading clusters...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Abuse Clusters</h1>
        <p>{error}</p>
      </div>
    );
  }

  const totalExposure = clusters.reduce(
    (total, cluster) => total + cluster.exposure_amount,
    0
  );

  const highRiskClusters = clusters.filter(
    (cluster) => cluster.risk_percentage >= 90
  ).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Abuse Clusters</h1>
          <p>
            Suspicious groups of related transactions detected by LossGraph.
          </p>
        </div>
      </div>

      {/* Summary */}
      <div className="cluster-summary">
        <div className="summary-card">
          <span>Total Clusters</span>
          <strong>{clusters.length}</strong>
        </div>

        <div className="summary-card">
          <span>High Risk Clusters</span>
          <strong>{highRiskClusters}</strong>
        </div>

        <div className="summary-card">
          <span>Total Exposure</span>
          <strong>
            ₹{totalExposure.toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </strong>
        </div>
      </div>

      {/* Clusters */}
      <div className="cluster-grid">
        {clusters.map((cluster, index) => {
          const riskClass =
            cluster.risk_percentage >= 90
              ? "risk-high"
              : cluster.risk_percentage >= 70
              ? "risk-medium"
              : "risk-low";

          return (
            <div className="cluster-card" key={`${cluster.merchant_id}-${index}`}>
              <div className="cluster-card-header">
                <div>
                  <h2>Cluster {index + 1}</h2>
                  <span className="merchant">
                    Merchant {cluster.merchant_id}
                  </span>
                </div>

                <span className={`risk-badge ${riskClass}`}>
                  {cluster.risk_percentage}% Risk
                </span>
              </div>

              <div className="cluster-stats">
                <div>
                  <span>Members</span>
                  <strong>{cluster.member_count}</strong>
                </div>

                <div>
                  <span>Exposure</span>
                  <strong>
                    ₹
                    {cluster.exposure_amount.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </strong>
                </div>
              </div>

              <div className="transactions-section">
                <span className="section-label">
                  Transactions ({cluster.transaction_codes.length})
                </span>

                <div className="transaction-list">
                  {cluster.transaction_codes.map((code, transactionIndex) => (
                    <Link
                      key={code}
                      to={`/transactions/${cluster.transaction_ids[transactionIndex]}`}
                      className="transaction-link"
                    >
                      {code}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {clusters.length === 0 && (
        <div className="empty-state">
          <h2>No suspicious clusters found</h2>
          <p>
            LossGraph did not detect any suspicious transaction groups.
          </p>
        </div>
      )}
    </div>
  );
}

export default ClusterExplorer;

