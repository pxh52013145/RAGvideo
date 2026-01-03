import React, { FC } from 'react'
import { FileText, MessageSquareText, Settings } from 'lucide-react'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip.tsx'

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from '@/components/ui/resizable'
import {ScrollArea} from "@/components/ui/scroll-area.tsx";
import logo from '@/assets/icon.svg'
interface IProps {
  Left: React.ReactNode
  Center: React.ReactNode
  Right: React.ReactNode
  sizes?: {
    left?: number
    center?: number
    right?: number
  }
}
const HomeLayout: FC<IProps> = ({ Left, Center, Right, sizes }) => {
  const [, setShowSettings] = useState(false)
  const location = useLocation()

  const navItems = [
    { to: '/rag', label: 'RAG问答', icon: MessageSquareText },
    { to: '/note', label: '知识库', icon: FileText },
  ]

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <ResizablePanelGroup direction="horizontal" className="h-full w-full">
        {/* 左边表单 */}
        <ResizablePanel defaultSize={sizes?.left ?? 24} minSize={10} maxSize={40}>
          <aside className="flex h-full flex-col overflow-hidden border-r border-neutral-200 bg-white">
            <header className="flex h-16 items-center justify-between px-6">
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-2xl">
                  <img src={logo} alt="logo" className="h-full w-full object-contain" />
                </div>
                <div className="text-2xl font-bold text-gray-800">RAG视频</div>
              </div>
              <div>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger onClick={() => setShowSettings(true)}>
                      <Link to={'/settings'}>
                        <Settings className="text-muted-foreground hover:text-primary cursor-pointer" />
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>全局配置</span>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </header>

            <div className="flex items-center gap-2 px-6 pb-4">
              {navItems.map(item => {
                const active = location.pathname === item.to || location.pathname.startsWith(item.to + '/')
                const Icon = item.icon
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={
                      'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ' +
                      (active ? 'bg-neutral-100 text-neutral-900' : 'text-neutral-500 hover:bg-neutral-50 hover:text-neutral-800')
                    }
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </div>
            <ScrollArea className="flex-1 overflow-auto">
              <div className=' p-4' >{Left}</div>
            </ScrollArea>
          </aside>
        </ResizablePanel>

        <ResizableHandle />

        {/* 中间历史 */}
        <ResizablePanel defaultSize={sizes?.center ?? 24} minSize={12} maxSize={60}>
          <aside className="flex h-full flex-col overflow-hidden border-r border-neutral-200 bg-white">
            <ScrollArea className="flex-1 overflow-auto">
            <div className="">{Center}</div>
            </ScrollArea>
          </aside>
        </ResizablePanel>

        <ResizableHandle />

        {/* 右边预览 */}
        <ResizablePanel defaultSize={sizes?.right ?? 52} minSize={20}>
          <main className="flex h-full flex-col overflow-hidden bg-white p-6">{Right}</main>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  )
}

export default HomeLayout
