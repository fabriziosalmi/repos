<!-- frontend/src/components/RepoCard.vue -->
<script setup lang="ts">
import { formatDistanceToNow } from 'date-fns';
// import { it } from 'date-fns/locale'; // Per avere "2 settimane fa" in italiano
import { Star, GitFork, Users, GitCommit } from 'lucide-vue-next'; // Import icons
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
</script>

<template>
  <div class="repo-card group flex flex-col border border-cyan-400/20 bg-slate-900/50 p-4 rounded-md
              backdrop-blur-sm transition-all duration-300 hover:border-cyan-400/80 hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/10">
    
    <!-- HEADER -->
    <div class="flex-grow">
      <header class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-bold text-cyan-300 group-hover:text-cyan-200 truncate">
          <a :href="repo.url" target="_blank" rel="noopener noreferrer" class="hover:underline">
            {{ repo.name }}
          </a>
        </h3>
        <span class="text-xs font-mono px-2 py-1 rounded-full bg-slate-800 text-fuchsia-400">{{ repo.status }}</span>
      </header>
      
      <!-- BODY -->
      <p class="text-sm text-slate-400 mb-4 h-10 overflow-hidden">
        {{ repo.description || 'No description available.' }}
      </p>
    </div>

    <!-- FOOTER / STATS -->
    <footer class="mt-auto border-t border-slate-700/50 pt-3 text-xs text-slate-300">
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
         Updated {{ formatDistanceToNow(new Date(repo.last_update), { addSuffix: true }) }}
       </div>
    </footer>
  </div>
</template>
