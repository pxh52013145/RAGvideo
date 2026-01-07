import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type DuplicateStrategy = 'ask' | 'skip' | 'regenerate'
interface SystemState {
  showFeatureHint: boolean // ✅ 是否显示功能提示
  setShowFeatureHint: (value: boolean) => void

  duplicateStrategy: DuplicateStrategy
  setDuplicateStrategy: (value: DuplicateStrategy) => void

  // 后续如果有其他全局状态，可以继续加
  sidebarCollapsed: boolean // ✅ 侧边栏是否收起
  setSidebarCollapsed: (value: boolean) => void
}
// 暂不启用
export const useSystemStore = create<SystemState>()(
  persist(
    set => ({
      showFeatureHint: true,
      setShowFeatureHint: value => set({ showFeatureHint: value }),

      duplicateStrategy: 'ask',
      setDuplicateStrategy: value => set({ duplicateStrategy: value }),

      sidebarCollapsed: false,
      setSidebarCollapsed: value => set({ sidebarCollapsed: value }),
    }),
    {
      name: 'system-store', // 本地存储的 key
    }
  )
)
