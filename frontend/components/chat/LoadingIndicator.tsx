'use client';

import { Bot } from 'lucide-react';

export default function LoadingIndicator() {
  return (
    <div className="flex gap-4 animate-slide-up">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
        <Bot className="w-5 h-5 text-white" />
      </div>

      <div className="flex-1">
        <div className="card rounded-2xl px-5 py-4 max-w-xs">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-accent-200 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm text-gray-500 dark:text-gray-400">Thinking...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
