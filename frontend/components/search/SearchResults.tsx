'use client';

import { SearchResult } from '@/types';
import { ExternalLink, BookOpen, Database, Folder } from 'lucide-react';

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
}

export default function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card p-6 space-y-3">
            <div className="skeleton h-6 w-3/4" />
            <div className="skeleton h-4 w-1/4" />
            <div className="skeleton h-20 w-full" />
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="card p-12 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          No results found. Try a different search query.
        </p>
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'publication':
        return <BookOpen className="w-5 h-5" />;
      case 'dataset':
        return <Database className="w-5 h-5" />;
      case 'project':
        return <Folder className="w-5 h-5" />;
      default:
        return <BookOpen className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Found {results.length} results
      </p>

      {results.map((result, index) => (
        <div
          key={result.id}
          className="card-hover p-6 space-y-3 animate-slide-up"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3 flex-1">
              <div className="flex-shrink-0 p-2 rounded-lg bg-accent-200/10 text-accent-200">
                {getIcon(result.sourceType)}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg mb-1">{result.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
                  {result.content}
                </p>
              </div>
            </div>

            {result.url && (
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-shrink-0 p-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover smooth-transition"
              >
                <ExternalLink className="w-5 h-5" />
              </a>
            )}
          </div>

          <div className="flex items-center gap-3 pt-3 border-t border-light-border dark:border-dark-border">
            <span className="text-xs px-2 py-1 rounded-full bg-light-hover dark:bg-dark-hover">
              {result.sourceType}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Relevance: {(result.score * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
