import { useState } from "react";

function Register() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [type, setType] = useState("borrower");
  const [otp, setOtp] = useState("");
  const [showOtp, setShowOtp] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  // Phone handler
  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, "");
    if (value.length > 10) return;
    setPhone(value);
    setError("");
  };

  // Name validation
  const isValidName = (name) => /^[a-zA-Z ]{2,50}$/.test(name.trim());

  // Send OTP
  const sendOtp = async () => {
    if (!isValidName(name)) {
      setError("Enter a valid name");
      return;
    }

    if (!/^[6-9]\d{9}$/.test(phone)) {
      setError("Enter a valid phone number");
      return;
    }

    setLoading(true);
    const fullPhone = `+91${phone}`;

    try {
      const res = await fetch("http://localhost:8000/register/request-otp", {
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

  // Register user
  const registerUser = async () => {
    if (otp.length !== 6) {
      setError("Enter valid 6-digit OTP");
      return;
    }

    const payload = {
      name: name.trim(),
      phoneNumber: `+91${phone}`,
      otp,
      type
    };

    try {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (data.success) {
        alert("Registration successful 🎉");
      } else {
        setError(data.message || "Invalid OTP");
      }
    } catch {
      setError("Registration failed");
    }
  };

  // Resend cooldown timer
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
    <div className="">
      <h2>Register</h2>

      {/* NAME */}
      <input
        type="text"
        placeholder="Full Name"
        value={name}
        disabled={showOtp}
        onChange={(e) => setName(e.target.value)}
      />

      {/* PHONE */}
      <div className="">
        <span>+91</span>
        <input
          type="tel"
          placeholder="9876543210"
          value={phone}
          disabled={showOtp}
          onChange={handlePhoneChange}
        />
      </div>

      {/* TYPE */}
      <select
        value={type}
        disabled={showOtp}
        onChange={(e) => setType(e.target.value)}
      >
        <option value="borrower">Borrower</option>
        <option value="lender">Lender</option>
      </select>

      {!showOtp && (
        <button onClick={sendOtp} disabled={loading}>
          {loading ? "Sending OTP..." : "Send OTP"}
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

          <button onClick={registerUser}>Register</button>

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

export default Register;
