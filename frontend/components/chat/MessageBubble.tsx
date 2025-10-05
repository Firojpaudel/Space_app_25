'use client';

import { Message } from '@/types';
import { User, Bot, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import EntityHighlight from './EntityHighlight';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-slide-up`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-br from-accent-100 to-accent-200'
            : 'bg-gradient-to-br from-gray-600 to-gray-700'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 space-y-2 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`group relative max-w-3xl rounded-2xl px-5 py-4 ${
            isUser
              ? 'bg-accent-200 text-white ml-auto'
              : 'card'
          }`}
        >
          {/* Copy Button */}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 smooth-transition p-1.5 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover"
              aria-label="Copy message"
            >
              {copied ? (
                <Check className="w-4 h-4 text-accent-200" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          )}

          {/* Message Text */}
          <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : 'dark:prose-invert'}`}>
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            )}
          </div>

          {/* Entity Highlights */}
          {message.entities && message.entities.length > 0 && (
            <div className="mt-3 pt-3 border-t border-light-border dark:border-dark-border">
              <EntityHighlight entities={message.entities} />
            </div>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {message.sources.slice(0, 3).map((source, index) => (
              <a
                key={source.id}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="citation-badge"
              >
                [{index + 1}] {source.title.slice(0, 40)}...
              </a>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-gray-500 dark:text-gray-400 px-2">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
