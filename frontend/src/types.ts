// src/types.ts
export interface Repo {
  name: string;
  description: string;
  language: string;
  version: string;
  stars: number;
  forks: number;
  commits: number;
  contributors: number;
  last_update: string; // ISO 8601 format string
  url: string;
  status: string;
}
