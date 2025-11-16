<!-- components/RepoDetailModal.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { X, Star, GitFork, Calendar, TrendingUp, Heart, Bus, AlertCircle } from 'lucide-vue-next';
import VueApexCharts from 'vue3-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { Repo, Commit, Contributor } from '../types';
import { formatDistanceToNow } from 'date-fns';

const props = defineProps<{
  repo: Repo;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const commits = ref<Commit[]>([]);
const contributors = ref<Contributor[]>([]);
const isLoadingDetails = ref(false);

// Star history chart configuration
const starHistoryOptions = computed<ApexOptions>(() => ({
  chart: {
    type: 'area',
    background: 'transparent',
    toolbar: { show: false },
    zoom: { enabled: false },
  },
  theme: { mode: 'dark' },
  stroke: { curve: 'smooth', width: 2, colors: ['#00ffcc'] },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3,
      stops: [0, 90, 100]
    }
  },
  dataLabels: { enabled: false },
  xaxis: {
    type: 'datetime',
    labels: { style: { colors: '#94a3b8' } }
  },
  yaxis: {
    labels: { style: { colors: '#94a3b8' } }
  },
  grid: {
    borderColor: '#334155',
    strokeDashArray: 4,
  },
  tooltip: {
    theme: 'dark',
    x: { format: 'dd MMM yyyy' }
  }
}));

// Mock star history data (in real app, fetch from backend)
const starHistorySeries = computed(() => [{
  name: 'Stars',
  data: generateMockStarHistory()
}]);

function generateMockStarHistory() {
  const data = [];
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  const totalStars = props.repo.stars;
  
  for (let i = 30; i >= 0; i--) {
    const date = now - (i * dayMs);
    const stars = Math.floor(totalStars * (1 - i / 35));
    data.push({ x: date, y: stars });
  }
  return data;
}

onMounted(async () => {
  if (props.isOpen) {
    await loadRepoDetails();
  }
});

async function loadRepoDetails() {
  isLoadingDetails.value = true;
  try {
    // In real app, these would be API calls
    // For now, use mock data
    commits.value = generateMockCommits();
    contributors.value = generateMockContributors();
  } catch (error) {
    console.error('Failed to load repo details:', error);
  } finally {
    isLoadingDetails.value = false;
  }
}

function generateMockCommits(): Commit[] {
  return [
    {
      sha: 'abc123',
      message: 'feat: add new feature',
      author: 'developer1',
      date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      url: props.repo.url + '/commit/abc123'
    },
    {
      sha: 'def456',
      message: 'fix: resolve bug in component',
      author: 'developer2',
      date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      url: props.repo.url + '/commit/def456'
    },
    {
      sha: 'ghi789',
      message: 'docs: update README',
      author: 'developer1',
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      url: props.repo.url + '/commit/ghi789'
    },
  ];
}

function generateMockContributors(): Contributor[] {
  return [
    { 
      login: 'developer1', 
      contributions: 145, 
      avatar_url: 'https://github.com/identicons/dev1.png',
      profile_url: 'https://github.com/developer1'
    },
    { 
      login: 'developer2', 
      contributions: 87, 
      avatar_url: 'https://github.com/identicons/dev2.png',
      profile_url: 'https://github.com/developer2'
    },
    { 
      login: 'developer3', 
      contributions: 42, 
      avatar_url: 'https://github.com/identicons/dev3.png',
      profile_url: 'https://github.com/developer3'
    },
  ];
}

function handleClose() {
  emit('close');
}

function handleBackdropClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    handleClose();
  }
}

function getMomentumColor() {
  const score = props.repo.momentum?.score || 0;
  if (score >= 70) return 'text-green-400';
  if (score >= 40) return 'text-yellow-400';
  return 'text-gray-400';
}

function getHealthColor() {
  const status = props.repo.issue_health?.status;
  if (status === 'healthy') return 'text-green-400';
  if (status === 'moderate') return 'text-yellow-400';
  if (status === 'needs_attention') return 'text-red-400';
  return 'text-gray-400';
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        @click="handleBackdropClick"
      >
        <div class="bg-slate-900 border-2 border-cyber-primary rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-cyber-glow">
          <!-- Header -->
          <div class="sticky top-0 bg-slate-900 border-b border-cyber-primary/30 p-6 flex justify-between items-start z-10">
            <div>
              <h2 class="text-2xl font-bold text-cyber-primary">{{ repo.name }}</h2>
              <p class="text-gray-400 mt-1">{{ repo.description || 'No description available' }}</p>
              <div class="flex gap-4 mt-3">
                <a :href="repo.url" target="_blank" class="text-sm text-cyan-400 hover:text-cyan-300 underline">
                  View on GitHub
                </a>
              </div>
            </div>
            <button
              @click="handleClose"
              class="p-2 hover:bg-slate-800 rounded-full transition-colors"
            >
              <X class="h-6 w-6 text-gray-400" />
            </button>
          </div>

          <!-- Content -->
          <div class="p-6 space-y-6">
            <!-- Stats Overview -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div class="flex items-center gap-2 text-yellow-400 mb-2">
                  <Star class="h-4 w-4" />
                  <span class="text-xs uppercase">Stars</span>
                </div>
                <p class="text-2xl font-bold">{{ repo.stars.toLocaleString() }}</p>
              </div>
              <div class="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div class="flex items-center gap-2 text-blue-400 mb-2">
                  <GitFork class="h-4 w-4" />
                  <span class="text-xs uppercase">Forks</span>
                </div>
                <p class="text-2xl font-bold">{{ repo.forks.toLocaleString() }}</p>
              </div>
              <div v-if="repo.momentum" class="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div class="flex items-center gap-2 mb-2" :class="getMomentumColor()">
                  <TrendingUp class="h-4 w-4" />
                  <span class="text-xs uppercase">Momentum</span>
                </div>
                <p class="text-2xl font-bold">{{ repo.momentum.score.toFixed(0) }}</p>
                <p class="text-xs text-gray-400 mt-1">+{{ repo.momentum.stars_7d }} (7d)</p>
              </div>
              <div v-if="repo.issue_health" class="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div class="flex items-center gap-2 mb-2" :class="getHealthColor()">
                  <Heart class="h-4 w-4" />
                  <span class="text-xs uppercase">Health</span>
                </div>
                <p class="text-2xl font-bold">{{ repo.issue_health.health_score.toFixed(0) }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ repo.issue_health.status }}</p>
              </div>
            </div>

            <!-- Star History Chart -->
            <div class="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
              <h3 class="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                <TrendingUp class="h-5 w-5" />
                Star History (Last 30 Days)
              </h3>
              <VueApexCharts
                type="area"
                height="250"
                :options="starHistoryOptions"
                :series="starHistorySeries"
              />
            </div>

            <!-- Recent Commits -->
            <div class="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
              <h3 class="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                <Calendar class="h-5 w-5" />
                Recent Commits
              </h3>
              <div v-if="isLoadingDetails" class="text-center py-8">
                <p class="text-gray-400 animate-pulse">Loading commits...</p>
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="commit in commits"
                  :key="commit.sha"
                  class="flex items-start gap-3 p-3 bg-slate-900/50 rounded border border-slate-700 hover:border-cyan-500/50 transition-colors"
                >
                  <div class="flex-1">
                    <p class="text-sm font-mono text-gray-300">{{ commit.message }}</p>
                    <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{{ commit.author }}</span>
                      <span>•</span>
                      <span>{{ formatDistanceToNow(new Date(commit.date), { addSuffix: true }) }}</span>
                    </div>
                  </div>
                  <a
                    :href="commit.url"
                    target="_blank"
                    class="text-cyan-400 hover:text-cyan-300 text-xs font-mono"
                  >
                    {{ commit.sha.substring(0, 7) }}
                  </a>
                </div>
              </div>
            </div>

            <!-- Top Contributors -->
            <div class="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
              <h3 class="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                <Bus class="h-5 w-5" />
                Top Contributors
              </h3>
              <div v-if="isLoadingDetails" class="text-center py-8">
                <p class="text-gray-400 animate-pulse">Loading contributors...</p>
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="contributor in contributors"
                  :key="contributor.login"
                  class="flex items-center gap-3 p-3 bg-slate-900/50 rounded border border-slate-700"
                >
                  <img
                    :src="contributor.avatar_url"
                    :alt="contributor.login"
                    class="w-10 h-10 rounded-full border-2 border-cyan-500/30"
                  />
                  <div class="flex-1">
                    <p class="text-sm font-bold text-gray-300">{{ contributor.login }}</p>
                    <p class="text-xs text-gray-500">{{ contributor.contributions }} contributions</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Health Alerts -->
            <div v-if="repo.bus_factor?.risk_level === 'critical' || repo.issue_health?.status === 'needs_attention'" 
                 class="bg-red-900/20 border border-red-500/50 p-4 rounded-lg">
              <div class="flex items-start gap-3">
                <AlertCircle class="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 class="font-bold text-red-400 mb-1">Action Required</h4>
                  <ul class="text-sm text-gray-300 space-y-1">
                    <li v-if="repo.bus_factor?.risk_level === 'critical'">
                      ⚠️ Critical bus factor: Project depends on single contributor
                    </li>
                    <li v-if="repo.issue_health?.status === 'needs_attention'">
                      ⚠️ Issue health needs attention: High response times or many stale issues
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.3s ease;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.9);
}
</style>
