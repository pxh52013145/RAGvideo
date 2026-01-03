import { useState } from 'react'
import { Database, Video } from 'lucide-react'

import NoteForm from '@/pages/HomePage/components/NoteForm'
import NoteHistory from '@/pages/HomePage/components/NoteHistory'
import { useTaskStore } from '@/store/taskStore'

const RagVideoPanel = () => {
  const [tab, setTab] = useState<'ingest' | 'tasks'>('ingest')

  const tasks = useTaskStore(state => state.tasks)
  const currentTaskId = useTaskStore(state => state.currentTaskId)
  const setCurrentTask = useTaskStore(state => state.setCurrentTask)

  return (
    <>
      <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between">
        <h2 className="font-semibold text-slate-800 flex items-center gap-2">
          <Database className="w-4 h-4 text-brand-500" />
          视频库
        </h2>
        <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
          {tasks.length} 项
        </span>
      </div>

      <div className="p-4 bg-slate-50 border-b border-slate-100">
        <div className="grid grid-cols-2 gap-1 bg-slate-200/50 p-1 rounded-lg">
          <button
            type="button"
            onClick={() => setTab('ingest')}
            className={[
              'text-xs font-semibold py-2 rounded-md transition-all flex items-center justify-center gap-1.5',
              tab === 'ingest' ? 'bg-white text-brand-700 shadow-sm' : 'text-slate-500 hover:text-slate-700',
            ].join(' ')}
          >
            <Video className="w-3.5 h-3.5" />
            添加视频
          </button>
          <button
            type="button"
            onClick={() => setTab('tasks')}
            className={[
              'text-xs font-semibold py-2 rounded-md transition-all',
              tab === 'tasks' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700',
            ].join(' ')}
          >
            任务列表
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {tab === 'ingest' ? (
          <div className="p-4">
            <NoteForm />
          </div>
        ) : (
          <div className="p-4">
            <NoteHistory onSelect={setCurrentTask} selectedId={currentTaskId} />
          </div>
        )}
      </div>
    </>
  )
}

export default RagVideoPanel

