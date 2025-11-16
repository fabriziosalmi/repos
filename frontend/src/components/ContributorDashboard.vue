<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
    <div class="mx-auto max-w-7xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
          🌟 Contributor Intelligence
        </h1>
        <p class="mt-2 text-gray-400">
          Aegis Module 3.1: Cross-project contributor analytics and community insights
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="h-12 w-12 animate-spin rounded-full border-4 border-purple-600 border-t-transparent"></div>
        <span class="ml-4 text-xl text-gray-400">Analyzing contributor data...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-lg bg-red-900/20 border border-red-500/50 p-6">
        <h3 class="text-xl font-semibold text-red-400">Error Loading Data</h3>
        <p class="mt-2 text-red-300">{{ error }}</p>
      </div>

      <!-- Dashboard Content -->
      <div v-else class="space-y-6">
        <!-- Statistics Overview -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="rounded-lg bg-slate-800/50 border border-purple-500/30 p-6 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <Users class="h-8 w-8 text-purple-400" />
              <div>
                <p class="text-sm text-gray-400">Total Contributors</p>
                <p class="text-3xl font-bold text-white">{{ stats?.total_contributors || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-lg bg-slate-800/50 border border-blue-500/30 p-6 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <TrendingUp class="h-8 w-8 text-blue-400" />
              <div>
                <p class="text-sm text-gray-400">Total Contributions</p>
                <p class="text-3xl font-bold text-white">{{ stats?.statistics.total_contributions.toLocaleString() || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-lg bg-slate-800/50 border border-green-500/30 p-6 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <UserPlus class="h-8 w-8 text-green-400" />
              <div>
                <p class="text-sm text-gray-400">Newcomers (30d)</p>
                <p class="text-3xl font-bold text-white">{{ stats?.newcomers.length || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-lg bg-slate-800/50 border border-yellow-500/30 p-6 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <Award class="h-8 w-8 text-yellow-400" />
              <div>
                <p class="text-sm text-gray-400">Avg Contributions</p>
                <p class="text-3xl font-bold text-white">{{ stats?.statistics.avg_contributions_per_contributor.toFixed(0) || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-4 border-b border-slate-700">
          <button
            @click="activeTab = 'top'"
            :class="[
              'px-6 py-3 font-semibold transition-colors',
              activeTab === 'top'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            ]"
          >
            🏆 Top Contributors
          </button>
          <button
            @click="activeTab = 'newcomers'"
            :class="[
              'px-6 py-3 font-semibold transition-colors',
              activeTab === 'newcomers'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            ]"
          >
            🆕 Newcomers
          </button>
          <button
            @click="activeTab = 'map'"
            :class="[
              'px-6 py-3 font-semibold transition-colors',
              activeTab === 'map'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            ]"
          >
            🌍 Global Map
          </button>
        </div>

        <!-- Top Contributors Tab -->
        <div v-if="activeTab === 'top'" class="space-y-4">
          <div
            v-for="(contributor, index) in stats?.top_contributors"
            :key="contributor.login"
            class="rounded-lg bg-slate-800/50 border border-slate-700 p-6 transition-all hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-4">
                <!-- Rank Badge -->
                <div
                  class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full text-2xl font-bold"
                  :class="{
                    'bg-gradient-to-br from-yellow-400 to-yellow-600 text-yellow-900': index === 0,
                    'bg-gradient-to-br from-gray-300 to-gray-500 text-gray-900': index === 1,
                    'bg-gradient-to-br from-orange-400 to-orange-600 text-orange-900': index === 2,
                    'bg-slate-700 text-gray-400': index > 2
                  }"
                >
                  {{ index + 1 }}
                </div>

                <!-- Avatar -->
                <img
                  :src="contributor.avatar_url"
                  :alt="contributor.login"
                  class="h-16 w-16 rounded-full border-2 border-purple-500"
                />

                <!-- Info -->
                <div>
                  <a
                    :href="contributor.profile_url"
                    target="_blank"
                    class="text-xl font-bold text-purple-400 hover:text-purple-300"
                  >
                    {{ contributor.login }}
                  </a>
                  <div class="mt-2 flex flex-wrap gap-4 text-sm text-gray-400">
                    <span>💼 {{ contributor.total_contributions }} contributions</span>
                    <span>📦 {{ contributor.total_repositories }} repositories</span>
                    <span>⭐ {{ contributor.total_stars.toLocaleString() }} total stars</span>
                    <span>🎯 Impact Score: {{ contributor.impact_score }}</span>
                  </div>
                  <div class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="lang in contributor.languages"
                      :key="lang"
                      class="rounded-full bg-blue-500/20 px-3 py-1 text-xs text-blue-300"
                    >
                      {{ lang }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Top Repositories -->
              <div class="text-right">
                <p class="text-sm text-gray-400 mb-2">Top Repos:</p>
                <div class="space-y-1">
                  <a
                    v-for="repo in contributor.repositories.slice(0, 3)"
                    :key="repo.name"
                    :href="repo.url"
                    target="_blank"
                    class="block text-sm text-cyan-400 hover:text-cyan-300"
                  >
                    {{ repo.name }} ({{ repo.contributions }})
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Newcomers Tab -->
        <div v-if="activeTab === 'newcomers'" class="space-y-4">
          <div
            v-for="newcomer in stats?.newcomers"
            :key="newcomer.login"
            class="rounded-lg bg-slate-800/50 border border-green-500/30 p-6"
          >
            <div class="flex items-start gap-4">
              <img
                :src="newcomer.avatar_url"
                :alt="newcomer.login"
                class="h-16 w-16 rounded-full border-2 border-green-500"
              />
              <div class="flex-1">
                <div class="flex items-center gap-3">
                  <a
                    :href="newcomer.profile_url"
                    target="_blank"
                    class="text-xl font-bold text-green-400 hover:text-green-300"
                  >
                    {{ newcomer.login }}
                  </a>
                  <span class="rounded-full bg-green-500/20 px-3 py-1 text-xs text-green-300">
                    🆕 {{ newcomer.days_since_first }} days ago
                  </span>
                </div>
                <div class="mt-2 flex flex-wrap gap-4 text-sm text-gray-400">
                  <span>💼 {{ newcomer.total_contributions }} contributions</span>
                  <span>📦 {{ newcomer.total_repositories }} repositories</span>
                </div>
                <div class="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
                  <a
                    v-for="repo in newcomer.repositories.slice(0, 3)"
                    :key="repo.name"
                    :href="repo.url"
                    target="_blank"
                    class="rounded-lg bg-slate-700/50 p-3 transition-colors hover:bg-slate-700"
                  >
                    <p class="text-sm font-medium text-white">{{ repo.name }}</p>
                    <p class="text-xs text-gray-400">{{ repo.contributions }} commits</p>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div v-if="stats?.newcomers.length === 0" class="rounded-lg bg-slate-800/50 p-12 text-center">
            <UserPlus class="mx-auto h-16 w-16 text-gray-600" />
            <p class="mt-4 text-gray-400">No new contributors in the last 30 days</p>
          </div>
        </div>

        <!-- Global Map Tab -->
        <div v-if="activeTab === 'map'" class="rounded-lg bg-slate-800/50 border border-slate-700 p-8">
          <div class="text-center">
            <Globe class="mx-auto h-24 w-24 text-purple-400 mb-4" />
            <h3 class="text-2xl font-bold text-white mb-2">Global Contributor Map</h3>
            <p class="text-gray-400 mb-6">
              Interactive map visualization coming soon
            </p>
            <p class="text-sm text-gray-500">
              This feature will show contributor locations based on GitHub profile data
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Users, TrendingUp, UserPlus, Award, Globe } from 'lucide-vue-next'

interface ContributorStats {
  total_contributors: number
  newcomers: any[]
  top_contributors: any[]
  statistics: {
    total_contributions: number
    avg_contributions_per_contributor: number
  }
}

const stats = ref<ContributorStats | null>(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref('top')

onMounted(async () => {
  try {
    const response = await fetch('/contributor-stats.json')
    if (!response.ok) {
      throw new Error('Failed to load contributor statistics')
    }
    stats.value = await response.json()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>
