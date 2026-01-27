import { useState } from "react";
import { useDispatch } from "react-redux";

function LoginWithOtp() {
    const dispatch = useDispatch();
    const [phone, setPhone] = useState("");
    const [showOtp, setShowOtp] = useState(false);
    const [otp, setOtp] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(0);

  // Phone input handler
  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, "");
    if (value.length > 10) return;
    setPhone(value);
    setError("");
  };

  // Send OTP
  const sendOtp = async () => {
    if (!/^[6-9]\d{9}$/.test(phone)) {
      setError("Enter a valid 10-digit phone number");
      return;
    }

    setLoading(true);
    const fullPhone = `+91${phone}`;

    try {
      const res = await fetch("http://localhost:8000/auth/request-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phoneNumber: fullPhone })
      });

      const data = await res.json();

      if (data.success) {
        setShowOtp(true);
        startResendCooldown();
      } else {
        setError("Failed to send OTP");
      }
    } catch {
      setError("Server error");
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP
  const verifyOtp = async () => {
    if (otp.length !== 6) {
      setError("Enter 6-digit OTP");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phoneNumber: `+91${phone}`,
          otp
        })
      });

      const data = await res.json();

      if (data.otp_sent) {
        alert("Login successful 🎉");
        useDispatch(login)
      } else {
        setError("Invalid OTP");
      }
    } catch {
      setError("OTP verification failed");
    }
  };

  // Resend cooldown
  const startResendCooldown = () => {
    setResendCooldown(30);
    const timer = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  return (
    <div>
      {/* PHONE INPUT */}
      <div>
        <span>+91</span>
        <input
          type="tel"
          value={phone}
          onChange={handlePhoneChange}
          placeholder="9876543210"
          disabled={showOtp}
        />
      </div>

      {!showOtp && (
        <button onClick={sendOtp} disabled={loading}>
          {loading ? "Sending..." : "Send Otp"}
        </button>
      )}

      {/* OTP SECTION */}
      {showOtp && (
        <>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
          />

          <button onClick={verifyOtp}>Verify OTP</button>

          <button
            onClick={sendOtp}
            disabled={resendCooldown > 0}
            style={{ marginTop: "8px" }}
          >
            {resendCooldown > 0
              ? `Resend OTP in ${resendCooldown}s`
              : "Resend OTP"}
          </button>
        </>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default LoginWithOtp;
