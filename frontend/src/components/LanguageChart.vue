<!-- frontend/src/components/LanguageChart.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { Repo } from '../types';

const props = defineProps<{
  repos: Repo[];
}>();

const emit = defineEmits<{
  languageClick: [language: string];
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
  chart: { 
    type: 'donut', 
    background: 'transparent',
    events: {
      dataPointSelection: (_event: any, _chartContext: any, config: any) => {
        const language = chartData.value.labels[config.dataPointIndex];
        if (language) {
          emit('languageClick', language);
        }
      }
    }
  },
  theme: { mode: 'dark', palette: 'palette2' },
  labels: chartData.value.labels,
  legend: { 
    show: true, 
    position: 'bottom', 
    labels: { colors: '#94a3b8' },
    onItemClick: {
      toggleDataSeries: false
    },
    onItemHover: {
      highlightDataSeries: true
    }
  },
  plotOptions: { 
    pie: { 
      donut: { 
        labels: { 
          show: true, 
          total: { show: true, label: 'Projects', color: '#00ffcc' } 
        } 
      } 
    } 
  },
  dataLabels: { enabled: false },
  states: {
    hover: {
      filter: {
        type: 'lighten',
        value: 0.15,
      }
    },
    active: {
      filter: {
        type: 'darken',
        value: 0.15,
      }
    }
  },
  tooltip: {
    y: {
      formatter: (val: number) => `${val} projects`
    }
  },
  responsive: [{
    breakpoint: 480,
    options: { chart: { width: 300 }, legend: { position: 'bottom' } }
  }]
}));
</script>

<template>
  <div class="border border-fuchsia-500/20 bg-slate-900/50 p-4 rounded-md backdrop-blur-sm">
    <h3 class="text-lg font-bold text-fuchsia-300 mb-4">Language Distribution</h3>
    <p class="text-xs text-gray-400 mb-2">Click to filter repositories</p>
    <VueApexCharts
      type="donut"
      :options="chartOptions"
      :series="chartData.series"
      class="cursor-pointer"
    />
  </div>
</template>
