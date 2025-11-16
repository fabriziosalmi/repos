<!-- frontend/src/components/RepoCard.vue -->
<script setup lang="ts">
import { formatDistanceToNow } from 'date-fns';
// import { it } from 'date-fns/locale'; // Per avere "2 settimane fa" in italiano
import { Star, GitFork, Users, GitCommit, TrendingUp, Heart, Bus, AlertTriangle } from 'lucide-vue-next'; // Import icons
import type { Repo } from '../types';

defineProps<{
  repo: Repo;
}>();

const getLanguageColor = (lang: string) => {
  // Simple hash to give a unique but consistent color
  const colors = ['bg-cyan-500', 'bg-fuchsia-500', 'bg-emerald-500', 'bg-amber-500', 'bg-red-500'];
  if (!lang) return 'bg-gray-500';
  let hash = 0;
  for (let i = 0; i < lang.length; i++) {
    hash = lang.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

const getMomentumColor = (score: number) => {
  if (score >= 70) return 'text-green-400';
  if (score >= 40) return 'text-yellow-400';
  return 'text-gray-500';
}

const getHealthColor = (status: string) => {
  if (status === 'healthy') return 'text-green-400';
  if (status === 'moderate') return 'text-yellow-400';
  if (status === 'needs_attention') return 'text-red-400';
  return 'text-gray-500';
}

const getBusFactorColor = (riskLevel: string) => {
  if (riskLevel === 'critical') return 'text-red-400';
  if (riskLevel === 'moderate') return 'text-yellow-400';
  if (riskLevel === 'healthy') return 'text-green-400';
  return 'text-gray-500';
}
</script>

<template>
  <div 
    class="repo-card group flex flex-col border border-cyan-400/20 bg-slate-900/50 p-4 rounded-md
           backdrop-blur-sm transition-all duration-300 hover:border-cyan-400/80 hover:scale-[1.02] 
           hover:shadow-2xl hover:shadow-cyan-500/10 cursor-pointer"
    role="button"
    tabindex="0"
    @keydown.enter="$emit('click')"
  >
    
    <!-- HEADER -->
    <div class="flex-grow">
      <header class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-bold text-cyan-300 group-hover:text-cyan-200 truncate flex-1">
          <a :href="repo.url" target="_blank" rel="noopener noreferrer" class="hover:underline">
            {{ repo.name }}
          </a>
        </h3>
        <div class="flex items-center gap-2">
          <!-- Momentum Score Indicator -->
          <div v-if="repo.momentum && repo.momentum.score > 0" 
               class="flex items-center gap-1 text-xs"
               :title="`Momentum Score: ${repo.momentum.score} | +${repo.momentum.stars_7d} stars (7d)`">
            <TrendingUp :class="['h-3 w-3', getMomentumColor(repo.momentum.score)]" />
            <span :class="getMomentumColor(repo.momentum.score)">+{{ repo.momentum.stars_7d }}</span>
          </div>
          <span class="text-xs font-mono px-2 py-1 rounded-full bg-slate-800 text-fuchsia-400">{{ repo.status }}</span>
        </div>
      </header>
      
      <!-- BODY -->
      <p class="text-sm text-slate-400 mb-4 h-10 overflow-hidden">
        {{ repo.description || 'No description available.' }}
      </p>
    </div>

    <!-- FOOTER / STATS -->
    <footer class="mt-auto border-t border-slate-700/50 pt-3 text-xs text-slate-300">
      <!-- Health & Risk Indicators -->
      <div v-if="repo.issue_health || repo.bus_factor" class="flex gap-3 mb-2 pb-2 border-b border-slate-700/30">
        <!-- Issue Health -->
        <div v-if="repo.issue_health" 
             class="flex items-center gap-1"
             :title="`Health: ${repo.issue_health.status} | Avg Response: ${repo.issue_health.avg_response_hours}h | Stale: ${repo.issue_health.stale_issues_count}`">
          <Heart :class="['h-3 w-3', getHealthColor(repo.issue_health.status)]" />
          <span :class="getHealthColor(repo.issue_health.status)">{{ repo.issue_health.health_score.toFixed(0) }}</span>
        </div>
        <!-- Bus Factor -->
        <div v-if="repo.bus_factor" 
             class="flex items-center gap-1"
             :title="`Bus Factor: ${repo.bus_factor.bus_factor} | Risk: ${repo.bus_factor.risk_level}`">
          <component :is="repo.bus_factor.risk_level === 'critical' ? AlertTriangle : Bus" 
                     :class="['h-3 w-3', getBusFactorColor(repo.bus_factor.risk_level)]" />
          <span :class="getBusFactorColor(repo.bus_factor.risk_level)">{{ repo.bus_factor.bus_factor }}</span>
        </div>
      </div>
      <div class="flex justify-between items-center mb-2">
        <div class="flex items-center gap-1">
          <span :class="[getLanguageColor(repo.language), 'w-3 h-3 rounded-full']"></span>
          <span>{{ repo.language || 'N/A' }}</span>
        </div>
        <span class="font-mono">{{ repo.version }}</span>
      </div>
      <div class="grid grid-cols-4 gap-2 text-center">
        <div class="stat-item flex flex-col items-center">
          <Star class="h-4 w-4 text-yellow-400" />
          <span>{{ repo.stars }}</span>
        </div>
        <div class="stat-item flex flex-col items-center">
          <GitFork class="h-4 w-4 text-blue-400" />
          <span>{{ repo.forks }}</span>
        </div>
        <div class="stat-item flex flex-col items-center">
          <GitCommit class="h-4 w-4 text-purple-400" />
          <span>{{ repo.commits }}</span>
        </div>
        <div class="stat-item flex flex-col items-center">
          <Users class="h-4 w-4 text-green-400" />
          <span>{{ repo.contributors }}</span>
        </div>
      </div>
       <div class="text-center text-slate-500 mt-3">
         Updated {{ repo.last_update_api ? formatDistanceToNow(new Date(repo.last_update_api), { addSuffix: true }) : repo.last_update_str || 'Unknown' }}
       </div>
    </footer>
  </div>
</template>
