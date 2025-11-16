<!-- src/App.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import RepoCard from './components/RepoCard.vue';
import LanguageChart from './components/LanguageChart.vue';
import { Search, Star, History } from 'lucide-vue-next';
import type { Repo } from './types';

type SortKey = 'stars' | 'last_update';

// Reactive state
const allRepositories = ref<Repo[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const sortKey = ref<SortKey>('stars');
const sortOrder = ref<'desc' | 'asc'>('desc');

// Lifecycle hooks
onMounted(async () => {
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
  // Filter first
  let filtered = allRepositories.value;
  if (searchTerm.value) {
    filtered = allRepositories.value.filter(repo =>
      repo.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    );
  }

  // Then sort
  return [...filtered].sort((a, b) => {
    let valA, valB;
    if (sortKey.value === 'last_update') {
      valA = new Date(a.last_update).getTime();
      valB = new Date(b.last_update).getTime();
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
            <!-- Placeholder for more charts or info -->
        </div>
        <LanguageChart :repos="allRepositories" />
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

      <div v-if="isLoading" class="text-center">
        <p class="text-2xl animate-pulse">Loading data from Cyberspace...</p>
      </div>
      <div v-else-if="error" class="text-center bg-red-900/50 border border-red-500 p-4 rounded-lg">
        <p class="font-bold text-xl text-red-400">[CONNECTION ERROR]</p>
        <p class="text-red-300">{{ error }}</p>
      </div>
      <TransitionGroup v-else tag="div" name="list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative">
        <RepoCard v-for="repo in processedRepositories" :key="repo.name" :repo="repo" />
      </TransitionGroup>
    </div>
  </main>
</template>
