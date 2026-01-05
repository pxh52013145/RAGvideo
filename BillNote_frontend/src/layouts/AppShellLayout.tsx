import { useMemo, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Menu } from 'lucide-react'

import AppSidebar from '@/components/AppSidebar'

const getTitle = (pathname: string) => {
  if (pathname.startsWith('/note')) return '知识库'
  if (pathname.startsWith('/rag')) return 'RAG 视频问答'
  if (pathname.startsWith('/settings')) return '设置'
  return 'RAGVideo'
}

const AppShellLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const location = useLocation()
  const title = useMemo(() => getTitle(location.pathname), [location.pathname])
  const toggleSidebar = () => setIsSidebarOpen(v => !v)

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50 text-slate-900 font-sans">
      <AppSidebar isOpen={isSidebarOpen} toggleOpen={toggleSidebar} />

      <main className="flex-1 flex flex-col h-full overflow-hidden transition-all duration-300">
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 justify-between lg:hidden">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={toggleSidebar}
              className="p-2 hover:bg-slate-100 rounded-md"
            >
              <Menu className="w-5 h-5 text-slate-600" />
            </button>
            <span className="font-semibold text-slate-800">{title}</span>
          </div>
        </header>

        <div className="flex-1 overflow-hidden relative">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default AppShellLayout
