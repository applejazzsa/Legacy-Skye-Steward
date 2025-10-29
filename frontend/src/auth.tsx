import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "./api";

// feat(auth): simple auth context with /me bootstrap

type TenantLink = { id: number; name: string; slug: string; role: "owner" | "manager" | "staff" };
type User = { id: number; email: string; tenants: TenantLink[] };

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const me = await api.me();
        if (!alive) return;
        setUser(me ?? null);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  async function login(email: string, password: string) {
    const res = await api.login(email, password);
    if (!res) return false;
    setUser(res.user as User);
    return true;
  }

  async function logout() {
    await api.logout();
    setUser(null);
  }

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

