// src/types.ts
export interface Momentum {
  score: number;
  stars_7d: number;
  stars_30d: number;
  trend: 'rising' | 'growing' | 'stable';
}

export interface IssueHealth {
  health_score: number;
  status: 'healthy' | 'moderate' | 'needs_attention' | 'unknown';
  avg_response_hours: number;
  stale_issues_count: number;
}

export interface BusFactor {
  bus_factor: number;
  risk_level: 'critical' | 'moderate' | 'healthy' | 'unknown';
}

export interface Commit {
  sha: string;
  message: string;
  author: string;
  date: string;
  url: string;
}

export interface Contributor {
  login: string;
  avatar_url: string;
  contributions: number;
  profile_url: string;
}

export interface Repo {
  name: string;
  full_name: string;
  description: string;
  language: string;
  version?: string;
  stars: number;
  forks: number;
  commits: number;
  contributors: number;
  last_update_api?: string; // ISO 8601 format from API
  last_update_str?: string; // Human readable format
  created_at_api?: string;
  url: string;
  status?: string;
  open_issues_count?: number;
  owner?: {
    login: string;
  };
  // Oracle V2 Advanced Metrics
  momentum?: Momentum;
  issue_health?: IssueHealth;
  bus_factor?: BusFactor;
}
