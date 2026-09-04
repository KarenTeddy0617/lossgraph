import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";

import {
  getDashboardOverview,
  type DashboardOverview,
} from "../api/dashboard";


function Dashboard() {
  const { user } = useAuth();

  const [data, setData] =
    useState<DashboardOverview | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    async function loadDashboard() {

      try {

        const result =
          await getDashboardOverview();

        setData(result);

      } catch (err) {

        console.error(err);

        setError(
          "Unable to load dashboard data."
        );

      } finally {

        setLoading(false);

      }
    }

    loadDashboard();

  }, []);


  return (
    <main className="main-content">

      {/* Header */}

      <header>

        <div>

          <h1>Dashboard</h1>

          <p>
            Transaction abuse overview
          </p>

        </div>

        <div>
          <strong>
            {user?.username}
          </strong>
        </div>

      </header>


      {/* Loading */}

      {loading && (
        <p>
          Loading dashboard...
        </p>
      )}


      {/* Error */}

      {error && (
        <p className="error">
          {error}
        </p>
      )}


      {/* Dashboard Data */}

      {data && (
        <>

          <section className="stats-grid">

            <div className="stat-card">

              <span>
                Total Transactions
              </span>

              <strong>
                {data.total_transactions}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Normal Transactions
              </span>

              <strong>
                {data.normal_transactions}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Abuse Transactions
              </span>

              <strong>
                {data.abuse_transactions}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Abuse Percentage
              </span>

              <strong>
                {data.abuse_percentage}%
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Abuse Exposure
              </span>

              <strong>
                ₹
                {data.abuse_exposure.toLocaleString(
                  "en-IN"
                )}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                High Risk Transactions
              </span>

              <strong>
                {data.high_risk_transactions}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Suspicious Clusters
              </span>

              <strong>
                {data.cluster_count}
              </strong>

            </div>


            <div className="stat-card">

              <span>
                Average Cluster Risk
              </span>

              <strong>
                {data.average_cluster_risk_percentage}%
              </strong>

            </div>

          </section>


          {/* Risk Summary */}

          <section className="dashboard-section">

            <h2>
              Risk Summary
            </h2>

            <div className="summary-card">

              <p>

                <strong>
                  {data.abuse_transactions}
                </strong>{" "}

                transactions have been
                identified as abuse.

              </p>


              <p>

                Total known abuse exposure:{" "}

                <strong>
                  ₹
                  {data.abuse_exposure.toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </p>


              <p>

                <strong>
                  {data.cluster_count}
                </strong>{" "}

                suspicious clusters detected.

              </p>

            </div>

          </section>

        </>
      )}

    </main>
  );
}


export default Dashboard;