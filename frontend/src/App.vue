<!-- src/App.vue -->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import RepoCard from './components/RepoCard.vue';
import SkeletonRepoCard from './components/SkeletonRepoCard.vue';
import LanguageChart from './components/LanguageChart.vue';
import InsightHub from './components/InsightHub.vue';
import RepoDetailModal from './components/RepoDetailModal.vue';
import CommitTimeline from './components/CommitTimeline.vue';
import { Search, Star, History, X } from 'lucide-vue-next';
import type { Repo } from './types';
import { useFilters } from './composables/useFilters';
import { useURLState } from './composables/useURLState';

type SortKey = 'stars' | 'last_update';

// Reactive state
const allRepositories = ref<Repo[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const sortKey = ref<SortKey>('stars');
const sortOrder = ref<'desc' | 'asc'>('desc');
const selectedRepo = ref<Repo | null>(null);
const isModalOpen = ref(false);

// Filters composable
const {
  activeLanguage,
  activeDateRange,
  hasActiveFilters,
  setLanguageFilter,
  setDateRangeFilter,
  clearFilters,
  applyFilters,
} = useFilters();

// URL state persistence
const { currentState: urlState, updateURL } = useURLState();

// Lifecycle hooks
onMounted(async () => {
  // Restore state from URL
  if (urlState.value.search) searchTerm.value = urlState.value.search;
  if (urlState.value.sortKey) sortKey.value = urlState.value.sortKey;
  if (urlState.value.sortOrder) sortOrder.value = urlState.value.sortOrder;
  if (urlState.value.language) setLanguageFilter(urlState.value.language);
  if (urlState.value.dateStart && urlState.value.dateEnd) {
    setDateRangeFilter({
      start: new Date(urlState.value.dateStart),
      end: new Date(urlState.value.dateEnd)
    });
  }

  try {
    const response = await fetch('repositories-data.json');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data: Repo[] = await response.json();
    allRepositories.value = data;
  } catch (e: any) {
    console.error("Failed to fetch repositories:", e);
    error.value = "Failed to load data from the central terminal. Please try again.";
  } finally {
    isLoading.value = false;
  }
});

// Computed properties
const processedRepositories = computed(() => {
  // Apply all filters (language, date range, search)
  const filtered = applyFilters(allRepositories.value, searchTerm.value);

  // Then sort
  return [...filtered].sort((a, b) => {
    let valA, valB;
    if (sortKey.value === 'last_update') {
      valA = a.last_update_api ? new Date(a.last_update_api).getTime() : 0;
      valB = b.last_update_api ? new Date(b.last_update_api).getTime() : 0;
    } else { // 'stars'
      valA = a.stars;
      valB = b.stars;
    }
    
    if (sortOrder.value === 'asc') {
      return valA - valB;
    } else {
      return valB - valA;
    }
  });
});

// Methods
const setSortKey = (key: SortKey) => {
  if (key === sortKey.value) {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
};

const getSortButtonClass = (key: SortKey) => {
  return [
    'px-4 py-2 rounded-full flex items-center gap-2 transition-all duration-300',
    sortKey.value === key
      ? 'bg-cyber-primary text-cyber-bg shadow-cyber-glow'
      : 'bg-cyber-bg/70 border border-cyber-primary/50 hover:bg-cyber-primary/20'
  ];
};

const openRepoModal = (repo: Repo) => {
  selectedRepo.value = repo;
  isModalOpen.value = true;
};

const closeRepoModal = () => {
  isModalOpen.value = false;
  selectedRepo.value = null;
};

const handleDateRangeChange = (range: { start: Date; end: Date }) => {
  setDateRangeFilter(range);
};

const formatDateRange = (range: { start: Date | null; end: Date | null }) => {
  if (!range.start || !range.end) return '';
  const format = (d: Date) => d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  return `${format(range.start)} - ${format(range.end)}`;
};

// Sync state to URL
watch([searchTerm, sortKey, sortOrder, activeLanguage, activeDateRange], () => {
  updateURL({
    search: searchTerm.value || undefined,
    sortKey: sortKey.value,
    sortOrder: sortOrder.value,
    language: activeLanguage.value || undefined,
    dateStart: activeDateRange.value?.start?.toISOString() || undefined,
    dateEnd: activeDateRange.value?.end?.toISOString() || undefined,
  });
});
</script>

<template>
  <main class="bg-cyber-bg text-cyber-text font-mono min-h-screen p-8">
    <div class="container mx-auto">
      <header class="text-center mb-12">
        <h1 class="text-4xl lg:text-5xl font-bold text-cyber-primary tracking-widest">fabriziosalmi // Holo-Dashboard</h1>
        <p class="text-lg mt-2 text-cyber-text/80">Operational status of all repositories.</p>
      </header>

      <div v-if="!isLoading && !error" class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div class="lg:col-span-2">
            <CommitTimeline :repos="allRepositories" @date-range-change="handleDateRangeChange" />
        </div>
        <LanguageChart :repos="allRepositories" @language-click="setLanguageFilter" />
      </div>

      <!-- Smart Insights -->
      <InsightHub v-if="!isLoading && !error" :repos="allRepositories" />

      <!-- Active Filters -->
      <div v-if="hasActiveFilters" class="flex flex-wrap gap-3 justify-center mb-6">
        <div v-if="activeLanguage" class="flex items-center gap-2 bg-cyber-primary/20 border border-cyber-primary px-4 py-2 rounded-full">
          <span class="text-sm">Language: <strong>{{ activeLanguage }}</strong></span>
          <button @click="setLanguageFilter(null)" class="hover:bg-cyber-primary/30 rounded-full p-1">
            <X class="h-4 w-4" />
          </button>
        </div>
        <div v-if="activeDateRange" class="flex items-center gap-2 bg-cyan-500/20 border border-cyan-500 px-4 py-2 rounded-full">
          <span class="text-sm">Date: <strong>{{ formatDateRange(activeDateRange) }}</strong></span>
          <button @click="setDateRangeFilter(null)" class="hover:bg-cyan-500/30 rounded-full p-1">
            <X class="h-4 w-4" />
          </button>
        </div>
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="text-sm px-4 py-2 border border-red-500/50 text-red-400 hover:bg-red-500/20 rounded-full transition-colors"
        >
          Clear All Filters
        </button>
      </div>

      <!-- Controls -->
      <div class="flex flex-col md:flex-row gap-6 justify-center items-center mb-12">
        <div class="relative w-full md:w-auto">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search a repository..."
            class="w-full md:w-72 bg-cyber-bg/70 border-2 border-cyber-primary/50 rounded-full py-2 px-6 text-cyber-text focus:outline-none focus:border-cyber-primary transition-colors"
          />
          <Search class="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-cyber-primary/70" />
        </div>
        <div class="flex gap-3">
          <button @click="setSortKey('stars')" :class="getSortButtonClass('stars')">
            <Star class="h-5 w-5" /> Stars
          </button>
          <button @click="setSortKey('last_update')" :class="getSortButtonClass('last_update')">
            <History class="h-5 w-5" /> Activity
          </button>
        </div>
      </div>

      <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 py-4">
        <SkeletonRepoCard v-for="i in 9" :key="`skeleton-${i}`" />
      </div>
      <div v-else-if="error" class="text-center bg-red-900/50 border border-red-500 p-4 rounded-lg">
        <p class="font-bold text-xl text-red-400">[CONNECTION ERROR]</p>
        <p class="text-red-300">{{ error }}</p>
      </div>
      <TransitionGroup v-else tag="div" name="list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 py-4 relative">
        <RepoCard 
          v-for="repo in processedRepositories" 
          :key="repo.name" 
          :repo="repo" 
          @click="openRepoModal(repo)"
        />
      </TransitionGroup>
    </div>

    <!-- Repository Detail Modal -->
    <RepoDetailModal
      v-if="selectedRepo"
      :repo="selectedRepo"
      :is-open="isModalOpen"
      @close="closeRepoModal"
    />
  </main>
</template>
