'use client';

import { useState, KeyboardEvent } from 'react';
import { Send, Mic, Paperclip } from 'lucide-react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function InputBox({ onSend, disabled }: InputBoxProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative flex items-end gap-3">
      {/* Input Field */}
      <div className="flex-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-2xl overflow-hidden shadow-sm focus-within:border-accent-200 dark:focus-within:border-accent-100 focus-within:shadow-md transition-all duration-200">
        <div className="flex items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about space biology research..."
            disabled={disabled}
            rows={1}
            className="flex-1 px-4 py-3 bg-transparent resize-none focus:outline-none max-h-32 custom-scrollbar text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            style={{ minHeight: '52px' }}
          />
          
          <div className="flex items-center gap-1 px-2 pb-2">
            <button
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150"
              aria-label="Attach file"
            >
              <Paperclip className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
            <button
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150"
              aria-label="Voice input"
            >
              <Mic className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Send Button */}
      <button
        onClick={handleSend}
        disabled={!input.trim() || disabled}
        className={`flex-shrink-0 p-3 rounded-xl transition-all duration-200 ${
          input.trim() && !disabled
            ? 'bg-accent-200 hover:bg-accent-100 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
            : 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
        }`}
        aria-label="Send message"
      >
        <Send className="w-5 h-5" />
      </button>
    </div>
  );
}
