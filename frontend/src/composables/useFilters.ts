// composables/useFilters.ts
import { ref, computed } from 'vue';
import type { Repo } from '../types';

export interface FilterState {
  language: string | null;
  dateRange: { start: Date | null; end: Date | null } | null;
  search: string;
}

const activeLanguage = ref<string | null>(null);
const activeDateRange = ref<{ start: Date | null; end: Date | null } | null>(null);

export function useFilters() {
  const setLanguageFilter = (language: string | null) => {
    activeLanguage.value = language;
  };

  const setDateRangeFilter = (range: { start: Date | null; end: Date | null } | null) => {
    activeDateRange.value = range;
  };

  const clearFilters = () => {
    activeLanguage.value = null;
    activeDateRange.value = null;
  };

  const applyFilters = (repos: Repo[], searchTerm: string = ''): Repo[] => {
    let filtered = [...repos];

    // Language filter
    if (activeLanguage.value) {
      filtered = filtered.filter(repo => repo.language === activeLanguage.value);
    }

    // Date range filter
    if (activeDateRange.value?.start || activeDateRange.value?.end) {
      filtered = filtered.filter(repo => {
        const repoDate = new Date(repo.last_update);
        const afterStart = !activeDateRange.value?.start || 
          repoDate >= activeDateRange.value.start;
        const beforeEnd = !activeDateRange.value?.end || 
          repoDate <= activeDateRange.value.end;
        return afterStart && beforeEnd;
      });
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(repo =>
        repo.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  };

  const filterState = computed<FilterState>(() => ({
    language: activeLanguage.value,
    dateRange: activeDateRange.value,
    search: '',
  }));

  const hasActiveFilters = computed(() => 
    activeLanguage.value !== null || 
    activeDateRange.value !== null
  );

  return {
    activeLanguage: computed(() => activeLanguage.value),
    activeDateRange: computed(() => activeDateRange.value),
    filterState,
    hasActiveFilters,
    setLanguageFilter,
    setDateRangeFilter,
    clearFilters,
    applyFilters,
  };
}
