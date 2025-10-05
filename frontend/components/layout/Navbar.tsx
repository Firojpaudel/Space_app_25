'use client';

import { useStore } from '@/store/useStore';
import { Moon, Sun, Menu, Search } from 'lucide-react';
import Image from 'next/image';

export default function Navbar() {
  const { theme, toggleTheme, toggleSidebar } = useStore();

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 h-16 shadow-sm">
      <div className="h-full px-4 flex items-center justify-between text-gray-900 dark:text-gray-100">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 smooth-transition"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-100 to-accent-200 flex items-center justify-center">
              <span className="text-white font-bold text-sm">K</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold gradient-text">K-OSMOS</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Space Biology Knowledge Engine
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 smooth-transition"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-yellow-400" />
            ) : (
              <Moon className="w-5 h-5 text-indigo-600" />
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}
