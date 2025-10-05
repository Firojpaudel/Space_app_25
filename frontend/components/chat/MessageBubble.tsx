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
    <div className={`flex gap-4 mb-6 animate-slide-up ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-accent-100 to-accent-200'
            : 'bg-gradient-to-br from-gray-700 to-gray-800 dark:from-gray-600 dark:to-gray-700'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-4xl ${isUser ? 'flex justify-end' : 'flex justify-start'}`}>
        <div className={`group relative ${isUser ? 'max-w-2xl' : 'w-full'}`}>
          {isUser ? (
            // User message bubble
            <div className="relative rounded-2xl px-4 py-3 bg-accent-200 text-white shadow-sm">
              <div className="prose prose-sm max-w-none prose-invert">
                <p className="whitespace-pre-wrap m-0 text-white">{message.content}</p>
              </div>
            </div>
          ) : (
            // Bot response - ChatGPT/Claude style
            <div className="relative w-full">
              {/* Copy Button */}
              <button
                onClick={handleCopy}
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 z-10"
                aria-label="Copy message"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-accent-200" />
                ) : (
                  <Copy className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                )}
              </button>

              {/* Bot Response Content - Clean, justified layout like ChatGPT */}
              <div className="pr-12">
                <div className="prose prose-gray dark:prose-invert max-w-none">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => (
                        <p className="mb-6 last:mb-0 leading-7 text-gray-800 dark:text-gray-200 text-justify">
                          {children}
                        </p>
                      ),
                      h1: ({ children }) => (
                        <h1 className="text-2xl font-bold mb-6 mt-8 first:mt-0 text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700 pb-3">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-xl font-semibold mb-4 mt-8 first:mt-0 text-gray-900 dark:text-gray-100">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-lg font-semibold mb-3 mt-6 first:mt-0 text-gray-900 dark:text-gray-100">
                          {children}
                        </h3>
                      ),
                      h4: ({ children }) => (
                        <h4 className="text-base font-semibold mb-2 mt-4 first:mt-0 text-gray-900 dark:text-gray-100">
                          {children}
                        </h4>
                      ),
                      ul: ({ children }) => (
                        <ul className="space-y-3 ml-6 mb-6 list-disc">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="space-y-3 ml-6 mb-6 list-decimal">
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className="text-gray-700 dark:text-gray-300 leading-7 text-justify pl-2">
                          {children}
                        </li>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-accent-200 pl-6 italic text-gray-600 dark:text-gray-400 my-6 bg-gray-50 dark:bg-gray-800/50 py-4 rounded-r text-justify">
                          {children}
                        </blockquote>
                      ),
                      code: ({ children, ...props }) => {
                        const isInline = !props.className?.includes('language-');
                        return isInline ? (
                          <code className="px-2 py-1 text-sm bg-accent-50/20 text-accent-200 dark:bg-accent-300/20 dark:text-accent-100 rounded font-mono border border-accent-100/20 dark:border-accent-200/20 mx-1">
                            {children}
                          </code>
                        ) : (
                          <code className="block">{children}</code>
                        );
                      },
                      pre: ({ children }) => (
                        <pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm border border-gray-200 dark:border-gray-700 my-6 font-mono leading-6">
                          {children}
                        </pre>
                      ),
                      a: ({ children, href }) => (
                        <a 
                          href={href} 
                          className="text-accent-200 hover:text-accent-100 dark:text-accent-100 dark:hover:text-accent-50 underline decoration-accent-200/30 hover:decoration-accent-200 transition-colors font-medium"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {children}
                        </a>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-semibold text-gray-900 dark:text-gray-100">
                          {children}
                        </strong>
                      ),
                      em: ({ children }) => (
                        <em className="italic text-gray-700 dark:text-gray-300">
                          {children}
                        </em>
                      ),
                      table: ({ children }) => (
                        <div className="overflow-x-auto my-6">
                          <table className="min-w-full border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
                            {children}
                          </table>
                        </div>
                      ),
                      th: ({ children }) => (
                        <th className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 text-left font-semibold text-gray-900 dark:text-gray-100 text-sm">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="px-4 py-3 border-b border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm leading-6">
                          {children}
                        </td>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Entity Highlights */}
              {message.entities && message.entities.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
                  <EntityHighlight entities={message.entities} />
                </div>
              )}
            </div>
          )}

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {message.sources.slice(0, 3).map((source, index) => (
                <a
                  key={source.id}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="citation-badge"
                >
                  <span className="mr-1">[{index + 1}]</span>
                  {source.title.slice(0, 40)}...
                </a>
              ))}
            </div>
          )}

          {/* Timestamp */}
          <div className={`mt-2 text-xs text-gray-500 dark:text-gray-400 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}
