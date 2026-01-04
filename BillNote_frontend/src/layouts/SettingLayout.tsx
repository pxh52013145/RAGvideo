import { Outlet } from 'react-router-dom'
import React from 'react'
import logo from '@/assets/icon.svg'

interface ISettingLayoutProps {
  Menu: React.ReactNode
}
const SettingLayout = ({ Menu }: ISettingLayoutProps) => {
  return (
    <div className="flex h-full w-full bg-slate-50 text-slate-900">
      <aside className="w-80 lg:w-96 bg-white border-r border-slate-200 flex flex-col z-10 shadow-sm">
        <header className="h-16 px-6 border-b border-slate-100 flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl overflow-hidden bg-slate-100 flex items-center justify-center">
            <img src={logo} alt="logo" className="h-full w-full object-contain" />
          </div>
          <div className="font-semibold text-slate-800">设置</div>
        </header>

        <div className="flex-1 overflow-auto p-4">{Menu}</div>
      </aside>

      <main className="flex-1 overflow-hidden bg-white">
        <Outlet />
      </main>
    </div>
  )
}
export default SettingLayout
