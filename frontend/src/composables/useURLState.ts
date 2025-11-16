// composables/useURLState.ts
import { ref, onMounted } from 'vue';

export interface URLState {
  search?: string;
  sortKey?: 'stars' | 'last_update';
  sortOrder?: 'asc' | 'desc';
  language?: string;
  dateStart?: string;
  dateEnd?: string;
}

export function useURLState() {
  // Initialize state from URL on mount
  const getInitialState = (): URLState => {
    const params = new URLSearchParams(globalThis.window.location.search);
    return {
      search: params.get('search') || undefined,
      sortKey: (params.get('sortKey') as 'stars' | 'last_update') || undefined,
      sortOrder: (params.get('sortOrder') as 'asc' | 'desc') || undefined,
      language: params.get('language') || undefined,
      dateStart: params.get('dateStart') || undefined,
      dateEnd: params.get('dateEnd') || undefined,
    };
  };

  const currentState = ref<URLState>({});

  onMounted(() => {
    currentState.value = getInitialState();
  });

  // Update URL when state changes
  const updateURL = (newState: Partial<URLState>) => {
    const merged = { ...currentState.value, ...newState };
    
    const params = new URLSearchParams();
    
    if (merged.search) params.set('search', merged.search);
    if (merged.sortKey) params.set('sortKey', merged.sortKey);
    if (merged.sortOrder) params.set('sortOrder', merged.sortOrder);
    if (merged.language) params.set('language', merged.language);
    if (merged.dateStart) params.set('dateStart', merged.dateStart);
    if (merged.dateEnd) params.set('dateEnd', merged.dateEnd);

    currentState.value = merged;

    const newURL = params.toString() 
      ? `${globalThis.window.location.pathname}?${params.toString()}`
      : globalThis.window.location.pathname;
    
    globalThis.window.history.replaceState({}, '', newURL);
  };

  const clearURLState = () => {
    currentState.value = {};
    globalThis.window.history.replaceState({}, '', globalThis.window.location.pathname);
  };

  return {
    currentState,
    updateURL,
    clearURLState,
    getInitialState,
  };
}
