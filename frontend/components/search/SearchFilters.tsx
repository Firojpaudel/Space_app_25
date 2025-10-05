'use client';

import { useStore } from '@/store/useStore';
import { Filter } from 'lucide-react';

export default function SearchFilters() {
  const { searchFilters, setSearchFilters } = useStore();

  const missions = ['ISS', 'Apollo', 'Space Shuttle', 'Skylab'];
  const organisms = ['Mouse', 'Human', 'Plant', 'Yeast', 'C. elegans'];
  const tissues = ['Bone', 'Muscle', 'Brain', 'Heart', 'Liver'];

  const handleFilterChange = (category: string, value: string, checked: boolean) => {
    const current = searchFilters[category as keyof typeof searchFilters] as string[] || [];
    const updated = checked
      ? [...current, value]
      : current.filter((v) => v !== value);

    setSearchFilters({
      ...searchFilters,
      [category]: updated,
    });
  };

  return (
    <div className="card p-4 space-y-4 sticky top-20">
      <div className="flex items-center gap-2 pb-3 border-b border-light-border dark:border-dark-border">
        <Filter className="w-5 h-5" />
        <h3 className="font-semibold">Filters</h3>
      </div>

      {/* Mission Filter */}
      <div>
        <h4 className="font-medium text-sm mb-2">Mission</h4>
        <div className="space-y-2">
          {missions.map((mission) => (
            <label key={mission} className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                onChange={(e) => handleFilterChange('mission', mission, e.target.checked)}
                className="rounded border-gray-300 text-accent-200 focus:ring-accent-200"
              />
              <span>{mission}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Organism Filter */}
      <div>
        <h4 className="font-medium text-sm mb-2">Organism</h4>
        <div className="space-y-2">
          {organisms.map((organism) => (
            <label key={organism} className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                onChange={(e) => handleFilterChange('organism', organism, e.target.checked)}
                className="rounded border-gray-300 text-accent-200 focus:ring-accent-200"
              />
              <span>{organism}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Tissue Filter */}
      <div>
        <h4 className="font-medium text-sm mb-2">Tissue</h4>
        <div className="space-y-2">
          {tissues.map((tissue) => (
            <label key={tissue} className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                onChange={(e) => handleFilterChange('tissue', tissue, e.target.checked)}
                className="rounded border-gray-300 text-accent-200 focus:ring-accent-200"
              />
              <span>{tissue}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
