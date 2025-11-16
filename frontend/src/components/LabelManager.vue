<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-screen items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')"></div>

          <!-- Modal -->
          <div class="relative w-full max-w-2xl rounded-xl bg-white shadow-2xl dark:bg-gray-800">
            <!-- Header -->
            <div class="flex items-center justify-between border-b border-gray-200 p-6 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <Tag class="h-6 w-6 text-blue-600" />
                <div>
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    Label Manager
                  </h2>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ repo.name }} - Issue #{{ issueNumber }}
                  </p>
                </div>
              </div>
              <button
                @click="$emit('close')"
                class="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700"
              >
                <X class="h-5 w-5" />
              </button>
            </div>

            <!-- Content -->
            <div class="p-6">
              <!-- Loading State -->
              <div v-if="loading" class="flex items-center justify-center py-12">
                <div class="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                <span class="ml-3 text-gray-600 dark:text-gray-400">Loading labels...</span>
              </div>

              <!-- Error State -->
              <div v-else-if="error" class="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
                <div class="flex items-start gap-3">
                  <AlertCircle class="h-5 w-5 flex-shrink-0 text-red-600 dark:text-red-400" />
                  <div>
                    <h3 class="font-semibold text-red-800 dark:text-red-400">Error</h3>
                    <p class="mt-1 text-sm text-red-700 dark:text-red-300">{{ error }}</p>
                    <button
                      @click="fetchLabels"
                      class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>

              <!-- Labels Grid -->
              <div v-else>
                <div class="mb-4">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search labels..."
                    class="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div class="max-h-96 space-y-2 overflow-y-auto">
                  <div
                    v-for="label in filteredLabels"
                    :key="label.name"
                    class="flex items-center justify-between rounded-lg border border-gray-200 p-3 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700/50"
                  >
                    <div class="flex items-center gap-3">
                      <div
                        class="h-6 w-6 rounded"
                        :style="{ backgroundColor: `#${label.color}` }"
                      ></div>
                      <div>
                        <div class="font-medium text-gray-900 dark:text-white">
                          {{ label.name }}
                        </div>
                        <div v-if="label.description" class="text-sm text-gray-500 dark:text-gray-400">
                          {{ label.description }}
                        </div>
                      </div>
                    </div>

                    <button
                      @click="toggleLabel(label.name)"
                      :disabled="actionLoading"
                      class="rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50"
                      :class="
                        isLabelActive(label.name)
                          ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400'
                          : 'bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400'
                      "
                    >
                      {{ isLabelActive(label.name) ? 'Remove' : 'Add' }}
                    </button>
                  </div>

                  <div v-if="filteredLabels.length === 0" class="py-8 text-center text-gray-500 dark:text-gray-400">
                    No labels found
                  </div>
                </div>

                <!-- Active Labels -->
                <div v-if="activeLabels.length > 0" class="mt-6 border-t border-gray-200 pt-4 dark:border-gray-700">
                  <h3 class="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Active Labels ({{ activeLabels.length }})
                  </h3>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="labelName in activeLabels"
                      :key="labelName"
                      class="inline-flex items-center gap-2 rounded-lg px-3 py-1 text-sm font-medium text-white"
                      :style="{ backgroundColor: `#${getLabelColor(labelName)}` }"
                    >
                      {{ labelName }}
                      <button
                        @click="toggleLabel(labelName)"
                        :disabled="actionLoading"
                        class="rounded hover:bg-black/10"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </span>
                  </div>
                </div>

                <!-- Success Message -->
                <Transition name="fade">
                  <div v-if="successMessage" class="mt-4 rounded-lg bg-green-50 p-3 dark:bg-green-900/20">
                    <div class="flex items-center gap-2 text-sm text-green-800 dark:text-green-400">
                      <Check class="h-4 w-4" />
                      {{ successMessage }}
                    </div>
                  </div>
                </Transition>
              </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-gray-200 p-6 dark:border-gray-700">
              <p class="text-sm text-gray-500 dark:text-gray-400">
                💡 <strong>Note:</strong> This feature requires a GitHub token with <code>repo</code> scope.
                Configure it in Vercel environment variables.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Tag, X, AlertCircle, Check } from 'lucide-vue-next'
import type { Repo } from '../types'

interface Label {
  name: string
  color: string
  description: string
}

interface Props {
  repo: Repo
  issueNumber: number
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const labels = ref<Label[]>([])
const activeLabels = ref<string[]>([])
const loading = ref(false)
const actionLoading = ref(false)
const error = ref('')
const searchQuery = ref('')
const successMessage = ref('')

// API endpoint (will be deployed to Vercel)
const API_URL = import.meta.env.VITE_API_URL || '/api/labels'

const filteredLabels = computed(() => {
  if (!searchQuery.value) return labels.value
  
  const query = searchQuery.value.toLowerCase()
  return labels.value.filter(
    label =>
      label.name.toLowerCase().includes(query) ||
      label.description.toLowerCase().includes(query)
  )
})

const isLabelActive = (labelName: string) => {
  return activeLabels.value.includes(labelName)
}

const getLabelColor = (labelName: string) => {
  const label = labels.value.find(l => l.name === labelName)
  return label?.color || '6B7280'
}

const fetchLabels = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const repoFullName = `${props.repo.owner?.login || 'unknown'}/${props.repo.name}`
    const response = await fetch(`${API_URL}?repo=${encodeURIComponent(repoFullName)}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch labels: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    labels.value = data.labels
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load labels'
  } finally {
    loading.value = false
  }
}

const toggleLabel = async (labelName: string) => {
  actionLoading.value = true
  error.value = ''
  successMessage.value = ''
  
  try {
    const repoFullName = `${props.repo.owner?.login || 'unknown'}/${props.repo.name}`
    const isActive = isLabelActive(labelName)
    
    const response = await fetch(API_URL, {
      method: isActive ? 'DELETE' : 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo: repoFullName,
        issue: props.issueNumber,
        ...(isActive ? { label: labelName } : { labels: [labelName] })
      })
    })
    
    if (!response.ok) {
      throw new Error(`Failed to ${isActive ? 'remove' : 'add'} label`)
    }
    
    const data = await response.json()
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    // Update active labels
    if (isActive) {
      activeLabels.value = activeLabels.value.filter(l => l !== labelName)
    } else {
      activeLabels.value.push(labelName)
    }
    
    successMessage.value = data.message
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Operation failed'
  } finally {
    actionLoading.value = false
  }
}

// Fetch labels when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    fetchLabels()
  } else {
    // Reset state when closing
    searchQuery.value = ''
    activeLabels.value = []
    successMessage.value = ''
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
