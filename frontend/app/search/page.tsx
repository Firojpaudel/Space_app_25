'use client';

import { useState } from 'react';
import { useStore } from '@/store/useStore';
import { searchAPI } from '@/utils/api';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import SearchFilters from '@/components/search/SearchFilters';
import SearchResults from '@/components/search/SearchResults';
import { Search } from 'lucide-react';
import { SearchResult } from '@/types';

export default function SearchPage() {
  const { sidebarOpen } = useStore();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const data = await searchAPI.search(q, {}, 20);
      setResults(data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      
      <div className="flex pt-16">
        <Sidebar />
        
        <main className={`flex-1 smooth-transition ${sidebarOpen ? 'ml-80' : 'ml-0'}`}>
          <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Search Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-2">Search Space Biology Research</h1>
              <p className="text-gray-500 dark:text-gray-400">
                Explore 1,175+ publications and datasets
              </p>
            </div>

            {/* Search Bar */}
            <div className="mb-8">
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search for research papers, datasets, or topics..."
                  className="input pl-12 text-lg h-14"
                />
                <Search className="absolute left-4 top-4 w-6 h-6 text-gray-400" />
                <button
                  onClick={() => handleSearch()}
                  disabled={loading}
                  className="absolute right-2 top-2 btn-primary h-10"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Filters */}
              <div className="lg:col-span-1">
                <SearchFilters />
              </div>

              {/* Results */}
              <div className="lg:col-span-3">
                <SearchResults results={results} loading={loading} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
