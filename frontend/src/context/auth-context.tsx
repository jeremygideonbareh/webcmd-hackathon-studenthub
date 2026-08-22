import * as React from "react";
import type { StreamType } from "@/lib/types";

export interface Level1User {
  email: string;
  university?: string;
  stream: StreamType;
  locality: string;
  gpa: number;
  skills: string[];
}

export interface Level2User {
  studentId: string;
  portalConnected: boolean;
}

interface AuthContextType {
  user: Level1User | null;
  level2: Level2User | null;
  isLevel1Authenticated: boolean;
  isLevel2Authenticated: boolean;
  loginLevel1: (data: Level1User) => void;
  loginLevel2: (data: Level2User) => void;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<Level1User | null>(() => {
    try {
      const saved = localStorage.getItem("atlas_level1_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [level2, setLevel2] = React.useState<Level2User | null>(() => {
    try {
      const saved = localStorage.getItem("atlas_level2_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const loginLevel1 = React.useCallback((data: Level1User) => {
    setUser(data);
    localStorage.setItem("atlas_level1_user", JSON.stringify(data));
    fetch("/api/auth/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).catch(() => {});
  }, []);

  const loginLevel2 = React.useCallback((data: Level2User) => {
    setLevel2(data);
    localStorage.setItem("atlas_level2_user", JSON.stringify(data));
  }, []);

  const logout = React.useCallback(() => {
    setUser(null);
    setLevel2(null);
    localStorage.removeItem("atlas_level1_user");
    localStorage.removeItem("atlas_level2_user");
  }, []);

  const value = React.useMemo(
    () => ({
      user,
      level2,
      isLevel1Authenticated: !!user?.email,
      isLevel2Authenticated: !!level2?.portalConnected,
      loginLevel1,
      loginLevel2,
      logout,
    }),
    [user, level2, loginLevel1, loginLevel2, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
