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
    <div className="relative flex items-end gap-2">
      {/* Input Field */}
      <div className="flex-1 card rounded-2xl overflow-hidden">
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
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 smooth-transition"
              aria-label="Attach file"
            >
              <Paperclip className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
            <button
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 smooth-transition"
              aria-label="Voice input"
            >
              <Mic className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Send Button */}
      <button
        onClick={handleSend}
        disabled={!input.trim() || disabled}
        className={`flex-shrink-0 p-3 rounded-xl smooth-transition ${
          input.trim() && !disabled
            ? 'bg-accent-200 hover:bg-accent-100 text-white shadow-lg shadow-accent-200/30'
            : 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
        }`}
        aria-label="Send message"
      >
        <Send className="w-5 h-5" />
      </button>
    </div>
  );
}
