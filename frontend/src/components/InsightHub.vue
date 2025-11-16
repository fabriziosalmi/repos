<script setup lang="ts">
import { computed } from 'vue';
import { TrendingUp, AlertCircle, Trophy, Users } from 'lucide-vue-next';
import type { Repo } from '../types';

const props = defineProps<{
  repos: Repo[];
}>();

interface Insight {
  id: string;
  type: 'hot' | 'help' | 'milestone' | 'health';
  icon: any;
  title: string;
  description: string;
  repo?: Repo;
  color: string;
}

const handleInsightClick = (insight: Insight) => {
  if (insight.repo) {
    globalThis.window.open(insight.repo.url, '_blank');
  }
};

const insights = computed<Insight[]>(() => {
  const result: Insight[] = [];
  
  // 1. Hot Project (highest momentum)
  const hotProject = props.repos
    .filter(r => r.momentum && r.momentum.score > 0)
    .sort((a, b) => (b.momentum?.score || 0) - (a.momentum?.score || 0))[0];
  
  if (hotProject && hotProject.momentum) {
    result.push({
      id: 'hot-project',
      type: 'hot',
      icon: TrendingUp,
      title: `🚀 Hot Project: ${hotProject.name}`,
      description: `Highest momentum this week with +${hotProject.momentum.stars_7d} stars in 7 days (Score: ${hotProject.momentum.score.toFixed(0)})`,
      repo: hotProject,
      color: 'border-green-500/50 bg-green-500/5'
    });
  }
  
  // 2. Help Wanted (repos with open issues and good health)
  const helpWanted = props.repos
    .filter(r => 
      r.issue_health?.status === 'healthy' && 
      r.open_issues_count && 
      r.open_issues_count > 0
    )
    .sort((a, b) => (b.open_issues_count || 0) - (a.open_issues_count || 0))[0];
  
  if (helpWanted && helpWanted.open_issues_count) {
    result.push({
      id: 'help-wanted',
      type: 'help',
      icon: Users,
      title: `🤝 Help Wanted: ${helpWanted.name}`,
      description: `${helpWanted.open_issues_count} open issue${helpWanted.open_issues_count > 1 ? 's' : ''} waiting for contributors. Join the community!`,
      repo: helpWanted,
      color: 'border-blue-500/50 bg-blue-500/5'
    });
  }
  
  // 3. New Milestone (repo that recently crossed star threshold)
  const milestoneRepo = props.repos
    .filter(r => {
      const stars = r.stars;
      // Find repos near milestone thresholds (100, 250, 500, 1000, etc.)
      const milestones = [100, 250, 500, 1000, 2500, 5000];
      return milestones.some(m => stars >= m && stars < m + 50);
    })
    .sort((a, b) => b.stars - a.stars)[0];
  
  if (milestoneRepo) {
    const nextMilestone = [100, 250, 500, 1000, 2500, 5000, 10000]
      .find(m => milestoneRepo.stars < m);
    const closestPast = [100, 250, 500, 1000, 2500, 5000]
      .reverse()
      .find(m => milestoneRepo.stars >= m);
    
    if (closestPast) {
      result.push({
        id: 'milestone',
        type: 'milestone',
        icon: Trophy,
        title: `🏆 Milestone: ${milestoneRepo.name}`,
        description: nextMilestone 
          ? `Reached ${closestPast} stars! Next goal: ${nextMilestone} stars`
          : `Amazing ${milestoneRepo.stars} stars!`,
        repo: milestoneRepo,
        color: 'border-yellow-500/50 bg-yellow-500/5'
      });
    }
  }
  
  // 4. Health Alert (repo that needs attention)
  const needsAttention = props.repos
    .filter(r => r.issue_health?.status === 'needs_attention')
    .sort((a, b) => (a.issue_health?.health_score || 100) - (b.issue_health?.health_score || 100))[0];
  
  if (needsAttention && needsAttention.issue_health) {
    result.push({
      id: 'health-alert',
      type: 'health',
      icon: AlertCircle,
      title: `⚠️ Needs Attention: ${needsAttention.name}`,
      description: `Issue health score: ${needsAttention.issue_health.health_score.toFixed(0)}. ${needsAttention.issue_health.stale_issues_count} stale issue${needsAttention.issue_health.stale_issues_count > 1 ? 's' : ''}.`,
      repo: needsAttention,
      color: 'border-red-500/50 bg-red-500/5'
    });
  }
  
  // Return top 3 most relevant insights
  return result.slice(0, 3);
});
</script>

<template>
  <div v-if="insights.length > 0" class="insight-hub mb-8">
    <h2 class="text-xl font-bold text-cyan-300 mb-4 flex items-center gap-2">
      <span class="animate-pulse">✨</span>
      Smart Insights
    </h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="insight in insights"
        :key="insight.id"
        :class="[
          'insight-card p-4 rounded-lg border-2 transition-all duration-300',
          'hover:scale-105 hover:shadow-lg cursor-pointer',
          insight.color
        ]"
        @click="handleInsightClick(insight)"
      >
        <div class="flex items-start gap-3">
          <component 
            :is="insight.icon" 
            :class="[
              'h-6 w-6 mt-1 flex-shrink-0',
              insight.type === 'hot' ? 'text-green-400' :
              insight.type === 'help' ? 'text-blue-400' :
              insight.type === 'milestone' ? 'text-yellow-400' :
              'text-red-400'
            ]"
          />
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-sm mb-1 text-white">
              {{ insight.title }}
            </h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              {{ insight.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.insight-card {
  backdrop-filter: blur(10px);
}
</style>
