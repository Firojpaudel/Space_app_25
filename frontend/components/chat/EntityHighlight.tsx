'use client';

import { ExtractedEntity } from '@/types';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface EntityHighlightProps {
  entities: ExtractedEntity[];
}

export default function EntityHighlight({ entities }: EntityHighlightProps) {
  const [selectedEntity, setSelectedEntity] = useState<ExtractedEntity | null>(null);

  const entityTypeColors = {
    organism: 'entity-organism',
    tissue: 'entity-tissue',
    gene: 'entity-gene',
    protein: 'entity-protein',
    mission: 'entity-mission',
  };

  const groupedEntities = entities.reduce((acc, entity) => {
    if (!acc[entity.type]) {
      acc[entity.type] = [];
    }
    acc[entity.type].push(entity);
    return acc;
  }, {} as Record<string, ExtractedEntity[]>);

  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
        Extracted Entities
      </p>
      
      <div className="flex flex-wrap gap-2">
        {Object.entries(groupedEntities).map(([type, items]) => (
          <div key={type} className="flex flex-wrap gap-1.5">
            {items.slice(0, 5).map((entity, index) => (
              <motion.button
                key={`${entity.type}-${entity.value}-${index}`}
                onClick={() => setSelectedEntity(entity)}
                className={`${entityTypeColors[entity.type as keyof typeof entityTypeColors]} text-xs font-medium`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {entity.value}
              </motion.button>
            ))}
          </div>
        ))}
      </div>

      {/* Entity Popover */}
      <AnimatePresence>
        {selectedEntity && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="popover mt-2"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
                  {selectedEntity.type}
                </span>
                <button
                  onClick={() => setSelectedEntity(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  ×
                </button>
              </div>
              <p className="font-medium">{selectedEntity.value}</p>
              {selectedEntity.confidence && (
                <p className="text-xs text-gray-500">
                  Confidence: {(selectedEntity.confidence * 100).toFixed(1)}%
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
