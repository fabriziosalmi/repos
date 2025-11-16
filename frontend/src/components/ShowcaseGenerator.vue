<!-- components/ShowcaseGenerator.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue';
import { Share2, Copy, Check, X as XIcon } from 'lucide-vue-next';
import type { Repo } from '../types';

const props = defineProps<{
  repo: Repo;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const copied = ref(false);
const selectedPlatform = ref<'twitter' | 'linkedin' | 'general'>('twitter');

// Generate showcase text based on repo metrics
const showcaseText = computed(() => {
  const { name, stars, url, description, momentum, issue_health } = props.repo;
  const starsGained = momentum?.stars_30d || 0;
  const healthScore = issue_health?.health_score || 0;
  
  const templates = {
    twitter: `🚀 Exciting progress on ${name}!

${starsGained > 0 ? `📈 +${starsGained} stars this month` : `⭐ ${stars} stars`}
${healthScore > 70 ? `💚 Health Score: ${healthScore.toFixed(0)}%` : ''}
${description ? `\n${description.substring(0, 100)}${description.length > 100 ? '...' : ''}` : ''}

Check it out: ${url}

#OpenSource #GitHub #Development`,

    linkedin: `🎯 Project Update: ${name}

I'm excited to share the latest progress on ${name}!

${description ? `📌 ${description}\n\n` : ''}Key Highlights:
${starsGained > 0 ? `• +${starsGained} GitHub stars this month (${stars} total)` : `• ${stars} GitHub stars`}
${healthScore > 70 ? `• Maintaining ${healthScore.toFixed(0)}% project health score` : ''}
• Active development and community engagement

${starsGained > 20 ? 'The momentum has been incredible, and I\'m grateful for the community support!' : 'Building something meaningful for the open-source community.'}

🔗 ${url}

#OpenSource #SoftwareDevelopment #GitHub #TechCommunity`,

    general: `${name} - ${description || 'Open source project'}

Stats:
- ⭐ ${stars} stars${starsGained > 0 ? ` (+${starsGained} this month)` : ''}
${healthScore > 0 ? `- 💚 ${healthScore.toFixed(0)}% health score` : ''}
- 🔧 Actively maintained

${url}

${momentum?.trend === 'rising' ? '📈 Trending up!' : ''}
${issue_health?.status === 'healthy' ? '✅ Healthy project' : ''}`
  };
  
  return templates[selectedPlatform.value];
});

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(showcaseText.value);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (error) {
    console.error('Failed to copy:', error);
  }
};

const handleShare = () => {
  const text = encodeURIComponent(showcaseText.value);
  const url = props.repo.url;
  
  const shareUrls = {
    twitter: `https://twitter.com/intent/tweet?text=${text}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
    general: `mailto:?subject=${encodeURIComponent(props.repo.name)}&body=${text}`
  };
  
  globalThis.window.open(shareUrls[selectedPlatform.value], '_blank');
};

const handleClose = () => {
  emit('close');
};

const getCharCount = computed(() => {
  const text = showcaseText.value;
  const maxChars = selectedPlatform.value === 'twitter' ? 280 : 3000;
  return {
    current: text.length,
    max: maxChars,
    isOverLimit: text.length > maxChars
  };
});
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        @click.self="handleClose"
      >
        <div class="bg-slate-900 border-2 border-cyber-primary rounded-lg max-w-2xl w-full shadow-cyber-glow">
          <!-- Header -->
          <div class="sticky top-0 bg-slate-900 border-b border-cyber-primary/30 p-6 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <Share2 class="h-6 w-6 text-cyber-primary" />
              <h2 class="text-xl font-bold text-cyber-primary">Generate Showcase</h2>
            </div>
            <button
              @click="handleClose"
              class="p-2 hover:bg-slate-800 rounded-full transition-colors"
            >
              <XIcon class="h-5 w-5 text-gray-400" />
            </button>
          </div>

          <!-- Content -->
          <div class="p-6 space-y-6">
            <!-- Platform Selection -->
            <div>
              <label class="text-sm font-bold text-gray-300 mb-3 block">Platform</label>
              <div class="flex gap-3">
                <button
                  @click="selectedPlatform = 'twitter'"
                  :class="[
                    'px-4 py-2 rounded-lg capitalize transition-all',
                    selectedPlatform === 'twitter'
                      ? 'bg-cyber-primary text-slate-900 font-bold'
                      : 'bg-slate-800 text-gray-300 hover:bg-slate-700'
                  ]"
                >
                  Twitter
                </button>
                <button
                  @click="selectedPlatform = 'linkedin'"
                  :class="[
                    'px-4 py-2 rounded-lg capitalize transition-all',
                    selectedPlatform === 'linkedin'
                      ? 'bg-cyber-primary text-slate-900 font-bold'
                      : 'bg-slate-800 text-gray-300 hover:bg-slate-700'
                  ]"
                >
                  LinkedIn
                </button>
                <button
                  @click="selectedPlatform = 'general'"
                  :class="[
                    'px-4 py-2 rounded-lg capitalize transition-all',
                    selectedPlatform === 'general'
                      ? 'bg-cyber-primary text-slate-900 font-bold'
                      : 'bg-slate-800 text-gray-300 hover:bg-slate-700'
                  ]"
                >
                  General
                </button>
              </div>
            </div>

            <!-- Preview -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="text-sm font-bold text-gray-300">Preview</label>
                <span 
                  :class="[
                    'text-xs',
                    getCharCount.isOverLimit ? 'text-red-400' : 'text-gray-500'
                  ]"
                >
                  {{ getCharCount.current }} / {{ getCharCount.max }} chars
                </span>
              </div>
              <div class="bg-slate-950 border border-slate-700 rounded-lg p-4 min-h-[200px] max-h-[300px] overflow-y-auto">
                <pre class="text-sm text-gray-300 whitespace-pre-wrap font-mono">{{ showcaseText }}</pre>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-3">
              <button
                @click="handleCopy"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-bold transition-all',
                  copied
                    ? 'bg-green-600 text-white'
                    : 'bg-slate-800 text-gray-300 hover:bg-slate-700 hover:text-white'
                ]"
              >
                <Check v-if="copied" class="h-5 w-5" />
                <Copy v-else class="h-5 w-5" />
                {{ copied ? 'Copied!' : 'Copy to Clipboard' }}
              </button>
              
              <button
                @click="handleShare"
                class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-cyber-primary text-slate-900 rounded-lg font-bold hover:bg-cyan-400 transition-all"
              >
                <Share2 class="h-5 w-5" />
                Share on {{ selectedPlatform === 'general' ? 'Email' : selectedPlatform }}
              </button>
            </div>

            <!-- Tips -->
            <div class="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
              <p class="text-xs text-cyan-300">
                💡 <strong>Tip:</strong> Customize the text before sharing! 
                {{ selectedPlatform === 'twitter' ? 'Keep it under 280 chars for Twitter.' : '' }}
                {{ selectedPlatform === 'linkedin' ? 'Add relevant hashtags to increase visibility.' : '' }}
              </p>
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
