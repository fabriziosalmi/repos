<!-- components/CommitTimeline.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import VueApexCharts from 'vue3-apexcharts';
import type { ApexOptions } from 'apexcharts';
import type { Repo } from '../types';
import { startOfMonth, subMonths, format } from 'date-fns';

const props = defineProps<{
  repos: Repo[];
}>();

const emit = defineEmits<{
  dateRangeChange: [range: { start: Date; end: Date }];
}>();

// Generate timeline data from repository last_update dates
const timelineData = computed(() => {
  // Group repos by month
  const monthlyActivity = new Map<string, number>();
  
  props.repos.forEach(repo => {
    const date = new Date(repo.last_update);
    const monthKey = format(startOfMonth(date), 'yyyy-MM');
    monthlyActivity.set(monthKey, (monthlyActivity.get(monthKey) || 0) + 1);
  });

  // Create series for last 12 months
  const data: { x: number; y: number }[] = [];
  const now = new Date();
  
  for (let i = 11; i >= 0; i--) {
    const month = subMonths(now, i);
    const monthKey = format(startOfMonth(month), 'yyyy-MM');
    const count = monthlyActivity.get(monthKey) || 0;
    data.push({
      x: startOfMonth(month).getTime(),
      y: count
    });
  }

  return data;
});

const chartOptions = computed<ApexOptions>(() => ({
  chart: {
    id: 'commit-timeline',
    type: 'area',
    height: 200,
    background: 'transparent',
    toolbar: {
      show: false,
      autoSelected: 'pan'
    },
    brush: {
      enabled: true,
      target: 'commit-timeline',
      autoScaleYaxis: false,
    },
    selection: {
      enabled: true,
      type: 'x',
      fill: {
        color: '#00ffcc',
        opacity: 0.1
      },
      stroke: {
        width: 1,
        dashArray: 3,
        color: '#00ffcc',
        opacity: 0.4
      }
    },
    events: {
      selection: (_chartContext: any, { xaxis }: any) => {
        if (xaxis?.min && xaxis?.max) {
          emit('dateRangeChange', {
            start: new Date(xaxis.min),
            end: new Date(xaxis.max)
          });
        }
      }
    },
    zoom: {
      enabled: true,
      type: 'x',
      autoScaleYaxis: false
    }
  },
  theme: { mode: 'dark' },
  stroke: {
    curve: 'smooth',
    width: 2,
    colors: ['#00ffcc']
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.5,
      opacityTo: 0.1,
      stops: [0, 90, 100]
    }
  },
  dataLabels: { enabled: false },
  xaxis: {
    type: 'datetime',
    labels: {
      style: { colors: '#94a3b8' },
      datetimeFormatter: {
        year: 'yyyy',
        month: "MMM 'yy",
        day: 'dd MMM',
        hour: 'HH:mm'
      }
    }
  },
  yaxis: {
    labels: {
      style: { colors: '#94a3b8' },
      formatter: (val: number) => Math.floor(val).toString()
    },
    title: {
      text: 'Updated Repos',
      style: { color: '#94a3b8' }
    }
  },
  grid: {
    borderColor: '#334155',
    strokeDashArray: 4
  },
  tooltip: {
    theme: 'dark',
    x: {
      format: 'MMM yyyy'
    },
    y: {
      formatter: (val: number) => `${val} repos updated`
    }
  }
}));

const chartSeries = computed(() => [{
  name: 'Repository Updates',
  data: timelineData.value
}]);
</script>

<template>
  <div class="border border-cyan-500/20 bg-slate-900/50 p-4 rounded-md backdrop-blur-sm">
    <h3 class="text-lg font-bold text-cyan-300 mb-2">Activity Timeline</h3>
    <p class="text-xs text-gray-400 mb-4">Drag to select date range and filter repositories</p>
    <VueApexCharts
      type="area"
      height="200"
      :options="chartOptions"
      :series="chartSeries"
    />
    <p class="text-xs text-gray-500 mt-2 text-center">
      💡 Tip: Click and drag on the chart to filter by date range
    </p>
  </div>
</template>
