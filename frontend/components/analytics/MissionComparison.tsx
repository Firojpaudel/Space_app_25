'use client';

import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function MissionComparison() {
  const data = [
    {
      x: ['ISS', 'Apollo', 'Space Shuttle', 'Skylab'],
      y: [345, 67, 123, 45],
      type: 'bar',
      marker: { color: ['#3CB371', '#2E8B57', '#1A4314', '#0B3D0B'] },
    },
  ];

  const layout = {
    title: {
      text: 'Research by Mission',
      font: { size: 16, family: 'Space Grotesk' },
    },
    xaxis: { title: 'Mission' },
    yaxis: { title: 'Number of Studies' },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Space Grotesk' },
  };

  return (
    <div>
      <Plot
        data={data as any}
        layout={layout as any}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%', height: '300px' }}
      />
    </div>
  );
}
