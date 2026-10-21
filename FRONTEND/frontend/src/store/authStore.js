
import { create } from "zustand";
import { authApi, initializeCsrf } from "../api/api";

export const useAuthStore = create((set) => ({
  user: null,
  loading: true,
  error: null,

  initialize: async () => {
    set({ loading: true, error: null });

    try {
      await initializeCsrf();

      const user = await authApi.me();
      set({ user, loading: false });
    } catch {
      set({ user: null, loading: false });
    }
  },

  register: async (payload) => {
    set({ error: null });

    try {
      return await authApi.register(payload);
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  login: async (payload) => {
    set({ error: null });

    try {
      await initializeCsrf();

      await authApi.login(payload);

      // Verify the cookie-based session with the backend.
      const user = await authApi.me();

      set({ user, loading: false });
      return user;
    } catch (error) {
      set({ user: null, error: error.message, loading: false });
      throw error;
    }
  },

  logout: async () => {
    set({ error: null });

    try {
      await initializeCsrf();
      await authApi.logout();
    } finally {
      // Clear local auth state even if the request fails.
      set({ user: null, loading: false });
    }
  },
}));
