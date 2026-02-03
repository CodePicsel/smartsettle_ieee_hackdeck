import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function CompleteProfile() {
  const navigate = useNavigate()
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
        sessionStorage.setItem("access_token", tempToken)
       console.log(data)
          // navigate('/')
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
    <div className="inset-0 h-screen ">
    <div className=" bg-amber-50 w-fit flex flex-col top-[50%] left-[50%] translate-[-50%] gap-5 absolute p-5 rounded-lg ">
      <h2 className="font-[poppins-sb] text-3xl">Complete Your Profile</h2>
      <div className="">
      <lable className='pl-5 font-thin'>Enter your Username</lable>
      <input
        type="text"
        placeholder="Full Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="block  bg-white w-[90%] place-self-center-safe overflow-auto rounded-lg p-2 m-2"
        onKeyDown={(e) => e.key == "Enter"? submitProfile():''}
        />
      </div>

      {/* <textarea
        placeholder="Full Address"
        value={address}
        rows={4}
        onChange={(e) => setAddress(e.target.value)}
      /> */}

      {error && <p style={{ color: "red" }}>{error}</p>}

      <button onClick={submitProfile} disabled={loading} className="bg-blue-600 text-white font-[poppins-sb] m-2 p-2 rounded-lg border border-blue-900 ">
        {loading ? "Submitting..." : "Complete Registration"}
      </button>
    </div>
    </div>
  );
}

export default CompleteProfile;
