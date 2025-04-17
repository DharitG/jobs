import { create } from 'zustand';

// Define the state structure
interface AppState {
  // Example state: theme preference
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: AppState['theme']) => void;

  // Add other global state properties here as needed
  // e.g., userProfile: UserProfile | null;
  // e.g., setUserProfile: (profile: UserProfile | null) => void;
}

// Create the store hook
export const useAppStore = create<AppState>((set) => ({
  // Initial state
  theme: 'system', // Default theme

  // Actions to update state
  setTheme: (newTheme) => set({ theme: newTheme }),

  // Add other initial state values and actions here
  // userProfile: null,
  // setUserProfile: (profile) => set({ userProfile: profile }),
}));

// Optional: Persist part of the store to localStorage (if needed)
// import { persist, createJSONStorage } from 'zustand/middleware';
// export const useAppStore = create(
//   persist<AppState>(
//     (set) => ({
//       theme: 'system',
//       setTheme: (newTheme) => set({ theme: newTheme }),
//     }),
//     {
//       name: 'app-storage', // Name for localStorage key
//       storage: createJSONStorage(() => localStorage), // Use localStorage
//       partialize: (state) => ({ theme: state.theme }), // Only persist the theme
//     }
//   )
// );
