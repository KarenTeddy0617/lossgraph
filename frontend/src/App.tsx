import {
  BrowserRouter,
  Navigate,
  NavLink,
  Outlet,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import TransactionDetail from "./pages/TransactionDetail";
import ClusterExplorer from "./pages/ClusterExplorer";
import AuditTrail from "./pages/AuditTrail";
import Evaluation from "./pages/Evaluation";


function ProtectedLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="app-layout">

      {/* Sidebar */}

      <aside className="sidebar">

        <h2>LossGraph</h2>

        <nav>

          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/transactions"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
            end
          >
            Transactions
          </NavLink>

          <NavLink
            to="/clusters"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            Clusters
          </NavLink>

          <NavLink
            to="/evaluation"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            Evaluation
          </NavLink>

          <NavLink
            to="/audit"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            Audit Trail
          </NavLink>

        </nav>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          Logout
        </button>

      </aside>


      {/* Page Content */}

      <div className="page-area">
        <Outlet />
      </div>

    </div>
  );
}


function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Login */}

        <Route
          path="/login"
          element={<Login />}
        />


        {/* Protected application */}

        <Route element={<ProtectedLayout />}>

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/transactions"
            element={<Transactions />}
          />

          <Route
            path="/transactions/:transactionId"
            element={<TransactionDetail />}
          />

          <Route
            path="/clusters"
            element={<ClusterExplorer />}
          />

          <Route
            path="/evaluation"
            element={<Evaluation />}
          />

          <Route
            path="/audit"
            element={<AuditTrail />}
          />

        </Route>


        {/* Unknown route */}

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;