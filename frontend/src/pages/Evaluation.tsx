import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";

interface ClassMetrics {
  precision: number;
  recall: number;
  f1_score: number;
  support: number;
}

interface EvaluationData {
  accuracy: number;
  roc_auc: number;
  precision: number;
  recall: number;
  f1_score: number;
  normal: ClassMetrics;
  abuse: ClassMetrics;
}

interface EvaluationResponse {
  status: string;
  evaluation: EvaluationData;
}

function Evaluation() {
  const [evaluation, setEvaluation] =
    useState<EvaluationData | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadEvaluation() {
      try {
        const data =
          await apiRequest<EvaluationResponse>(
            "/evaluation/"
          );

        if (data.status !== "success") {
          throw new Error(
            "Evaluation results are not available."
          );
        }

        setEvaluation(data.evaluation);
      } catch (err) {
        console.error(err);
        setError(
          "Failed to load model evaluation results."
        );
      } finally {
        setLoading(false);
      }
    }

    loadEvaluation();
  }, []);

  if (loading) {
    return <div style={{ padding: "24px" }}>Loading evaluation...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: "24px", color: "red" }}>
        {error}
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div style={{ padding: "24px" }}>
        No evaluation results available.
      </div>
    );
  }

  const formatPercent = (value: number) =>
    `${(value * 100).toFixed(2)}%`;

  return (
    <div style={{ padding: "24px" }}>
      <h1>Model Evaluation</h1>

      <p>
        Performance of the LossGraph abuse detection model
        on the evaluation dataset.
      </p>

      {/* Overall metrics */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "16px",
          marginTop: "24px",
        }}
      >
        <div className="metric-card">
          <h3>Accuracy</h3>
          <strong>
            {formatPercent(evaluation.accuracy)}
          </strong>
        </div>

        <div className="metric-card">
          <h3>ROC-AUC</h3>
          <strong>
            {evaluation.roc_auc.toFixed(2)}
          </strong>
        </div>

        <div className="metric-card">
          <h3>Precision</h3>
          <strong>
            {formatPercent(evaluation.precision)}
          </strong>
        </div>

        <div className="metric-card">
          <h3>Recall</h3>
          <strong>
            {formatPercent(evaluation.recall)}
          </strong>
        </div>

        <div className="metric-card">
          <h3>F1 Score</h3>
          <strong>
            {formatPercent(evaluation.f1_score)}
          </strong>
        </div>
      </div>

      {/* Class performance */}

      <h2 style={{ marginTop: "40px" }}>
        Class Performance
      </h2>

      <div
        style={{
          marginTop: "16px",
          border: "1px solid #ddd",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr
              style={{
                background: "#f5f5f5",
                textAlign: "left",
              }}
            >
              <th style={{ padding: "12px" }}>
                Class
              </th>

              <th style={{ padding: "12px" }}>
                Precision
              </th>

              <th style={{ padding: "12px" }}>
                Recall
              </th>

              <th style={{ padding: "12px" }}>
                F1 Score
              </th>

              <th style={{ padding: "12px" }}>
                Support
              </th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td style={{ padding: "12px" }}>
                Normal
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.normal.precision
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.normal.recall
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.normal.f1_score
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {evaluation.normal.support}
              </td>
            </tr>

            <tr>
              <td style={{ padding: "12px" }}>
                Abuse
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.abuse.precision
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.abuse.recall
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {formatPercent(
                  evaluation.abuse.f1_score
                )}
              </td>

              <td style={{ padding: "12px" }}>
                {evaluation.abuse.support}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Evaluation;