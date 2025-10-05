'use client';

import { Source } from '@/types';
import { ExternalLink, BookOpen, Database, Folder } from 'lucide-react';

interface SourcesPanelProps {
  sources: Source[];
}

export default function SourcesPanel({ sources }: SourcesPanelProps) {
  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'publication':
        return <BookOpen className="w-4 h-4" />;
      case 'dataset':
        return <Database className="w-4 h-4" />;
      case 'project':
        return <Folder className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  return (
    <div className="w-96 border-l border-light-border dark:border-dark-border bg-light-bg dark:bg-dark-bg overflow-y-auto custom-scrollbar">
      <div className="p-4 border-b border-light-border dark:border-dark-border sticky top-0 bg-light-bg dark:bg-dark-bg z-10">
        <h3 className="font-semibold text-lg">Sources ({sources.length})</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Referenced in this response
        </p>
      </div>

      <div className="p-4 space-y-3">
        {sources.map((source, index) => (
          <div
            key={source.id}
            className="card-hover p-4 space-y-2 animate-slide-up"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2 flex-1 min-w-0">
                <div className="flex-shrink-0 p-2 rounded-lg bg-accent-200/10 text-accent-200">
                  {getSourceIcon(source.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm line-clamp-2">{source.title}</h4>
                  {source.authors && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {source.authors}
                    </p>
                  )}
                </div>
              </div>
              
              {source.url && (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 p-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover smooth-transition"
                  aria-label="Open source"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            {source.abstract && (
              <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
                {source.abstract}
              </p>
            )}

            <div className="flex items-center justify-between pt-2 border-t border-light-border dark:border-dark-border">
              <span className="text-xs px-2 py-1 rounded-full bg-light-hover dark:bg-dark-hover">
                {source.type}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Relevance: {(source.score * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
