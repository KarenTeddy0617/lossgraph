import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/client";

interface AuditEvent {
  id: number;
  merchant_id: number;
  event_type: string;
  transaction_id: number | null;
  action: string | null;
  reason: string | null;
  created_at: string;
}

function AuditTrail() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAuditEvents() {
      try {
        const data = await apiRequest<AuditEvent[]>("/audit/");
        setEvents(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load audit trail.");
      } finally {
        setLoading(false);
      }
    }

    loadAuditEvents();
  }, []);

  if (loading) {
    return <div style={{ padding: "24px" }}>Loading audit trail...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: "24px", color: "red" }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "24px" }}>
      <h1>Audit Trail</h1>

      <p>
        History of transaction risk assessments and system
        actions.
      </p>

      {events.length === 0 ? (
        <p>No audit events found.</p>
      ) : (
        <div
          style={{
            marginTop: "24px",
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
                <th style={{ padding: "12px" }}>Event</th>
                <th style={{ padding: "12px" }}>Transaction</th>
                <th style={{ padding: "12px" }}>Merchant</th>
                <th style={{ padding: "12px" }}>Action</th>
                <th style={{ padding: "12px" }}>Reason</th>
                <th style={{ padding: "12px" }}>Time</th>
              </tr>
            </thead>

            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td style={{ padding: "12px" }}>
                    {event.event_type}
                  </td>

                  <td style={{ padding: "12px" }}>
                    {event.transaction_id ? (
                      <Link
                        to={`/transactions/${event.transaction_id}`}
                      >
                        Transaction #{event.transaction_id}
                      </Link>
                    ) : (
                      "-"
                    )}
                  </td>

                  <td style={{ padding: "12px" }}>
                    {event.merchant_id}
                  </td>

                  <td style={{ padding: "12px" }}>
                    {event.action || "-"}
                  </td>

                  <td style={{ padding: "12px" }}>
                    {event.reason || "-"}
                  </td>

                  <td style={{ padding: "12px" }}>
                    {new Date(
                      event.created_at
                    ).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AuditTrail;