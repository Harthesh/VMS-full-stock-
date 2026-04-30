import { createContext, useEffect, useMemo, useState } from "react";
import { fetchCurrentUser, loginRequest } from "../../api/auth";

export const AuthContext = createContext(null);

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = window.localStorage.getItem("vms_access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchCurrentUser()
      .then(setUser)
      .catch(() => {
        window.localStorage.removeItem("vms_access_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(payload) {
    const data = await loginRequest(payload);
    window.localStorage.setItem("vms_access_token", data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    window.localStorage.removeItem("vms_access_token");
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

