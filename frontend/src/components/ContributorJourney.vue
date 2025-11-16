<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 p-6">
    <div class="mx-auto max-w-5xl">
      <!-- Header with Back Button -->
      <div class="mb-8 flex items-center gap-4">
        <button
          @click="goBack"
          class="rounded-lg bg-slate-800 p-3 text-gray-400 transition-colors hover:bg-slate-700 hover:text-white"
        >
          <ArrowLeft class="h-5 w-5" />
        </button>
        <div>
          <h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
            Contributor Journey
          </h1>
          <p class="mt-1 text-gray-400">
            Aegis Module 3.2: Individual contributor timeline and evolution
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="h-12 w-12 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
        <span class="ml-4 text-xl text-gray-400">Loading contributor journey...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-lg bg-red-900/20 border border-red-500/50 p-6">
        <h3 class="text-xl font-semibold text-red-400">Error</h3>
        <p class="mt-2 text-red-300">{{ error }}</p>
      </div>

      <!-- Contributor Profile -->
      <div v-else-if="contributor" class="space-y-6">
        <!-- Profile Card -->
        <div class="rounded-xl bg-slate-800/50 border border-indigo-500/30 p-8 backdrop-blur-sm">
          <div class="flex items-start gap-6">
            <img
              :src="contributor.avatar_url"
              :alt="contributor.login"
              class="h-32 w-32 rounded-full border-4 border-indigo-500 shadow-xl shadow-indigo-500/20"
            />
            <div class="flex-1">
              <a
                :href="contributor.profile_url"
                target="_blank"
                class="text-3xl font-bold text-indigo-400 hover:text-indigo-300"
              >
                {{ contributor.login }}
              </a>
              
              <!-- Stats Grid -->
              <div class="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
                <div>
                  <p class="text-sm text-gray-400">Total Contributions</p>
                  <p class="text-2xl font-bold text-white">{{ contributor.total_contributions }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-400">Repositories</p>
                  <p class="text-2xl font-bold text-white">{{ contributor.total_repositories }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-400">Impact Score</p>
                  <p class="text-2xl font-bold text-white">{{ contributor.impact_score }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-400">Total Stars</p>
                  <p class="text-2xl font-bold text-white">{{ contributor.total_stars.toLocaleString() }}</p>
                </div>
              </div>

              <!-- Languages -->
              <div class="mt-4">
                <p class="mb-2 text-sm text-gray-400">Languages</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="lang in contributor.languages"
                    :key="lang"
                    class="rounded-full bg-indigo-500/20 px-3 py-1 text-sm text-indigo-300"
                  >
                    {{ lang }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="rounded-xl bg-slate-800/50 border border-slate-700 p-8">
          <h2 class="mb-6 text-2xl font-bold text-white flex items-center gap-2">
            <Clock class="h-6 w-6 text-indigo-400" />
            Contribution Timeline
          </h2>

          <div class="relative">
            <!-- Timeline Line -->
            <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-indigo-500 to-purple-500"></div>

            <!-- Timeline Events -->
            <div class="space-y-8">
              <!-- First Contribution -->
              <div class="relative pl-20">
                <div class="absolute left-6 flex h-4 w-4 items-center justify-center">
                  <div class="h-4 w-4 rounded-full bg-green-500 ring-4 ring-green-500/20"></div>
                </div>
                <div class="rounded-lg bg-slate-700/50 p-4">
                  <div class="flex items-center gap-2">
                    <Sparkles class="h-5 w-5 text-green-400" />
                    <h3 class="font-semibold text-white">First Contribution</h3>
                  </div>
                  <p class="mt-1 text-sm text-gray-400">
                    {{ formatDate(contributor.first_contribution) }}
                  </p>
                  <p class="mt-2 text-sm text-gray-300">
                    Started contributing to the projects
                  </p>
                </div>
              </div>

              <!-- Repository Milestones -->
              <div
                v-for="repo in contributor.repositories.slice(0, 10)"
                :key="repo.name"
                class="relative pl-20"
              >
                <div class="absolute left-6 flex h-4 w-4 items-center justify-center">
                  <div class="h-4 w-4 rounded-full bg-indigo-500 ring-4 ring-indigo-500/20"></div>
                </div>
                <div class="rounded-lg bg-slate-700/50 p-4 transition-all hover:bg-slate-700">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <GitBranch class="h-5 w-5 text-indigo-400" />
                      <a
                        :href="repo.url"
                        target="_blank"
                        class="font-semibold text-indigo-400 hover:text-indigo-300"
                      >
                        {{ repo.name }}
                      </a>
                    </div>
                    <span class="text-sm text-gray-400">{{ repo.contributions }} commits</span>
                  </div>
                  <div class="mt-2 flex gap-4 text-sm text-gray-400">
                    <span>⭐ {{ repo.stars }} stars</span>
                    <span>💻 {{ repo.language }}</span>
                  </div>
                </div>
              </div>

              <!-- Latest Contribution -->
              <div class="relative pl-20">
                <div class="absolute left-6 flex h-4 w-4 items-center justify-center">
                  <div class="h-4 w-4 rounded-full bg-purple-500 ring-4 ring-purple-500/20 animate-pulse"></div>
                </div>
                <div class="rounded-lg bg-slate-700/50 p-4">
                  <div class="flex items-center gap-2">
                    <Zap class="h-5 w-5 text-purple-400" />
                    <h3 class="font-semibold text-white">Latest Activity</h3>
                  </div>
                  <p class="mt-1 text-sm text-gray-400">
                    {{ formatDate(contributor.last_contribution) }}
                  </p>
                  <p class="mt-2 text-sm text-gray-300">
                    Most recent contribution
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Contribution Distribution -->
        <div class="rounded-xl bg-slate-800/50 border border-slate-700 p-8">
          <h2 class="mb-6 text-2xl font-bold text-white flex items-center gap-2">
            <BarChart class="h-6 w-6 text-indigo-400" />
            Repository Distribution
          </h2>

          <div class="space-y-3">
            <div
              v-for="repo in contributor.repositories.slice(0, 10)"
              :key="repo.name"
              class="group"
            >
              <div class="flex items-center justify-between mb-1">
                <a
                  :href="repo.url"
                  target="_blank"
                  class="text-sm text-indigo-400 hover:text-indigo-300"
                >
                  {{ repo.name }}
                </a>
                <span class="text-sm text-gray-400">
                  {{ repo.contributions }} ({{ getPercentage(repo.contributions) }}%)
                </span>
              </div>
              <div class="h-2 rounded-full bg-slate-700 overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 group-hover:from-indigo-400 group-hover:to-purple-400"
                  :style="{ width: `${getPercentage(repo.contributions)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Clock, Sparkles, GitBranch, Zap, BarChart } from 'lucide-vue-next'
import { formatDistanceToNow, format } from 'date-fns'

interface Repository {
  name: string
  url: string
  contributions: number
  stars: number
  language: string
}

interface Contributor {
  login: string
  avatar_url: string
  profile_url: string
  total_contributions: number
  total_repositories: number
  repositories: Repository[]
  first_contribution: string
  last_contribution: string
  languages: string[]
  total_stars: number
  total_forks: number
  impact_score: number
}

interface Props {
  login: string
}

const props = defineProps<Props>()

const contributor = ref<Contributor | null>(null)
const loading = ref(true)
const error = ref('')

const getPercentage = (contributions: number) => {
  if (!contributor.value) return 0
  return Math.round((contributions / contributor.value.total_contributions) * 100)
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'Invalid date'
  return `${format(date, 'MMM d, yyyy')} (${formatDistanceToNow(date, { addSuffix: true })})`
}

const goBack = () => {
  window.history.back()
}

onMounted(async () => {
  try {
    const response = await fetch('/contributor-stats.json')
    if (!response.ok) {
      throw new Error('Failed to load contributor data')
    }
    
    const data = await response.json()
    const found = data.all_contributors.find((c: Contributor) => c.login === props.login)
    
    if (!found) {
      throw new Error(`Contributor "${props.login}" not found`)
    }
    
    contributor.value = found
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>
