"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { AuthContext } from "./context";
import { authApi } from "@/lib/api/auth";
import { tokenUtils } from "./utils";
import type { User } from "@/lib/types";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    try {
      const token = tokenUtils.getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const userData = await authApi.me();
      setUser(userData);
    } catch (error) {
      tokenUtils.removeToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password });
      tokenUtils.setToken(response.access_token);
      if (response.user) {
        setUser(response.user);
      } else {
        await loadUser();
      }
      router.push("/");
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string, username: string) => {
    try {
      const response = await authApi.register({ email, password, username });
      tokenUtils.setToken(response.access_token);
      if (response.user) {
        setUser(response.user);
      } else {
        await loadUser();
      }
      router.push("/");
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      tokenUtils.removeToken();
      setUser(null);
      router.push("/login");
    }
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


