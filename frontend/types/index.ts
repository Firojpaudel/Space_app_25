export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  entities?: ExtractedEntity[];
}

export interface Source {
  id: string;
  title: string;
  authors?: string;
  score: number;
  url?: string;
  type: 'publication' | 'dataset' | 'project';
  abstract?: string;
}

export interface ExtractedEntity {
  type: 'organism' | 'tissue' | 'gene' | 'protein' | 'mission';
  value: string;
  confidence?: number;
  start?: number;
  end?: number;
}

export interface SearchFilters {
  mission?: string[];
  organism?: string[];
  tissue?: string[];
  studyType?: string[];
  dateRange?: {
    start?: string;
    end?: string;
  };
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  sourceType: 'publication' | 'dataset' | 'project';
  url?: string;
  score: number;
  highlights?: string[];
  metadata: Record<string, any>;
}

export interface AnalyticsData {
  trends: TrendData[];
  missionComparison: MissionData[];
  entityDistribution: EntityDistribution[];
}

export interface TrendData {
  year: number;
  count: number;
  category: string;
}

export interface MissionData {
  mission: string;
  count: number;
  organisms: string[];
}

export interface EntityDistribution {
  entity: string;
  count: number;
  type: string;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
}

export type Theme = 'light' | 'dark';
