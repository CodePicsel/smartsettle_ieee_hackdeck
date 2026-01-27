import { createContext, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { login, logout } from "../app/authSlice";

const BASE_URL = "http://localhost:8000";

export const AuthContext = createContext();

function AuthLoader({ children }) {
  const dispatch = useDispatch();
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
      setBooting(false);
      return;
    }

    const restoreSession = async () => {
      try {
        const res = await fetch(`${BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error("Invalid token");

        const user = await res.json();
        dispatch(login(user));
      } catch {
        sessionStorage.removeItem("access_token");
        dispatch(logout());
      } finally {
        setBooting(false);
      }
    };

    restoreSession();
  }, []);

  if (booting) {
    return (
      <div className="h-screen flex items-center justify-center text-slate-400">
        Restoring session...
      </div>
    );
  }

  return children;
}

export default AuthLoader;
