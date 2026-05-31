import { create } from 'zustand'

export const useUIStore = create((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  graphFilters: { contentTypes: [], tagIds: [], dateRange: null },
  setGraphFilters: (filters) => set({ graphFilters: filters }),

  selectedNodeId: null,
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),

  graphLayout: 'force',
  setGraphLayout: (layout) => set({ graphLayout: layout }),
}))
