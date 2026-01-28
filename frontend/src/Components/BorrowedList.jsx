import { useEffect, useState } from "react";

const BASE_URL = "http://localhost:8000";

function BorrowedList() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
      setError("Not authenticated");
      setLoading(false);
      return;
    }

    const fetchBorrowed = async () => {
      try {
        const res = await fetch(`${BASE_URL}/borrowed`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error("Failed to fetch borrowed loans");

        const data = await res.json();
        setLoans(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBorrowed();
  }, []);

  if (loading) {
    return <p className="p-4 text-slate-400">Loading borrowed loans...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500">{error}</p>;
  }

  if (loans.length === 0) {
    return (
      <p className="p-4 text-slate-400">
        You haven’t borrowed any money yet.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {loans.map((loan) => (
        <div
          key={loan.loan_id}
          className="border border-slate-700 bg-slate-900 rounded-lg p-4 flex justify-between items-center"
        >
          <div>
            <h3 className="text-lg font-semibold text-blue-500">
              ₹{loan.amount}
            </h3>
            <p className="text-sm text-slate-400">
              Lender: {loan.lender_name}
            </p>
            <p className="text-sm text-slate-400">
              Interest: {loan.interest_rate}% • {loan.duration_months} months
            </p>
          </div>

          <div className="text-right">
            <p className="font-semibold">
              EMI ₹{loan.installment_amount}
            </p>
            <p
              className={`text-sm ${
                loan.status === "active"
                  ? "text-emerald-400"
                  : "text-slate-400"
              }`}
            >
              {loan.status.toUpperCase()}
            </p>
            {loan.next_due_date && (
              <p className="text-xs text-slate-400">
                Next due:{" "}
                {new Date(loan.next_due_date).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default BorrowedList;
    