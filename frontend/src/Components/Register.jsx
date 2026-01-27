import { useEffect, useState } from "react";

function CompleteProfile() {
  const [name, setName] = useState("");
  // const [address, setAddress] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const tempToken = sessionStorage.getItem("temp_token");

  // Protect route
  useEffect(() => {
    if (!tempToken) {
      setError("Session expired. Please login again.");
    }
  }, [tempToken]);

  const isValidName = (name) => /^[a-zA-Z ]{2,50}$/.test(name.trim());

  const submitProfile = async () => {
    if (!isValidName(name)) {
      setError("Enter a valid name");
      return;
    }

    // if (address.trim().length < 10) {
    //   setError("Address must be at least 10 characters");
    //   return;
    // }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${tempToken}`
        },
        body: JSON.stringify({
          name: name.trim(),
          // address: address.trim()
        })
      });

      const data = await res.json();

      if (data) {
        if(data.user.name == name)
        alert("Registration completed 🎉");
        // redirect to dashboard later
      } else {
        setError(data.message || "Registration failed");
      }
    } catch {
      setError("Server error");
    } finally {
      setLoading(false);
    }
  };

  if (!tempToken) {
    return <p style={{ color: "red" }}>{error}</p>;
  }

  return (
    <div style={{ width: "320px" }}>
      <h2>Complete Your Profile</h2>

      <input
        type="text"
        placeholder="Full Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      {/* <textarea
        placeholder="Full Address"
        value={address}
        rows={4}
        onChange={(e) => setAddress(e.target.value)}
      /> */}

      {error && <p style={{ color: "red" }}>{error}</p>}

      <button onClick={submitProfile} disabled={loading}>
        {loading ? "Submitting..." : "Complete Registration"}
      </button>
    </div>
  );
}

export default CompleteProfile;
