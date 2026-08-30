import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getTransactions,
  type Transaction,
} from "../api/transactions";

function Transactions() {
  const navigate = useNavigate();

  const [transactions, setTransactions] =
    useState<Transaction[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTransactions() {
      try {
        const result = await getTransactions();
        setTransactions(result);
      } catch (err) {
        console.error(err);
        setError("Unable to load transactions.");
      } finally {
        setLoading(false);
      }
    }

    loadTransactions();
  }, []);

  return (
    <main className="main-content">
      <h1>Transactions</h1>

      <p>All transactions recorded in LossGraph.</p>

      {loading && <p>Loading transactions...</p>}

      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Transaction</th>
                <th>Amount</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.id}</td>

                  <td>{transaction.transaction_code}</td>

                  <td>
                    ₹
                    {Number(transaction.amount).toLocaleString(
                      "en-IN"
                    )}
                  </td>

                  <td>
                    {transaction.is_abuse ? (
                      <span className="status-abuse">
                        ABUSE
                      </span>
                    ) : (
                      <span className="status-normal">
                        NORMAL
                      </span>
                    )}
                  </td>

                  <td>
                    <button
                      onClick={() =>
                        navigate(
                          `/transactions/${transaction.id}`
                        )
                      }
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {transactions.length === 0 && (
            <p>No transactions found.</p>
          )}
        </div>
      )}
    </main>
  );
}

export default Transactions;