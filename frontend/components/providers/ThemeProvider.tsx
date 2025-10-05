'use client';

import { useEffect } from 'react';
import { useStore } from '@/store/useStore';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useStore();

  // Initialize theme on mount
  useEffect(() => {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    
    // If no saved preference, check system preference
    if (!savedTheme) {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initialTheme = systemPrefersDark ? 'dark' : 'dark'; // Default to dark
      setTheme(initialTheme);
      localStorage.setItem('theme', initialTheme);
    } else if (savedTheme !== theme) {
      setTheme(savedTheme);
    }
  }, []);

  // Apply theme class whenever theme changes
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  return <>{children}</>;
}
