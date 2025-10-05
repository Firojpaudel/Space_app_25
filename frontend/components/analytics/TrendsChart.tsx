'use client';

import { useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { TrendData } from '@/types';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface TrendsChartProps {
  data: TrendData[];
}

export default function TrendsChart({ data }: TrendsChartProps) {
  const chartData = [
    {
      x: data.map((d) => d.year),
      y: data.map((d) => d.count),
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#2E8B57', size: 8 },
      line: { color: '#2E8B57', width: 3 },
      name: 'Publications',
    },
  ];

  const layout = {
    title: {
      text: 'Research Trends Over Time',
      font: { size: 18, family: 'Space Grotesk' },
    },
    xaxis: { title: 'Year' },
    yaxis: { title: 'Number of Publications' },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Space Grotesk' },
  };

  return (
    <div>
      <Plot
        data={chartData as any}
        layout={layout as any}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%', height: '400px' }}
      />
    </div>
  );
}
