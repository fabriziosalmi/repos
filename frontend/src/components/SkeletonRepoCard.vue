<!-- components/SkeletonRepoCard.vue -->
<script setup lang="ts">
// No props needed for skeleton loader
</script>

<template>
  <div class="repo-card flex flex-col border border-cyan-400/10 bg-slate-900/50 p-4 rounded-md backdrop-blur-sm animate-pulse">
    <!-- Header skeleton -->
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2 flex-1">
        <div class="h-6 bg-slate-700/50 rounded w-3/4"></div>
      </div>
      <div class="h-4 w-4 bg-slate-700/50 rounded"></div>
    </div>

    <!-- Description skeleton -->
    <div class="space-y-2 mb-4">
      <div class="h-3 bg-slate-700/50 rounded w-full"></div>
      <div class="h-3 bg-slate-700/50 rounded w-5/6"></div>
    </div>

    <!-- Language badge skeleton -->
    <div class="mb-4">
      <div class="h-5 bg-slate-700/50 rounded-full w-20 inline-block"></div>
    </div>

    <!-- Stats skeleton -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="flex items-center gap-2">
        <div class="h-4 w-4 bg-slate-700/50 rounded"></div>
        <div class="h-4 bg-slate-700/50 rounded w-12"></div>
      </div>
      <div class="flex items-center gap-2">
        <div class="h-4 w-4 bg-slate-700/50 rounded"></div>
        <div class="h-4 bg-slate-700/50 rounded w-12"></div>
      </div>
      <div class="flex items-center gap-2">
        <div class="h-4 w-4 bg-slate-700/50 rounded"></div>
        <div class="h-4 bg-slate-700/50 rounded w-12"></div>
      </div>
      <div class="flex items-center gap-2">
        <div class="h-4 w-4 bg-slate-700/50 rounded"></div>
        <div class="h-4 bg-slate-700/50 rounded w-16"></div>
      </div>
    </div>

    <!-- Footer skeleton -->
    <div class="flex items-center gap-3 pt-3 border-t border-slate-700/50">
      <div class="h-4 bg-slate-700/50 rounded w-24"></div>
      <div class="h-4 bg-slate-700/50 rounded w-16"></div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
