import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/api";
import { tokenStore } from "../utils/tokenStore";

export interface User {
  id: number;
  name: string;
  email: string;
  picture: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isNewUser: boolean;
  login: (googleCredentialToken: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isNewUser, setIsNewUser] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem("ai_research_user");
    const token = tokenStore.getToken();
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        tokenStore.removeToken();
        localStorage.removeItem("ai_research_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (googleCredentialToken: string) => {
    setIsLoading(true);
    try {
      const response = await api.post("/auth/google", {
        credential: googleCredentialToken,
      });
      const { token, access_token, user: loggedUser, is_new_user } = response.data;
      const jwtToken = token || access_token;
      tokenStore.setToken(jwtToken);
      localStorage.setItem("ai_research_user", JSON.stringify(loggedUser));
      setIsNewUser(!!is_new_user);
      setUser(loggedUser);
    } catch (error) {
      console.error("Login verification failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    tokenStore.removeToken();
    localStorage.removeItem("ai_research_user");
    setIsNewUser(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        isNewUser,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
