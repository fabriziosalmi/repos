<!-- frontend/src/components/LanguageChart.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { Repo } from '../types';

const props = defineProps<{
  repos: Repo[];
}>();

const chartData = computed(() => {
  const langCount = props.repos.reduce((acc, repo) => {
    const lang = repo.language || 'Unknown';
    acc[lang] = (acc[lang] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const sortedLangs = Object.entries(langCount).sort((a, b) => b[1] - a[1]);
  
  return {
    labels: sortedLangs.map(entry => entry[0]),
    series: sortedLangs.map(entry => entry[1]),
  };
});

const chartOptions = computed<ApexOptions>(() => ({
  chart: { type: 'donut', background: 'transparent' },
  theme: { mode: 'dark', palette: 'palette2' },
  labels: chartData.value.labels,
  legend: { show: true, position: 'bottom', labels: { colors: '#94a3b8' } },
  plotOptions: { pie: { donut: { labels: { show: true, total: { show: true, label: 'Progetti', color: '#00ffcc' } } } } },
  dataLabels: { enabled: false },
  responsive: [{
    breakpoint: 480,
    options: { chart: { width: 300 }, legend: { position: 'bottom' } }
  }]
}));
</script>

<template>
  <div class="border border-fuchsia-500/20 bg-slate-900/50 p-4 rounded-md backdrop-blur-sm">
    <h3 class="text-lg font-bold text-fuchsia-300 mb-4">Distribuzione Linguaggi</h3>
    <VueApexCharts
      type="donut"
      :options="chartOptions"
      :series="chartData.series"
    />
  </div>
</template>
