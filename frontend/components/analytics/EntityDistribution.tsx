'use client';

import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function EntityDistribution() {
  const data = [
    {
      labels: ['Mouse', 'Human', 'Plant', 'Yeast', 'C. elegans'],
      values: [234, 189, 145, 98, 76],
      type: 'pie',
      marker: {
        colors: ['#66CDAA', '#3CB371', '#2E8B57', '#1A4314', '#0B3D0B'],
      },
    },
  ];

  const layout = {
    title: {
      text: 'Research by Organism',
      font: { size: 16, family: 'Space Grotesk' },
    },
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
