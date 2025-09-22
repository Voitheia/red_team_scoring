import React, { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin } from "./api/api";

interface User {
  id: string;
  username: string;
  admin: boolean;
  is_blue_team: boolean;
  blueteam_num: number
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  console.log("Running FC for Auth Provider");
  useEffect(() => {
    const storedToken = localStorage.getItem("authToken");
    if (storedToken) {
      setToken(storedToken);
      fetch("http://localhost:3000/me", {
        headers: { Authorization: `Bearer ${storedToken}` },
      })
        .then((res) => (res.ok ? res.json() : Promise.reject()))
        .then((data) => setUser(data.user))
        .catch(() => {
          localStorage.removeItem("authToken");
          setToken(null);
        })
        .finally(() => setLoading(false));
        console.log("Load done. Loading:", loading);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const res = await apiLogin(username, password);
    console.log(res);
    setToken(res.token);
    setUser({id: res.userid, username: res.username, admin: res.admin, is_blue_team: res.is_blue_team, blueteam_num: res.blueteam_num});
    localStorage.setItem("authToken", res.token);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("authToken");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  console.log("Running ctx:",ctx);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};
