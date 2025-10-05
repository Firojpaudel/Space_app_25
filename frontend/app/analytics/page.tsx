'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/store/useStore';
import { analyticsAPI } from '@/utils/api';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import TrendsChart from '@/components/analytics/TrendsChart';
import MissionComparison from '@/components/analytics/MissionComparison';
import EntityDistribution from '@/components/analytics/EntityDistribution';

export default function AnalyticsPage() {
  const { sidebarOpen } = useStore();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const trends = await analyticsAPI.getTrends();
        setData(trends);
      } catch (error) {
        console.error('Error loading analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  return (
    <div className="min-h-screen">
      <Navbar />
      
      <div className="flex pt-16">
        <Sidebar />
        
        <main className={`flex-1 smooth-transition ${sidebarOpen ? 'ml-80' : 'ml-0'}`}>
          <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-2">Research Analytics</h1>
              <p className="text-gray-500 dark:text-gray-400">
                Insights and trends from space biology research
              </p>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="card p-6">
                    <div className="skeleton h-64 w-full" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-6">
                <div className="card p-6">
                  <TrendsChart data={data?.trends || []} />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="card p-6">
                    <MissionComparison />
                  </div>

                  <div className="card p-6">
                    <EntityDistribution />
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
