'use client';

import { Bot } from 'lucide-react';

export default function LoadingIndicator() {
  return (
    <div className="flex gap-4 mb-6 animate-slide-up">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 dark:from-gray-600 dark:to-gray-700 flex items-center justify-center shadow-sm">
        <Bot className="w-4 h-4 text-white" />
      </div>

      <div className="flex-1 w-full">
        <div className="max-w-xs">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">K-OSMOS is thinking...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
