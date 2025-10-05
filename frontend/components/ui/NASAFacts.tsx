'use client';

import { useState, useEffect } from 'react';
import { Rocket, Star, Moon, Zap } from 'lucide-react';

const nasaFacts = [
  {
    icon: Rocket,
    fact: "NASA's budget is less than Americans spend on pizza each year",
    detail: "NASA's annual budget (~$25B) vs pizza industry (~$50B)"
  },
  {
    icon: Star,
    fact: "A day on Venus is longer than its year",
    detail: "Venus rotates so slowly that one day (243 Earth days) > one year (225 Earth days)"
  },
  {
    icon: Moon,
    fact: "The Moon is moving away from Earth at 3.8cm per year",
    detail: "Same rate your fingernails grow! Eventually, Earth days will be 47 hours long"
  },
  {
    icon: Zap,
    fact: "Space smells like hot metal and welding fumes",
    detail: "Astronauts report this distinct smell when returning from spacewalks"
  },
  {
    icon: Rocket,
    fact: "There's a graveyard of spacecraft on Mars",
    detail: "Over 11 missions have crashed or been lost on the Red Planet"
  },
  {
    icon: Star,
    fact: "Neutron stars are so dense, a teaspoon would weigh 6 billion tons",
    detail: "That's about 900 times the mass of the Great Pyramid of Giza"
  },
  {
    icon: Moon,
    fact: "Saturn's moon Titan has lakes of liquid methane",
    detail: "The only other place in our solar system with stable surface liquids"
  },
  {
    icon: Zap,
    fact: "Jupiter's Great Red Spot is shrinking",
    detail: "This storm has been raging for 400+ years but is now smaller than ever recorded"
  },
  {
    icon: Rocket,
    fact: "The ISS travels at 17,500 mph - that's 5 miles per second 🚀",
    detail: "It completes one orbit around Earth every 90 minutes"
  },
  {
    icon: Star,
    fact: "There are more possible chess games than atoms in the observable universe",
    detail: "Shannon number: 10^120 vs atoms: ~10^80"
  }
];

interface NASAFactsProps {
  className?: string;
  showIcon?: boolean;
}

export default function NASAFacts({ className = "", showIcon = true }: NASAFactsProps) {
  const [currentFact, setCurrentFact] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentFact((prev) => (prev + 1) % nasaFacts.length);
        setIsVisible(true);
      }, 300);
    }, 8000); // Change fact every 8 seconds

    return () => clearInterval(interval);
  }, []);

  const fact = nasaFacts[currentFact];
  const IconComponent = fact.icon;

  return (
    <div className={`transition-all duration-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'} ${className}`}>
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 dark:from-purple-400/10 dark:to-blue-400/10 rounded-lg p-3 border border-purple-200/20 dark:border-purple-700/20">
        <div className="flex items-start gap-2">
          {showIcon && (
            <div className="flex-shrink-0 mt-0.5">
              <IconComponent className="w-4 h-4 text-purple-500 dark:text-purple-400" />
            </div>
          )}
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-1">
              {fact.fact}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {fact.detail}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export { nasaFacts };
