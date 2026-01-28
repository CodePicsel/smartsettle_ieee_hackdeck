import { useEffect, useState } from "react";

const useProfile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = sessionStorageStorage.getItem("access_token"); // adjust if needed

        const res = await fetch("http://localhost:8000/auth/verify-otp", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        // if (!res.) {
        //   throw new Error("Failed to fetch profile");
        // }

        const data = await res.json();
        setUser(data.user); // 👈 important
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  return { user, loading, error };
};

export default useProfile;
