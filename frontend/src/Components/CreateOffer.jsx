import { useState } from "react";
import { useNavigate } from "react-router-dom";

const BASE_URL = "http://localhost:8000";

function CreateOffer() {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("access_token");

  const [amountAvailable, setAmountAvailable] = useState("");
  const [interestRate, setInterestRate] = useState("");
  const [duration, setDuration] = useState("");
  const [minBorrow, setMinBorrow] = useState("");
  const [maxBorrow, setMaxBorrow] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successData, setSuccessData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Basic validation
    if (
      !amountAvailable ||
      !interestRate ||
      !duration ||
      !minBorrow ||
      !maxBorrow
    ) {
      setError("Please fill all required fields");
      return;
    }

    if (Number(minBorrow) > Number(maxBorrow)) {
      setError("Min borrow amount cannot exceed max borrow amount");
      return;
    }

    if (Number(maxBorrow) > Number(amountAvailable)) {
      setError("Max borrow amount cannot exceed available amount");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/offers`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          amount_available: Number(amountAvailable),
          annual_interest_rate: Number(interestRate),
          duration_months: Number(duration),
          installments_count: Number(duration), // monthly EMI
          periodicity: "MONTHLY",
          min_borrow_amount: Number(minBorrow),
          max_borrow_amount: Number(maxBorrow),
          description: description.trim(),
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Failed to create offer");
      }

      // ✅ backend-calculated data
      setSuccessData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return <p className="text-red-500 p-4">Please login first.</p>;
  }

  return (
    <div className="max-w-lg mx-auto p-6 bg-slate-900 text-slate-100 rounded-lg border border-slate-700">
      <h2 className="text-2xl font-bold mb-4 text-center">
        Create Lending Offer
      </h2>

      {!successData ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="number"
            placeholder="Total Amount Available"
            value={amountAvailable}
            onChange={(e) => setAmountAvailable(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          <input
            type="number"
            placeholder="Annual Interest Rate (%)"
            value={interestRate}
            onChange={(e) => setInterestRate(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          <input
            type="number"
            placeholder="Duration (months)"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          <input
            type="number"
            placeholder="Minimum Borrow Amount"
            value={minBorrow}
            onChange={(e) => setMinBorrow(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          <input
            type="number"
            placeholder="Maximum Borrow Amount"
            value={maxBorrow}
            onChange={(e) => setMaxBorrow(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          <textarea
            placeholder="Offer description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 rounded bg-black border"
          />

          {error && <p className="text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded font-semibold"
          >
            {loading ? "Creating..." : "Create Offer"}
          </button>
        </form>
      ) : (
        // ✅ Success View
        <div className="text-center space-y-3">
          <h3 className="text-xl font-semibold text-emerald-400">
            Offer Created Successfully 🎉
          </h3>

          <p><b>Offer ID:</b> {successData.offer_id}</p>
          <p><b>Status:</b> {successData.status}</p>
          <p><b>Monthly EMI:</b> ₹{successData.installment_amount}</p>
          <p className="text-sm text-slate-400">
            Created at {new Date(successData.created_at).toLocaleString()}
          </p>

          <button
            onClick={() => navigate("/")}
            className="mt-4 bg-slate-700 p-2 rounded"
          >
            Go to Profile
          </button>
        </div>
      )}
    </div>
  );
}

export default CreateOffer;
